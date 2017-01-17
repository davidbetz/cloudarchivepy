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

from general import debug

import ruamel.yaml as yaml
  
import settings

tracking_accounts = {}
storage_accounts = {}
areas = {}

def load():
    with open(settings.config_location, 'r') as f:
        config = yaml.load(f)

    if config is not None:
        if 'environment' in config:
            settings.environment = config['environment'].lower()
        else:
            settings.environment  = 'production'

        for area in config['areas']:
            if not 'environment' in area:
                area['environment'] = 'production'

            areas[area['name'].lower()] = area

        for account in config['storageAccounts']:
            if account['key1'].startswith("(") and account['key1'].endswith(")"):
                key1FileName = account['key1'][1:-1]
                with open(key1FileName, 'r') as f:
                    account['key1'] = f.read().strip()

            if account['key2'].startswith("(") and account['key2'].endswith(")"):
                key2FileName = account['key2'][1:-1]
                with open(key2FileName, 'r') as f:
                    account['key2'] = f.read().strip()

            storage_accounts[account['name'].lower()] = account

        for account in config['trackingAccounts']:
            if account['location'].startswith("(") and account['location'].endswith(")"):
                key1FileName = account['location'][1:-1]
                with open(key1FileName, 'r') as f:
                    account['location'] = f.read().strip()

            if account['key1'].startswith("(") and account['key1'].endswith(")"):
                key1FileName = account['key1'][1:-1]
                with open(key1FileName, 'r') as f:
                    account['key1'] = f.read().strip()

            if account['key2'].startswith("(") and account['key2'].endswith(")"):
                key2FileName = account['key2'][1:-1]
                with open(key2FileName, 'r') as f:
                    account['key2'] = f.read().strip()

            tracking_accounts[account['name'].lower()] = account

def load_area(name):
    if name not in areas:
        load()
    if name not in areas:
        return None
    return areas[name]

def load_storage(name):
    if name not in storage_accounts:
        load()
    if name not in storage_accounts:
        return None
    return storage_accounts[name]

def load_tracking(name):
    if name not in tracking_accounts:
        load()
    if name not in tracking_accounts:
        return None
    return tracking_accounts[name]

