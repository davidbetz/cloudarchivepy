from asset_provider_builder import create as asset_provider_builder_create

from general import debug, get_kwarg, urljoin

import asset_status_code

import threading

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
    
def spawned(list, options, client, area_config, asset):
    selector = asset['RelativePath']
    if area_config['remoteBranch'] != None:
        selector = urljoin(area_config['remoteBranch'], selector)

    area = area_config['name']
    code = client.check(area, selector, asset.hash())
    # debug.log('code', code)
    if options['full'] or code == asset_status_code.not_found or code == asset_status_code.different:
        if options['live']:
            client.update(area, selector, get_content_type(asset['Extension']), asset.read())
            list.append({
                'category': "asset",
                'fileType' : asset['Extension'],
                'selector' : asset['RelativePath'],
                'hash': asset.hash()
                }
            )
            debug.logline("Updated file selector ({})".format(asset['RelativePath']))
        else:
            debug.logline("File selector would have been updated in live mode. ({}, {})".format(area, selector))

def update(area_config, package, options):
    list = []
    client = asset_provider_builder_create(area_config)

    if options['live']:
        client.ensure_access(area_config['name'])

    threads = []
    max_threads = 1
    if hasattr(settings, 'max_threads'):
        max_threads = int(settings.max_threads)
    print('max threads: {}'.format(max_threads))
    for asset in package['assets']:
        if max_threads == 1:
            spawned(list, options, client, area_config, asset)
        else:
            t = threading.Thread(target=spawned, args=(list, options, client, area_config, asset,))
            threads.append(t)
            t.start()
            #print('+{}'.format(asset['RelativePath']))
            if len(threads) >= max_threads:
                for t2 in threads:
                    t2.join()
                    #print('-{}'.format(asset['RelativePath']))
                threads = []
   
    return list


def get_content_type(extension):
    content_type = [y for x,y in content_types if x == extension]
    if len(content_type) > 0:
        content_type = content_type[0]
    return content_type
