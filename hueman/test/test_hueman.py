import unittest

import mock

from hueman.groups import Hueman


class TestHueman(unittest.TestCase):
    def setUp(self):
        cfg = {'bridges': [{'hostname': 'limelight01.example.com', 'username': 'your-app-hash-here'}, {'hostname': 'limelight02.example.com', 'username': 'your-app-hash-here'}]}
        with mock.patch('hueman.entities.Bridge._get') as _get:
            _get.return_value = {'lights': {'1': {'name': 'light-1', 'swversion': '65003148', 'pointsymbol': {'1': 'none', '3': 'none', '2': 'none', '5': 'none', '4': 'none', '7': 'none', '6': 'none', '8': 'none'}, 'state': {'on': False, 'hue': 13122, 'colormode': 'ct', 'effect': 'none', 'alert': 'none', 'xy': [0.5119, 0.4147], 'reachable': True, 'bri': 159, 'sat': 211, 'ct': 467}, 'type': 'Extended color light', 'modelid': 'LCT001'}, '3': {'name': 'light-3', 'swversion': '65003148', 'pointsymbol': {'1': 'none', '3': 'none', '2': 'none', '5': 'none', '4': 'none', '7': 'none', '6': 'none', '8': 'none'}, 'state': {'on': False, 'hue': 13122, 'colormode': 'ct', 'effect': 'none', 'alert': 'none', 'xy': [0.5119, 0.4147], 'reachable': True, 'bri': 144, 'sat': 211, 'ct': 467}, 'type': 'Extended color light', 'modelid': 'LCT001'}, '2': {'name': 'light-2', 'swversion': '65003148', 'pointsymbol': {'1': 'none', '3': 'none', '2': 'none', '5': 'none', '4': 'none', '7': 'none', '6': 'none', '8': 'none'}, 'state': {'on': False, 'hue': 13122, 'colormode': 'hs', 'effect': 'none', 'alert': 'none', 'xy': [0.5119, 0.4147], 'reachable': True, 'bri': 144, 'sat': 211, 'ct': 467}, 'type': 'Extended color light', 'modelid': 'LCT001'}}, 'config': {}, 'groups': {}, 'schedules': {}}  # noqa
            self.hueman = Hueman(cfg)

    def test_set_attribute(self):
        self.hueman.bri(50)
        self.assertEqual(self.hueman['limelight01.example.com']._nstate['bri'], 50)
        self.assertEqual(self.hueman['limelight02.example.com']._nstate['bri'], 50)

    def test_plugin_calling(self):
        self.hueman.plugins['colour'] = mock.Mock()
        self.hueman.colour('white')
        self.assertTrue(mock.call(self.hueman['limelight01.example.com'], 'white') in self.hueman.plugins['colour'].mock_calls)
        self.assertTrue(mock.call(self.hueman['limelight02.example.com'], 'white') in self.hueman.plugins['colour'].mock_calls)
        self.assertTrue(len(self.hueman.plugins['colour'].mock_calls) == 2)
