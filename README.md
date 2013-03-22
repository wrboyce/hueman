hueman
======

A human interface for managing your hues.


Installation
------------

Simple enough, either install directly from The Cheese Shop using your choice of `easy_install` or `pip`:

    % easy_install hueman
    % pip install hueman

Or, directly from github if you are so inclined:

    % pip install git+https://github.com/wrboyce/hueman.git#egg=hueman
    % pip install https://github.com/wrboyce/hueman/archive/master.tar.gz


Configuration
-------------

The default path for the configuration file is `~/.hueman.yml`, this can be overridden with the `-c`/`--config` options.

### Bridges

You can generate an initial config with `hueman --setup`. This will detect your Hue Bridges and attempt to pair with each one:

    % hueman --setup
    Found bridge at 1.2.3.4
    Press link button on bridge 1.2.3.4
    Waiting...
    Successfully registered with bridge 1.2.3.4

Alternatively, you can add the relevant configuration sections manually:

    bridges:
      - hostname: 1.2.3.4
        username: apphash

### Groups

In the absense of support for creating Groups in the Philips Hue API, we have to settle for client-side groups.

    groups:
      office:
        - office.desklamp
        - office.floorlamp
      bedroom:
        - bedroom.hers
        - bedroom.his

### Plugins

Chances are you won't need to define this section for a while, not least until I have finalised the Plugin API. A plugin is basically a custom class which is passed the controller (Light, Group, Bridge) when it is called.

    class MyBrightPlugin(object):
        def __call__(self, controller):
            controller.brightness('100%')
    class MyBrightnessSettingsPlugin(object)
        def __init__(self, brightness='100%')
            self.brightness = brightness
        def __call__(self, controller):
            controller.brightness('100%')
    class MyBrightnessArgumentPlugin(object):
        def __init__(self, controller, arg):
            controller.brightness(arg)

To load a plugin, you must give it a name and tell hueman where to find it:

    plugins:
      my_bright_plugin: my_hueman_plugins.MyBrightPlugin
      my_variable_brightness_plugin:
        path: my_hueman_plugins.MyBrightnessSettingsPlugin
        settings:
          brightness: 50%
      my_brightness_argument_plugin: my_hueman_plugins.MyBrightnessArgumentPlugin


### Presets

Presets are a simple static state that is applied to the controller. A preset can also define a transition from one state to another.

    my_bright_preset:
      brightness: 100%
    my_bright_transition:
      - brightness: 0
      - brightness: 100%
        time: 10s

### Scenes

Scenes are similar to presets, only they define explicitly which controllers they apply to:

    my_bright_office_scene:
      office.desklamp:
        brightness: 100%
      office.floorlamp:
        brightness: 100%


Usage
-----

### Commandline

The basic usage of hueman from the commandline looks like:

    % hueman [TARGET_OPTS] [COMMAND]

`TARGET_OPTS` specify which controllers the command should be passed to, and `COMMAND` tells describes the new state.

    % hueman -a on  # turn all lights on
    % hueman -a brightness:100% # set all lights to 100% brightness
    % hueman -a my bright plugin # invoke MyBrightPlugin on all lights
    % hueman -a my bright preset # set all lights to preset "my_bright_preset"

Whole words in command are joined together with underscores, and parsed in the following order:

    on -> turn the controller on
    off -> turn the controller off
    some_other_string -> look for a plugin, then a preset
    some_var:new_val -> look for plugin and call with new_val, failing that set some_var to new_val
    some_var:val1,val2 -> as above, but fail is unable to find a plugin

If you omit the `TARGET_OPTS` section, then hueman assumes you are invoking a scene. Any additional options will be applied to all controllers in the scene.

    % hueman my bright office scene
    % hueman my bright office scene saturation:100%

#### Finding the Light

List your Lights & Groups:

    % hueman -L
    bedroom.hers
    bedroom.his
    office.desklamp
    office.floorlamp
    % hueman -Lv
    bedroom.hers (<<state>>)
    bedroom.his (<<state>>)
    office.desklamp (<<state>>)
    office.floorlamp (<<state>>)
    % hueman -Lg
    all:
      bedroom.hers
      bedroom.his
      office.desklamp
      office.floorlamp
    bedroom:
      bedroom.hers
      bedroom.his
    office:
      office.desklamp
      office.floorlamp

The main method of finding targets is via the `-f`/`--find` argument. You can find multiple targets by either passing `-f` multiple times, or passing a comma-seperated list. All names are case intensitive.

    % hueman -f bedroom.his -f bedroom.hers on
    % hueman -f bedroom.his,bedroom.hers

`find` is pretty smart, and can generally work out if you are talking about a group or a light:

    % hueman -f bedroom on
    % hueman -f his,hers on

If you need to be explicit, you can be:

    % hueman -f bedroom. on
    % hueman -f .his,.hers on

You can also use wildcards:

    % hueman -f bedroom.h* on

Or full-blown regexs!

    % hueman -f /^bedroom.h(er|i)s$/ on

If `find` is too vague, you can target groups/lights explicity, too:

    % hueman -g bedroom on
    % hueman -l bedroom.his,bedroom.hers on
    % hueman -g bedroom -l his,hers on


API
---

`hueman` exposes a simple API for getting/setting group/light state. The top-level class is `Hueman`:

    >>> hue = Hueman(TODO)
    >>> light = hue.group('office').light('floorlamp')


`Controller`s expose multiple methods for controlling lights:

* `brightness(int)`
* `hue(int)`
* `saturation(int)`
* `cie(int)`
* `temp(int)`
* `flash(bool|1)`
* `time(time_delta)`
* `colour(colour_str)`
* `rgb(rgbhex_str)`
* `preset(preset_str)`

Access values by calling the relevant method without any arguments:

    >>> light.brightness()
    100

And set by passing a relevant argument:

    >>> light.brightness(10)

`int` values have a few tricks up their sleeves:

    >>> light.brightness()
    100
    >>> light.brightness('100%')  # set absolute percentage
    >>> light.brightness()
    255
    >>> light.brightness(100)
    >>> light.brightness('+20')  # increase relative to current value
    >>> light.brightness()
    120
    >>> light.brightness('-25%')  # decrease current value by percentage
    >>> light.brightness()
    90
    >>> light.brightness('~200%')  # set to percentage of current value
    >>> light.brightness()
    180

`flash(bool|1)` can take three values:

    >>> light.flash(True)  # keep flashing until I say otherwise
    >>> light.flash(1)  # flash once
    >>> light.flash(False)  # no more flashing

`time_delta` units default to 1/10s of a second, but you can override that easily:

    >>> light.time(10)  # delay for one second
    >>> light.time('10m')  # delay for 10 minutes

The `colour` plugin should accept most colours you can think of, express them as one word and be creative!

    >>> light.colour('red')
    >>> light.colour('darkred')

If you can't find the colour you're looking for, then simply you can send an rgb:

    >>> light.rgb('FF0000')
    >>> light.rgb('#00FF00')
    >>> light.rgb({'red': 0, 'green': 0, 'blue': 255})

And of course, you can load presets:

    >>> light.preset('red_alert')

None of these changes take effect until you `commit` them:

    >>> light.brightness('100%')
    >>> light.commit()
    >>> light.brightness('100%', commit=True)  # same as above

They can be chained, too:

    >>> light.brightness('100%').colour('red').commit()
    >>> light.brightness(0).colour('blue', commit=True).brightness('80%').colour('purple').time('30s').commit()

All of the above works with `Bridge`, `Group`, and `Light`:

    >>> hue.preset('red_alert', commit=True)  # Red Alert every light!
    >>> hue.group('bedroom').brightness(255).temp(0).time(0).commit()  # WAKE UP!

Or you can just search `Bridge` directly using `.find` which returns a `GroupController`.

    >>> hue.find(['office.', '.his']).preset('red alert').commit()  # All office lights and bedroom.his
    >>> hue.find(re.compile('\.h(?:er|i)s?$'))  # Regexs, too

### Group Controllers

GroupControllers group together items and allow commands to be dispatched to them as groups.

    >>> gc = GroupController('bedroom.*', '*.*lamp')
    >>> gc.preset('relax').commit()

### Hueman

A superclass of `GroupController` designed to consume a configuration and create the appropriate `Bridge`, `Group` and `Light` instances. Provides transparency across multiple `Bridge`s.

    >>> hueman = Hueman({'bridges': [{'hostname': 'limelight01.example.com', 'username': 'app-hash-01'}, {'hostname': 'limelight02.example.com', 'username': 'app-hash-02'})
    >>> hueman.on()

### Configuration

A configuration is a dictionary with a simple structure, the `plugins` and `presets` sections are optional.

    {'bridges': [
        {'hostname': 'limelight01.example.com', 'username': 'app-hash-01'},
        {'hostname': 'limelight02.example.com', 'username': 'app-hash-02'},
     ],
     'plugins': {
        'colour': 'hueman.plugins.Colour',
        'weather': {
            'path': 'hueman.plugins.Weather',
            'settings': {
                'latitude': 0.0,
                'longitude': 0.0,
            },
        },
     },
     'presets': {
        'full': {'brightness': '100'},
        'sunset': {'colour': 'orange', 'brightness': '60%'},  # presets can call plugins
     }
    }

TODO
====

* unit tests
* schedule management
* api: reading state from GroupControllers
* api: `parse_colour` -- check for colours in `_nstate`
* redo parse_XX functions and 'filter' parameter (preprocessor -- always a method)
* Move ("rgb" and "colour") into `Plugins` (`Class(**settings)(target)`)
* `Group(Controller, GroupController)`?
* `Hueman` should accept host/user args directly
