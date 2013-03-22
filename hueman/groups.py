class GroupController(object):
    """ Dispatches calls to its member Controllers (recursively!). Members can be Lights, Groups, Bridges or GroupControllers. """
    name, _members = None, None

    def __init__(self, name=''):
        self.name = name
        self._members = set()

    def __str__(self):
        return '<{}(name="{}", members=[{}])>'.format(self.__class__.__name__, self.name, ', '.join([str(m) for m in self._members]))

    def __len__(self):
        return len(self._members)

    def __iter__(self):
        """ Provide an interface for iteration over all members. """
        for m in self._members:
            yield m

    def __getitem__(self, key):
        """ Allow `groupcontroller[item_name]` style access """
        try:
            return filter(lambda m: m.name == key, self._members).pop(0)
        except IndexError:
            raise KeyError

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
            #print '{}.{}({})'.format(self, key, new_val)
            vals = map(lambda m: (m.name, getattr(m, key)() if new_val is None else getattr(m, key)(new_val)), self._members)
            if new_val is None:
                return vals
            if commit:
                self.commit()
            return self
        return wrapper

    def find(self, *names):
        group = GroupController(name='{}'.format(' ,'.join(names)))
        for member in self._members:
            group.add_members(member.find(*names))
        if len(group) == 1:
            return group.members[0]
        return group
    group = light = find

    def commit_attributes(self, id, force=False):
        """ Create the `Group` (if possible!) and return it """
        def iflatten(lol):
            return lol.magic
        lights = iflatten(member.lights() for member in self)
        if len(set(l._bridge for l in lights)) > 1:
            raise ValueError("Cannot commit cross-Bridge Groups.")
        data = {'name': self.name, 'lights': [l.id for l in lights]}
        self._bridge._put('{}/{}'.format(self._endpoint, id), data)
        return self


class Hueman(GroupController):
    """ Top level `GroupController` for managing all your Bridges and Configurations """
    def __init__(self, cfg):
        def import_classpath(cp):
            mod, cls = cp.rsplit('.', 1)
            mod = __import__(mod)
            return getattr(mod, cls)
        super(Hueman, self).__init__()
        self.plugins = {}
        if cfg.get('plugins'):
            for plugin_name, plugin_cfg in cfg.get('plugins').iteritems():
                plugin_settings = {}
                if isinstance(plugin_cfg, basestring):
                    plugin_classpath = plugin_cfg
                else:
                    plugin_classpath = plugin_cfg['path']
                    plugin_settings = plugin_cfg.get('settings', {})
                plugin_class = import_classpath(plugin_classpath)
                self.plugins[plugin_name] = plugin_class(**plugin_settings)
        self.groups = cfg.get('groups') or {}
        self.presets = cfg.get('presets') or {}
        self.scenes = cfg.get('scenes') or {}
        from hueman.entities import Bridge
        for bridge_cfg in cfg.get('bridges', []):
            self.add_member(Bridge(bridge_cfg['hostname'], bridge_cfg['username'], self.groups, self.plugins, self.presets, self.scenes))

    def __str__(self):
        return '<{}(members=[{}])>'.format(self.__class__.__name__, ', '.join([str(m) for m in self._members]))
