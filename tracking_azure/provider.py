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
    from azure.storage.table import TableService, Entity
    from azure.common import AzureMissingResourceHttpError

    class AzureTrackingProvider():
        def _get_table(self, area):
            area_config = config.load_area(area)

            trackingContainer = area_config['trackingContainer'] if 'trackingContainer' in area_config else 'cloudarchive'
            
            return trackingContainer


        def prepare(self, area):
            assert area is not None, 'area is none; should already be validated'

            area_config = config.load_area(area)

            tracking_config = config.load_tracking(area_config['tracking'])

            table_service = TableService(account_name=tracking_config['name'], account_key=tracking_config['key1'])

            trackingContainer = self._get_table(area)

            table_service.create_table(self._get_table(area))


        def read(self, area, selector):
            assert area is not None, 'area is none; should already be validated'

            area_config = config.load_area(area)

            tracking_config = config.load_tracking(area_config['tracking'])

            table_service = TableService(account_name=tracking_config['name'], account_key=tracking_config['key1'])
            
            area = area.lower()

            item = table_service.query_entity(self._get_table(area), area, selector.replace('/','_'))

            item = item[0] if len(item) > 0 else {}

            return item


        def update(self, area, selector, manifest, hash):
            assert area is not None, 'area is none; should already be validated'

            area_config = config.load_area(area)

            tracking_config = config.load_tracking(area_config['tracking'])

            table_service = TableService(account_name=tracking_config['name'], account_key=tracking_config['key1'])
            
            area = area.lower()

            entity = {
                'PartitionKey': area,
                'RowKey': selector.replace('/','_'),
                'selector': selector,
                'hash': hash
            }

            for key, value in [(key, value) for key, value in manifest.iteritems() if key[0] != '_']:
                if key in ('PartitionKey', 'RowKey', 'selector', 'hash'):
                    continue

                entity[key] = value

            table_service.insert_or_replace_entity(self._get_table(area), entity)

except:
    pass