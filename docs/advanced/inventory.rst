Inventory
=========

With so much going on, its useful to be able to see what is available - and what it does.

Plugins
-------

Gathering information about registered plugins is still undecided, but it'll look something like this::

    % hueman -LP
    colour
    rgb
    weather

    % hueman -LPv
    colour:colour_name
        Lookup and set a colour by name
    rgb:rgb_hex
        Set a colour by hex value
    weather
        Pick a colour based on daily weather forecast

    % hueman -h weather
    Pick a colour based on the daily weather forecast
    Required settings: latitude, longitude

Presets
-------

You can list all available presets with ``hueman -Lp``::

    % hueman -Lp
    bright
    red

And view their states by adding the ``verbose`` flag::

    % hueman -Lpv
    bright  {bri: 100%}
    red     {sat: 255}

Scenes
------

Likewise with scenes::

    % hueman -Ls
    work mode
    % hueman -Lsv
    work mode:
        office:     {bri: 240, ct: 100}
        bedroom:    {on: No}
