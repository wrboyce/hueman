from __future__ import print_function

import argparse
import inspect
from operator import attrgetter
import os
import re

import yaml

from hueman.groups import GroupController, Hueman


def cli(args=None):
    """ Commandline Entrypoint """
    ## Build arguments from configfile & commandline
    preset = argparse.ArgumentParser()
    preset.add_argument('-c', '--config', action='store', dest='cfg_file', default='~/.hueman.yml')

    # Inventory
    preset.add_argument('-L', '--list')
    preset.add_argument('-p', action='store_true', dest='plugins')
    preset.add_argument('-P', action='store_true', dest='presets')
    preset.add_argument('-s', action='store_true', dest='scenes')
    preset.add_argument('-v', '--verbose', action='store_true')

    # Targets
    preset.add_argument('-a', '--all', action='store_true', help='Apply command to all lights')
    preset.add_argument('-f', '--find', action='store', help='Find a group/light - supports wildcards and /regex/')
    preset.add_argument('-g', '--group', action='store', dest='group', help='Apply command to a specific group')
    preset.add_argument('-l', '--light', action='store', help='Apply command to a specific light')

    # Command
    preset.add_argument('command', metavar='COMMAND', nargs='*')
    args = preset.parse_args(args)

    ## Initialise the Hueman
    hue = loader(args.cfg_file)

    if args.list:
        if 'a' in args.list:
            args.all = True
        if args.all or 'l' in args.list:
            print("Lights")
            print("======")
            lights = set(light for bridge, lights in hue.lights() for light in lights)
            for light in sorted(lights, key=attrgetter('name' if not args.verbose else 'id')):
                out = '{0}'.format(light.name)
                if args.verbose:
                    out = '[{0}] {1} (<<{2}>>)'.format(light.id, out, light.state)
                print(out)
            print()
        if args.all or 'p' in args.list:
            print("Plugins")
            print("=======")
            for plugin_name, plugin in hue.plugins.iteritems():
                plugin_signature = '{0}'.format(plugin_name)
                plugin_argspec = inspect.getargspec(plugin.__call__)[0][2:]
                if plugin_argspec:
                    plugin_signature = '{0}:{1}'.format(plugin_signature, ','.join(plugin_argspec))
                if args.verbose:
                    plugin_signature = '{0}\n    {1}'.format(plugin_signature, plugin.__doc__.strip())
                print(plugin_signature)
            print()
        if args.all or 'P' in args.list:
            print("Presets")
            print("=======")
            print(yaml.dump(hue.presets))
        if args.all or 's' in args.list:
            print("Scenes")
            print("======")
            print(yaml.dump(hue.scenes))
        exit()
    ## Find the target groups/lights
    if not any([args.all, args.find, args.group, args.light]):
        return  # must specify a target! TODO scene
        try:
            return hue.scene('_'.join(args.command))
        except KeyError:
            exit('Must specify a target or valid scene')
    target = hue if args.all else GroupController(name='cli')
    if args.find:
        targets = []
        for t in args.find.split(','):
            if not (t.startswith('/') and t.endswith('/')) and ('*' in t or '?' in t or '#' in t):  # wildcards
                t = t.replace('*', '.*').replace('?', '.').replace('#', '[0-9]')
                t = '/{0}/'.format(t)
            if t[0] == '/' and t[-1] == '/':
                t = re.compile(t.strip('/'), re.I)
            targets.append(t)
        target.add_members(hue.find(*targets))
    if args.group:
        for g in args.group.split(','):
            target.add_member(hue.group(g))
    if args.light:
        for l in args.light.split(','):
            target.add_member(hue.light(l))
    ## process the command
    target._apply_command(args.command).commit()


def loader(cfg_file='~/.hueman.yml'):
    """ Shortcut function to furnish you with a configured `Hueman`. """
    cfg = yaml.load(open(os.path.expanduser(cfg_file)).read())
    return Hueman(cfg)
