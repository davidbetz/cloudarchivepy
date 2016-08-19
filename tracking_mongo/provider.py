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
        def read(self, area, selector):
            assert area is not None, 'area is none; should already be validated'

            area_config = config.load_area(area)

            tracking_config = config.load_tracking(area_config['tracking'])

            client = MongoClient(tracking_config['location'])

            db = client[area_config['trackingContainer']]

            db.authenticate(tracking_config['key1'], tracking_config['key2'], source='admin')

            area = area.lower()

            # hash = base64.b64encode(hashlib.md5(buffer).digest())

            item = db['{}'.format(area)].find({
                'selector': selector
            })

            return item


        def update(self, area, selector, manifest, hash):
            assert area is not None, 'area is none; should already be validated'

            area_config = config.load_area(area)

            tracking_config = config.load_tracking(area_config['tracking'])

            client = MongoClient(tracking_config['location'])

            db = client[area_config['trackingContainer']]

            db.authenticate(tracking_config['key1'], tracking_config['key2'], source='admin')

            print('location:{}'.format(tracking_config['location']))
            print('trackingContainer:{}'.format(area_config['trackingContainer']))
            print('key1:{}'.format(tracking_config['key1']))
            print('key2:{}'.format(tracking_config['key2']))

            area = area.lower()

            entity = {
                'selector': selector,
                'hash': hash
            }

            for key, value in [(key, value) for key, value in manifest.iteritems() if key[0] != '_']:
                if key in ('selector', 'hash'):
                    continue

                entity[key] = value

            db['{}'.format(area)].insert_one(entity)

except:
    pass