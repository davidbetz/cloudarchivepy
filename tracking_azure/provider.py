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
        def prepare(self, area):
            if area is None:
                return null

            area_config = config.load_area(area)

            tracking_config = config.load_tracking(area_config['tracking'])

            table_service = TableService(account_name=tracking_config['name'], account_key=tracking_config['key1'])
            
            table_service.create_table(area_config['container'])


        def read(self, area, selector):
            if area is None:
                return null

            area_config = config.load_area(area)

            tracking_config = config.load_tracking(area_config['tracking'])

            table_service = TableService(account_name=tracking_config['name'], account_key=tracking_config['key1'])
            
            area = area.lower()

            item = table_service.query_entity(area_config['container'], area, selector.replace('/','_'))

            item = item[0] if len(item) > 0 else {}

            return item


        def update(self, area, selector, hash):
            if area is None:
                return null

            area_config = config.load_area(area)

            tracking_config = config.load_tracking(area_config['tracking'])

            table_service = TableService(account_name=tracking_config['name'], account_key=tracking_config['key1'])
            
            area = area.lower()

            # hash = base64.b64encode(hashlib.md5(buffer).digest())

            table_service.insert_or_replace_entity(area_config['container'], {
                'PartitionKey': area,
                'RowKey': selector.replace('/','_'),
                'selector': selector,
                'hash': hash
            })

except:
    pass