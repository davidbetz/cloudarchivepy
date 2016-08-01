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
    from azure.common import AzureMissingResourceHttpError
    from azure.storage.blob import BlockBlobService, ContentSettings, PublicAccess
    from azure.storage import CorsRule

    class AzureAssetProvider():
        def prepare(self, area):
            assert area is not None, 'area is none; should already be validated'

            area_config = config.load_area(area)

            storage_config = config.load_storage(area_config['storage'])

            blob_service = BlockBlobService(account_name=storage_config['name'], account_key=storage_config['key1'])

            blob_service.create_container(area_config['container'])

            blob_service.set_container_acl(area_config['container'], public_access=PublicAccess.Container)

        def check(self, area, selector, hash):
            assert area is not None, 'area is none; should already be validated'

            area_config = config.load_area(area)

            storage_config = config.load_storage(area_config['storage'])

            area = area.lower()

            blob_service = BlockBlobService(account_name=storage_config['name'], account_key=storage_config['key1'])

            if not blob_service.exists(area_config['container'], selector):
                return asset_status_code.not_found

            blob = blob_service.get_blob_properties(area_config['container'], selector)

            storedHash = blob.properties.content_settings.content_md5

            return asset_status_code.same if storedHash == hash else asset_status_code.different


        def stream(self, area, selector):
            assert area is not None, 'area is none; should already be validated'

            area_config = config.load_area(area)
            
            storage_config = config.load_storage(area_config['storage'])

            area = area.lower()

            blob_service = BlockBlobService(account_name=storage_config['name'], account_key=storage_config['key1'])

            blob = blob_service.get_blob_properties(area_config['container'], selector)

            stream = io.BytesIO()
            blob.get_blob_to_stream(area_config['container'], selector, stream)

            return (blob.properties.content_settings.content_type, stream)

        def read(self, area, selector):
            assert area is not None, 'area is none; should already be validated'

            area_config = config.load_area(area)
            
            storage_config = config.load_storage(area_config['storage'])
            
            area = area.lower()

            blob_service = BlockBlobService(account_name=storage_config['name'], account_key=storage_config['key1'])

            return block_blob.get_blob_to_bytes(area_config['container'], selector)

        def get_url(self, area, selector):
            assert area is not None, 'area is none; should already be validated'

            if selector == None:
                return null

            area_config = config.load_area(area)
            
            storage_config = config.load_storage(area_config['storage'])

            area = area.lower()

            selector = selector.lower()

            blob_service = BlockBlobService(account_name=storage_config['name'], account_key=storage_config['key1'])

            return blob_service.make_blob_url(
                container_name=area_config['container'],
                blob_name=selector,
            )

        def ensure_access(self, area):
            assert area is not None, 'area is none; should already be validated'

            area_config = config.load_area(area)
            
            storage_config = config.load_storage(area_config['storage'])
            
            area = area.lower()

            blob_service = BlockBlobService(account_name=storage_config['name'], account_key=storage_config['key1'])

            self.initialize_cors(blob_service)

        def update(self, area, selector, content_type, buffer):
            assert area is not None, 'area is none; should already be validated'

            area_config = config.load_area(area)
            
            storage_config = config.load_storage(area_config['storage'])
            
            area = area.lower()

            # httplib.HTTPConnection.debuglevel = 1
            # http.client.HTTPConnection.debuglevel = 1

            blob_service = BlockBlobService(account_name=storage_config['name'], account_key=storage_config['key1'])

            hash = base64.b64encode(hashlib.md5(buffer).digest())

            content_settings = ContentSettings(content_md5=hash)
            if content_type is not None and len(content_type) > 0:
                content_settings.content_type = content_type

            blob_service.create_blob_from_bytes(
                area_config['container'],
                selector,
                buffer,
                content_settings=content_settings,
                validate_content=False
            )

            return hash

        def initialize_cors(self, blob_service):
            blob_service.set_blob_service_properties(cors=[CorsRule(
                allowed_origins=['*'],
                allowed_methods=['GET'],
                allowed_headers = ['*'],
                exposed_headers = ['*'],
                max_age_in_seconds = 1800
            )])
except:
    pass