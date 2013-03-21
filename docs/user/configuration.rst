Initial Configuration
=====================

Adding Your Bridges
-------------------

The bare minimum configuration for Hueman is letting it know where your bridges are and providing a username for each one. Knowing these details is currently an exercise for the reader.

By default (and who doesn't like defaults?) your configuration file is stored at ``~/.hueman.yml``, add your bridges like so:

..  code-block:: yaml

    bridges:
      - hostname: limelight01.example.com
        username: your-app-hash-goes-here
      - hostname: limelight02.example.com
        username: your-app-hash-goes-here

That's it, you're ready to go!
