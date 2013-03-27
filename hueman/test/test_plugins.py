import colorsys
import unittest

import mock

from hueman.plugins import Colour, RGB


class TestColourPlugin(unittest.TestCase):
    def setUp(self):
        self.controller = mock.Mock()

    def test_colour(self):
        Colour._get_colour = mock.Mock(return_value='ff0000')
        colour = Colour()
        colour(self.controller, 'red')
        colour._get_colour.assert_called_once_with('red')
        self.controller.rgb.assert_called_once_with('ff0000')


class TestRGBPlugin(unittest.TestCase):
    def setUp(self):
        self.controller = mock.Mock()
        self.rgb = RGB()

    def _test_for_red(self):
        hue, _lightness, saturation = colorsys.rgb_to_hls(1.0, 0, 0)
        self.controller.hue.assert_called_once_with('{0}%'.format(hue * 100))
        self.controller.sat.assert_called_once_with('{0}%'.format(saturation * 100))

    def test_rgb_web(self):
        self.rgb(self.controller, 'ff0000')
        self._test_for_red()

    def test_rgb_web_hash(self):
        self.rgb(self.controller, '#ff0000')
        self._test_for_red()

    def test_rgb_dict_255(self):
        self.rgb(self.controller, {'r': 255, 'g': 0, 'b': 0})
        self._test_for_red()

    def test_rgb_tuple_255(self):
        self.rgb(self.controller, (255, 0, 0))
        self._test_for_red()

    def test_rgb_invalid(self):
        self.assertRaises(ValueError, self.rgb, self.controller, 'red')
