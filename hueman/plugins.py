import requests


class Colour(object):
    """ Lookup a colour RGB, convert to XYZ and update the state. """
    def __call__(self, controller, name):
        r = requests.get('http://www.colourlovers.com/api/colors?keywords={}&numResults=1&format=json'.format(name)).json()
        return controller.rgb(r[0]['hex'])


class RGB(object):
    def __call__(self, controller, val):
        def rgb2xyz(rgb):
            """
                0.4887180  0.3106803  0.2006017
                0.1762044  0.8129847  0.0108109
                0.0000000  0.0102048  0.9897952
            """
            for k, v in rgb.iteritems():
                rgb[k] = v / 255
            x = rgb['r'] * 0.4887180 + rgb['g'] * 0.3106803 + rgb['b'] * 0.2006017
            y = rgb['r'] * 0.1762044 + rgb['g'] * 0.8129847 + rgb['b'] * 0.0108109
            z = rgb['r'] * 0.0000000 + rgb['g'] * 0.0102048 + rgb['b'] * 0.9897952
            return [x, y, z]
        rgb = None
        if isinstance(val, basestring):
            if val.startswith('#'):
                val = val[:1]
            rgb = {
                'r': int(val[0:2], 16),
                'g': int(val[2:4], 16),
                'b': int(val[4:6], 16),
            }
        elif isinstance(val, tuple):
            rgb = {
                'r': val[0],
                'g': val[1],
                'b': val[2],
            }
        elif isinstance(val, dict) and 'r' in val and 'g' in val and 'b' in val:
            rgb = val
        if rgb is None:
            raise ValueError("Cannot parse RGB value '{}'".format(val))
        val = rgb2xyz(rgb)
        controller.xy(val[:2])
