Plugins
=======

Plugins are where the real fun begins. Hueman comes with a few plugins, but you can also add your own (more on that later). Plugins can be invoked one of two ways, either just the name like a plugin, or name:args - if the plugin requires arguments::

    % hueman -a plugin
    % hueman -a plugin:args


Colour
------

The colour plugin allows you to set your bulbs to a "natural" colour::

    % hueman -a colour:red

RGB
---

If you can't quite find the colour you're looking for, you can instead provide an RGB hex::

    % hueman -a rgb:ff0000

Always Take the Weather With You
--------------------------------

The weather plugin requires some configuration before you can use it. Plugin settings are defined in your config file:

..  code-block:: yaml

    plugins:
      weather:
        settings:
          latitude: 0.0
          longitude: 0.0

::
    % hueman -a weather

Mixing it Up
------------

And, of course, you can mix plugins and attributes (and scenes, and presets...)::

    % hueman -a colour:red bri:75%
    % hueman -a slowly bright colour:red
    % hueman work mode colour:red

Rolling Your Own
----------------

Plugins are a simple class which implement the ``__call__`` function, with settings being passed to the ``__init__`` function::

    class MyPlugin1(object):
        def __call__(self, controller, value):
            controller.brightness(value)


    class MyPlugin2(object):
        def __init__(self, default_brightness):
            self.default_brightness = default_brightness

        def __call__(self, controller):
            self.controller.brightness(default_brightness)

The ``__call__`` method should accept at a minimum one argument (in addition to ``self``) which is the target of the action. Plugins must be registered in your config file:

..  code-block:: yaml

    presets:
      myplug1: module.path.MyPlugin1
      myplug2:
        path: module.path.MyPlugin2
        settings:
          default_brightness: 255

``path`` should be a standard Python import path, and settings is a dictionary passed to ``__init__`` as kwargs. Once registered plugins can be invoked by name::

    % hueman -g bedroom myplug1:100
    % hueman -g office myplug2

Refer to the API Documentation for more information on Plugin authoring.
