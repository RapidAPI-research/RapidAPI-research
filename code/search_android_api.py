import os
import re
import json
from tqdm import tqdm

locations = open('location.txt').read().split('\n')[:-1]
locations.sort()

## get key leakage in Android APKs
path_key_host = []
for repo in tqdm(locations):
    code = open(repo.replace('app_decoding', 'apps_with_rapidapi')).read()
    data = re.findall('"([^"]*)"', code)
    key = ''
    for possible_key in data:
        if len(possible_key) != 50:
            continue
        if any(not char.isalnum() for char in possible_key):
            continue
        key = possible_key
    host = ''
    for possible_host in data:
        if 'p.rapidapi.com' in possible_host:
            host = possible_host
    path_key_host.append((repo, key, host))


key_host = list(set([i[1:] for i in path_key_host]))
print(len(set([key[0] for key in key_host])))





### get apk privacy policy link and data safety

## get apk package name (run on palmetto)

import os
from tqdm import tqdm
from xml.dom import minidom


repos = os.listdir('apps_with_rapidapi/')
repos = [repo for repo in repos if repo.endswith('apk') == False and repo.startswith('0')]


for repo in tqdm(repos):
    try:
        file = minidom.parse('apps_with_rapidapi/' + repo + '/AndroidManifest.xml')
        models = file.getElementsByTagName('manifest')
        with open('apks.txt', 'a') as f:
            x = f.write(models[0].attributes['package'].value + '\t' + repo + '\n')
    except:
        continue


## get apk privacy policy link from package name (run on linux)

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

apks = open('apks.txt').read().split('\n')[:-1]
driver = webdriver.Chrome(ChromeDriverManager().install())

for apk in tqdm(apks):
    package, repo = apk.split('\t')
    apk_data = {}
    time.sleep(3)
    driver.get('https://play.google.com/store/apps/details?id=' + package)
    if driver.title == 'Not Found':
        #apk_data[apk] = 'apk not found'
        continue
    time.sleep(3)
    driver.get('https://play.google.com/store/apps/datasafety?id=' + package)
    apk_data['package'] = package
    apk_data['repo'] = repo
    apk_data['data_safety'] = ''
    for element in driver.find_elements(By.CLASS_NAME, 'Mf2Txd'):
        apk_data['data_safety'] = apk_data['data_safety'] + element.text + '\n'
    privacy_policy_link = ''
    for element in driver.find_elements(By.CLASS_NAME, 'GO2pB'):
        if element.get_attribute('href') == None:
            continue
        if 'privacy' in element.text:
            privacy_policy_link = element.get_attribute('href')
            apk_data['privacy_policy_link'] = privacy_policy_link
    if privacy_policy_link == '':
        apk_data['privacy_policy_link'] = 'not found'
    with open('apks_privacy_policy.json', 'a') as f:
        x = f.write(json.dumps(apk_data) + '\n')
    
driver.close()


## analyze apk and called api

import re
import json
from tqdm import tqdm

def read_apis():
    apis = open('api.json').read().split('\n')[:-1]
    apis = [json.loads(api) for api in apis]
    return apis


def get_left(data):
    left = data[:data.find('.p.rapidapi.com')]
    left = left[::-1]
    for i in range(0, len(left)):
        if left[i].isalnum() == False and left[i] != '-':
            break
    if i + 1 != len(left):
        left = left[:i]
    left = left[::-1]
    return left


def get_right(data):
    right = data[data.find('.p.rapidapi.com'):]
    for i in range(0, len(right)):
        if right[i].isalnum() == False and right[i] != '-' and right[i] != '/' and right[i] != '.':
            break
    if i + 1 != len(right):
        right = right[:i]
    if right[-1] == '/':
        right = right[:-1]
    return right


def find_rapidapi(data):
    left = get_left(data)
    right = get_right(data)
    return left, right




## Get what api the apks call

apis = read_apis()
apis_url = {}
for api in apis:
    for function in api['functions']:
        for parameter in function['parameters']:
            if parameter['name'] == 'X-RapidAPI-Host':
                apis_url[parameter['example_value']] = api


apk_hosts = []
for location in tqdm(locations):
    apk = location.split('/')[1]
    code = open(location.replace('app_decoding', 'apps_with_rapidapi')).read()
    data = re.findall('"([^"]*)"', code)
    for possible_host in data:
        if '.p.rapidapi.com' in possible_host:
            left = find_rapidapi(possible_host)[0]
            right = find_rapidapi(possible_host)[1]
            if (apk, left, right) in apk_hosts:
                continue
            apk_hosts.append((apk, left, right))


def get_longest_match(url, possible_functions):
    max_value = 0
    max_percentage = 0
    max_function = 0
    for function in possible_functions:
        final_function = function['url'].replace('https://', '').replace('v2', 'v1').replace('v3', 'v1')
        k = 0
        for i in range(0, min(len(url), len(final_function))):
            if url[i] == final_function[i]:
                k = k + 1
        if k > max_value:
            max_value = k
            max_percentage = k/len(final_function)
            max_function = function
        elif k == max_value:
            if k/len(final_function) > max_percentage:
                max_value = k
                max_percentage = k/len(final_function)
                max_function = function
    return max_function


apk_url_api_function = []
for host in tqdm(apk_hosts):
    apk, apk_host_url, apk_function_url = host
    if apk_function_url == '.p.rapidapi.com':
        for api_url in apis_url:
            if api_url == apk_host_url + '.p.rapidapi.com':
                if (apk, api, '') in apk_url_api_function:
                    continue
                apk_url_api_function.append((apk, api, '', apk_host_url + apk_function_url))
    else:
        apk_function_url = apk_function_url.replace('v2', 'v1').replace('v3', 'v1')
        for api_url in apis_url:
            if api_url == apk_host_url + '.p.rapidapi.com':
                api = apis_url[api_url]
                final_function = get_longest_match(apk_host_url + apk_function_url, api['functions'])
                if (apk, api, final_function) in apk_url_api_function:
                    continue
                apk_url_api_function.append((apk, api, final_function, apk_host_url + apk_function_url))





# Then check whether the called api is collecting data

## find api parameter that mention in api/function/parameter description
def validate_data_collection_in_description(possible_data_collection_api):
    # if the subject is a user, then the data is for users
    users = ['user', 'person', 'your']
    # other data related to a person
    # skip the data that can be used by not a person, such as name (product name) or address (weather of address)
    if 'name' in personal_data:
        personal_data.remove('name')
    data_collection_api = []
    for i in possible_data_collection_api:
        api, function, parameter = i
        content = (parameter['description'] + '\n' + function['name'] + '\n' + function['description'] + '\n' + api['name'] + '\n' + api['content']).lower()
        sentences = re.split(r' *[\n\,\.!][\'"\)\]]* *', content)
        parameter['name'] = ''.join([char if char.isalpha() else ' ' for char in parameter['name']])
        for sentence in sentences:
            if parameter['name'] not in sentence:
                continue
            # your + any data type works
            if any (word in sentence.split() for word in users):
                if (api, function, parameter) not in data_collection_api:
                    data_collection_api.append((api, function, parameter))
                continue
        # otherwise, only above data works and the name/address don't work
        if parameter['name'] in personal_data and parameter['name'] in content:
            if (api, function, parameter) not in data_collection_api:
                data_collection_api.append((api, function, parameter))
    return data_collection_api


import get_data_collection

possible_data_collection_api = get_data_collection.get_data_collection_in_parameter(apis)

data_collection_api = validate_data_collection_in_description(possible_data_collection_api)




apk_api_with_data_collection = []
for i in apk_url_api_function:
    apk, api, function, url = i
    for j in data_collection_api:
        api2, function2, parameter = j
        if api == api2:
            if function == '':
                if (apk, api, parameter['name']) in apk_api_with_data_collection:
                    continue
                apk_api_with_data_collection.append((apk, api, parameter['name']))
            else:
                if function == function2:
                    if (apk, api, parameter['name']) in apk_api_with_data_collection:
                        continue
                    apk_api_with_data_collection.append((apk, api, parameter['name']))


len(set([i[0] for i in apk_api_with_data_collection]))


def get_collect_data_from_data_safety_section(data_safety):
    data_collect = 0
    apk_collected_data = []
    for line in data_safety:
        if line == 'Data collected':
            data_collect = 1
            continue
        if line == 'Security practices':
            break
        if data_collect == 1:
            if line == 'expand_more':
                continue
            if ',' in line:
                apk_collected_data = apk_collected_data + line.lower().split(',')
            elif 'and' in line:
                apk_collected_data = apk_collected_data + line.lower().split(' and ')
            else:
                apk_collected_data = apk_collected_data + [line.lower()]
    return apk_collected_data


# check whether the collected data of api is in privacy policy/data safety session

apks_privacy_policy = open('apks_privacy_policy.json').read().split('\n')[:-1]
apks_privacy_policy = [json.loads(apk) for apk in apks_privacy_policy]


for i in apk_api_with_data_collection:
    repo, api, api_collected_data = i
    if api_collected_data == 'username':
        api_collected_data = 'name'
    for apk in apks_privacy_policy:
        if repo == apk['repo']:
            privacy_policy_link = apk['privacy_policy_link']
            data_safety = apk['data_safety'].split('\n')
            apk_collected_data = get_collect_data_from_data_safety_section(data_safety)
            #print(host, api_collected_data, apk_collected_data, privacy_policy_link)
            if api_collected_data not in apk_collected_data:
                print(repo, api['api_link'], api_collected_data + ' not mentioned')


# 28/427


# 1 contact => email
# 2 taint analysis of apk?

for location in locations:
    if '01D8B6DB1A889DCEA72F4A6FE1C33256DDD15BC19AF21022DB86AF2F1DC27763' in location:
        print(location)





times = {}
for i in apk_url_api_function:
    if i[1]['api_link'] in times:
        times[i[1]['api_link']].append(i[0])
    else:
        times[i[1]['api_link']]=[i[0]]


times2 = {}
for i in times:
    for api in apis:
        if api['api_link'] == i:
            if api['category'] in times2:
                times2[api['category']] = times2[api['category']] + len(set(times[i]))
            else:
                times2[api['category']] = len(set(times[i]))
