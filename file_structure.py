from general import debug, urlclean, urljoin, urlsplit

import os
import hashlib
import datetime
import json
import re

import econtent

import constants

from raw_file_data import RawFileData

'''
    def create_catalog(area_config, full_update):
    return _create([{ 'extension': '.manifest' }], area_config, full_update, manifest_search=True);
'''

def create(area_config, full_update):
    return _create(area_config['fileTypes'], area_config, full_update);


def _create(file_type_data, area_config, full_update):
    package = { 'area': area_config['name'], 'assets': [], 'tracking_data': [] }

    stabilizationPath = os.path.join(area_config['folder'], constants.dates)
    try:
        with open(stabilizationPath, 'r') as f:
            package['tracking_data'] = json.loads(f.read())
    except IOError:
        pass

    remoteBranch = area_config['remoteBranch'] if 'remoteBranch' in area_config else ''

    result = _load(file_type_data, remoteBranch, area_config['folder'], area_config['folder'], package, full_update)

    package['assets'].extend(result)

    return package


def _load(file_type_data, remote_branch, base_folder, folder, package, full_update):
    context = urlclean(folder[len(base_folder):])
    partArray = urlsplit(context) or []
    part_list = []

    part_list = [(_[1:] if _.startswith("$") else _) for _ in partArray]

    context = '/'.join(part_list)
    asset_list = []

    try:
        folder_manitest = econtent.read_file(urljoin('/' + folder, '.manifest'))
    except:
        folder_manitest = None
    
    #debug.log('folder_manitest', folder_manitest)

    if len(file_type_data) > 0:
        walked = next(os.walk(folder))

        files = walked[2]
        dirs = walked[1]

        filtered_blob_data = [os.path.join(folder, _) for _ in files if _[0] != '_' and _[0] != '.']

        for p in filtered_blob_data:
            extension = os.path.splitext(p)[1][1:]
            if len([_ for _ in file_type_data if _['extension'] == extension]) == 0:
                continue

            file_stat = os.stat(p)

            created = [_ for _ in package['tracking_data'] if _['category'] == "asset" and _['selector'] == urljoin(context, p)]
            if len(created) > 0:
                created = created[0].created
            else:
                created = datetime.datetime.fromtimestamp(file_stat.st_ctime).replace(microsecond=0).isoformat() + 'Z'

            base_file_name = os.path.basename(p)

            rfd = RawFileData(p)
            rfd['CreatedDateTime'] = created
            rfd['ModifiedDateTime'] = datetime.datetime.fromtimestamp(file_stat.st_mtime).replace(microsecond=0).isoformat() + 'Z'
            rfd['Name'] = base_file_name
            rfd['IsExplicitMaster'] = constants.master in context
            rfd['Extension'] = extension
            rfd['Path'] = urlclean(context.replace(constants.master, ''))
            rfd['RelativePath'] = urljoin(rfd['Path'], rfd['Name'])
            rfd['Manifest'] = {}

            if folder_manitest is not None:
                for key, value in folder_manitest.iteritems():
                    rfd['Manifest'][key] = value

            file_manifest_path = urljoin('/' + os.path.dirname(p), '.' + base_file_name + '.manifest')
            try:
                file_manifest = econtent.read_file(file_manifest_path)
                for key, value in file_manifest.iteritems():
                    rfd['Manifest'][key] = value
            except:
                file_manifest = None

            render_manifest(rfd)

            existing = [_ for _ in package['tracking_data'] if _['category'] == "asset" and _['selector'] == urljoin(remote_branch, urljoin(context, base_file_name))]
            existing = existing[0] if len(existing) > 0 else { 'hash': '' }

            if full_update:
                asset_list.append(rfd)
            elif existing['hash'] != rfd.hash():
                rfd['OldHash'] = existing['hash']
                asset_list.append(rfd)

    for d in dirs:
        result = _load(file_type_data, remote_branch, base_folder, os.path.join(folder, d), package, full_update)
        package['assets'].extend(result)

    return asset_list

def render_manifest(rfd):
    manifest = rfd['Manifest']

    require_update = [(key, value[2:-2]) for key, value in manifest.iteritems() if len(value) > 3 and value[:2] == '{{' and value[-2:] == '}}']

    for key, value in require_update:
        (based_on, right) = value.split('|', 1)
        (regex, number) = right.rsplit('|', 1)

        if len(number) > 1 and number[0] == '$':
            try:
                number = int(number[1:])
            except:
                continue

        try:
            basis = manifest[based_on]
        except:
            try:
                basis = rfd[based_on]
            except:
                continue

        sr = re.search(regex, basis)
        if sr != None:
            code = sr.group(number)

            manifest[key] = code