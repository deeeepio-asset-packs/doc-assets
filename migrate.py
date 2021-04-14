import grequests
import shutil
import os
import re

OLD_PATH = './images/skins/' 
NEW_PATH = './images/skans/' 
ADDITION = 'custom/' 

ASSET_REGEX = '\A(?P<file_name>.+?)\.(?P<file_type>[a-zA-Z0-9]+)\Z'
CUSTOM_REGEX = '\A(?P<skin_id>[0-9]+)-(?:[0-9]+)?\Z' 

SKINS_LIST_URL = 'https://api.deeeep.io/skins?cat=all' 

debug = print

def async_get(*all_requests): 
    requests_list = [] 

    for request in all_requests: 
        if type(request) is str: # plain url
            to_add = grequests.get(request) 
        elif type(request) is tuple: # (method, url) 
            to_add = grequests.request(*request) 
        else: 
            to_add = request
        
        requests_list.append(to_add) 
    
    def handler(request, exception): 
        debug('connection error') 
        debug(exception) 

    datas = grequests.map(requests_list, exception_handler=handler) 

    #debug(datas) 

    jsons = [] 

    for data in datas: 
        to_append = None
        
        if data: 
            if data.ok and data.text: 
                to_append = data.json() 
            else: 
                debug(data.text) 
        else: 
            debug('connection error, no data') 

        jsons.append(to_append) 

    #debug(jsons) 

    return jsons

def map_skins(): 
    skins_list = async_get(SKINS_LIST_URL)[0] 
    mapping = {} 

    for skin in skins_list: 
        name = skin['name'] 
        compressed = name.replace(' ', '').replace("'", '').replace('’', '').replace('-', '')
        lowered = compressed.lower() 

        asset_name = skin['asset'] 

        file_name_match = re.compile(ASSET_REGEX).match(asset_name) 

        if file_name_match: 
            file_name = file_name_match.group('file_name') 

            id_match = re.compile(CUSTOM_REGEX).match(file_name) 

            if id_match: 
                file_name = id_match.group('skin_id') 

            mapping[lowered] = file_name

            print(f'{lowered}: {file_name}') 
        else: 
            print(f'failed regex: {asset_name}')
    
    print() 

    return mapping

mapping = map_skins() 

renames = {} 

with os.scandir(OLD_PATH) as iterator: 
    count = 0
    missing = [] 
    found = [] 

    for file_obj in iterator: 
        file_name = file_obj.name
        old_path = file_obj.path

        stripped_match = re.compile(ASSET_REGEX).match(file_name) 

        if stripped_match: 
            stripped = stripped_match.group('file_name') 
            suffix = stripped_match.group('file_type') 

            if suffix == 'png': 
                new_name = None
                display = None

                if stripped in mapping: 
                    display = new_name = mapping[stripped] 

                    key = stripped
                else: 
                    find_count = 0

                    key = None

                    for name, replacement in mapping.items(): 
                        if stripped in name: 
                            key = name
                            potential_new_name = replacement
                            find_count += 1
                        
                    if find_count == 1: 
                        new_name = potential_new_name
                        display = new_name + ' (searched)' 
                    else: 
                        key = None

                        print(find_count) 
                
                if new_name: 
                    del mapping[key] 
                    #print(f'{stripped}: {display}') 

                    new_path = NEW_PATH

                    if new_name.isnumeric(): 
                        new_path += ADDITION
                    
                    new_path += f'{new_name}.{suffix}' 

                    print(f'{stripped}: {new_path}') 
                    
                    renames[old_path] = new_path

                    print(old_path) 

                    #shutil.copy(old_path, new_path) 
                else: 
                    missing.append(stripped) 

                count += 1
            else: 
                print(f'non-png: {file_name}')
        else: 
            print(f'invalid: {file_name}') 
    
    print() 

    print(', '.join(missing)) 
    print(len(missing)) 
    print(len(renames)) 

    print() 

    print(count) 
    print(len(mapping)) 

    print() 

    counts = {} 

    for name, replacement in renames.items(): 
        print(f'{name}: {replacement}') 

        shutil.copy(name, replacement) 

        if replacement not in counts: 
            counts[replacement] = [] 
        
        counts[replacement].append(name) 

    for val in counts.values(): 
        if len(val) > 1: 
            print(val) 
    
    print(mapping) 