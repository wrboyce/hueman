hueman
======

A human interface for managing your hues.


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

Turn a room on

    % hueman -g lounge on

Turn a light on

    % hueman -l bedroom.hers on

The `-l` and `-g` options can be combined to control pseudo-groups of lights

    % hueman -l office.desklamp,bedroom.his -g lounge on
    % hueman -l bedroom.his -l bedroom.hers on

You can get also away with being relatively vague

    % hueman -f his,desklamp,lounge on

Invoking presets is easy...

    % hueman -a red alert

Or just setting values directly:

    % hueman -a brightness:100% colour:blue

And, you guessed it… Combining the two:

    % hueman -a red alert colour:yellow brightness:20%

Some of those words are mighty long:

    $ hueman -a bri:150 hue:0

You can also address `hueman` with _very_ basic natural language:

    % hueman red alert in all rooms
    % hueman set half brightness in office
    % hueman mood lighting, lounge
    % hueman make the lounge pink
    % hueman darkness


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

`hueman` exposes a simple API for getting/setting group/light state. The top-level class is `Hue`:

    >>> hue = Hue(username, password)
    >>> light = hue.group('office').light('floorlamp')


`Hue` exposes methods for controlling lights:

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

All of the above works with `Hue`, `Group`, and `Light`:

    >>> hue.preset('red_alert', commit=True)  # Red Alert every light!
    >>> hue.group('bedroom').brightness(255).temp(0).time(0).commit()  # WAKE UP!

Or you can just search `Hue` directly:

    >>> hue.find(['office.', '.his']).preset('red alert').commit()  # All office lights and bedroom.his
    >>> hue.find(re.compile('\.h(?:er|i)s?$'))  # Regexs, too
