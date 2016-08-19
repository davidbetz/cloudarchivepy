from general import debug

import io
import hashlib

try:
    import httplib
except:
    import http.client

import asset_status_code
import config

import base64

try:
    from pymongo import MongoClient

    class MongoTrackingProvider():
        def _get_database(self, area):
            area_config = config.load_area(area)

            trackingContainer = area_config['trackingContainer'] if 'trackingContainer' in area_config else 'cloudarchive'
            
            return trackingContainer


        def read(self, area, selector):
            assert area is not None, 'area is none; should already be validated'

            area_config = config.load_area(area)

            tracking_config = config.load_tracking(area_config['tracking'])

            client = MongoClient(tracking_config['location'])

            db = client[self._get_database(area)]

            db.authenticate(tracking_config['key1'], tracking_config['key2'], source='admin')

            item = db[area_config['name']].find_one({
                'selector': selector
            })

            return item


        def update(self, area, selector, manifest, hash):
            assert area is not None, 'area is none; should already be validated'

            area_config = config.load_area(area)

            tracking_config = config.load_tracking(area_config['tracking'])

            client = MongoClient(tracking_config['location'])

            db = client[self._get_database(area)]

            db.authenticate(tracking_config['key1'], tracking_config['key2'], source='admin')

            entity = self.read(area_config['name'], selector) or {
                    'selector': selector
                }

            for key, value in [(key, value) for key, value in manifest.iteritems() if key[0] != '_']:
                if key in ('selector'):
                    continue

                entity[key] = value

            db[area_config['name']].replace_one({ 'selector': selector }, entity, True)

except:
    pass