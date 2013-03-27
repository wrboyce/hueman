import colorsys

import requests


class Colour(object):
    """ Lookup a colour RGB, convert to XYZ and update the state. """
    def __call__(self, controller, name):
        r = requests.get('http://www.colourlovers.com/api/colors?keywords={0}&numResults=1&format=json'.format(name)).json()
        return controller.rgb(r[0]['hex'])


class RGB(object):
    def __call__(self, controller, val):
        # TODO: this needs a fair bit of work...
        def _norm(rgb):  # this function should check what it is normalising
            d = {}
            for k, v in rgb.iteritems():
                d[k] = float(v) / 255
            return d
        if isinstance(val, basestring):
            if val.startswith('#'):
                val = val[:1]
            rgb = {
                'r': int(val[0:2], 16),
                'g': int(val[2:4], 16),
                'b': int(val[4:6], 16),
            }
        elif isinstance(val, tuple):  # again, check the values
            rgb = {
                'r': val[0],
                'g': val[1],
                'b': val[2],
            }
        elif isinstance(val, dict) and 'r' in val and 'g' in val and 'b' in val:
            rgb = val  # one more time, check the values
        if rgb is None:
            raise ValueError("Cannot parse RGB value '{0}'".format(val))
        rgb = _norm(rgb)
        hue, _lightness, sat = colorsys.rgb_to_hls(rgb['r'], rgb['g'], rgb['b'])
        controller.hue(hue * 65535).sat(sat * 255)
