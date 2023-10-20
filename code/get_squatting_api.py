from calendar import different_locale
import json
from tqdm import tqdm

### For url squatting attack

def read_apis():
    apis = open('dataset/api.json').read().split('\n')[:-1]
    apis = [json.loads(api) for api in apis]
    return apis


def get_host_urls_to_api(apis):
    # extract all the host url from apis
    host_urls_to_api = {}
    for api in apis:
        for function in api['functions']:
            for parameter in function['parameters']:
                if parameter['name'] == 'X-RapidAPI-Host':
                    host_urls_to_api[parameter['example_value']] = api
    return host_urls_to_api


def compare_two_string(string1, string2):
    if len(string1) == len(string2):
        same_char = 0
        for a in range(0, len(string1)):
            if string1[a] == string2[a]:
                same_char = same_char + 1
        if same_char == len(string1) - 1:
            return True
    return False


def compare_two_different_string(string1, string2):
    same_char = 0
    later_one = 0
    for char in range(0, len(string2)):
        if string1[char + later_one] == string2[char]:
            same_char = same_char + 1
        if string1[char + later_one] != string2[char]:
            later_one = 1
            if string1[char + later_one] == string2[char]:
                same_char = same_char + 1
            else:
                break
    if same_char == len(string1) - 1:
            return True
    return False


def find_similar_urls(host_urls):
    # find similar urls with only one character difference after removing numbers and symbols 
    # possible squatting ways: change or add a character or symbol
    similar_urls = []
    with tqdm(total = len(host_urls)) as pbar:
        for i in range(0, len(host_urls)):
            x = pbar.update(1)
            url1 = ''.join([char for char in host_urls[i] if not char.isdigit()])
            #url1 = host_urls[i]
            for j in range(i, len(host_urls)):
                url2 = ''.join([char for char in host_urls[j] if not char.isdigit()])
                #url2 = host_urls[j]
                if url1 == url2:
                    continue
                if len(url1) == len(url2):
                    if compare_two_string(url1, url2) == True:
                        similar_urls.append((host_urls[i], host_urls[j]))
                if len(url1) - len(url2) == 1:
                    if compare_two_different_string(url1, url2) == True:
                        similar_urls.append((host_urls[i], host_urls[j]))
                if len(url2) - len(url1) == 1:
                    if compare_two_different_string(url2, url1) == True:
                        similar_urls.append((host_urls[i], host_urls[j]))
    return similar_urls


def get_groups(similar_urls):
    # cluster the urls into groups if two urls are similar
    groups = []
    for similar_url in similar_urls:
        groups.append(similar_url)
    while True:
        k = 0
        for i in range(0, len(groups)):
            for j in range(0, len(groups)):
                if i == j:
                    continue
                if len(set(groups[i]) & set(groups[j])) > 0:
                    groups[i] = groups[i] + groups[j]
                    groups[j] = []
                    k = k + 1
        groups1 = []
        for i in groups:
            if i != []:
                groups1.append(i)
        groups = groups1
        if k == 0:
            break
    return groups


def get_possible_squatting_urls(groups):
    # for each group, find the commonly used url and the hardly used url, which is possible to be squatting url
    possible_squatting_urls = {}
    for group in groups:
        url_times = {}
        for url in set(group):
            url_remove_number = ''.join([char for char in url if not char.isdigit()])
            if url_remove_number in url_times:
                url_times[url_remove_number] = url_times[url_remove_number] + 1
            else:
                url_times[url_remove_number] = 1
            sorted_times = sorted(url_times.items(), key=lambda kv: kv[1], reverse = True)
        group_keyword = ''.join([char for char in sorted_times[0][0] if not char.isdigit()])
        # remove url without content or testing urls
        if group_keyword == '.p.rapidapi.com' or 'test' in group_keyword:
            continue
        for url_and_times in sorted_times:
            if url_and_times[0] != group_keyword:
                possible_squatting_urls[url_and_times[0]] = sorted_times[0]
    # ignore if one squat another url only used one time
    possible_squatting_urls_1_more = {}
    for url in possible_squatting_urls:
        if possible_squatting_urls[url][1] > 1:
            possible_squatting_urls_1_more[url] = possible_squatting_urls[url]    
    return possible_squatting_urls, possible_squatting_urls_1_more


def main():

    # read api data
    apis = read_apis()

    # extract url and map to api
    host_urls_to_api = get_host_urls_to_api(apis)
    host_urls = list(set(host_urls_to_api.keys()))

    # find similar url pairs (only one character different)
    similar_urls = find_similar_urls(host_urls)
    similar_urls = list(set(similar_urls))
    similar_urls.sort()

    # cluster the urls into groups
    groups = get_groups(similar_urls)

    # find possible squatting urls
    possible_squatting_urls, possible_squatting_urls_1_more = get_possible_squatting_urls(groups)

    print(possible_squatting_urls, possible_squatting_urls_1_more)


'''
amazon-data-scrapper.p.rapidapi.com
('amazon-data-scraper.p.rapidapi.com', 18)

amazon-data-scapper.p.rapidapi.com
('amazon-data-scraper.p.rapidapi.com', 18)

amazon-data-scraper-.p.rapidapi.com
('amazon-data-scraper.p.rapidapi.com', 18)

chatopt.p.rapidapi.com
('chatgpt.p.rapidapi.com', 3)

climate-change-news-.p.rapidapi.com
('climate-change-news.p.rapidapi.com', 25)

currency-convertor.p.rapidapi.com
('currency-converter.p.rapidapi.com', 13)

instagram-.p.rapidapi.com
('instagram.p.rapidapi.com', 8)

qr-code-genrator.p.rapidapi.com
('qr-code-generator.p.rapidapi.com', 15)

qr-cose.p.rapidapi.com
('qr-code.p.rapidapi.com', 10)

'''


# The AppCrazy couldn't detect some cases such as chatgpt => chatopt and qrcode => qrcose 

import deformation_method
from optparse import  OptionParser


def get_hosts(apis):
    hosts = []
    for api in apis:
        for function in api['functions']:
            for parameter in function['parameters']:
                if parameter['name'] == 'X-RapidAPI-Host':
                    hosts.append(parameter['example_value'])
    hosts = [host.replace('.p.rapidapi.com', '') for host in hosts]
    hosts = list(set(hosts))
    return hosts


def get_hosts_ignore_number(hosts):
    hosts_ignore_number = {}
    for host in hosts:
        url = ''.join([char for char in host if not char.isdigit()])
        if url in hosts_ignore_number:
            hosts_ignore_number[url].append(host)
        else:
            hosts_ignore_number[url] = [host]
    return hosts_ignore_number


def get_possible_squatting_urls(hosts_ignore_number):
    possible_squatting_urls = []
    for host in hosts_ignore_number:
        try:
            p_variants = deformation_method.DeformationMethod(host)
            p_variants.packagename_deformation()
            p_result_dic = p_variants.variant_dic
            for j in p_result_dic:
                if j in hosts_ignore_number:
                    possible_squatting_urls.append((host, j))
        except:
            continue
    return possible_squatting_urls


def present_results(hosts_ignore_number, possible_squatting_urls):
    for i in possible_squatting_urls:
        url1_times = len(hosts_ignore_number[i[0]])
        url2_times = len(hosts_ignore_number[i[1]])
        if url1_times == 1 and url2_times == 1:
            continue
        # same words and same number (very limited)
#        for j in hosts_ignore_number[i[0]]:
#            for k in hosts_ignore_number[i[1]]:
#                url1 = ''.join([char for char in j if char.isdigit()])
#                url2 = ''.join([char for char in k if char.isdigit()])
#                if url1 == url2:
#                    print(j, k)
        # same words, ignore number
        if url1_times > url2_times:
            print(i[0], len(hosts_ignore_number[i[0]]))
            print(i[1], len(hosts_ignore_number[i[1]]))
            print()
        else:
            print(i[1], len(hosts_ignore_number[i[1]]))
            print(i[0], len(hosts_ignore_number[i[0]]))
            print()



def main():
    apis = read_apis()

    hosts = get_hosts(apis)

    hosts_ignore_number = get_hosts_ignore_number(hosts)

    possible_squatting_urls = get_possible_squatting_urls(hosts_ignore_number)

    present_results(hosts_ignore_number, possible_squatting_urls)


'''
amazon-data-scrapper 3
amazon-data-scrapper- 1

amazon-data-scraper 18
amazon-data-scrapper 3

amazon-scraper 5
amazon-scrapper 2

amazon-scraper 5
amazon-scraper- 1

climate-change-news 25
climate-change-news- 1

currency-converter 13
currency-convertor 1

instagram 8
instagram- 1

qr-code-generator 15
qr-code-genrator 1
'''




'''
k = 0
for result in results:
    url1 = ''.join([char for char in result[0] if not char.isdigit()])
    url2 = ''.join([char for char in result[1] if not char.isdigit()])
    if url1 not in possible_squatting_urls_1_more and url2 not in possible_squatting_urls_1_more:
        continue
    k = k + 1
    print(k)
    print()
    if url1 in possible_squatting_urls_1_more:
        print(result[0], result[1], possible_squatting_urls_1_more[url1])
    if url2 in possible_squatting_urls_1_more:
        print(result[1], result[0], possible_squatting_urls_1_more[url2])
    print()
    print(host_urls_to_api[result[0]]['developer'], host_urls_to_api[result[1]]['developer'])
    print()
    print(host_urls_to_api[result[0]]['content'])
    print()
    print(host_urls_to_api[result[1]]['content'])
    print()
'''



test = []
for api in apis:
    if api['name'][-1].isdigit():
        test.append(api['name'])


test2 = []
for i in tqdm(test):
    for api in apis:
        if ''.join([char for char in i if not char.isdigit()]) == api['name']:
            test2.append((i, api['name']))


('exampleapi2', 'exampleapi')
('CricketAPI2', 'CricketAPI')
('Amazon53', 'Amazon')
('livescore1', 'livescore')
('Auth100', 'Auth')
('Chain49', 'Chain')
('prueba2', 'prueba')
('amazon-scraper11', 'amazon-scraper')



for url in possible_squatting_urls_1_more:
    print(url, test.count(url), possible_squatting_urls_1_more[url])








similar_urls = find_similar_urls(host_urls)



def find_similar_urls2(similar_urls):
    similar_urls2 = []
    for i in tqdm(similar_urls):
        url1, url2 = i
        if url1 == url2:
            continue
        if len(url1) == len(url2):
            if compare_two_string(url1, url2) == True:
                similar_urls2.append(i)
        if len(url1) - len(url2) == 1:
            if compare_two_different_string(url1, url2) == True:
                similar_urls2.append(i)
        if len(url2) - len(url1) == 1:
            if compare_two_different_string(url2, url1) == True:
                similar_urls2.append(i)
    return similar_urls2


similar_urls2 = find_similar_urls2(similar_urls)

similar_urls3 = []
for i in similar_urls2:
    try:
        k = 0
        if i[0][-16].isnumeric():
            k = k + 1
        if i[1][-16].isnumeric():
            k = k + 1
        if k > 1:
            similar_urls3.append(i)
    except:
        continue   


for i in similar_urls3:
    url1, url2 = i
    api1 = ''
    api2 = ''
    for api in apis:
        for function in api['functions']:
            for parameter in function['parameters']:
                if parameter['name'] == 'X-RapidAPI-Host':
                    if url1 == parameter['example_value']:
                        api1 = api
                    if url2 == parameter['example_value']:
                        api2 = api
    k = 0
    if api1['name'][-1].isnumeric():
        k = k + 1
    if api2['name'][-1].isnumeric():
        k = k + 1
    if k == 1:
        print(api1['name'], api1['api_link'])
        print(api2['name'], api2['api_link'])
        print()





Throne of Glass API https://rapidapi.com/hkbertoson/api/throne-of-glass-api2/
Throne of Glass API 2 https://rapidapi.com/jamesqquick/api/throne-of-glass-api-2/

Color Extractor for Apparel 2 https://rapidapi.com/farba/api/color-extractor-for-apparel-2/
Color Extractor for Apparel https://rapidapi.com/farba/api/color-extractor-for-apparel2/


Translator https://rapidapi.com/w3care3/api/translator7/
Translator 7 https://rapidapi.com/krovin70/api/translator-7/


notes https://rapidapi.com/djnotes/api/notes2/
Notes 2 https://rapidapi.com/ethanl2014/api/notes-2/





1 links one character different
2 links remove number one different
3 name different


import json
import signal
import requests
from tqdm import tqdm


def handler(signum, frame):
    raise Exception(" ")

signal.signal(signal.SIGALRM, handler)



apis = open('api2.json').read().split('\n')[:-1]
apis = [json.loads(i) for i in apis]
links = [i for i in apis if i['website'] != '']

k = 0
for link in tqdm(links):
    try:
        x = signal.alarm(30)
        code = requests.head(link['website']).status_code
        #print(i['website'], code)
        if code != 200:
            k = k + 1
        x = signal.alarm(0)
    except:
        k = k + 1
        

a=open('api_spam.json')
a=open('api_spam.json').read().split('\n')[:-1]
a=[json.loads(i) for i in a]
times={}
for i in a:
    if i['developer_link'] in times:
        times[i['developer_link']] = times[i['developer_link']] + 1
    else:
        times[i['developer_link']] = 1

sorted_times = sorted(times.items(), key=lambda kv: kv[1], reverse = True)