#!/usr/bin/python3

import requests
from os import path
import xml.etree.ElementTree as ET

# This program connects to a NewTek Tricaster through it's DataLink feature
# This feature is only available on Advanced Edition Tricasters
# You'll need a few things to get this to work:
    # 1. Get your Tricaster's IP address
    # 2. You'll need to setup a lower third template with %webkey 01% in a text field


def tricaster_data_link(ip, name='LiveLT', webkey='WebKey 01'):

    # create XML file using user entries
    xml_root = ET.Element('shortcuts')
    shortcut_element = ET.SubElement(xml_root, 'shortcut')
    shortcut_element.set('name', 'datalink_set')
    ET.SubElement(shortcut_element, 'entry', key='key', value=webkey)
    ET.SubElement(shortcut_element, 'entry', key='value', value=name)

    try:
        url = f'http://{ip}:5952/v1/shortcut'
        r = requests.post(url=url, data=ET.tostring(xml_root), headers={"Content-Type": "text/xml"}, timeout=1)
        return r.status_code, name
    
    except Exception as e:
        raise e


if __name__ == '__main__':
    print('Testing tricaster connection...')
    ip = str(input('Input Tricaster IP: '))
    response, name = tricaster_data_link(ip=ip, name='LiveLT')
    print(f'Tricaster responded with code: {response}\nCurrently showing: {name}')