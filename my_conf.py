import os
import json 
from pprint import pprint

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'deribit_download.json')
config = {
    'storage_dir': '~/'
}
if os.path.exists(file_path):
    print('using config from', file_path)
    try:
        with open(file_path) as config_file:
            config.update(json.load(config_file))
            print('config successfully used')
            pprint(config)
    except:
        print('could not use config! using defaults')
else:
    print('no config file found, using defaults')
    

