import unittest

import mock

from hueman.entities import Light


class TestLight(unittest.TestCase):
    def setUp(self):
        self.id = 'ID'
        self.name = 'NAME'
        self.light = Light(mock.MagicMock(), self.id, self.name, {})

    def test_reset(self):
        self.light._cstate = {'on': False}
        self.light._nstate = {'on': True}
        self.light.reset()
        self.assertEqual(self.light._cstate, {'on': False})
        self.assertEqual(self.light._nstate, {})

    def test_state(self):
        self.assertTrue(self.light.state is not self.light._cstate)
        self.assertEqual(self.light.state, self.light._cstate)

    def test_set_attribute(self):
        self.light.bri(100)
        self.assertEqual(self.light._nstate['bri'], 100)

    def test_set_attribute_commit(self):
        self.light.bri(100, commit=True)
        self.assertEqual(self.light._cstate['bri'], 100)

    def test_get_attribute(self):
        self.light._cstate = {'bri': 100}
        self.assertEqual(self.light.bri(), 100)

    def test_set_int_attribute_min(self):
        self.light.bri(-10)
        self.assertEqual(self.light._nstate['bri'], 0)

    def test_set_int_attribute_max(self):
        self.light.bri(500)
        self.assertEqual(self.light._nstate['bri'], 255)

    def test_set_int_attribute_abs_percentage(self):
        self.light.bri('50%')
        self.assertEqual(self.light._nstate['bri'], 127)

    def test_set_int_attribute_rel_percentage(self):
        self.light._cstate = {'bri': 200}
        self.light.bri('~50%')
        self.assertEqual(self.light._nstate['bri'], 100)

    def test_set_int_attribute_add_percentage(self):
        self.light._cstate = {'bri': 200}
        self.light.bri('+25%')
        self.assertEqual(self.light._nstate['bri'], 250)

    def test_set_int_attribute_sub_percentage(self):
        self.light._cstate = {'bri': 200}
        self.light.bri('-25%')
        self.assertEqual(self.light._nstate['bri'], 150)

    def test_set_int_attribute_invalid(self):
        self.assertRaises(ValueError, self.light.bri, 'abc')

    def test_set_readonly_attribute(self):
        self.assertRaises(ValueError, self.light.reachable, False)

    def test_set_time_attribute_float(self):
        self.light.transitiontime(0.1)
        self.assertEqual(self.light._nstate['transitiontime'], 1)

    def test_set_time_attribute_str(self):
        self.light.transitiontime('0.1')
        self.assertEqual(self.light._nstate['transitiontime'], 1)

    def test_set_time_attribute_str_secs(self):
        self.light.transitiontime('1s')
        self.assertEqual(self.light._nstate['transitiontime'], 10)

    def test_set_time_attribute_str_mins(self):
        self.light.transitiontime('1m')
        self.assertEqual(self.light._nstate['transitiontime'], 600)

    def test_set_time_attribute_str_mins_secs(self):
        self.light.transitiontime('1m30s')
        self.assertEqual(self.light._nstate['transitiontime'], 900)

    def test_set_time_attribute_str_mins_secs_decimal(self):
        self.light.transitiontime('1.5m')
        self.assertEqual(self.light._nstate['transitiontime'], 900)

    def test_set_time_attribute_invalid(self):
        self.assertRaises(ValueError, self.light.transitiontime, 'abc')

    def test_set_alias_attribute(self):
        self.light.brightness(100)
        self.assertEqual(self.light._nstate['bri'], 100)

    def test_preset(self):
        self.light._bridge._preset.return_value = {'bri': 255}
        self.light.preset('bright')
        self.light._bridge._preset.assert_called_once_with('bright')
        self.assertEqual(self.light._nstate['bri'], 255)

    def test_commit(self):
        self.light._cstate = {'on': False}
        self.light._nstate = {'on': True}
        self.light.commit()
        self.light._bridge._put.assert_called_once_with('lights/ID/state', {'on': True})
        self.assertEqual(self.light._cstate, {'on': True})
        self.assertEqual(self.light._nstate, {})

    def test_preset_transition(self):
        self.light._bridge._preset.return_value = [{'bri': 0}, {'bri': 255, 'transitiontime': 10}]
        self.light.preset('slow_bright')
        self.light._bridge._preset.assert_called_once_with('slow_bright')
        self.light._bridge._put.assert_called_once_with('lights/ID/state', {'transitiontime': 0.0, 'bri': 0})
        self.assertEqual(self.light._nstate['bri'], 255)
        self.assertEqual(self.light._nstate['transitiontime'], 100)
