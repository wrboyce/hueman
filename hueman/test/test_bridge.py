import unittest

import mock

from hueman.entities import Bridge


class TestBridge(unittest.TestCase):
    def setUp(self):
        group_cfg = {'g1+3': ['light-1', 'light-3']}
        with mock.patch('hueman.entities.Bridge._get') as _get:
            _get.return_value = {u'lights': {u'1': {u'name': u'light-1', u'swversion': u'65003148', u'pointsymbol': {u'1': u'none', u'3': u'none', u'2': u'none', u'5': u'none', u'4': u'none', u'7': u'none', u'6': u'none', u'8': u'none'}, u'state': {u'on': False, u'hue': 13122, u'colormode': u'ct', u'effect': u'none', u'alert': u'none', u'xy': [0.5119, 0.4147], u'reachable': True, u'bri': 159, u'sat': 211, u'ct': 467}, u'type': u'Extended color light', u'modelid': u'LCT001'}, u'3': {u'name': u'light-3', u'swversion': u'65003148', u'pointsymbol': {u'1': u'none', u'3': u'none', u'2': u'none', u'5': u'none', u'4': u'none', u'7': u'none', u'6': u'none', u'8': u'none'}, u'state': {u'on': False, u'hue': 13122, u'colormode': u'ct', u'effect': u'none', u'alert': u'none', u'xy': [0.5119, 0.4147], u'reachable': True, u'bri': 144, u'sat': 211, u'ct': 467}, u'type': u'Extended color light', u'modelid': u'LCT001'}, u'2': {u'name': u'light-2', u'swversion': u'65003148', u'pointsymbol': {u'1': u'none', u'3': u'none', u'2': u'none', u'5': u'none', u'4': u'none', u'7': u'none', u'6': u'none', u'8': u'none'}, u'state': {u'on': False, u'hue': 13122, u'colormode': u'hs', u'effect': u'none', u'alert': u'none', u'xy': [0.5119, 0.4147], u'reachable': True, u'bri': 144, u'sat': 211, u'ct': 467}, u'type': u'Extended color light', u'modelid': u'LCT001'}}, u'config': {}, u'groups': {}, u'schedules': {}}  # noqa
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
