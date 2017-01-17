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
