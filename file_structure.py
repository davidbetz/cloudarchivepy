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

def create(area_config, options):
    return _create(area_config['fileTypes'], area_config, options);


def _create(file_type_data, area_config, options):
    package = { 'area': area_config['name'], 'assets': [], 'tracking_data': [] }

    stabilizationPath = os.path.join(area_config['folder'], constants.dates)
    try:
        with open(stabilizationPath, 'r') as f:
            package['tracking_data'] = json.loads(f.read())
    except IOError:
        pass

    remoteBranch = area_config['remoteBranch'] if 'remoteBranch' in area_config else ''

    assets, manifests = _load(file_type_data, remoteBranch, area_config['folder'], area_config['folder'], package, options)

    package['assets'] = assets
    package['manifests'] = manifests

    #debug.log('assets', assets)
    #debug.log('manifests', manifests)

    return package


def _load(file_type_data, remote_branch, base_folder, folder, package, options):
    context = urlclean(folder[len(base_folder):])
    partArray = urlsplit(context) or []
    part_list = [(_[1:] if _.startswith("$") else _) for _ in partArray]

    context = '/'.join(part_list)
    asset_list = []
    manifests = []

    try:
        folder_manitest = econtent.read_file(urljoin('/' + folder, '.manifest'))
    except:
        folder_manitest = None
    
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
            rfd['Category'] = 'asset'
            rfd['CreatedDateTime'] = created
            rfd['ModifiedDateTime'] = datetime.datetime.fromtimestamp(file_stat.st_mtime).replace(microsecond=0).isoformat() + 'Z'
            rfd['Name'] = base_file_name
            rfd['IsExplicitMaster'] = constants.master in context
            rfd['Extension'] = extension
            rfd['Path'] = urlclean(context.replace(constants.master, ''))
            rfd['RelativePath'] = urljoin(rfd['Path'], rfd['Name'])
            rfd['Manifest'] = {}

            if check_for_changes(rfd, package['tracking_data'], urljoin(remote_branch, urljoin(context, base_file_name)), options):
                asset_list.append(rfd)

            # TODO: folder manifest even a good idea? everything would have to be updated on update, or extra tracking required
            if folder_manitest is not None:
                for key, value in folder_manitest.iteritems():
                    rfd['Manifest'][key] = value

            manifest_base_name = '.' + base_file_name + '.manifest'
            file_manifest_path = urljoin('/' + os.path.dirname(p), manifest_base_name)
            try :
                file_manifest = econtent.read_file(file_manifest_path)
                manifests.append({ 'file_manifest': file_manifest, 'related_selector': rfd['RelativePath'], 'related_filename': p, 'rfd': rfd })
            except:
                file_manifest = None

            if file_manifest is not None:
                for key, value in file_manifest.iteritems():
                    rfd['Manifest'][key] = value

                file_manifest_stat = os.stat(file_manifest_path)

                manifest_created = [_ for _ in package['tracking_data'] if _['category'] == "manifest" and _['selector'] == urljoin(context, manifest_base_name)]

                if len(manifest_created) > 0:
                    manifest_created = manifest_created[0]['created']
                else:
                    manifest_created = datetime.datetime.fromtimestamp(file_manifest_stat.st_ctime).replace(microsecond=0).isoformat() + 'Z'

                manifest_rfd = RawFileData(file_manifest_path)
                manifest_rfd['Category'] = 'manifest'
                manifest_rfd['CreatedDateTime'] = manifest_created
                manifest_rfd['ModifiedDateTime'] = datetime.datetime.fromtimestamp(file_manifest_stat.st_mtime).replace(microsecond=0).isoformat() + 'Z'
                manifest_rfd['Name'] = manifest_base_name
                manifest_rfd['Extension'] = '.manifest'
                manifest_rfd['Path'] = urljoin(context, manifest_base_name)
                manifest_rfd['RelativePath'] = urljoin(context, manifest_base_name)
                rfd['manifest_rfd'] = manifest_rfd
                #manifest_rfd['rfd'] = rfd

                if check_for_changes(manifest_rfd, package['tracking_data'], urljoin(context, manifest_base_name), options):
                    asset_list.append(rfd)

            render_manifest(rfd)

    for d in dirs:
        result, manifests_next_set = _load(file_type_data, remote_branch, base_folder, os.path.join(folder, d), package, options)
        asset_list.extend(result)
        manifests.extend(manifests_next_set)

    return (asset_list, manifests)

def check_for_changes(data, tracking, selector, options):
    type = 'manifest' if data.is_manifest else 'asset'
    existing = [_ for _ in tracking if _['category'] == type and _['selector'] == selector]
    existing = existing[0] if len(existing) > 0 else { 'hash': '' }

    '''
    debug.log('type', type)
    debug.log('existing', existing)
    debug.log('hash', existing['hash'])
    debug.log('data.hash()', data.hash())
    '''

    if options['full']:
        if options['verbose']:
            print('new item ({})'.format(selector))
        return True

    elif existing['hash'] != data.hash():
        if options['verbose']:
            print('hash mismatch for {} ({}|{}|{})'.format(type, selector, existing['hash'], data.hash()))
        data['OldHash'] = existing['hash']
        return True

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
