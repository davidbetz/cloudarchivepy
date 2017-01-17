"""
CloudArchivePy
Copyright (C) 2016-2017 David Betz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from general import debug, urljoin

import io
import hashlib

try:
    import httplib
except:
    import http.client

import config

import json

import requests

class ElasticTrackingProvider():
    def _call(self, verb, endpoint, obj = None):
        headers = {
            "Accept": "application/json",
        }

        endpoint = endpoint.lower()

        verb = verb.lower()

        jsonData = json.dumps(obj)

        if verb == 'get':
            response = requests.get(endpoint, headers=headers)
        elif verb == 'head':
            response = requests.head(endpoint, headers=headers)
        elif verb == 'post':
            response = requests.post(endpoint, headers=headers, data=jsonData)
        elif verb == 'put':
            response = requests.put(endpoint, headers=headers, data=jsonData)
        elif verb == 'delete':
            response = requests.delete(endpoint, headers=headers)
        else:
            raise ValueError('invalid verb ({})'.format(verb))

        return response


    def _get_endpoint(self, area):
        assert area is not None, 'area is none; should already be validated'

        area_config = config.load_area(area)

        tracking_config = config.load_tracking(area_config['tracking'])

        location = tracking_config['location']

        location = location.replace('https://', 'https://{}:{}@'.format(tracking_config['key1'], tracking_config['key2']))
        location = location.replace('http://', 'http://{}:{}@'.format(tracking_config['key1'], tracking_config['key2']))
        
        trackingContainer = area_config['trackingContainer'] if 'trackingContainer' in area_config else 'cloudarchive'

        return '{}/{}'.format(location, trackingContainer)


    def prepare(self, area):
        assert area is not None, 'area is none; should already be validated'

        area_config = config.load_area(area)

        endpoint = self._get_endpoint(area)

        result = self._call('head', endpoint)

        if result.status_code == 404:
            obj = {
                'settings': {
                    'index': {
                        'number_of_shards': 4
                    }
                },
                'mappings': {
                    area: {
                        'properties': {
                            'area': {
                                'type': 'string'
                            },
                            "selector": {
                                "type": "string",
                                "fields": {
                                    "raw": {
                                        "type": "string",
                                        "index": "not_analyzed"
                                    }
                                }
                            },
                            "hash": {
                                "type": "string",
                                "fields": {
                                    "raw": {
                                        "type": "string",
                                        "index": "not_analyzed"
                                    }
                                }
                            },
                        }
                    }
                }
            }

            results = self._call('post', endpoint, obj)


    def read(self, area, selector):
        if area is None:
            return null

        area_config = config.load_area(area)

        tracking_config = config.load_tracking(area_config['tracking'])
        
        endpoint = self._get_endpoint(area)

        result = self._call('get', endpoint + '/' + area_config['name'])

        try:
            return json.loads(result)
        except:
            return None


    def update(self, area, selector, manifest, hash):
        assert area is not None, 'area is none; should already be validated'

        endpoint = self._get_endpoint(area)
        
        # httplib.HTTPConnection.debuglevel = 1
        # http.client.HTTPConnection.debuglevel = 1

        area = area.lower()

        area_config = config.load_area(area)

        endpoint = urljoin(endpoint, area_config['name'], selector.replace('/','_'))

        entity = self.read(area, selector) or {
            'selector': selector
        }

        for key, value in [(key, value) for key, value in manifest.iteritems() if key[0] != '_']:
            if key in ('area', 'selector', 'hash'):
                continue

            entity[key] = value

        result = self._call('post', endpoint, entity)