from __future__ import print_function

import sys
import getopt
import datetime
import argparse

from general import debug

import config
import file_structure
import asset_client

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

    # debug.log('args', args)
    # debug.log('options', options)
    try:
        '''
        options['area'] = 'books'
        options['verbose'] = True
        options['live'] = False
        options['full'] = True
        '''

        full = "full" if options['full'] else ''

        if (options['verbose']):
            pass

        index(options)

        #print("Finished. Press enter to exit.")
    except getopt.GetoptError:
        sys.exit(2)

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

    #+
    package = file_structure.create(area_config, options['full'])

    # debug.log('package', [_['RelativePath'] for _ in package['assets']])
    #+

    if package is not None and len(package['assets']) > 0:
        if (options['live']):
            print("Publishing area...")

        now = datetime.datetime.utcnow()
        updated_list = []

        asset_count = package['assets']

        storage = config.load_storage(area_config['storage'])
        if asset_count > 0 and storage is None:
            print("Storage provider is not set, but there are assets to deploy.")
            sys.exit(2)

        elif asset_count > 0:
            updated_list.extend(asset_client.update(area_config, package, options))

        if len(updated_list) > 0:
            later = datetime.datetime.utcnow()
            if options['verbose']:
                print("Publish complete ({} ms)".format((later - now).Milliseconds))
                print("Updating timestamps and hashes...")

            file_structure.finalize(area_config['folder'],  updated_list, package['tracking_data'])

        print("area complete. Items indexed: {}".format(len(updated_list)))

    else:
        print("area complete. No items updated")


if __name__ == '__main__':
    app(sys.argv[1:])