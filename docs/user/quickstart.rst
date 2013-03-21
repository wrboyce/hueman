Quick Start
===========

Ok, time to get your hands dirty. This section assumes that you already have Hueman installed and configured. If you do not, head over to the Installation or Configuration section.


Finding the Light
-----------------

Now hueman can talk to your bridges, listing the available lights is simple::

    % hueman -L
    bedroom.hers
    bedroom.his
    office.desklamp
    office.floorlamp

Now we know what we're dealing with, there are a few ways to direct commands to lights, the most direct of which of which is ``-l``/``--light``::

    % hueman -l bedroom.hers,bedroom.his on
    % hueman -l bedroom.hers -l bedroom.his off

Next up is the ``-f``/``--find``, which allows you to match lights with more flexibility, such as:

* Full name::

    % hueman -f office.desklamp,office.floorlamp on

* Simple Wildcards::

    % hueman -f office.* on

* Regular Expressions::

    % hueman -f /office/ on
    % hueman -f /^office\.(desk|floor)lamp$/ on

And finally, sometimes all you need is a sledgehammer::

    % hueman -a on


The Colour of Magic
-------------------

The Hue bulbs are mighty versatile things, and Hueman aims to match that. You can control any aspect of the bulbs via Hueman with a very simply syntax: ``key:val``.

The bulbs currently expose the following attributes:

* bri
* hue
* sat
* xy
* ct
* transitiontime
* effect
* colormode

In addition, Hueman provides these aliases:

* brightness (bri)
* saturation (sat)
* time (transitiontime)
* mode (colormode)

You can also shorten any value to its shortest unique prefix (b -> bri, s -> sat)

Refer to the `Hue API docs <http://developers.meethue.com>`_ for more information on these attributes.

    ::

    % hueman -a bri:100 sat:100 time:10
