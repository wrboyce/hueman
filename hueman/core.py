import argparse
from itertools import ifilter
import json
import re
import os

import requests
import yaml


class Controller(object):
    _attributes = {
        'on': {
            'key': 'on',
        },
        'brightness': {
            'key': 'bri',
            'filter': 'parse_int',
            'min': 0,
            'max': 255
        },
        'hue': {
            'key': 'hue',
            'filter': 'parse_int',
            'min': 0,
            'max': 65535,
        },
        'saturation': {
            'key': 'sat',
            'filter': 'parse_int',
            'min': 0,
            'max': 255,
        },
        'xyz': {
            'filter': 'parse_xyz',
            'key': 'xy',
        },
        'cie': {
            'key': 'xy',
        },
        'temp': {
            'key': 'ct',
            'filter': 'parse_int',
            'min': '153',
            'max': '500',
        },
        'alert': {
            'key': 'alert',
        },
        'effect': {
            'key': 'effect',
        },
        'time': {
            'key': 'transitiontime',
        },
        'mode': {
            'key': 'colormode',
        },
        'reachable': {
            'key': 'reachable',
            'readonly': True,
        }
    }
    id, name = None, None
    _bridge, _cstate, _nstate = None, None, None

    def __str__(self):
        return '<{}(id={}, name="{}")>'.format(self.__class__.__name__, self.id, self.name)

    ## Given a configured "Bridge", lookup all entities
    @classmethod
    def get_all(cls, bridge):
        objects = GroupController()
        data = bridge._get('{}/get'.format(cls._endpoint))
        for id, dict in data.iteritems():
            objects.add_member(cls(bridge, id=id, name=dict['name'].replace('.', '-')))
        return objects

    def __init__(self, bridge, id, name, cstate=None, nstate=None):
        self._bridge = bridge
        self.id = id
        self.name = name
        self._cstate = cstate  # current state
        self._nstate = nstate if nstate is not None else {}  # next state
        if self._cstate is None:
            self._get_state()

    ## get/put state
    def _get_state(self):
        self._cstate = self._bridge._get('{}/{}/{}'.format(self._endpoint, self.id, self._state_endpoint))['state']

    def commit(self):
        self._bridge._put('{}/{}/{}'.format(self._endpoint, self.id, self._state_endpoint), self._nstate)
        self._cstate = self._nstate.copy()
        self._nstate = {}
        return self

    ## State/value juggling magic
    ## usage: controller.brightness() -> current_brightness
    ##        controller.brightness(100)
    def __getattr__(self, key):
        if key in self._bridge._plugins:
            def pluginwrapper(self, commit=False, **kwargs):
                self._apply_plugin(key, commit, **kwargs)
                return self
            return pluginwrapper
        if not key in Controller._attributes:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, key))
        attr_cfg = Light._attributes[key]
        filter_fun = attr_cfg.get('filter', None)
        if filter_fun is not None and not callable(filter_fun):
            filter_fun = getattr(self, filter_fun, None)
        elif filter_fun is None:
            filter_fun = lambda v, c: v
        def gettersetter(new_val=None, commit=False):  # noqa
            print '{}.{}({})'.format(self, key, new_val)
            if new_val is None:
                return self._cstate[attr_cfg['key']]
            elif attr_cfg.get('readonly', False):
                raise ValueError("Attempted to set readonly value")
            self._nstate[attr_cfg['key']] = filter_fun(new_val, attr_cfg)
            if commit:
                self.commit()
            return self
        return gettersetter

    ## Parsing functions
    def parse_int(self, val, cfg):
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

    def parse_xyz(self, val, _cfg):
        """ Parse a colour in the XYZ space, dropping the [unsupported] Z property. """
        if len(val) > 2:
            val = val[:2]
        return val

    def parse_time(self, val, _cfg):
        """ Parse a time from "shorthand" format: 10m, 30s, 1m30s. """
        time = 0
        if 'm' in val:
            mins, val = val.split('m')
            time += (int(mins) * 60)
        val = val.strip('s')
        time += int(val)
        return (time * 10)

    ## Utilities
    def colour(self, val, commit=False):
        """ Lookup a colour RGB, convert to XYZ and update the state. """
        r = requests.get('http://www.colourlovers.com/api/colors?keywords={}&numResults=1&format=json'.format(val)).json()
        return self.rgb(r[0]['hex'], commit)

    def rgb(self, val, commit=False):
        def rgb2xyz(rgb):
            """
                0.4887180  0.3106803  0.2006017
                0.1762044  0.8129847  0.0108109
                0.0000000  0.0102048  0.9897952
            """
            for k, v in rgb.iteritems():
                rgb[k] = v / 255
            x = rgb['r'] * 0.4887180 + rgb['g'] * 0.3106803 + rgb['b'] * 0.2006017
            y = rgb['r'] * 0.1762044 + rgb['g'] * 0.8129847 + rgb['b'] * 0.0108109
            z = rgb['r'] * 0.0000000 + rgb['g'] * 0.0102048 + rgb['b'] * 0.9897952
            return [x, y, z]
        rgb = None
        if isinstance(val, basestring):
            if val.startswith('#'):
                val = val[:1]
            rgb = {
                'r': int(val[0:2], 16),
                'g': int(val[2:4], 16),
                'b': int(val[4:6], 16),
            }
        elif isinstance(val, tuple):
            rgb = {
                'r': val[0],
                'g': val[1],
                'b': val[2],
            }
        elif isinstance(val, dict) and 'r' in val and 'g' in val and 'b' in val:
            rgb = val
        if rgb is None:
            raise ValueError("Cannot parse RGB value '{}'".format(val))
        val = rgb2xyz(rgb)
        self.xyz(val, commit)
        return self

    def preset(self, name, commit=False):
        """ Load a preset state """
        def _transition(presets):  # Transitions have to be applied immediately [TODO] state-stack for transitions
            for data in presets:
                if data is not presets[-1]:
                    data['time'] = 0
                self._apply(data, True)
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

    def _apply_plugin(self, plugin_name, commit, **kwargs):
        """ Placeholder code to remind me what I was thinking... plugins: name: 'path.to.Plugin'. """
        self._bridge._plugins[plugin_name](self, **kwargs)
        if commit:
            self.commit()
        return self

    def _apply_command(self, command, commit=False):
        """
            Parse a command into a state change, and optionally commit it.

            Commands can look like:
                * on
                * off
                * preset name
                * arg:val arg2:val2
                * preset name arg:val arg2:val2
                * arg:val preset name
                * arg:val preset name arg2:val2
        """
        preset, kvs = [], []
        for s in command:
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
                    for k2 in self._attributes.keys():
                        if k2.startswith(k):
                            k = k2
                            break
                getattr(self, k)(v)
        if commit:
            self.commit()
        return self


class GroupController(object):
    """ Dispatches calls to its member Controllers (recursively!). Members can be Lights, Groups, Bridges or GroupControllers. """
    name, _members = None, None

    def __init__(self, name=''):
        self.name = name
        self._members = set()

    def __str__(self):
        return '<{}(name="{}", members={})>'.format(self.__class__.__name__, self.name, [m for m in self._members])

    def __len__(self):
        return len(self._members)

    def __iter__(self):
        """ Provide an interface for iteration over all members. """
        for m in self._members:
            yield m

    def __getitem__(self, key):
        """ Allow `groupcontroller[item_name]` style access """
        return filter(lambda m: m.name == key, self._members).pop(0)

    def add_member(self, obj):
        """ Add a single Light/Group/Bridge or GroupController to the current GroupController. """
        self._members.add(obj)

    def add_members(self, iter):
        """ Shortcut to `add_member` when you want to add many, will consume any iterable. """
        for obj in iter:
            self.add_member(obj)

    @property
    def members(self):
        return list(self._members)

    ## `Controller` interface
    def __getattr__(self, key):
        """ Dispatch calls to members, values are returned as a list of two-tuples: (name, value). """
        def wrapper(new_val=None, commit=False):
            print '{}.{}({})'.format(self, key, new_val)
            vals = map(lambda m: (m.name, getattr(m, key)() if new_val is None else getattr(m, key)(new_val)), self._members)
            if new_val is None:
                return vals
            if commit:
                self.commit()
            return self
        return wrapper

    def find(self):
        raise NotImplemented
    groups = lights = find


class Group(Controller):
    _lights = None

    _endpoint = 'groups'
    _state_endpoint = 'action'

    @classmethod
    def get_all(cls, bridge, lights):
        groups = super(Group, cls).get_all(bridge)
        for g in groups:
            lights = filter(lambda l: l.id in g._member_ids, lights)
            g._lights = {l.name: l for l in lights}
        return groups

    def light(self, name):
        if name is None:
            return self._lights.values()
        return self._lights[name]
    __getitem__ = light

    def lights(self, *names):
        return filter(lambda l: l.name in names, self._lights.values())


class Light(Controller):
    _endpoint = 'lights'
    _state_endpoint = 'state'


class Bridge(Group):
    def __init__(self, hostname, username, plugins=None, presets=None):
        self._bridge = self
        self.id = 0  # Group with id=0 is reserved for all lights in system (conveniently)
        self._hostname = self.name = hostname
        self._username = username
        self._get_members()
        self._plugins = plugins if plugins is not None else {}
        self._presets = presets if presets is not None else {}
        self._load_global_presets()

        self._cstate = {}
        self._nstate = {}

    def _get_members(self):
        d = self._get('')
        self._lights = GroupController(name='[{}].lights'.format(self.name))
        for l_id, l_data in d.get('lights', {}).iteritems():
            self._lights.add_member(Light(self, l_id, l_data['name'].replace(' ', '-'), l_data.get('state', None)))
        self._groups = GroupController(name='[{}].groups'.format(self.name))
        for g_id, g_data in d.get('groups', {}).iteritems():
            self._groups.add_member(Group(self, g_id, g_data['name'], g_data.get('state', None)))

    def _load_global_presets(self):
        try:
            cfg_file = file('hueman.yml').read()
            cfg_dict = yaml.load(cfg_file)
            self._presets = cfg_dict.get('presets', {}).update(self._presets)
        except IOError:
            pass

    def _preset(self, name):
        name = name.replace(' ', '_')
        return self._presets[name].copy()

    def _get(self, path):
        return requests.get('http://{}/api/{}/{}'.format(self._hostname, self._username, path)).json()

    def _put(self, path, data):
        print path, data
        d = requests.put('http://{}/api/{}/{}'.format(self._hostname, self._username, path), json.dumps(data)).json()
        print d
        return d

    def group(self, name):
        """ Lookup a group by name, if name is None return all groups. """
        if name is None:
            return self._groups.items()
        return self._groups[name]

    def light(self, name):
        """ Lookup a light by name, if name is None return all lights. """
        if name is None:
            return self._lights.items()
        if '.' in name:
            group, light = name.split('.')
            return self.group(group).light(light)
        else:
            return self._lights[name]

    def _find(self, name):
        """ name: group.light, group., .light, group, light """
        try:
            group_name, light_name = name.split('.')
            if not group_name:
                group_name = None
            if not light_name:
                light_name = None
        except ValueError:
            group_name = name
            light_name = None
        # room.lamp -> group=room light=lamp
        # room. -> group=room light=None
        # .lamp -> group=None light=lamp
        # room -> group=room light=None
        # lamp -> group=lamp light=None -- handle this case now
        if light_name is None and self.group(group_name) is None:
            return self.light(light_name)
        if group_name is None:
            return self.light(light_name)
        return self.group(group_name).light(light_name)

    def find(self, *names):
        group = GroupController()
        for name in names:
            if isinstance(name, re):
                group.add_members(ifilter(lambda l: name.match(l.name) is not None, self.lights()))
            elif isinstance(name, basestring):
                group.add_member(self._find(name))
        return group


class Hueman(GroupController):
    """ Top level `GroupController` for managing all your Bridges and Configurations """
    def __init__(self, cfg):
        def import_classpath(cp):
            mod, cls = cp.rsplit('.', 1)
            mod = __import__(mod)
            return getattr(mod, cls)
        super(Hueman, self).__init__()
        plugins = {}
        presets = {}
        for plugin_name, plugin_cfg in cfg.get('plugins', {}).iteritems():
            plugin_settings = {}
            if isinstance(plugin_cfg, basestring):
                plugin_classpath = plugin_cfg
            else:
                plugin_classpath = plugin_cfg['path']
                plugin_settings = plugin_cfg.get('settings', {})
            plugin_class = import_classpath(plugin_classpath)
            plugins[plugin_name] = plugin_class(**plugin_settings)
        for preset_name, preset_state in cfg.get('presets', {}).iteritems():
            presets[preset_name] = preset_state
        for bridge_cfg in cfg.get('bridges', []):
            self.add_member(Bridge(bridge_cfg['hostname'], bridge_cfg['username'], plugins, presets))


def cli(args):
    ## Build arguments from configfile & commandline
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', action='store', dest='cfg_file', default='~/.hueman.yml')
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-f', '--find', action='store')
    parser.add_argument('-g', '--group', action='store', dest='group')
    parser.add_argument('-l', '--light', action='store')
    parser.add_argument('command', metavar='COMMAND', nargs='*')
    args = parser.parse_args(args)
    cfg = yaml.load(file(os.path.expanduser(args.cfg_file)).read())
    hue = Hueman(cfg)  # init Bridges and Plugins, and load Presets
    ## Find the target groups/lights
    if not any([args.all, args.find, args.group, args.light]):
        return  # must specify a target!
    target = hue if args.all else GroupController(hue)
    if args.find:
        for t in args.find.split(','):
            if '*' in t or '?' in t or '#' in t:  # wildcards
                t = t.replace('*', '.*').replace('?', '.').replace('#', '[0-9]')
                t = '/{}/'.format(t)
            if t[0] == '/' and t[-1] == '/':
                t = re.compile(t.strip('/'), re.I)
            target.add_member(hue.find(t))
    if args.group:
        for g in args.group.split(','):
            target.add_member(hue.group(g))
    if args.light:
        for l in args.light.split(','):
            _target = hue
            if '.' in l:
                g, l = l.split()
                _target = hue.group(g)
            target.add_member(_target.light(l))
    ## process the command
    target._apply_command(args.command).commit()
