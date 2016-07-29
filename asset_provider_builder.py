import config

from storage_azure.provider import AzureAssetProvider
from storage_s3.provider import S3AssetProvider

def create(area_config):
    storage_name = area_config['storage']
    storage_config = config.load_storage(storage_name)
    name = storage_config['provider'].lower()

    if name == "azure":
        provider = AzureAssetProvider()
    elif name == "s3":
        provider = S3AssetProvider()
    else:
        raise ValueError("no")

    return provider
