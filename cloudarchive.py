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

import sys
import os
import getopt
import datetime
import argparse

import econtent

from general import debug

import config
import file_structure
import client

import settings

from middleware import Handler as MiddlewareHandler

def app(argv):
    options = {}
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("-a", '--area', help="Area to use", required=True)
    parser.add_argument("-v", '--verbose', help="Verbose", action="store_true", default=False)
    parser.add_argument("-l", '--live', help="Live run. Without this, it's a simulation.", action="store_true", default=False)
    parser.add_argument("-f", '--full',  help="Full update, default is incremental.", action="store_true", default=False)


    args = parser.parse_args()

    options['area'] = args.area
    options['verbose'] = args.verbose
    options['live'] = args.live
    options['full'] = args.full

    try:
        full = "full" if options['full'] else ''

        if (options['verbose']):
            pass

    except getopt.GetoptError:
        sys.exit(2)

    index(options)

def run(options):
    config = Config.Load()
    if options.area is None:
        print("Area is required.")
        return
    else:
        areaData = [_ for _ in config.areas if _['name'].lower() == options.area.lower()]

    for area in areaData:
        index(options, area['name'], options['full'])

def index(options):
    area_config = config.load_area(options['area'])

    if area_config is None:
        print("Area not found ({})".format(options['area']))
        return

    if options['verbose']:
        print("Storage: area_config.StorageName")

    print("Beginning fullscan...")

    package = file_structure.create(area_config, options)

    handler = MiddlewareHandler(area=area_config['name'], assets=package['assets'], manifests=package['manifests'])
    filtered_mw = [mw for a, mw in settings.middleware if a == area_config['name']]
    try:
        handler.set(filtered_mw[0])
    except:
        pass
    handler.execute()

    if handler['pending_list'] is not None:
        package['assets'].extend(handler['pending_list'])

    assets = []
    for n in package['assets']:
        if n['Category'] == 'asset':
            assets.append(n)

    asset_count = len(assets)
    #([_ for _ in package['assets'] if 'Category' in _ and _['Category'] == 'asset'])

    if package is not None and asset_count > 0:
        if (options['live']):
            print("Publishing area...")

        now = datetime.datetime.utcnow()

        updated_count = 0
        storage = config.load_storage(area_config['storage'])
        if asset_count > 0 and storage is None:
            print("Storage provider is not set, but there are assets to deploy.")
            sys.exit(2)

        elif asset_count > 0:
            updated_count = client.update(area_config, package, options)

        if updated_count > 0:
            later = datetime.datetime.utcnow()
            if options['verbose']:
                print("Publish complete ({} ms)".format((later - now).total_seconds() * 1000))
                print("Updating timestamps and hashes...")            

        print("Area complete. Items indexed: {}".format(updated_count))

    else:
        print("Area complete. No items updated")


if __name__ == '__main__':
    app(sys.argv[1:])