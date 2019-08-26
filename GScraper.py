"""
Getting Started

This tool requires the following packages:
- Selenium
- BeautifulSoup4

`pip install selenium, beautifulsoup4`
"""


"""
Imports
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup
import re
import os
import time
import random
import json


"""
Constants
"""

# Define the URLs as constants
LOGIN_URL = 'https://www.gartner.com/reviews/login'
BETTYBLOCKS = 'https://www.gartner.com/reviews/market/enterprise-high-productivity-application-paas/vendor/betty-blocks/product/betty-blocks'
MENDIX = 'https://www.gartner.com/reviews/market/enterprise-high-productivity-application-paas/vendor/mendix/product/mendix-platfor'
OUTSYSTEMS = 'https://www.gartner.com/reviews/market/enterprise-high-productivity-application-paas/vendor/outsystems/product/outsystems-platform'

# Extra
QUICKBASE = 'https://www.gartner.com/reviews/market/enterprise-high-productivity-application-paas/vendor/quick-base/product/quick-base'
SALESFORCE = 'https://www.gartner.com/reviews/market/enterprise-high-productivity-application-paas/vendor/salesforce/product/salesforce-lightning-platform'


"""
Functions
"""

# Obtain HTML-source of JS-rendered page, parse with BeautifulSoup and return parsed HTML
def get_inner_html(driver, pagetype):
    if pagetype == 'review':
        try:
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, 'review')))
        finally:
            inner_html = driver.execute_script('return document.body.innerHTML')
    elif pagetype == 'list':
        try:
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'reviewSnippetCard')))
        finally:
            inner_html = driver.execute_script('return document.body.innerHTML')
    parsed_html = BeautifulSoup(inner_html, features='html.parser')
    return parsed_html

# Obtain URLs of full reviews and return a list
def get_review_url(platform_url, file):
    review_url_list = []
    driver = webdriver.Firefox()
    driver.get(platform_url)
    source_code = get_inner_html(driver, 'list')
    next_page = find_next_page(platform_url, source_code)
    review_urls = source_code.find_all('a', text='Read Full Review')
    for url in review_urls:
        url = 'https://www.gartner.com' + url.get('href')
        review_url_list.append(url)
        print(url)
    while next_page is not None:
        driver.get(next_page)
        source_code = get_inner_html(driver, 'list')
        next_page = find_next_page(platform_url, source_code)
        review_urls = source_code.find_all('a', text='Read Full Review')
        for url in review_urls:
            url = 'https://www.gartner.com' + url.get('href')
            review_url_list.append(url)
            print(url)
    driver.close()    
    return review_url_list

# Find the next page and return the URL if it exists
def find_next_page(platform_url, parsed_html_code):
    next_page = parsed_html_code.find('a', attrs={'data-pagination-type':'Next page'})
    if next_page != None:
        next_page_url = platform_url + next_page.get('href')
        return next_page_url

# Login to the website (not recommended)
def login(driver, url, username, password):
    driver.get(url)
    username = driver.find_element_by_id('authUser') #username form field
    password = driver.find_element_by_id('authPass') #password form field
    username.send_keys(username)
    password.send_keys(password)
    submitButton = driver.find_element_by_class_name('login-btn-primary') 
    submitButton.click()

# Start browser session and login if needed, cycle through reviews, save the data in a list, return list
def store_data(url_list, login='no', username='email', password='password'):
    data = []
    driver = webdriver.Firefox()
    if login == 'yes':
        login(driver, LOGIN_URL, user=username, pw=password)
    for url in url_list:
        for attempt in range(3):
            try:
                driver.get(url)
                number = 1 + int(url_list.index(url))
                print('{} - {}'.format(number, url))
                source_code = get_inner_html(driver, 'review')

                # General Information about the author, company and review
                if source_code.find('time', attrs={'itemprop':'datePublished'}):
                    publication_date = source_code.find('time', attrs={'itemprop':'datePublished'}).text.strip()
                else:
                    publication_date = None
                if source_code.find('span', attrs={'data-key':'job-role-id'}):
                    author_job = source_code.find('span', attrs={'data-key':'job-role-id'}).text
                else:
                    author_job = None
                if source_code.find('span', attrs={'data-key':'disclosure-source'}):
                    review_source = source_code.find('span', attrs={'data-key':'disclosure-source'}).text
                else:
                    review_source = None
                if source_code.find('span', attrs={'data-key':'industry-code'}):
                    industry = source_code.find('span', attrs={'data-key':'industry-code'}).text
                else:
                    industry = None
                if source_code.find('span', attrs={'data-key':'company-size-id'}):
                    company_size = source_code.find('span', attrs={'data-key':'company-size-id'}).text
                else:
                    company_size = None
                if source_code.find('span', attrs={'data-key':'go-live-year'}):
                    go_live_year = source_code.find('span', attrs={'data-key':'go-live-year'}).text
                else:
                    go_live_year = None

                # Lesson Learned
                if source_code.find('h2', attrs={'data-key':'review-headline'}):
                    headline = source_code.find('h2', attrs={'data-key':'review-headline'}).text.strip('"')
                else: headline = None
                if source_code.find('p', attrs={'data-key':'review-summary'}):
                    summary = source_code.find('p', attrs={'data-key':'review-summary'}).text
                else:
                    summary = None
                if source_code.find('p', attrs={'data-key':'lessonslearned-like-most'}):
                    liked_most = source_code.find('p', attrs={'data-key':'lessonslearned-like-most'}).text
                else:
                    liked_most = None
                if source_code.find('p', attrs={'data-key':'lessonslearned-dislike-most'}):
                    disliked_most = source_code.find('p', attrs={'data-key':'lessonslearned-dislike-most'}).text
                else:
                    disliked_most = None
                if source_code.find('p', attrs={'data-key':'lessonslearned-advice'}):
                    advice = source_code.find('p', attrs={'data-key':'lessonslearned-advice'}).text
                else:
                    advice = None
                if source_code.find('p', attrs={'data-key':'lessonslearned-you-did-differently-v2'}):
                    do_differently = source_code.find('p', attrs={'data-key':'lessonslearned-you-did-differently-v2'}).text
                else:
                    do_differently = None

                # Evaluating & Contracting
                if source_code.find('ul', attrs={'data-key':'vendors-considered'}):
                    vendors_considered_snip = source_code.find('ul', attrs={'data-key':'vendors-considered'})
                    vendors_considered = []
                    for li in vendors_considered_snip.find_all('li'):
                        vendors_considered.append(li.text)
                if source_code.find('div', attrs={'data-key':'vendors-considered-other'}):
                    vendors_considered.append(source_code.find('div', attrs={'data-key':'vendors-considered-other'}).text)
                else:
                    vendors_considered = None
                if source_code.find('ul', attrs={'data-key':'why-purchase-s24'}):
                    purchase_reasons_snip = source_code.find('ul', attrs={'data-key':'why-purchase-s24'})
                    purchase_reasons = []
                    for li in purchase_reasons_snip.find_all('li'):
                        purchase_reasons.append(li.text)
                else:
                    purchase_reasons = None
                if source_code.find('ul', attrs={'data-key':'factors-drove-decision-s24'}):
                    key_factors_snip = source_code.find('ul', attrs={'data-key':'factors-drove-decision-s24'})
                    key_factors = []
                    for li in key_factors_snip.find_all('li'):
                        key_factors.append(li.text)
                else:
                    key_factors = None

                # Integration & Deployment
                if source_code.find('div', attrs={'data-key':'main-technologies'}):
                    technologies = source_code.find('div', attrs={'data-key':'main-technologies'}).text
                else: 
                    technologies = None
                if source_code.find('div', attrs={'data-key':'deployment-time'}):
                    deployment_time = source_code.find('div', attrs={'data-key':'deployment-time'}).text
                else:
                    deployment_time = None
                if source_code.find('div', attrs={'data-key':'implementation-strategy'}):
                    implementation_strategy = source_code.find('div', attrs={'data-key':'implementation-strategy'}).text
                else:
                    implementation_strategy = None


                # Additional Context
                if source_code.find('div', attrs={'data-key':'version-number'}):
                    version_number = source_code.find('div', attrs={'data-key':'version-number'}).text
                else:
                    version_number = None
                if source_code.find('div', attrs={'data-key':'deployment-scale'}):
                    deployment_scale = source_code.find('div', attrs={'data-key':'deployment-scale'}).text
                else:
                    deployment_scale = None
                if source_code.find('div', attrs={'data-key':'time-used-service'}):
                    time_used = source_code.find('div', attrs={'data-key':'time-used-service'}).text
                else:
                    time_used = None
                if source_code.find('div', attrs={'data-key':'frequency-of-usage'}):
                    usage_frequency = source_code.find('div', attrs={'data-key':'frequency-of-usage'}).text
                else:
                    usage_frequency = None
                if source_code.find('div', attrs={'data-key':'deployment-country-multi'}):
                    deployment_region = source_code.find('div', attrs={'data-key':'deployment-country-multi'}).text
                elif source_code.find('ul', attrs={'data-key':'deployment-region'}):
                    deployment_region_snip = source_code.find('ul', attrs={'data-key':'deployment-region'})
                    deployment_region = []
                    for li in deployment_region_snip.find_all('li'):
                        deployment_region.append(li.text)
                else:
                    deployment_region = None

                # Set the format of the JSON file
                data.append({
                    'general_info': {
                        'url': url,
                        'date': publication_date,
                        'author_job': author_job,
                        'review_source': review_source,
                        'industry': industry,
                        'company_size': company_size,
                        'go_live_year': go_live_year
                    },
                    'lesson_learned': {
                        'headline': headline,
                        'summary': summary,
                        'liked_most': liked_most,
                        'disliked_most': disliked_most,
                        'advice': advice,
                        'do_differently': do_differently
                    },
                    'evaluation_contracting': {
                        'vendors_considered': vendors_considered,
                        'purchase_reasons': purchase_reasons,
                        'key_factors': key_factors
                    },
                    'integration_deployment': {
                        'technologies': technologies,
                        'deployment_time': deployment_time,
                        'implementation_strategy': implementation_strategy
                    },
                    'additional_context': {
                        'version_number': version_number,
                        'deployment_scale': deployment_scale,
                        'time_used': time_used,
                        'usage_frequency': usage_frequency,
                        'deployment_region': deployment_region
                    }
                })

            except (WebDriverException, TimeoutException) as err:
                print('{}. Will try again in 60s...'.format(err))
                time.sleep(60)
                driver.close()
                driver = webdriver.Firefox()
                continue

            else:
                """
                Attempts to prevent/delay account restriction when logged in.
                With sleep = 60s: Account restriction after +-150 requests. 
                An increased sleep may allow for more requests before restriction.
                """
                if login == 'yes':
                    time.sleep(random.randint(300, 600))

                """ 
                Gartner.com allows unregistered users to only read 8 reviews in one session.
                This bypasses the limit by starting a new session after every 5 reviews.
                """ 
                time.sleep(60)
                if (number % 5) == 0:
                    driver.close()
                    driver = webdriver.Firefox()
                break

    driver.close()
    return data


"""
Script
"""

# Select the platform
platform = SALESFORCE

# The output file name will contain the platform_name
if platform == BETTYBLOCKS:
    platform_name = 'bettyblocks'
elif platform == MENDIX:
    platform_name = 'mendix'
elif platform == OUTSYSTEMS:
    platform_name = 'outsystems'
elif platform == QUICKBASE:
    platform_name = 'quickbase'
elif platform == SALESFORCE:
    platform_name = 'salesforce'

# Create file in the /Data folder to store the review URLs or load the file if it already exists
if os.path.isfile('Data/{}_urls.json'.format(platform_name)) and not os.stat('Data/{}_urls.json'.format(platform_name)).st_size == 0:
    print('File {}_urls.json already exists! The file will be loaded instead..\n'.format(platform_name))
    with open('Data/{}_urls.json'.format(platform_name), 'r', encoding='utf-8') as file:
        review_url_list = json.load(file)
else:
    print('Creating {}_urls.json..'.format(platform_name))
    with open('Data/{}_urls.json'.format(platform_name), 'w', encoding='utf-8') as file:
        review_url_list = get_review_url(platform, file)
        json.dump(review_url_list, file, indent=4)
print('Done! The selected platform has {} verified reviews.\n'.format(len(review_url_list)))

# Check whether datafile already exists and scrape the data if needed
if os.path.isfile('Data/{}_reviews.json'.format(platform_name)) and not os.stat('Data/{}_reviews.json'.format(platform_name)).st_size == 0:
    print('File {}_reviews.json already exists!\n'.format(platform_name))
else:
    print('Creating {}_reviews.json..'.format(platform_name))
    with open('Data/{}_reviews.json'.format(platform_name), 'w', encoding='utf-8') as file:
        data = store_data(review_url_list, login='no')
        json.dump(data, file, indent=4)
        print('The file has been saved.\n')
