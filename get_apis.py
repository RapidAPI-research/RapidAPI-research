import os
import re
import time
import json
import nltk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())

'''
categories = open('category.txt').read().lower().split('\n')[:-1]
categories.sort()
done = os.listdir('category')

for category in categories:
    if category.replace('https://rapidapi.com/category/', '') + '.txt' in done:
        continue
    all_links = []
    driver.get(category)
    while True:
        time.sleep(5)
        page_links = [link.get_attribute('href') for link in driver.find_elements(By.CLASS_NAME, 'CardLink')]
        if page_links[0] in all_links:
            break
        all_links = all_links + page_links
        next_page = driver.find_elements(By.CLASS_NAME, 'r-page-link')[-2]
        next_page.send_keys(Keys.ENTER)
        time.sleep(5)
    with open('category/' + category.replace('https://rapidapi.com/category/', '') + '.txt', 'w') as f:
        for link in all_links:
            x = f.write(link + '\n')
'''

'''import spacy
from spacy.language import Language
from spacy_langdetect import LanguageDetector
# get words from downloaded apis


apis = open('api.json').read().split('\n')[:-1]
apis = [json.loads(i) for i in apis]


def get_lang_detector(nlp, name):
    return LanguageDetector()

nlp = spacy.load("en_core_web_sm")
Language.factory("language_detector", func=get_lang_detector)
nlp.add_pipe('language_detector', last=True)


words = {}
for api in tqdm(apis):
    content = api['content'] + '. ' + api['name']
    doc = nlp(content.lower())
    if doc._.language['language'] == 'en':
        for word in doc:
            if word.is_alpha:
                if word.lemma_ in word.text:
                    if word.lemma_ in words:
                        words[word.lemma_] = words[word.lemma_] + 1
                    else:
                        words[word.lemma_] = 1
                else:
                    if word.lemma_ in words:
                        words[word.lemma_] = words[word.lemma_] + 1
                    else:
                        words[word.lemma_] = 1
                    if word.text in words:
                        words[word.text] = words[word.text] + 1
                    else:
                        words[word.text] = 1

sorted_x = sorted(test.items(), key=lambda kv: kv[1], reverse = True)

with open('words_new_2.txt', 'w') as f:
    for i in sorted_x:
        x = f.write(i[0] + '\n')



test ={}
for api in tqdm(apis):
    sentences = re.split(r' *[\n\,\.!][\'"\)\]]* *', api['content'].lower())
    for sentence in sentences:
        for word in nltk.word_tokenize(sentence):
            if word in stopwords:
                continue
            if word in test:
                test[word] = test[word] + 1
            else:
                test[word] = 1

sorted_x = sorted(test.items(), key=lambda kv: kv[1], reverse = True)

from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

test = []
for i in tqdm(sorted_x):
    try:
        if detect(i[0]) == 'vi':
            continue
        test.append(i)
        if len(test) == 2000:
            break
    except:
        continue
'''


words = open('words_new.txt').read().split('\n')[:-1]
done = os.listdir('words')
for word in words:
    if word + '.txt' in done:
        continue
    driver.refresh()
    all_links = []
    search_area = driver.find_elements(By.CLASS_NAME, 'MainSearchField')[0]
    search_area.send_keys(word)
    time.sleep(20)
    while True:
        time.sleep(5)
        page_links = [link.get_attribute('href') for link in driver.find_elements(By.CLASS_NAME, 'CardLink')]
        if page_links[0] in all_links:
            break
        all_links = all_links + page_links
        try:
            next_page = driver.find_elements(By.CLASS_NAME, 'r-page-link')[-2]
            next_page.send_keys(Keys.ENTER)
        except:
            break
        time.sleep(5)
    with open('words/' + word + '.txt', 'w') as f:
        for link in all_links:
            x = f.write(link + '\n')


driver.close()

b = os.listdir('words')
b.sort()
k = 0
for i in b:
    print(i, len(open('words/' + i).read().split('\n')[:-1]))
    k = k + len(open('words/' + i).read().split('\n')[:-1])

print(k)