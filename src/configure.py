"""
This module parse the json setting to a python singleton
the actual setting is in file `settings.json`
About the format of the file, please check
https://github.com/urfdvw/macropad-xiao#configure
"""
import json
with open('settings.json') as f:
    configure = json.load(f)

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