"""
CloudArchivePy
Copyright (C) 2016-2017 David Betz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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
    try:
        tracking_name = area_config['tracking']
    except:
        raise ValueError('tracking not set')

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
