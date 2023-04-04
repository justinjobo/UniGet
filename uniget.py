#!/usr/bin/python3

# This script will download all of the latest configs from Unimus allowing use of linux search functions rather than only Unimus ones.
# Added Feature - Simply type "uniget FILENAME" to ssh to the address of the device using the config's filename
# Written by Justin Thompson // 2020

import sys
import base64
import json
import requests
import os
import subprocess

#### START IMPORT API TOKEN ####
#You can find this under User Management > API tokens
try:
    token = open('token.txt', 'r')
except IOError:
    print('Error opening token.txt - please make sure that it exists\nYou can find this in Unimus under User Management > API tokens')
    exit()
token = str(token.read())
#### END IMPORT API TOKEN ####


#### START IMPORT URL ####
#Example: https://example.unimus.net
try:
    url = open('url.txt', 'r')
except IOError:
    print('Error opening url.txt - please make sure that it exists\nExample: https://example.unimus.net\n')
    exit()
url = str(url.read())
#### END IMPORT URL ####

# Create configs folder if it doesn't exist:
if not os.path.exists('configs'):
    os.makedirs('configs')


ids=[]
descriptions=[]
configs=[]

def get_totalpages(uri, headers):
    try:
        response = requests.get(uri, headers=headers) # To disable SSL verification, pass this parameter: verify=False
    except requests.exceptions.ConnectionError:
        print('Connection Error! Can you ping the URL? Also, please make sure there is only 1 line in each file url.txt and token.txt with no EOL marker.')
        exit()
    devices = response.json()
    totalpages = devices['paginator']['totalPages']
    return totalpages

def resolve_hostname(input):
    i = 0
    try:
        filenames = open('./filenames', 'r+')
    except IOError:
        print('[ERR] Run uniget.py first, then try again.')
    filenames = filenames.read()
    try:
        addresses = open('./addresses', 'r+')
    except IOError:
        print('[ERR] Run uniget.py first, then try again.')
    addresses = addresses.read()
    addresses = addresses.splitlines()
    for filename in filenames.splitlines():
        if filename == input:
            print(addresses[i])
        i = i + 1

def get_ids_and_descriptions():
    page=0
    device=0
    uri = (url + "//api/v2/devices?page=0&size=50")
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    totalpages = get_totalpages(uri, headers) #finds the total number of pages using a 50 size limit (50 is the maximum Unimus will allow)
    try:
        addresses = open('./addresses', 'r+')
    except IOError:
        addresses = open('./addresses', 'w+')
    addresses.truncate(0)
    try:
        filenames = open('./filenames', 'r+')
    except IOError:
        filenames = open('./filenames', 'w+')
    filenames.truncate(0)
    while page <= totalpages: #loads all of the ids into the ids array + all the descriptions into the descriptions array + writes files with the addresses and descriptions (substituting spaces with hyphens) so we can easily lookup the address of the device using the filename
        uri = (url + "//api/v2/devices?page=" + str(page) + "&size=50")
        response = requests.get(uri, headers=headers) # To disable SSL verification, pass this parameter: verify=False
        devices = response.json()
        for device in range(len(devices['data'])):
            ids.append(devices['data'][device]['id'])
            description = devices['data'][device]['description']
            description = description.replace(' ', '-')
            descriptions.append(description)
            addresses.write(devices['data'][device]['address'] + '\n')
            filenames.write(description + '\n')
        page = page + 1

def get_configs(): #decrypts the base64 config (the "bytes" value) and writes it to a file in the configs folder. Skips devices that dont have a config.
    i = 0
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    for device in ids:
        uri = (url + "//api/v2/devices/" + str(device) + "/backups/latest")
        response = requests.get(uri, headers=headers) # To disable SSL verification, pass this parameter: verify=False
        devicedata = response.json()
        try:
            config = devicedata['data']['bytes']
            try:
                description = open('configs/' + str(descriptions[i]), 'r+')
            except IOError:
                description = open('configs/' + str(descriptions[i]), 'w+')
            description.truncate(0)
            base64_message = config
            base64_bytes = base64_message.encode('ascii')
            message_bytes = base64.b64decode(base64_bytes)
            message = message_bytes.decode('ascii')
            description.write(message)
            description.close()
            i = i + 1
        except TypeError:
            i = i + 1
            continue
        except UnicodeDecodeError:
            i = i + 1
            continue

if len(sys.argv) == 1:
    print("Welcome to UniGet. This program will download the latest config files of all devices in Unimus.\n")
    print("Fetching info...")
    get_ids_and_descriptions()
    print("Saving configs and updating hostname resolution files...")
    get_configs()
    print("Done!")
elif len(sys.argv) == 2:
    resolve_hostname(sys.argv[1])
else:
    print('[ERR] Too many arguments.\nExamples:\n./uniget.py my-filename\n./uniget.py')
