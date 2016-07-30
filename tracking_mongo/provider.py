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
            if area is None:
                return null

            area_config = config.load_area(area)

            tracking_config = config.load_tracking(area_config['tracking'])

            client = MongoClient("mongodb://{}:{}@{}".format(tracking_config['key1'], tracking_config['key2'], tracking_config['location']))

            db = client[area_config['container']]

            area = area.lower()

            # hash = base64.b64encode(hashlib.md5(buffer).digest())

            item = db['{}_tracking'.format(area)].find({
                'selector': selector
            })

            debug.log('item', item)

            return item


        def update(self, area, selector, hash):
            if area is None:
                return null

            area_config = config.load_area(area)

            tracking_config = config.load_tracking(area_config['tracking'])

            location = "mongodb://{}:{}@{}".format(tracking_config['key1'], tracking_config['key2'], tracking_config['location'])

            debug.log('location', location)

            client = MongoClient(location)

            db = client[area_config['container']]

            area = area.lower()

            # hash = base64.b64encode(hashlib.md5(buffer).digest())

            db['{}_tracking'.format(area)].insert_one({
                'selector': selector,
                'hash': hash
            })

except:
    pass