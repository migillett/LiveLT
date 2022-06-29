#!/usr/bin/python3

from http.client import InvalidURL
from logging import exception
import requests
from os import path

# This program connects to a NewTek Tricaster through it's DataLink feature
# This feature is only available on Advanced Edition Tricasters
# You'll need a few things to get this to work:
    # 1. Get your Tricaster's IP address
    # 2. You'll need to setup a lower third template with %webkey 01% in a text field


def tricaster_data_link(ip, data='LiveLT', webkey='WebKey 01'):

    payload = f'''<shortcuts>
    <shortcut name="datalink_set">
    <entry key="key" value="{webkey}" />
    <entry key="value" value="{data}" />
    </shortcut>
</shortcuts>'''

    url = f'http://{ip}:5952/v1/shortcut'

    try:
        r = requests.post(url=url, data=payload, headers={"Content-Type": "text/xml"}, timeout=1)
        return r.status_code
    
    except Exception as e:
        raise e


if __name__ == '__main__':
    tricaster_data_link(ip = '192.168.1.10', data='Test Name')