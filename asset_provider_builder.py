import config

try:
    from storage_azure.provider import AzureAssetProvider
except:
    pass

try:
    from storage_s3.provider import S3AssetProvider
except:
    pass

def create(area_config):
    storage_name = area_config['storage']
    storage_config = config.load_storage(storage_name)
    name = storage_config['provider'].lower()

    if name == "azure":
        try:
            provider = AzureAssetProvider()
        except:
            raise ValueError("azure missing; is azure-storage installed?")
    elif name == "s3":
        try:
            provider = S3AssetProvider()
        except:
            raise ValueError("s3 missing; is boto3 installed?")
    else:
        raise ValueError("no")

    return provider
