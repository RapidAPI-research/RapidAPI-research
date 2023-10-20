## find api without function and only for advertising
# 9% has a website for normal api, 78.9% for no function api

import re
import json
from tqdm import tqdm
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0


def read_apis():
    apis = open('dataset/api.json').read().split('\n')[:-1]
    apis = [json.loads(api) for api in apis]
    return apis


def detect_ads(apis):
    no_functions = []
    no_functions_with_url = []
    languages = {}
    urls = {}
    for api in tqdm(apis):
        if api['functions'] == []:
            no_functions.append(api)
            try:
                language = detect(api['content'])
            except:
                continue
            if language in languages:
                languages[language] = languages[language] + 1
            else:
                languages[language] = 1
            if 'http' in api['content']:
                no_functions_with_url.append(api)
                try:
                    url = re.search("(?P<url>https?://[^\s]+)", api['content']).group("url")
                except:
                    continue
                if url in urls:
                    urls[url] = urls[url] + 1
                else:
                    urls[url] = 1
    languages = sorted(languages.items(), key=lambda kv: kv[1], reverse = True)
    return no_functions, no_functions_with_url, languages, urls


def main():

    apis = read_apis()

    no_functions, no_functions_with_url, languages, urls = detect_ads(apis)

    print(len(apis))
    print(len(no_functions))
    print(len(no_functions_with_url))
    print(languages)
    print(len(urls))

    # 7107, 2414, 2074, 1706 vi, 1944 urls
    # 34% no function, 29% with url, 71% is vi,



# failed
'''
import requests
url = 'https://www.virustotal.com/vtapi/v2/url/scan'
params = {'apikey': '', 'url': 'https://lichvannien.net/am-lich/nam/2023/thang/5/ngay/3'}
headers = {"content-type": "application/x-www-form-urlencoded"}
response = requests.post(url, data=params, headers = headers)
print(response.json())



def get_malicious_website(html):
    virustotal = 'https://www.virustotal.com/vtapi/v2/url/report'
    result = {}
    with tqdm(total = len(html)) as pbar:
        for website in html:
            x = pbar.update(1)
            try:
                try:
                    with timeout(90, exception = RuntimeError):
                        params = {'apikey': '1d6f24128287da549933fbd012cf258a304a9fecc40dcb84d47c86eb0b052501', 'resource': website}
                        response = requests.get(virustotal, params = params)
                        time.sleep(60)
                        result[website] = response.json()
                        with open('virustotal.json', 'a') as f:
                            x = json.dump(response.json(), f)
                            x = f.write('\n')
                except RuntimeError:
                    continue
            except:
                continue
    malicious_websites = []
    for i in result:
        try:
            if i['positives'] > 0:
                malicious_websites.append(i)
        except:
            continue
    return malicious_websites

'''