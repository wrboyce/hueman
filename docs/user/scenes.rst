Scenes
======

Scenes are a culmination of Groups and Presets. They allow you apply a set of actions to predefined a light. As usual, scenes are defined in your config file.

Setting the Scene
-----------------

Scenes are defined like so, mapping lights/groups to states:

..  code-block:: yaml

    scenes:
      work_mode:
        office:
          bri: 240
          ct: 100
        bedroom:
          on: No

Each state is applied in the same manner as a preset, and targets are resolved using the same rules as ``find``.


Reliving the Moment
-------------------

Brining a scene back is the same as invoking a prefix, only you do not need to (and it would not make sense to) define a target::

    % hueman work mode
