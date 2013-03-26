from __future__ import print_function

from copy import copy
from itertools import chain, ifilter
import json
import re

import requests
import yaml

from hueman.groups import GroupController


class Controller(object):
    _attributes = {
        'on': {},
        'bri': {
            'preprocessor': 'int',
            'min': 0,
            'max': 255
        },
        'hue': {
            'preprocessor': 'int',
            'min': 0,
            'max': 65535,
        },
        'sat': {
            'preprocessor': 'int',
            'min': 0,
            'max': 255,
        },
        'xy': {},
        'ct': {
            'preprocessor': 'int',
            'min': '153',
            'max': '500',
        },
        'colormode': {},
        'transitiontime': {
            'preprocessor': 'time',
        },
        'reachable': {
            'readonly': True,
        },
        'alert': {},
        'effect': {},
        ## Aliases
        'brightness': 'bri',
        'saturation': 'sat',
        'cie': 'xy',
        'temp': 'ct',
        'time': 'transitiontime',
        'colourmode': 'colormode',
        'mode': 'colormode',
    }

    def __str__(self):
        return '<{0}(id={1}, name="{2}")>'.format(self.__class__.__name__, self.id, self.name)

    def __init__(self, bridge, id, name, cstate=None, nstate=None):
        self._bridge = bridge
        self.id = id
        self.name = name.replace(' ', '-').lower()
        self._cstate = cstate  # current state
        self._nstate = nstate if nstate is not None else {}  # next state
        if self._cstate is None:
            self._get_state()

    ## get/put state
    def _get_state(self):
        self._cstate = self._bridge._get('{0}/{1}/{2}'.format(self._endpoint, self.id, self._state_endpoint))['state']

    def commit(self):
        """ Send any outstanding changes to the Endpoint. """
        self._bridge._put('{0}/{1}/{2}'.format(self._endpoint, self.id, self._state_endpoint), self._nstate)
        self._cstate = self._nstate.copy()
        self._nstate = {}
        return self

    def reset(self):
        """ Drop any uncommitted changes. """
        self._nstate = {}
        return self

    @property
    def state(self):
        """ Return the current state """
        ## TODO only return relevant parts
        return self._cstate.copy()

    ## State/value juggling magic
    ## usage: controller.brightness() -> current_brightness
    ##        controller.brightness(100)
    def __getattr__(self, key):
        """ Complex Logic be here... TODO: Document Me! """
        ## First we check for a plugin
        if key in self._bridge._plugins:
            def pluginwrapper(*args, **kwargs):
                self._apply_plugin(key, *args, **kwargs)
                return self
            return pluginwrapper
        try:
            attr_cfg = Light._attributes[key]
            while isinstance(attr_cfg, basestring):
                key = attr_cfg
                attr_cfg = Light._attributes[attr_cfg]
        except KeyError:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(self.__class__.__name__, key))
        attr_cfg = attr_cfg.copy()
        attr_cfg['key'] = key
        ## Get the preprocessor, if one is defined
        preprocessor = attr_cfg.get('preprocessor', None)
        if isinstance(preprocessor, basestring):  # strings map to self._pp_{preprocessor}
            preprocessor = getattr(self, '_pp_{0}'.format(preprocessor), None)
        elif not callable(preprocessor):  # if not, wrap in a lambda so we can call blindly later
            preprocessor = lambda v, c: v
        ## Return a wrapper for getting/setting the attribute
        def gettersetter(new_val=None, commit=False):  # noqa
            #print('{0}.{1}({2})'.format(self, key, new_val))
            if new_val is None:
                return self._cstate[key]
            elif attr_cfg.get('readonly', False):
                raise ValueError("Attempted to set readonly value '{0}'".format(key))
            self._nstate[key] = preprocessor(new_val, attr_cfg)
            if commit:
                self.commit()
            return self
        return gettersetter

    ## Preprocessors
    def _pp_int(self, val, cfg):
        """ Parse a numerical value, keeping it within a min/max range, and allowing percentage changes. """
        min_val, max_val = cfg.get('min', 0), cfg.get('max', None)
        try:
            val = int(val)
        except ValueError:
            if not val.endswith('%'):
                raise
            change = None  # absolute
            val = val[:-1]
            if val[0] in ('+', '-', '~'):
                change, val = val[0], val[1:]
            val = int(val)
            if change is None:
                if max_val is None:
                    raise ValueError("Cannot set to a percentage of an unknown value!")
                val = (max_val * val) / 100
            else:
                current_val = self._cstate[cfg['key']]
                diff = (current_val * val) / 100
                if change == '-':  # decrease by...
                    val = (current_val - diff)
                if change == '+':  # increase by...
                    val = (current_val + diff)
                if change == '~':  # relative (percentages only)
                    val = diff
        if min_val is not None and val < min_val:
            val = min_val
        if max_val is not None and val > max_val:
            val = max_val
        return val

    def _pp_time(self, val, _cfg):
        """ Parse a time from "shorthand" format: 10m, 30s, 1m30s. """
        time = 0
        try:
            time = float(val)
        except ValueError:
            if 'm' in val:
                mins, val = val.split('m')
                time += (float(mins) * 60)
            val = val.strip('s')
            if val:
                time += float(val)
        return (time * 10)

    def preset(self, name, commit=False):
        """ Load a preset state """
        def _transition(presets):  # Transitions have to be applied immediately [TODO] state-stack for transitions
            for data in presets:
                commit = False
                if data is not presets[-1]:
                    data['time'] = 0
                    commit = True
                self._apply(data, commit)
            return self
        preset_data = self._bridge._preset(name)
        if isinstance(preset_data, list):
            return _transition(preset_data)
        return self._apply(preset_data, commit)

    def _apply(self, state, commit=False):
        for key, val in state.iteritems():
            getattr(self, key)(val)
        if commit:
            self.commit()
        return self

    def _apply_plugin(self, plugin_name, *args, **kwargs):
        self._bridge._plugins[plugin_name](self, *args, **kwargs)
        if kwargs.get('commit', False):
            self.commit()
        return self

    def _apply_command(self, command, commit=False):
        """
            Parse a command into a state change, and optionally commit it.

            Commands can look like:
                * on
                * off
                * plugin name
                * plugin:arg
                * preset name
                * arg:val arg2:val2
                * preset name arg:val arg2:val2
                * arg:val preset name
                * arg:val preset name arg2:val2
        """
        preset, kvs = [], []
        if isinstance(command, basestring):
            command = command.split(' ')
        for s in command:
            if s.startswith('_'):
                continue
            if ':' not in s:
                preset.append(s)
            else:
                kvs.append(s.split(':'))
        if preset:
            preset = ' '.join(preset)
            if preset == 'on':
                self.on(True)
            elif preset == 'off':
                self.on(False)
            else:
                self.preset(preset)
        if kvs:
            for k, v in kvs:
                if k not in self._attributes:
                    for k2 in chain(self._bridge._plugins.keys(), self._attributes.keys()):
                        if k2.startswith(k):
                            k = k2
                            break
                getattr(self, k)(v)
        if commit:
            self.commit()
        return self


class Group(Controller):
    """ Mostly useless currently, until we can create new Groups using the Hue API. """
    _endpoint = 'groups'
    _state_endpoint = 'action'

    def light(self, name):
        """ Lookup a light by name, if name is None return all lights. """
        if name is None:
            group = GroupController(name='{0}.light:{1}'.format(self.name, name))
            group.add_members(self._lights)
            return group
        try:
            return self._lights[name]
        except KeyError:
            return None

    def lights(self, *names):
        if not names:
            return self.light(None)
        return filter(lambda l: l.name in names, self._lights)


class Light(Controller):
    """ A light, a bulb... The fundamental endpoint. """
    _endpoint = 'lights'
    _state_endpoint = 'state'


class Bridge(Group):
    def __str__(self):
        tmpl = '<Bridge(hostname="{0}", groups=[{1}], lights=[{2}]>'
        return tmpl.format(self._hostname, ', '.join([str(g) for g in self._groups]), ', '.join([str(l) for l in self._lights]))

    def __init__(self, hostname, username, groups={}, plugins={}, presets={}, scenes={}):
        self._bridge = self
        self.id = 0  # Group with id=0 is reserved for all lights in system (conveniently)
        self._hostname = self.name = hostname
        self._username = username
        self._get_lights()
        self._build_groups(groups)
        self._plugins = plugins
        self._presets = presets
        self._load_global_presets()

        self._cstate = {}
        self._nstate = {}

    def _get_lights(self):
        d = self._get('')
        self._lights = GroupController(name='[{0}].lights'.format(self.name))
        for l_id, l_data in d.get('lights', {}).iteritems():
            self._lights.add_member(Light(self, l_id, l_data['name'].replace(' ', '-'), l_data.get('state', None)))

    def _build_groups(self, g_cfg):
        self._groups = GroupController(name='[{0}].groups'.format(self.name))
        for g_name, g_lights in g_cfg.iteritems():
            g = GroupController(g_name)
            g.add_members(self.find(*g_lights))
            self._groups.add_member(g)

    def _load_global_presets(self):
        try:
            cfg_file = open('hueman.yml').read()
            cfg_dict = yaml.load(cfg_file)
            self._presets = cfg_dict.get('presets', {}).update(self._presets)
        except IOError:
            pass

    def _preset(self, name):
        name = name.replace(' ', '_')
        return copy(self._presets[name])

    def _get(self, path):
        return requests.get('http://{0}/api/{1}/{2}'.format(self._hostname, self._username, path)).json()

    def _put(self, path, data):
        return requests.put('http://{0}/api/{1}/{2}'.format(self._hostname, self._username, path), json.dumps(data)).json()

    def group(self, name):
        """ Lookup a group by name, if name is None return all groups. """
        if name is None:
            return self._groups
        try:
            return self._groups[name]
        except KeyError:
            matches = filter(lambda g: g.name.startswith(name), self._groups)
            if len(matches) == 1:
                return matches[0]
            raise

    def find(self, *names):
        group = GroupController()
        for name in names:
            if isinstance(name, re._pattern_type):
                group.add_members(ifilter(lambda l: name.match(l.name) is not None, self._lights))
            elif isinstance(name, basestring):
                try:
                    group.add_member(self.group(name))
                except KeyError:
                    try:
                        group.add_member(self.light(name))
                    except KeyError:
                        pass
        return group
