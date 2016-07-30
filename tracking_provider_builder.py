import config

try:
    from tracking_azure.provider import AzureTrackingProvider
except:
    pass

try:
    from tracking_mongo.provider import MongoTrackingProvider
except:
    pass

from tracking_elastic.provider import ElasticTrackingProvider

def create(area_config):
    tracking_name = area_config['tracking']
    tracking_config = config.load_tracking(tracking_name)
    name = tracking_config['provider'].lower()

    if name == "azure":
        try:
            provider = AzureTrackingProvider()
        except:
            raise ValueError("azure missing; is azure-storage installed?")
    elif name == "mongo":
        try:
            provider = MongoTrackingProvider()
        except:
            raise ValueError("pymongo missing; is pymongo installed?")
    elif name == "elastic":
        # elastic is http-based, so no external anything required
        provider = ElasticTrackingProvider()
    else:
        raise ValueError("no")

    return provider
