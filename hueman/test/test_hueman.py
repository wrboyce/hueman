import unittest

import mock

from hueman.groups import Hueman


class TestHueman(unittest.TestCase):
    def setUp(self):
        cfg = {'bridges': [{'hostname': 'limelight01.example.com', 'username': 'your-app-hash-here'}, {'hostname': 'limelight02.example.com', 'username': 'your-app-hash-here'}]}
        with mock.patch('hueman.entities.Bridge._get') as _get:
            _get.return_value = {u'lights': {u'1': {u'name': u'light-1', u'swversion': u'65003148', u'pointsymbol': {u'1': u'none', u'3': u'none', u'2': u'none', u'5': u'none', u'4': u'none', u'7': u'none', u'6': u'none', u'8': u'none'}, u'state': {u'on': False, u'hue': 13122, u'colormode': u'ct', u'effect': u'none', u'alert': u'none', u'xy': [0.5119, 0.4147], u'reachable': True, u'bri': 159, u'sat': 211, u'ct': 467}, u'type': u'Extended color light', u'modelid': u'LCT001'}, u'3': {u'name': u'light-3', u'swversion': u'65003148', u'pointsymbol': {u'1': u'none', u'3': u'none', u'2': u'none', u'5': u'none', u'4': u'none', u'7': u'none', u'6': u'none', u'8': u'none'}, u'state': {u'on': False, u'hue': 13122, u'colormode': u'ct', u'effect': u'none', u'alert': u'none', u'xy': [0.5119, 0.4147], u'reachable': True, u'bri': 144, u'sat': 211, u'ct': 467}, u'type': u'Extended color light', u'modelid': u'LCT001'}, u'2': {u'name': u'light-2', u'swversion': u'65003148', u'pointsymbol': {u'1': u'none', u'3': u'none', u'2': u'none', u'5': u'none', u'4': u'none', u'7': u'none', u'6': u'none', u'8': u'none'}, u'state': {u'on': False, u'hue': 13122, u'colormode': u'hs', u'effect': u'none', u'alert': u'none', u'xy': [0.5119, 0.4147], u'reachable': True, u'bri': 144, u'sat': 211, u'ct': 467}, u'type': u'Extended color light', u'modelid': u'LCT001'}}, u'config': {}, u'groups': {}, u'schedules': {}}  # noqa
            self.hueman = Hueman(cfg)

    def test_set_attribute(self):
        self.hueman.bri(50)
        self.assertEqual(self.hueman['limelight01.example.com']._nstate['bri'], 50)
        self.assertEqual(self.hueman['limelight02.example.com']._nstate['bri'], 50)
