Groups
======

Brighter Together
-----------------

Due to limitations in the Philips Hue API, we have to define groups client-side. Groups are defined in your config file:

..  code-block:: yaml

    groups:
      bedroom:
        - bedroom.hers
        - bedroom.his
      office:
        - office.desklamp
        - office.floorlamp


Introducing --group
-------------------

Now you have groups configured, you can reference them with the ``-g``/``--group`` argument::

    % hueman -g office on
    % hueman -g bedroom,office off


Another Trick up --find's Sleeve
--------------------------------

Find can also reference groups::

    % hueman -f office on
    % hueman -f bedroom,office on

Note that when using find, groups will take precedence over lights.
