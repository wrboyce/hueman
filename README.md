hueman
======

A human interface for managing your hues.


Overview
--------

Blurb.


Usage
-----

### Configuration

You will need to perform some basic configuration in `~/.hueman.yml`:

    hues:
      - hostname: limelight.fbcnt.in
        password: your-app-hash-here

### Commandline

List your Lights & Groups:

    % hueman -L
    Bedroom:
        His
        Hers
    Lounge:
        Ceiling
        FloorLamp
    Office:
        DeskLamp
        FloorLamp
    % hueman -Lv
    [3] Bedroom:
        [3] His (<<state>>)
        [4] Hers (<<state>>)
    [2] Lounge:
        [5] Ceiling (<<state>>)
        [2] FloorLamp (<<state>>)
    [1] Office:
        [1] DeskLamp (<<state>>)
        [6] FloorLamp (<<state>>)

Turn all the lights on

    % hueman -a on

#### Finding the Light

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

#### Presets

Invoking presets is easy...

    % hueman -a red alert

Or just setting values directly:

    % hueman -a brightness:100% colour:blue

And, you guessed it… Combining the two:

    % hueman -a red alert colour:yellow brightness:20%

Some of those words are mighty long, so you can shorten them to their shortest unique string:

    $ hueman -a bri:150 hue:0


Settings
--------

### Presets

Hueman comes with a set of predefined presets, but you can also define your own. Add them to the `presets` directive in your `hueman.yml`:

    presets:
      wake_up:
        brightness: 100%
        temp: 0%
      underwater:
        color: blue
        brightness: 30%


### Transitions

Presets can transition between two states, the implied `time` for the initial `state` is `0`:

    presets:
      wake_up_slowly:
        - brightness: 30%
          temp: 80%
        - brightness: +300%
          temp: 0%
          time: 30m


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

`colour` should accept most colours you can think of, express them as one word and be creative!

    >>> light.colour('red')
    >>> light.colour('darkred')

If you can't find the colour you're looking for, then simply you can send an rgb:

    >>> light.rgb('FF0000')
    >>> light.rgb('#00FF00')

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

I haven't quite decided how `GroupController` will work yet, but it'll allow you to dispatch commands to arbitary groups of lights. Something like this:

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

* refactor & add setup.py
* commandline entrypoint
* test with a real Hue!
* unit tests
* group creation/management
* schedule management
* api: reading state from Hue/Group/GroupController
* api: `parse_colour` -- check for colours in `_nstate`
* api: add `Controller.reset` to drop `_nstate`
* redo parse_XX functions and 'filter' parameter (preprocessor -- always a method)
* plugin loading
* Move ("rgb" and "colour") into `Plugins` (`Class(**settings)(target)`)
* `Group(Controller, GroupController)`?
* `Hueman` should accept host/user args directly
* move command processing onto `Controller._parse_command`
* protect against access to _vars in above
