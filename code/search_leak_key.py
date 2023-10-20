import os
import re
import json
from tqdm import tqdm

repos = os.listdir('repos')

path_key_host = []
for repo in tqdm(repos):
    for path, subdirs, files in os.walk('repos/' + repo):
        for name in files:
            try:
                code = open(os.path.join(path, name)).read().lower()
            except:
                continue
            if 'x-rapidapi-key' in code:
                key = ''
                have_key = 0
                for line in code.split('\n'):
                    if 'x-rapidapi-key' in line:
                        data = re.findall('"([^"]*)"', line)
                        for possible_key in data:
                            if len(possible_key) != 50:
                                continue
                            if any(not char.isalnum() for char in possible_key):
                                continue
                            key = possible_key
                            have_key = 1
                if have_key == 0:
                    continue
                host = ''
                for line in code.split('\n'):
                    if 'x-rapidapi-host' in line:
                        data = re.findall('"([^"]*)"', line)
                        for possible_host in data:
                            if 'p.rapidapi.com' in possible_host:
                                host = possible_host
                path_key_host.append((path, key, host))


# 2,153 keys from 6495 repos to 694 APIs.

for possible_key in path_key_host:
    if possible_key[1][10:13] == 'msh' and possible_key[1][28:30] == 'p1' and possible_key[1][35:38] == 'jsn':
        continue
    print(possible_key)


apis = open('/home/Downloads/rapidapi/api2.json').read().split('\n')[:-1]
apis = [json.loads(api) for api in apis]

api_path_key_host = []
for i in tqdm(path_key_host):
    path, key, host = i
    for api in apis:
        for function in api['functions']:
            for parameter in function['parameters']:
                if parameter['name'] == 'X-RapidAPI-Host':
                    if parameter['example_value'] == host:
                        api_path_key_host.append((api, path, key, host))


'''
api_path_key_host = list(set(api_path_key_host))


price = {}
for i in api_path_key_host:
    api = i[0]['api_link']
    if api in price:
        continue
    price[api] = i[0]['free']


times = {}
for i in price:
    if price[i] in times:
        times[price[i]] = times[price[i]] + 1
    else:
        times[price[i]] = 1
'''



# 15 paid, 385 freemium, 165 free


test = []
for i in api_path_key_host:
    if i[0]['free'] == 'FREE':
        test.append((i[0]['api_link'], i[1], i[2], i[3]))


len(set([i[2] for i in test]))


## keys used by several developers

developers_keys = list(set([(i[1].split('/')[1], i[2]) for i in api_path_key_host]))
developer_times = {}
for i in developers_keys:
    if i[1] in developer_times:
        developer_times[i[1]] = developer_times[i[1]] + 1
    else:
        developer_times[i[1]] = 1


sorted_x = sorted(developer_times.items(), key=lambda kv: kv[1], reverse = True)

sorted_x[:10]

k = 0
for i in sorted_x:
    if i[1] > 1:
        k = k + 1


'''
## apis used by several developers

developer_host = list(set([(i[1].split('/')[1], i[3]) for i in api_path_key_host]))
host_times = {}
for i in developer_host:
    if i[1] in host_times:
        host_times[i[1]] = host_times[i[1]] + 1
    else:
        host_times[i[1]] = 1


sorted_x = sorted(host_times.items(), key=lambda kv: kv[1], reverse = True)

('wft-geo-db.p.rapidapi.com', 19)
('covid-193.p.rapidapi.com', 22)
('coinranking1.p.rapidapi.com', 23)
('bing-news-search1.p.rapidapi.com', 25)
('iamai.p.rapidapi.com', 46)

for i in sorted_x[:5]:
    for api in apis:
        for function in api['functions']:
            for parameter in function['parameters']:
                if parameter['name'] == 'X-RapidAPI-Host':
                    if parameter['example_value'] == i[0]:
                        data = api['free']
    print(data)
'''





def get_apis_can_edit_data(apis):
    api_can_edit_data = []
    for api in apis:
        can_get = 0
        can_edit = 0
        for function in api['functions']:
            if function['get_or_post'] == 'GET' or function['get_or_post'] == 'POST':
                can_get = 1
            if function['get_or_post'] != 'GET' and function['get_or_post'] != 'POST':  # 217
                can_edit = 1
        if can_get == 1 and can_edit == 1:
            api_can_edit_data.append(api)
    return api_can_edit_data


def get_apis_can_edit_data_without_auth(apis):
    api_can_edit_data_without_auth = []
    for api in apis:
        can_get = 0
        can_edit = 0
        for function in api['functions']:
            if function['get_or_post'] == 'GET' or function['get_or_post'] == 'POST':
                can_get = 1
            if function['get_or_post'] != 'GET' and function['get_or_post'] != 'POST':  # 217
                auth = 0
                for parameter in function['parameters']:
                    if 'auth' in (parameter['name'] + parameter['type']).lower():
                        auth = 1
                if auth == 0:           # 150
                    can_edit = 1
        if can_get == 1 and can_edit == 1:
            #print(api['api_link'])
            #print([function['get_or_post'] for function in api['functions']])
            #print([function['name'] for function in api['functions']])
            api_can_edit_data_without_auth.append(api)
    return api_can_edit_data_without_auth


apis_can_edit_data = get_apis_can_edit_data(apis)
api_can_edit_data_without_auth = get_apis_can_edit_data_without_auth(apis)


test = []
for i in api_path_key_host:
    api, path, key, host = i
    if api in api_can_edit_data_without_auth:
        if (api, path, key, host) in test:
            continue
        test.append((api, path, key, host))


print(len(set([i[0]['api_link'] for i in test])))
print(len(set([i[2] for i in test])))

