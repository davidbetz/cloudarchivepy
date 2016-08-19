from general import debug, get_kwarg, urljoin

import threading

import datetime

import os

import json

from asset_provider_builder import create as asset_provider_builder_create

from tracking_provider_builder import create as tracking_provider_builder_create

import asset_status_code

import constants

import settings

content_types = [
    ("css", "text/css"),
    ("js", "text/javascript"),
    ("xml", "text/xml"),
    ("json", "application/json"),
    ("svg", "image/svg+xml"),
    ("png", "image/png"),
    ("jpg", "image/jpeg"),
    ("jpeg", "image/jpeg"),
    ("gif", "image/gif"),
    ("pdf", "application/pdf"),
    ("txt", "text/plain"),
    ("md", "text/plain"),
    ("htm", "text/html"),
    ("html", "text/html"),
]
    
def spawned(pending_persist, options, provider, tracking_provider, area_config, asset):
    selector = asset['RelativePath']
    try:
        selector = urljoin(area_config['remoteBranch'], selector)
    except:
        pass

    area = area_config['name']
    #++ may want to readd this concept at some point
    #code = provider.check(area, selector, asset.hash())
    #if options['full'] or code == asset_status_code.not_found or code == asset_status_code.different:
    if options['live']:
        provider.update(area, selector, get_content_type(asset['Extension']), asset.read())

        hash = asset.hash()

        if tracking_provider is not None:
            tracking_provider.update(area, selector, asset['Manifest'], hash)

        pending_persist.append({
            'category' : 'asset',
            'fileType' : asset['Extension'],
            'selector' : selector,
            'hash': hash
            }
        )

        try:
            manifest_rfd = asset['manifest_rfd']
            pending_persist.append({
                'category' : 'manifest',
                'fileType' : '.manifest',
                'selector' : manifest_rfd['RelativePath'],
                'hash': manifest_rfd.hash()
                }
            )
        except:
            pass

        if not asset.is_manifest:
            print("Updated file ({})".format(asset['RelativePath']))
    else:
        if not asset.is_manifest:
            print("File would have been updated in live mode. ({}, {})".format(area, selector))

def update(area_config, package, options):
    pending_persist = []

    area = area_config['name'].lower()

    provider = asset_provider_builder_create(area_config)
    if hasattr(provider, 'prepare'):
        getattr(provider, 'prepare')(area)

    if options['live']:
        provider.ensure_access(area)

    try:
        tracking_provider = tracking_provider_builder_create(area_config)
        if hasattr(tracking_provider, 'prepare'):
            getattr(tracking_provider, 'prepare')(area)
    except:
        pass

    threads = []
    max_threads = 1
    if hasattr(settings, 'max_threads'):
        max_threads = int(settings.max_threads)

    print('Max threads: {}'.format(max_threads))

    def run(threads):
        for t in threads:
            t.join()
        del threads[:]
        finalize(area_config, pending_persist, options)
        count = len(pending_persist)
        del pending_persist[:]
        return count

    count = 0
    cancelled = False
    try:
        for asset in [_ for _ in package['assets'] if not _.is_manifest]:
            if cancelled:
                break
            if max_threads == 1:
                spawned(pending_persist, options, provider, tracking_provider, area_config, asset)
                finalize(area_config, pending_persist, options)
                del pending_persist[:]
            else:
                t = threading.Thread(target=spawned, args=(pending_persist, options, provider, tracking_provider, area_config, asset,))
                threads.append(t)
                t.start()
                if len(threads) >= max_threads:
                    count = count + run(threads)
    except KeyboardInterrupt:
        cancelled = True

    if max_threads == 1:
        finalize(area_config, pending_persist, options)
        count = len(pending_persist)
    elif len(threads) > 0:
        count = count + run(threads)

    return count


def get_content_type(extension):
    content_type = [y for x,y in content_types if x == extension]
    if len(content_type) > 0:
        content_type = content_type[0]
    return content_type


def finalize(area_config, updated_summary_array, options):
    base_folder = area_config['folder']

    utc = datetime.datetime.utcnow()

    stabilizationPath = os.path.join(base_folder, constants.dates)
    
    list = []
    try:
        with open(stabilizationPath, 'r') as f:
            list = json.loads(f.read())
    except IOError:
        pass

    for summary in updated_summary_array:
        if options['verbose']:
            print('updating status ({})'.format(summary['selector']))
        entry = [_ for _ in list if _['selector'] == summary['selector'] and _['fileType'] is None]
        if len(entry) > 0:
            entry = entry[0]
            entry['fileType'] = summary.FileType

        entry = [_ for _ in list if _['selector'] == summary['selector'] and (_['fileType'] == summary['fileType'] or false)]
        if len(entry) > 0:
            entry = entry[0]
            entry['updated'] = utc.replace(microsecond=0).isoformat() + 'Z'
            entry['hash'] = summary['hash'].decode()
            entry['category'] = summary['category']

        else:
            list.append({
                'selector': summary['selector'],
                'fileType': summary['fileType'],
                'created': utc.replace(microsecond=0).isoformat() + 'Z',
                'updated': utc.replace(microsecond=0).isoformat() + 'Z',
                'category': summary['category'],
                'hash': summary['hash'].decode()
            })

    assetData = sorted([_ for _ in list], key=lambda _: (_['created']))

    with open(stabilizationPath, 'w+') as f:
        f.write(json.dumps(assetData, indent=4, sort_keys=True))