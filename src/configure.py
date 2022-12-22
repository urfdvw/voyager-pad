"""
This module parse the json setting to a python singleton
the actual setting is in file `settings.json`
About the format of the file, please check
https://github.com/urfdvw/macropad-xiao#configure
"""
import json

# read json
with open('settings.json') as f:
    configure_json = json.load(f)

# change string key to int key
configure = {
    int(layer): {
        int(key_number): configure_json[layer][key_number]
        for key_number in configure_json[layer]
    }
    for layer in configure_json
}

# change macro to list of list
macro = {
    layer: {
        key_number: [
            [key.strip("", ) for key in hotkey.split( '|')]
            for hotkey
            in configure[layer][key_number][1].split( '~')
        ]
        for key_number in configure[layer]
    }
    for layer in configure
}
