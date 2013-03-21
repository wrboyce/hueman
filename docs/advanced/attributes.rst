Attributes
==========

We touched on modifying light attributes in the getting started section; in this section we will look at some more advanced means Hueman can modify the state of lights offering a greater degree of flexibility.

Relative Values and Percentages
-------------------------------

The following attributes (and their aliases) can be modified using percentages and relative values:

* bri
* hue
* sat
* ct

Supported operations are:

* Absolute percentage::

    % hueman -a bri:100%  # set brightness to 255

* Relative percentage::

    % hueman -a bri:~50%  # set brightness to 50% of current value, 127

* Addition and Subtraction::

    % hueman -a bri:+23  # increase brightness by 23 -> 150
    % hueman -a bri:-50  # decreate brightness by 50 -> 100

* You can also do relative percentage addition and substraction::

    % hueman -a bri:-50%  # decreate brightness by 50% -> 50
    % hueman -a bri:+200%  # increase brightness by 200% -> 150

These values are also clippped within their known ranges, to avoid any weird behaviour::

    % hueman -a bri:500  # brightness is set to known max, 255

Fancy Durations
---------------

The default unit for ``transitiontime`` is tenths of a second, not very Hueman at all. Hueman understands seconds `and` minutes::

    % hueman -a bright transitiontime:900  # 900 tenths of a second (or 90 seconds, or one and a half minutes)
    % hueman -a bright time:1m30s  # as above, but much more readable

Note that ``time`` is simply an alias of ``transitiontime``, both keys will accept either format of duration.
