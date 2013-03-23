import json
import re

from httpretty import HTTPretty, httprettified

from hueman.groups import Hueman


@httprettified
def test_build_lights():
    response = """{
        "lights": {
            "1": {
                "state": {
                    "on": false,
                    "bri": 159,
                    "hue": 13122,
                    "sat": 211,
                    "xy": [
                        0.5119,
                        0.4147
                    ],
                    "ct": 467,
                    "alert": "none",
                    "effect": "none",
                    "colormode": "ct",
                    "reachable": true
                },
                "name": "light-1"
            },
            "2": {
                "state": {
                    "on": true,
                    "bri": 254,
                    "hue": 33863,
                    "sat": 49,
                    "xy": [
                        0.368,
                        0.3686
                    ],
                    "ct": 231,
                    "alert": "none",
                    "effect": "none",
                    "colormode": "ct",
                    "reachable": true
                },
                "name": "light-2"
            },
            "3": {
                "state": {
                    "on": true,
                    "bri": 254,
                    "hue": 33863,
                    "sat": 49,
                    "xy": [
                        0.368,
                        0.3686
                    ],
                    "ct": 231,
                    "alert": "none",
                    "effect": "none",
                    "colormode": "ct",
                    "reachable": true
                },
                "name": "light-3"
            }
        }
    }"""
    put_response = "[]"
    HTTPretty.register_uri(HTTPretty.GET, 'http://limelight.example.com/api/test/', body=response, content_type='application/json')
    HTTPretty.register_uri(HTTPretty.PUT, 'http://limelight.example.com/api/test/groups/0/action', body=put_response, content_type='application/json')
    HTTPretty.register_uri(HTTPretty.PUT, 'http://limelight.example.com/api/test/lights/1/state', body=put_response, content_type='application/json')
    HTTPretty.register_uri(HTTPretty.PUT, 'http://limelight.example.com/api/test/lights/2/state', body=put_response, content_type='application/json')
    cfg = {
        'bridges': [{'hostname': 'limelight.example.com', 'username': 'test'}],
        'groups': {
            'g1': ['light-1'],
            'g2+3': ['light-2', 'light-3']
        },
        'presets': {
            'bright': {
                'brightness': '100%'
            },
            'slow_bright': [{'bri': '50%'}, {'bri': '100%', 'time': '1m30s'}]
        },
        'scenes': {
            's1+2': {
                'light-1': 'bright',
                'light-2': {
                    'bri': 255,
                    'sat': 255,
                    'hue': 0
                }
            }
        }
    }

    def _last_request_body():
        body = HTTPretty.last_request.body
        if hasattr(body, 'decode'):
            encoding = 'utf-8'
            try:
                encoding = HTTPretty.last_request.headers.get_content_charset()
            except AttributeError:
                pass
            body = body.decode(encoding or 'utf-8')
        return json.loads(body)

    hueman = Hueman(cfg)
    assert len(hueman['limelight.example.com'].light(None)) == 3
    assert hueman['limelight.example.com'].light('light-1') == hueman.find('light-1').members[0]
    hueman.on(False, commit=True)
    assert _last_request_body() == {'on': False}
    hueman.bri(255).commit()
    assert len(hueman.bri()) == len(filter(lambda a: a[1] == 255, hueman.brightness()))
    assert _last_request_body() == {'bri': 255}

    assert hueman['limelight.example.com'].light('light-4') is None

    try:
        hueman.reachable(False)
        assert True is False
    except ValueError, e:
        assert e.args[0] == "Attempted to set readonly value 'reachable'"

    try:
        hueman['limelight.example.com'].moose(100)
        assert True is False
    except AttributeError, e:
        assert e.args[0] == "'Bridge' object has no attribute 'moose'"

    l1 = hueman['limelight.example.com'].light('light-1')
    l1.brightness(200).commit()
    assert l1.brightness() == 200
    l1.brightness('100%').commit()
    assert l1.brightness() == 255
    l1.brightness(-10).commit()
    assert l1.brightness() == 0
    l1.brightness(200, commit=True).brightness('~50%').commit()
    assert l1.brightness() == 100
    l1.brightness('+50%').commit()
    assert l1.brightness() == 150
    l1.brightness('-50%').commit()
    assert l1.brightness() == 75
    l1.brightness(500).commit()
    assert l1.brightness() == 255

    assert len(hueman.find(re.compile('light-[1-3]', re.I))) == 3

    l1._apply_command('_skip:True', commit=True)
    assert _last_request_body() == {}
    l1._apply_command('br:100', commit=True)
    assert _last_request_body() == {'bri': 100}
    l1._apply_command('bright', commit=True)
    assert _last_request_body() == {'bri': 255}
    l1._apply_command('on', commit=True)
    assert _last_request_body() == {'on': True}
    l1._apply_command('off', commit=True)
    assert _last_request_body() == {'on': False}
    l1._apply_command('slow bright')
    assert _last_request_body() == {'transitiontime': 900, 'bri': 255}

    l2 = hueman['limelight.example.com'].light('light-2')
    hueman.scene('s1+2', True)
    assert l1.bri() == 255
    assert l2.sat() == 255


if __name__ == '__main__':
    test_build_lights()
