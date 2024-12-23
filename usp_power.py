#!/usr/bin/env python3

import requests
import sys
import argparse

HOST = 'unifi-controller-url:8443'
USER = 'admin'
PASS = 'hunter2'
DEFAULT_MAC = 'aa:bb:cc:dd:ee:ff'
DEFAULT_SITE = 'abcdwxyz'

class Unifi:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.csrf = ''

    def login(self):
        payload = {'username': self.username, 'password': self.password}
        r = self.request('/api/login', payload)
        if not r.ok:
            print(f'Login failed at {self.host}/api/login: {r.text}', file=sys.stderr)
        return r.ok

    def request(self, path, data=None, method='POST'):
        if data is None:
            data = {}
        method = method.lower()
        if method not in ['get', 'post', 'put', 'delete']:
            raise ValueError(f"Unsupported HTTP method: {method}")
        uri = f'https://{self.host}{path}'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if self.csrf:
            headers['X-CSRF-Token'] = self.csrf
        r = getattr(self.session, method)(
            uri, json=data, verify=True, headers=headers
        )
        self.csrf = r.headers.get('X-CSRF-Token', self.csrf)
        return r

def validate_response(res) -> bool:
    try:
        response_data = res.json()
        if res.status_code == 200 and response_data.get('meta', {}).get('rc') == 'ok':
            return True
    except ValueError:
        pass
    print(f'Error while accessing {res.url}: {res.text}', file=sys.stderr)
    return False

def bool_to_state(state) -> str:
    return 'on' if state else 'off'

def get_new_state(action, cur_state):
    if action == 'toggle':
        return not cur_state
    elif action == 'on':
        return True
    elif action == 'off':
        return False
    else:
        raise ValueError(f"Invalid action: {action}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False,
        description="Control UniFi USP-Plug outlet power state")
    parser.add_argument('--help','-h',
        action='help',
        help=argparse.SUPPRESS)
    parser.add_argument('action',
        choices=['get', 'on', 'off', 'toggle'],
        nargs='?',
        help="Get or Set desired power state")
    parser.add_argument('--site','-s',
        default=DEFAULT_SITE,
        help='Site ID (as shown in Unifi web interface)')
    parser.add_argument('--mac','-m',
        default=DEFAULT_MAC,
        help='MAC address of USP-Plug')
    args = parser.parse_args()
    action = args.action
    if not action:
        parser.print_help()
        exit()

    SITE = args.site.lower() if args.site else DEFAULT_SITE
    MAC = args.mac.lower() if args.mac else DEFAULT_MAC

    sess = Unifi(host=HOST, username=USER, password=PASS)
    if not sess.login():
        exit(2)

    res = sess.request(f'/api/s/{SITE}/stat/device/{MAC}', method='get')
    if not validate_response(res):
        exit(1)
    device_cfg = res.json().get('data', [{}])[0]
    device_id = device_cfg.get('_id')
    device_name = device_cfg.get('name', MAC)
    outlet_config = device_cfg.get('outlet_overrides', [])
    if not isinstance(outlet_config, list) or len(outlet_config) == 0:
        print('Error: no outlets found', file=sys.stderr)
        exit(3)
    if 'relay_state' not in outlet_config[0]:
        print('Error: relay_state not found in outlet configuration', file=sys.stderr)
        exit(4)
    cur_state = bool(outlet_config[0]['relay_state'])
    if action == 'get':
        print(f'{device_name} is {bool_to_state(cur_state)}')
        exit(0)
    new_state = get_new_state(action, cur_state)
    if cur_state == new_state:
        print(f'No action required ({device_name} is already {action})')
        exit(0)
    outlet_config[0]['relay_state'] = new_state
    payload = {'outlet_overrides': outlet_config}
    print(f'Setting {device_name} outlet state: {bool_to_state(new_state)}')
    res = sess.request(f'/api/s/{SITE}/rest/device/{device_id}', method='put', data=payload)
    if not validate_response(res):
        exit(1)
    print('Success')
