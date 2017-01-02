import unittest

import mock

from hueman.entities import Bridge


class TestBridge(unittest.TestCase):
    def setUp(self):
        group_cfg = {'g1+3': ['light-1', 'light-3']}
        with mock.patch('hueman.entities.Bridge._get') as _get:
            _get.return_value = {'lights': {'1': {'name': 'light-1', 'swversion': '65003148', 'pointsymbol': {'1': 'none', '3': 'none', '2': 'none', '5': 'none', '4': 'none', '7': 'none', '6': 'none', '8': 'none'}, 'state': {'on': False, 'hue': 13122, 'colormode': 'ct', 'effect': 'none', 'alert': 'none', 'xy': [0.5119, 0.4147], 'reachable': True, 'bri': 159, 'sat': 211, 'ct': 467}, 'type': 'Extended color light', 'modelid': 'LCT001'}, '3': {'name': 'light-3', 'swversion': '65003148', 'pointsymbol': {'1': 'none', '3': 'none', '2': 'none', '5': 'none', '4': 'none', '7': 'none', '6': 'none', '8': 'none'}, 'state': {'on': False, 'hue': 13122, 'colormode': 'ct', 'effect': 'none', 'alert': 'none', 'xy': [0.5119, 0.4147], 'reachable': True, 'bri': 144, 'sat': 211, 'ct': 467}, 'type': 'Extended color light', 'modelid': 'LCT001'}, '2': {'name': 'light-2', 'swversion': '65003148', 'pointsymbol': {'1': 'none', '3': 'none', '2': 'none', '5': 'none', '4': 'none', '7': 'none', '6': 'none', '8': 'none'}, 'state': {'on': False, 'hue': 13122, 'colormode': 'hs', 'effect': 'none', 'alert': 'none', 'xy': [0.5119, 0.4147], 'reachable': True, 'bri': 144, 'sat': 211, 'ct': 467}, 'type': 'Extended color light', 'modelid': 'LCT001'}}, 'config': {}, 'groups': {}, 'schedules': {}}  # noqa
            self.bridge = Bridge('limelight.example.com', 'you-app-hash-here', groups=group_cfg)
            _get.assert_called_once_with('')
        self.bridge._get = mock.Mock()
        self.bridge._put = mock.Mock()

    def test_n_lights(self):
        self.assertEqual(len(self.bridge._lights), 3)

    def test_n_groups(self):
        self.assertEqual(len(self.bridge._groups), 1)

    def test_get_light(self):
        l = self.bridge.light('light-1')
        self.assertEqual(l.id, '1')

    def test_get_group(self):
        g = self.bridge.group('g1+3')
        self.assertEqual(g.name, 'g1+3')
        self.assertEqual(sorted([l.id for l in g.members]), ['1', '3'])

    def test_find_light(self):
        group = self.bridge.find('light-1')
        self.assertEqual(len(group.members), 1)
        self.assertEqual(group.members[0].id, '1')

    def test_find_lights(self):
        group = self.bridge.find('light-1', 'light-2')
        self.assertEqual(sorted([l.id for l in group.members]), ['1', '2'])
