hueman
======

[![Build Status](https://travis-ci.org/wrboyce/hueman.png?branch=master)](https://travis-ci.org/wrboyce/hueman)

A human interface for managing your hues.


Installation
------------

Simple enough, either install directly from the Cheese Shop using the normal methods:

    % pip install hueman

Or if you would rather run the bleeding-edge version:

    % pip install hueman==dev


Contributing
------------

1. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
2. [Fork](https://help.github.com/articles/fork-a-repo) the [repo](https://github.com/wrboyce/hueman) on github and start hacking away :)
3. Write unit tests covering your changes.
4. Add yourself to the [AUTHORS](https://github.com/wrboyce/hueman/blob/master/AUTHORS.md) file.
5. Send a [Pull Request](https://help.github.com/articles/creating-a-pull-request), and possibly nag [the maintainer](https://twitter.com/wrboyce) if it isn't merged in a timely manner!


TODO
----

* schedule management
* api: reading state from GroupControllers
* api: `parse_colour` -- check for colours in `_nstate`
* Move ("rgb" and "colour") into `Plugins` (`Class(**settings)(target)`)
* unittests: GroupController.find, Hueman.scene, Hueman plugin loading, Bridge.preset, Controller._apply_command, hueman.utils
