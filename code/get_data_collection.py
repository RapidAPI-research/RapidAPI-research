import re
import time
import json
import spacy
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

nlp = spacy.load("en_core_web_sm")


def read_apis():
    apis = open('api2.json').read().split('\n')[:-1]
    apis = [json.loads(api) for api in apis]
    return apis


### find data collection in parameter
# we remove the "key" and "password" here because they are more sensitive and we will check them later
personal_data = ['name', 'first name', 'last name', 'full name', 'username']
personal_data = personal_data + ['email', 'e-mail', 'email address']
personal_data = personal_data + ['phone number', 'telephone', 'phone', 'phonebook', 'contact']
personal_data = personal_data + ['ip address', 'mac address']
personal_data = personal_data + ['birthday', 'age', 'gender', 'profession', 'income', 'race', 'religion', 'ethnicity', 'affiliation', 'orientation', 'account']
personal_data = personal_data + ['passport number', 'driver license', 'social security number', 'vehicle identification number', 'insurance policy number', 'ssn', 'vin']
personal_data = personal_data + ['bank account number', 'debit card number', 'credit card number']
address = ['address', 'location', 'geographic', 'gps', 'geolocation', 'position', 'latitude', 'longitude']
address = address + ['zipcode', 'zip code', 'postal code']
address = address + ['country', 'country code', 'state', 'city']
nouns = personal_data + address
nouns_one_word = [''.join(noun.split()) for noun in nouns]
nouns_last_word = [noun.split()[-1] for noun in nouns]


## first check parameter name of api
def get_data_collection_in_parameter(apis):
    default_parameters = ['Request URL', 'X-RapidAPI-Key', 'X-RapidAPI-Host']
    possible_data_collection_api = []
    for api in apis:
        if api['functions'] == []:
            continue
        for function in api['functions']:
            for parameter in function['parameters']:
                if parameter['name'] in default_parameters:
                    continue
                if ''.join([char if char.isalpha() else ' ' for char in parameter['name']]) in nouns_one_word:
                    #print(parameter['name'])
                    possible_data_collection_api.append((api, function, parameter))
    return possible_data_collection_api


### next, check the parameter information to find people-related information (not product name, country code)
def get_noun(i):
    if i.head == i:
        return i
    if i.head.pos_ == 'NOUN':
        return i.head
    return get_noun(i.head)


# check the source of data (such as name) and find the most used words are "person name" and "user name"
def get_source_of_name(possible_data_collection_api):
    source_of_name = {}
    for parameter in tqdm(possible_data_collection_api):
        _, _, parameter = parameter
        if parameter['description'] == '':
            continue
        doc = nlp(parameter['description'])
        for word in doc:
            if get_noun(word) == word:
                continue
            # get the source of "data", such as word = "your" from parameter['name'] = "name"
            if get_noun(word).text.lower() == re.split('[: /._]', parameter['name'].lower())[-1] and (word.pos_ == 'NOUN' or word.pos_ == 'PRON'):
                if (word.text.lower(), parameter['name']) in source_of_name:
                    source_of_name[(word.text.lower(), parameter['name'])] = source_of_name[(word.text.lower(), parameter['name'])] + 1
                else:
                    source_of_name[(word.text.lower(), parameter['name'])] = 1
    sorted_x = sorted(source_of_name.items(), key=lambda kv: kv[1])
    for i in sorted_x[-50:]:
        print(i)


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
                if (api, parameter) not in data_collection_api:
                    data_collection_api.append((api, parameter))
                continue
        # otherwise, only above data works and the name/address don't work
        if parameter['name'] in personal_data and parameter['name'] in content:
            if (api, parameter) not in data_collection_api:
                data_collection_api.append((api, parameter))
    return data_collection_api



### check whether api collects the key/password (very sensitive data) from others
def get_key_from_parameter(apis):
    ask_for_key = []
    for api in apis:
        if api['functions'] == []:
            continue
        for function in api['functions']:
            for parameter in function['parameters']:
                if 'key' in parameter['name'] and 'word' not in parameter['name']:
                    if (api, parameter) not in ask_for_key:
                        ask_for_key.append((api, parameter))
    return ask_for_key


# also check asking for password
def get_password_from_parameter(apis):
    ask_for_password = []
    for api in apis:
        if api['functions'] == []:
            continue
        for function in api['functions']:
            for parameter in function['parameters']:
                if 'password' in parameter['name']:
                    if (api, parameter) not in ask_for_password:
                        ask_for_password.append((api, parameter))
    return ask_for_password


def compare_words(words1, words2):
    common_words_in_url = ['http', '']
    for word in words1 & words2:
        if word not in common_words_in_url:
            return True
    return False


## check the source of key
# 0 api
# 1 api description
# 2 privacy policy link
# 3 developer
# 4 parameter description
def check_source_of_key(ask_for_key):
    ask_rapid_key = []
    official = []
    very_possible = []
    not_sure = []
    no_source = []
    no_source_no_website = []
    for i in ask_for_key:
        api, parameter = i
        # check whether the ky is rapid key
        if len(parameter['example_value']) == 50 or 'rapid' in parameter['description']:
            ask_rapid_key.append(i)
            continue
        api_name = set(re.split('[: /.]', api['name'].lower()))
        api_description = set(re.split('[: /.]', api['content'].lower()))
        privacy_policy_link_words = set(re.split('[: /.]', api['website'].lower().lower()))
        parameter_description = set(re.split('[: /.]', parameter['description'].lower()))
        developer = set(api['developer'].lower().split())
        same_value = 0
        # check whether the key source from description and api name are corresponding
        if compare_words(parameter_description, api_name) == True:
            same_value = same_value + 1
        # check whether the key source from description and api description are corresponding
        if compare_words(parameter_description, api_description) == True:
            same_value = same_value + 1
        # check whether the key source from description and privacy policy link are corresponding'
        if compare_words(parameter_description, privacy_policy_link_words) == True:
            same_value = same_value + 1
        # check whether the key source from description and developer are corresponding
        # if so, we consider it as official api and the key is from the official developer and api
        if compare_words(parameter_description, developer) == True:
            official.append(i)
            continue
        # check whether the key is constant for the api and not sure whether it is published by official developer
        if same_value == 3:
            very_possible.append(i)
        elif same_value == 2:
            not_sure.append(i)
        # if less than 2, the api doesn't the mention source of key
        else:
            # if the api doesn't provide a privacy policy, we don't know where is the source of the key totally
            if api['website'] == '':
                no_source_no_website.append(i)
            else:
                no_source.append(i)
    return ask_rapid_key, official, very_possible, not_sure, no_source, no_source_no_website


import signal

def handler(signum, frame):
    print("timeout")
    raise Exception("end of time")

signal.signal(signal.SIGALRM, handler)

## check whether can get privacy policy link
def get_privacy_policy(data_collection_api):
    done = {}
    results = {}
    for i in tqdm(data_collection_api):
        api, parameter = i
        if api['api_link'] in done:
            results[(api['api_link'], parameter['name'])] = done[api['api_link']]
            continue
        if api['website'] == '':
            done[api['api_link']] = 'don\'t have company link'
            results[(api['api_link'], parameter['name'])] = 'don\'t have company link'
            continue
        #print(api['website'])
        try:
            x = signal.alarm(30)
            url_results = requests.get(api['website'])
            x = signal.alarm(0)
        except:
            done[api['api_link']] = 'broken link'
            results[(api['api_link'], parameter['name'])] = 'broken link'
            continue
        soup = BeautifulSoup(url_results.text, 'html.parser')
        for link in soup.find_all('a'):
            if 'privacy' in link.text.lower():
                done[api['api_link']] = link.get('href')
                if link.get('href').startswith('http') == False:
                    privacy_policy_link = api['website'][:-1] + link.get('href')
                else:
                    privacy_policy_link = link.get('href')
                results[(api['api_link'], parameter['name'])] = privacy_policy_link
        if (api['api_link'], parameter['name']) not in results:
            done[api['api_link']] = 'don\'t have a privacy policy link'
            results[(api['api_link'], parameter['name'])] = 'don\'t have a privacy policy link'
        time.sleep(2)
    return results


## Download privacy policy

import os
import trafilatura
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


# Use chrome webdriver to download html and pdf files
# Get privacy policy pages with webdriver can enable the javascript
def download_privacy_policy(pp_link):
    try:
        done = os.listdir('privacy_policy')
    except:
        x = os.system('mkdir privacy_policy')
        done = []
    for i in tqdm(pp_link):
        api, parameter = i
        api_link = api.replace('/', '~')
        privacy_policy_link = pp_link[i]
        if api_link + '.html' in done or api_link + '.pdf' in done:
            continue
        if privacy_policy_link == '':
            continue
        if privacy_policy_link.endswith('.pdf'):
            x = os.system('curl -L ' + privacy_policy_link + ' >privacy_policy/' + api_link + '.pdf')
        else:
            x = os.system('curl -L ' + privacy_policy_link + ' >privacy_policy/' + api_link + '.html')



# Policylint will keep head content and this library only keeps the main content
def html_to_txt():
    x = os.system('mkdir privacy_policy_txt')
    for file in tqdm(os.listdir('privacy_policy')):
        time.sleep(0.01)
        if file.endswith('.pdf'):
            x = os.system('pdftotext ' + 'privacy_policy/' + file + ' ' + 'privacy_policy_txt/' + file[:-4] + '.txt > /dev/null 2>&1')
        else:
            downloaded = trafilatura.load_html(open('privacy_policy/' + file).read())
            content = trafilatura.extract(downloaded)
            if content == None:
                continue
            with open('privacy_policy_txt/' + file[:-5] + '.txt', 'w') as f:
                x = f.write(content)


def get_incomplete_policy(pp_link):
    incomplete_privacy_policy = []
    for result in pp_link:
        api_link, parameter_name = result
        parameter_name = ''.join([char if char.isalpha() else ' ' for char in parameter_name])
        try:
            content = open('privacy_policy_txt/' + api_link.replace('/', '~') + '.txt', encoding = 'unicode_escape').read().lower()
        except:
            print('download privacy policy failed')
            incomplete_privacy_policy.append(result)
            continue
        if parameter_name == 'address' and ('email address' in content or 'ip address' in content or 'mac address' in content):
            content = content.replace('ip address','').replace('email address','').replace('mac address','')
        if 'name' in parameter_name:
            parameter_name = 'name'
        if 'email' in parameter_name and 'e-mail' in content:
            print(result, 'privacy policy is complete')
        if 'e-mail' in parameter_name and 'email' in content:
            print(result, 'privacy policy is complete')
        if parameter_name in content:
            print(result, 'privacy policy is complete')
        else:
            print(result, 'privacy policy is incomplete')
            incomplete_privacy_policy.append(result)
    return incomplete_privacy_policy


def main():

    apis = read_apis()

    possible_data_collection_api = get_data_collection_in_parameter(apis)

    data_collection_api = validate_data_collection_in_description(possible_data_collection_api)
    # 954 (667 APIs)

    ask_for_key = get_key_from_parameter(apis)
    # 1495 (1067)

    ask_for_password = get_password_from_parameter(apis)
    # 333 (240)

    ask_rapid_key, official, very_possible, not_sure, no_source, no_source_no_website = check_source_of_key(ask_for_key)
    # 21,66,58,87,1018,245
    # 17, 66+58 = 97, 71, a+b = 915 

    results = get_privacy_policy(data_collection_api + ask_for_key + ask_for_password)
    # 1776

    pp_link = {}
    for result in results:
        if results[result].endswith(' link'):
            continue
        pp_link[result] = results[result]
    
    download_privacy_policy(pp_link)

    html_to_txt()

    incomplete_privacy_policy = get_incomplete_policy(pp_link)
    # 8/12







'''


def get_data_collection_in_description(outputs):
    add_sentences = {"how old are you": 'age', "when were you born": 'age', "where do you live":'location' ,"where are you from": 'location', "what can i call you": 'name', 'male or female': 'gender', 'what city do you live in?': 'location'}
    skills = []
    for output in tqdm(outputs):
        filename, api_or_function_or_parameter, output = output
        output = output.lower()
        if 'you' not in output:
            continue
        if ' ' not in output:
            continue
        sentences = re.split(r' *[\n\,\.!][\'"\)\]]* *', output)
        for sentence in sentences:
            if any ('your ' + word + ' is' in sentence for word in nouns):
                continue
            if any (word in sentence for word in nouns) and 'your' in sentence:
                doc = nlp(sentence)
                for word in nouns:
                    if word not in sentence or 'your' not in sentence:
                        continue
                    if word == 'name' and 'your name' not in sentence:
                        continue
                    if word == 'address' and 'email address' in sentence:
                        continue
                    if word == 'address' and 'ip address' in sentence:
                        continue
                    for l in doc:
                        if l.text == 'your' and l.head.text in nouns_last_word and l.head.text in word:
                            if 'name' in word:
                                skills.append((filename, api_or_function_or_parameter, output, 'collect data name'))
                            else:
                                skills.append((filename, api_or_function_or_parameter, output, 'collect data ' + word))
            for sent in add_sentences:
                    if sent in sentence.translate(str.maketrans('', '', string.punctuation)):
                        skills.append((filename, api_or_function_or_parameter, output, 'collect data ' + add_sentences[sent]))
    return skills

api_name = []
api_description = []
function_name = []
function_description = []
parameter_name = []
parameter_example = []
parameter_description = []
for api in apis:
    api_name.append((api['api_link'], api['name']))
    api_description.append((api['api_link'], api, api['content']))
    if api['functions'] == []:
        continue
    for function in api['functions']:
        function_name.append((api['api_link'], function['name']))
        function_description.append((api['api_link'], function, function['description']))
        for parameter in function['parameters']:
            if parameter['name'] in default_parameters:
                continue
            parameter_name.append((api['api_link'], parameter, parameter['name']))
            parameter_example.append((api['api_link'], parameter, parameter['example_value']))
            parameter_description.append((api['api_link'], parameter, parameter['description']))


test = {}
for parameter in parameter_name:
    if 'key' in parameter[2].lower():
        print(parameter[0], parameter[2])
    if parameter[2] in test:
        test[parameter[2]] = test[parameter[2]] + 1
    else:
        test[parameter[2]] = 1


results = get_data_collection_in_description(api_description + function_description + parameter_description)


results = get_data_collection_in_description(api_description)
for result in results:
    _, api, _, _ = result
    if api['functions'] == []:
        continue
    for function in api['functions']:
        for parameter in function['parameters']:
            if parameter['name'] in default_parameters:
                continue
            print(parameter['name'])


results = get_data_collection_in_description(function_description)
for result in results:
    _, function, _, _ = result
    for parameter in function['parameters']:
        if parameter['name'] in default_parameters:
            continue
        print(parameter['name'])



results = []
for word in api_name + function_name:# + parameter_name + parameter_example:
    if ''.join([char for char in word[1].lower() if char.isalpha()]) in nouns:
        results.append(())


'''



test = {}
for i in apis:
    if i['free']  in test:
        if i['website']!='':
            test[i['free']] = test[i['free']] + 1
    else:
        if i['website']!='':
            test[i['free']] = 1



test2 = {}
for i in apis:
    if i['free']  in test2:
        test2[i['free']] = test2[i['free']] + 1
    else:
        test2[i['free']] = 1

#freemium: 4792/10020 = 48%
#free: 5114/8385 = 61%
#paid: 476/965 = 49%



test = {}
for i in apis:
    if i['category']  in test:
        if i['website']!='':
            test[i['category']] = test[i['category']] + 1
    else:
        if i['website']!='':
            test[i['category']] = 1



test2 = {}
for i in apis:
    if i['category']  in test2:
        test2[i['category']] = test2[i['category']] + 1
    else:
        test2[i['category']] = 1


for i in test:
    print(i,test[i]/test2[i])