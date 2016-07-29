from general import debug, urlclean, urljoin, urlsplit

import os

import fnmatch

import hashlib

import datetime

import constants

from raw_file_data import RawFileData

def create(area_config, full_update):
    #asset_type_data = [_['extension'] for _ in area_config['fileTypes']]
    asset_type_data = area_config['fileTypes']

    if area_config is None:
        raise ValueError("area_config missing")

    if 'name' not in area_config:
        raise ValueError("Required area name")

    if 'folder' not in area_config:
        raise ValueError("Required area folder")

    package = { 'area': area_config['name'], 'assets': [], 'tracking_data': [] }

    stabilizationPath = os.path.join(area_config['folder'], constants.dates)
    if os.path.exists(stabilizationPath):
        with open(stabilizationPath, 'r') as f:
            package['tracking_data'] = json.loads(f.read())

    result = load_raw_structure(asset_type_data, area_config['folder'], area_config['folder'], package, full_update)

    #debug.log('a', area_config['folder'])
    #debug.log('a', result)

    package['assets'].extend(result)

    return package


def load_raw_structure(file_type_data, base_folder, folder, package, full_update):
    context = urlclean(folder[len(base_folder):]).lower()
    partArray = urlsplit(context) or []
    part_list = []

    part_list = [(_[1:] if _.startswith("$") else _) for _ in partArray]

    context = '/'.join(part_list)
    #debug.log('context', context)
    asset_list = []
    asset_type_list = file_type_data or []
    if len(asset_type_list) > 0:
        filtered_blob_data = [os.path.join(folder, _) for _ in os.walk(folder).next()[2] if _[0] != '_' and _[0] != '.']
        #filtered_blob_data.extend([_ for _ in fnmatch.filter(filenames, '*.py') if _[0] != '_' and _[0] != '.'])
        
        '''
        filtered_blob_data =
            Directory
                .GetFiles(folder)
                .Select(p => new FileInfo(p))
                .Where(p => !p.Name.startswith("_") and !p.Name.startswith("."))
        '''
        #debug.log('base_folder', base_folder)
        #debug.log('folder', folder)
        # debug.log('filtered_blob_data', filtered_blob_data)

        for p in filtered_blob_data:
            extension = os.path.splitext(p)[1][1:]
            if len([_ for _ in asset_type_list if _['extension'] == extension]) == 0:
                continue

            file_stat = os.stat(p)

            created = [_ for _ in package['tracking_data'] if _['Category'] == "asset" and _['Selector'] == urljoin(context, p.Name)]
            if len(created) > 0:
                # debug.log('created', created)
                created = created[0].created
            else:
                created = datetime.datetime.fromtimestamp(file_stat.st_ctime).replace(microsecond=0).isoformat() + 'Z'

            #created = package.tracking_data.FirstOrDefault(o => o.Category == "asset" and o.Selector.Equals(Url.Join(context, p.Name)))?.Created or p.CreationTime
            #created = package.tracking_data.FirstOrDefault(o => o.Category == "asset" and o.Selector.Equals(Url.Join(context, p.Name)))?.Created or p.CreationTime.ToUniversalTime()

            base_file_name = os.path.basename(p)

            rfd = RawFileData(p)
            rfd['CreatedDateTime'] = created
            #rfd['ModifiedDateTime'] = p.LastWriteTime.ToUniversalTime()
            rfd['ModifiedDateTime'] = datetime.datetime.fromtimestamp(file_stat.st_mtime).replace(microsecond=0).isoformat() + 'Z'
            rfd['Name'] = base_file_name.lower()
            rfd['IsExplicitMaster'] = constants.master in context.lower()
            rfd['Extension'] = extension
            rfd['Path'] = urlclean(context.lower().replace(constants.master, ''))
            rfd['RelativePath'] = urljoin(rfd['Path'], rfd['Name'])
            # rfd['Content'] = hashlib.md5(p).hexdigest() if os.path.exists(p) else ''

            #debug.log('base_file_name', base_file_name)
            #debug.log('context', context)
            #debug.log('rfd', rfd)

            #existing = package.tracking_data.FirstOrDefault(o => o.Category == "asset" and o.Selector.Equals(Url.Join(context, p.Name)))
            existing = [_ for _ in package['tracking_data'] if _['Category'] == "asset" and _['Selector'] == urljoin(context, base_file_name)]
            existing = existing[0] if len(existing) > 0 else { 'Hash': '' }

            if full_update:
                asset_list.append(rfd)
            elif existing['Hash'] != rfd.hash():
                rfd['OldHash'] = existing['Hash']
                asset_list.append(rfd)

    #+ sub-structure
    '''
    sub_folder_data = []
    for dirs in os.listdir(folder):
        sub_folder_data.extend([os.path.join(root,_) for _ in dirs if _[0] != '_' and _[0] != '.'])

    debug.log('os.listdir(folder)', os.listdir(folder))
    debug.log('sub_folder_data', sub_folder_data)
    '''

    for d in os.walk(folder).next()[1]:
        '''
        (d in Directory
        .GetDirectories(folder)
        .Select(p => new DirectoryInfo(p))
        .Where(p => p.Name[0] != "."))
        '''
        result = load_raw_structure(file_type_data, base_folder, os.path.join(folder, d), package, full_update)
        #debug.log('result', result)
        #debug.log('os.path.join(folder, d)', os.path.join(folder, d))
        package['assets'].extend(result)

    return asset_list


def finalize(base_folder, updatedSelectors, list, datetime):
    utv = datetime.utcnow()
    stabilizationPath = os.path.join(base_folder, constants.dates)
    #jilStabilizationPath = Path.Combine(base_folder, ".jil" + Constants.Dates)
    
    if os.path.exists(stabilizationPath):
        with open(stabilizationPath, 'r') as f:
            list = json.loads(f.read())

    #elif (File.Exists(jilStabilizationPath))
    #
    #    list = JsonConvert.DeserializeObject<List<SelectorSummary>>(File.ReadAllText(jilStabilizationPath))
    #
    if list is None:
        list = []

    for summary in updatedSelectorList:
        entry = [_ for _ in list if _['Selector'] == summary['Selector'] and _['FileType'] is None]
        #entry = list.FirstOrDefault(p => p.Selector.Equals(summary.Selector) and p.FileType is None)
        if len(entry) != None:
            entry = entry[0]
            entry['FileType'] = summary.FileType

        #++ FileType is None => default selector
        #entry = list.FirstOrDefault(p => p.Selector.Equals(summary.Selector) and (p.FileType?.Equals(summary.FileType) or false))
        entry = [_ for _ in list if _['Selector'] == summary['Selector'] and (_['FileType'] == summary['FileType'] or false)]
        if entry != None:
            entry = entry[0]
            entry['Updated'] = utc
            entry['Hash'] = summary.Hash
            entry['Category'] = summary.Category

        else:
            #++ TODO: add time zone setting
            list.append({
                'Selector': summary['Selector'],
                'FileType': summary['FileType'],
                'Created': utc,
                'Updated': utc,
                'Category': summary['Category'],
                'Hash': summary['Hash']
            })


    #list.Where(p => p.Category == "asset").OrderByDescending(p => p.Created)
    assetData = sorted([_ for _ in list if _['Category'] == 'asset'], lambda _: (_['Created']))
    list = []
    list.extend(assetData)
    #File.WriteAllText(os.path.join(base_folder, Constants.Dates), json.dumps(list, Formatting.Indented), Encoding.UTF8)
    with open(stabilizationPath, 'w+') as f:
        f.write(json.dumps(list))