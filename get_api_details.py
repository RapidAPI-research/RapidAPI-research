import time
import json
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())

apis = open('dataset.txt').read().lower().split('\n')[:-1]

done = open('api.jsonl').read()
print(len(done.split('\n')))

for api in tqdm(apis):
    if api in done:
        continue
    try:
        all_links = []
        try:
            driver.get(api)
        except:
            continue
        while True:
            if 'Access denied' in driver.title:
                print('wait for 10 minutes')
                time.sleep(600) 
                driver.get(api)
            else:
                break

        time.sleep(2)
        try:
            name = driver.find_elements(By.CLASS_NAME, 'Name')[0].text.split('\n')[0]
        except:
            continue

        try:
            free = driver.find_elements(By.CLASS_NAME, 'badge-secondary')[0].text
        except:
            free = ''

        try:
            official_verified = driver.find_elements(By.CLASS_NAME, 'TagName')
            if len(official_verified) == 2:
                official = 'Official'
                verified = 'Verified'
            elif 'official' in driver.find_elements(By.CLASS_NAME, 'TagName')[0].text.lower():
                official = 'Official'
                verified = ''
            elif 'Verified' in driver.find_elements(By.CLASS_NAME, 'TagName')[0].text:
                verified = 'Verified'
                official = ''
        except:
            verified = ''
            official = ''

        try:
            popularity = driver.find_elements_by_class_name('Value')[0].text
        except:
            popularity = ''

        try:
            latency = driver.find_elements_by_class_name('Value')[1].text
        except:
            latency = ''

        try:    
            service = driver.find_elements_by_class_name('Value')[2].text
        except:
            service = ''

        try:
            developer, last_update, category =  driver.find_elements(By.CLASS_NAME, 'About')[0].text[3:].split(' | ')[:3]
        except:
            developer = ''
            last_update = ''
            category = ''

        content = ''
        for paragraph in driver.find_elements(By.CLASS_NAME, 'MarkdownPreview'):
            content = content + paragraph.text
        
        try:
            playground = driver.find_elements(By.CLASS_NAME, 'PlaygroundContainer')[0].get_attribute('src')
        except:
            continue

        try:
            driver.get(api + 'details')
        except:
            continue
        time.sleep(2)

        website = ''
        for href in driver.find_elements_by_xpath("//a[@href]"):
            if 'Product Website' in href.text:
                website = href.get_attribute("href")

        try:
            rating = driver.find_elements_by_class_name('b-rating')[0].get_attribute('aria-valuenow')
        except:
            rating = ''

        try:
            driver.find_elements_by_link_text('Terms of use')[0].click()
            time.sleep(2)
            terms_of_use = driver.find_elements_by_class_name('modal-body')[0].text
        except:
            terms_of_use = ''
        
        driver.get(playground)
        time.sleep(5)

        function_categories = driver.find_elements(By.CLASS_NAME, 'ant-collapse-header')

        k = 0
        for function_category in function_categories:
            time.sleep(2)
            category_name = function_category.text
            if category_name == 'Header Parameters':
                break            
            if k > 0:
                function_category.click()
            k = k + 1

        functions = []
        for function_data in driver.find_elements(By.CLASS_NAME, 'content'):
            time.sleep(2)
            function = {}
            get_or_post = function_data.find_elements(By.CLASS_NAME, 'sc-jnqLxu')[0].text
            function_name = function_data.find_elements(By.CLASS_NAME, 'endpoint-name')[0].text
            try:
                function_data.click()
            except:
                continue

            try:
                description = driver.find_elements(By.CLASS_NAME, 'sc-kJwmPe')[0].text
            except:
                description = ''

            function['get_or_post'] = get_or_post
            function['name'] = function_name
            function['description'] = description

            parameters = []
            for line in driver.find_elements(By.CLASS_NAME, 'sc-gCkVGe'):
                parameter = {}
                try:
                    parameter['name'] = line.find_elements(By.CLASS_NAME, 'name')[0].text
                except:
                    continue
                try:
                    parameter['type'] = line.find_elements(By.CLASS_NAME, 'type')[0].text
                except:
                    parameter['type'] = ''
                try:
                    parameter['meta_fields'] = line.find_elements(By.CLASS_NAME, 'meta-fields')[0].text
                except:
                    parameter['meta_fields'] = ''
                try:
                    parameter['example_value'] = line.find_elements(By.CLASS_NAME,'ant-input')[0].get_attribute('value')
                except:
                    parameter['example_value'] = line.find_elements(By.CLASS_NAME, 'ant-form-item-control-input')[0].text
                try:
                    parameter['description'] = line.find_elements(By.CLASS_NAME, 'description')[0].text
                except:
                    parameter['description'] = ''
                try:
                    parameter['required'] = line.find_elements(By.CLASS_NAME, 'condition')[0].text
                except:
                    parameter['required'] = ''

                parameters.append(parameter)

            function['parameters'] = parameters
            functions.append(function)

        with open('api.jsonl', 'a') as f:
            api_data = {'api_link': api, 'name': name, 'free': free, 'official':official, 'verified':verified, 'popularity': popularity, 'latency': latency, 'service': service, "developer": developer, 'last_update': last_update, 'category': category, 'content': content, 'website': website, 'terms_of_use': terms_of_use, 'rating': rating, 'functions': functions}
            x = f.write(json.dumps(api_data) + '\n')

    except:
        continue

driver.close()

