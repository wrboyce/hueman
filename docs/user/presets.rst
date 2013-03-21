Presets
=======

Presets allow you to save a lamp state and recall it by name. Hueman comes with some presets, but you can define your own in your config file.

Defining Presets
----------------

Presets can change any attribute normally available::

    presets:
      bright:
        bri: 255
      red:
        sat: 255

Invoking Presets
----------------

Invoking presets is easy, just say their name::

    % hueman -a bright
    % hueman -g bedroom red

Or even combine them::

    % hueman -l office bright red


Transitions
-----------

Presets can also hold two states and have the lights transition into the second state over a predefined time:

..  code-block:: yaml

    presets:
      slowly_bright:
        - bri: 100
        - bri: 255
          time: 100

::

    % hueman -a slowly bright
