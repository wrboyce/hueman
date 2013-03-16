hueman
======

A human interface for managing your hues.


Usage
-----

**NB:** _the `hueman` command does not yet exist, this exists only as an example/development goal!_

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

Turn all the lights on

    % hueman -a on

Turn a room on

    % hueman -g lounge on

Turn a light on

    % hueman -l bedroom.hers on

The `-l` and `-g` options can be combined to control pseudo-groups of lights

    % hueman -l office.desklamp,bedroom.his -g lounge on
    % hueman -l bedroom.his -l bedroom.hers on
