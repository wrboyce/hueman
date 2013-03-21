import argparse
from operator import attrgetter
import os
import re

import yaml

from core import GroupController, Hueman


def cli(args=None):
    """ Commandline Entrypoint """
    ## Build arguments from configfile & commandline
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', action='store', dest='cfg_file', default='~/.hueman.yml')
    parser.add_argument('-L', '--list', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-a', '--all', action='store_true', help='Apply command to all lights')
    parser.add_argument('-f', '--find', action='store', help='Find a group/light - supports wildcards and /regex/')
    parser.add_argument('-g', '--group', action='store', dest='group', help='Apply command to a specific group')
    parser.add_argument('-l', '--light', action='store', help='Apply command to a specific light')
    parser.add_argument('command', metavar='COMMAND', nargs='*', help='Scene name/State change')
    args = parser.parse_args(args)

    ## Initialise the Hueman
    hue = loader(args.cfg_file)

    if args.list:
        lights = set(light for bridge, lights in hue.lights() for light in lights)
        for light in sorted(lights, key=attrgetter('name' if not args.verbose else 'id')):
            out = '{}'.format(light.name)
            if args.verbose:
                out = '[{}] {} (<<{}>>)'.format(light.id, out, light.state)
            print out
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
            if t[0] == '/' and t[-1] == '/':
                t = re.compile(t.strip('/'), re.I)
            elif '*' in t or '?' in t or '#' in t:  # wildcards
                t = t.replace('*', '.*').replace('?', '.').replace('#', '[0-9]')
                t = '/{}/'.format(t)
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
    cfg = yaml.load(file(os.path.expanduser(cfg_file)).read())
    return Hueman(cfg)
