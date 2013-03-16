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
            'key': 'Hue',
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
    _hue, _id, _name, _cstate, _nstate = None, None, None, None, None

    ## Given a configured "Hue", lookup all entities
    @classmethod
    def get_all(cls, hue):
        objects = []
        data = hue._get('{}/get'.format(cls._endpoint))
        for id, dict in data.iteritems():
            objects.append(cls(hue, id=id, name=dict['name']))
        return objects

    def __init__(self, hue, id, name):
        self._hue = hue
        self._id = id
        self._name = name
        self._nstate = {}  # next state
        self._cstate = None  # current state
        self._get_state()

    ## get/put state
    def _get_state(self):
        self._cstate = self._hue._get('{}/{}/{}'.format(self._endpoint, self._id, self._state_endpoint))['state']

    def commit(self):
        self._hue._put('{}/{}/{}'.format(self._endpoint, self._id, self._state_endpoint), self._nstate)
        self._cstate = self._nstate.copy()
        self._nstate = {}
        return self

    ## State/value juggling magic
    ## usage: controller.brightness() -> current_brightness
    ##        controller.brightness(100)
    def __getattr__(self, key):
        if key not in Light._attributes:
            return self.__dict__[key]
        attr_cfg = Light._attributes[key]
        filter_fun = attr_cfg.get('filter', None)
        if filter_fun is None:
            filter_fun = lambda v, c: v
        if not callable(filter_fun):
            filter_fun = getattr(self, filter_fun, None)
        val = self._cstate[attr_cfg['key']]
        def gettersetter(new_val=None, commit=False):  # noqa
            if new_val is None:
                return val
            elif attr_cfg.get('readonly', False):
                raise ValueError("Attempted to set readonly value")
            self._state[attr_cfg['key']] = filter_fun(new_val, attr_cfg)
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
                current_val = self._state[cfg['key']]
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

    def parse_xyz(self, val):
        """ Parse a colour in the XYZ space, dropping the [unsupported] Z property. """
        if len(val) > 2:
            val = val[:2]
        return val

    ## Utilities
    def colour(self, val, commit=False):
        """ Lookup a colour RGB, convert to XYZ and update the state. """
        r = requests.get('http://www.colourlovers.com/api/colors?keywords={}&numResults=1&format=json'.format(val)).json()
        return self.rgb(r['rgb'], commit)

    def rgb(self, val, commit=False):
        def rgb2xyz(rgb):
            """
                0.4887180  0.3106803  0.2006017
                0.1762044  0.8129847  0.0108109
                0.0000000  0.0102048  0.9897952
            """
            for k, v in rgb.iteritems():
                v = v / 255
                if v > 0.04045:
                    v = 1.055 * pow(v, 1 / 2.4) - 0.055
                else:
                    v *= 12.92
                rgb[k] = v
            r, g, b = rgb['r'], rgb['g'], rgb['b']
            x = rgb['r'] * 0.4887180 + rgb['g'] * 0.3106803 + rgb['b'] * 0.2006017
            y = rgb['r'] * 0.1762044 + rgb['g'] * 0.8129847 + rgb['b'] * 0.0108109
            z = rgb['r'] * 0.0000000 + rgb['g'] * 0.0102048 + rgb['b'] * 0.9897952
            return [x, y, z]
        rgb = None
        if isinstance(val, basestring):
            if val.startswith('#'):
                val = val[:1]
            val = {
                'r': int(val[0:2], 16),
                'g': int(val[2:2], 16),
                'b': int(val[4:2], 16),
            }
        elif isinstance(val, tuple):
            val = {
                'r': val[0],
                'g': val[1],
                'b': val[2],
            }
        if rgb is None:
            raise ValueError("Cannot parse RGB value")
        val = rgb2xyz(rgb)
        self.xyz(val, commit)
        return self

    def preset(self, name, commit=False):
        """ Load a preset state """
        preset_data = self._hue._preset(name)
        if isinstance(preset_data, list):
            return self._transition(preset_data)
        return self._apply(preset_data, commit)

    def _transition(self, presets, commit=True):
        for data in presets:
            if data is not presets[-1]:
                data['time'] = 0
            self._apply(data, True)
        return self

    def _apply(self, state, commit=False):
        for key, val in state.iteritems():
            getattr(self, key)(val)
        if commit:
            self.commit()
        return self


class GroupController(object):
    """ Dispatches calls to its member Controllers (recursively!). """
    _name, _members = None, None

    def __init__(self, name=''):
        self._name = name
        self._members = set()

    def __getattr__(self, key):
        def wrapper(v=None):
            map(lambda m: getattr(m, key)(v), self._member)
        return wrapper

    def add_member(self, obj):
        self._members.add(obj)


class Group(Controller):
    _endpoint = 'groups'
    _state_endpoint = 'action'


class Light(Controller):
    _endpoint = 'lights'
    _state_endpoint = 'state'


class Hue(Group):
    def __init__(self, hostname, username):
        self._id = 0  # Group with id=0 is reserved for all lights in system (conveniently)
        self._hostname = hostname
        self._username = username
        self._get_members()
        self._load_presets()

    def _get_members(self):
        self._groups = Group.get_all(self)
        self._lights = Light.get_all(self)

    def _load_presets(self):
        self._presets = {}
        for cfg in ('presets.yml', os.path.expanduser('~/.hueman.yml')):
            try:
                cfg_file = file(cfg).read()
                cfg_dict = yaml.load(cfg_file)
                self._presets.update(cfg_dict.get('presets'), cfg_dict)
            except IOError:
                pass

    def _preset(self, name):
        name = name.replace(' ', '_')
        return self._presets[name].copy()

    def _get(self, path):
        return requests.get('http://{}/api/{}/{}'.format(self._hostname, self._username, path)).json()

    def _put(self, path, data):
        return requests.put('http://{}/api/{}/{}'.format(self._hostname, self._username, path), data).json()

    def groups(self, name=None):
        if name is None:
            return self._groups
        return self._groups[name]
    group = groups

    def lights(self, name=None):
        if name is None:
            return self._lights
        return self._lights[name]
    light = lights

    def get(self, names):
        def find(name):
            if '.' not in name:
                name = '{}.'.format(name)
            group, light = name.split('.')
            if group and light:
                return self.group(group).light(light)
            if group:
                return self.group(group)
            if light:
                return self.light(light)
        if not hasattr(names, '__iter__'):
            names = [names]
        group = GroupController(name=', '.join(names))
        for name in names:
            group.add_member(find(name))
