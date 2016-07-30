from general import debug

import boto3

import io
import hashlib

try:
    import httplib
except:
    import http.client

import asset_status_code
import config

import base64

class S3AssetProvider():
    def check(self, area, selector, hash):
        if area is None:
            return asset_status_code.error

        area_config = config.load_area(area)

        storage_config = config.load_storage(area_config['storage'])

        s3 = boto3.resource('s3', aws_access_key_id=storage_config['key1'], aws_secret_access_key=storage_config['key2'])

        area = area.lower()

        bucket_name = storage_config['name']
        key = area + '/' + selector
        
        try:
            obj = s3.Object(bucket_name, key).load()
        except:
            return asset_status_code.not_found

        stored_hash = response_metadata['x-amz-meta-content-md5']
        if len(stored_hash) == 0:
            return asset_status_code.not_found

        return asset_status_code.same if stored_hash == hash else asset_status_code.different

    # not really a stream mechanism
    def stream(self, area, selector):
        return self.read(area, selector)

    def read(self, area, selector):
        if area is None:
            return null

        area_config = config.load_area(area)

        storage_config = config.load_storage(area_config['storage'])

        client = boto3.client('s3', aws_access_key_id=storage_config['key1'], aws_secret_access_key=storage_config['key2'])

        area = area.lower()

        hash = base64.b64encode(hashlib.md5(buffer).digest())

        args = {
            'Bucket': storage_config['name'],
            'Key': area + '/' + selector
        }

        return client.get_object(**args)['Body']

    def get_url(self, area, selector):
        if area is None:
            return null

        area_config = config.load_area(area)

        storage_config = config.load_storage(area_config['storage'])

        client = boto3.client('s3', aws_access_key_id=storage_config['key1'], aws_secret_access_key=storage_config['key2'])

        area = area.lower()

        hash = base64.b64encode(hashlib.md5(buffer).digest())

        args = {
            'Bucket': storage_config['name'],
            'Key': area + '/' + selector
        }

        return client.generate_presigned_url(ClientMethod='get_object', Params=args)

    # S3 buckets are not like Azure containers; S3 buckets are like Azure accounts; thus, S3 doesn't use area
    def ensure_access(self, area):
        # does this exist? not seeing it in source code at https://github.com/boto/boto3
        return

    def update(self, area, selector, content_type, buffer):
        if area is None:
            return null

        area_config = config.load_area(area)

        storage_config = config.load_storage(area_config['storage'])

        client = boto3.client('s3', aws_access_key_id=storage_config['key1'], aws_secret_access_key=storage_config['key2'])

        area = area.lower()

        hash = base64.b64encode(hashlib.md5(buffer).digest()).decode()

        args = {
            'Bucket': storage_config['name'],
            'Key': area + '/' + selector,
            'Body': buffer,
            'ContentMD5': hash,
            'ACL': 'public-read'
        }

        if content_type is not None and len(content_type) > 0:
            args.ContentType = content_type

        client.put_object(**args)

        return hash

    def clean_selector(self, selector):
        return selector.Replace('/', '_').Replace('.', '=')