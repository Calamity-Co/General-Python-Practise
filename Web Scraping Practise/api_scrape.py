from bs4 import BeautifulSoup
import requests
import simplejson as json
import re
import ast
import csv
import pandas as pd
import tqdm
from progress.bar import Bar


urls_csv = 'product_urls.csv'


def get_raw_urls(urls_csv):
    array_of_product_information = []
    product_ids = []
    with open(urls_csv, 'r') as f:
        for line in f.readlines():
            url = line.strip().split(',')
            array_of_product_information.append((url[1]))
            
    return array_of_product_information[1:5000]

def strip_urls_for_prod_id(array_of_product_information):
    array_of_product_ids = []
    bad_urls = []
    for x in array_of_product_information:
        matches = re.search(r'.*/(.*).prd', x) 
        try:
            array_of_product_ids.append(matches.group(1))
        except:
            bad_urls.append(x)
            
    return array_of_product_ids, bad_urls

def strip_raw_json(r_text):
    r_text = r_text.replace('\n',"")
    r_text = r_text.replace('\r',"")
    r_text = r_text.replace('\t',"")
    r_text = r_text.replace('(',"")
    r_text = r_text.replace(')',"")
    r_text = r_text.replace(';',"")
        
    return r_text

def get_raw_json(product_id):
    r = requests.get('http://www.very.co.uk/json/catalog/product/productInfo.jsp?sdgProductId=' + product_id)
    text = strip_raw_json(r.text)
    return text


product_info_df = pd.DataFrame(columns=['itemNumber', 'identification', 'Cnet Enabled', 'collect plus', 
                              'number of images', 'description word count', 'number of options',
                              'now from', 'now to price', 'save from price', 'save to price',
                              'was from', 'was to', 'stars', 'count of reviews'])



urls = get_raw_urls(urls_csv)
product_ids, bad_urls = strip_urls_for_prod_id(urls)

bar = Bar('Processing', max=len(product_ids), suffix = '%(percent).1f%% - %(eta)ds')

for x in product_ids:
    
    product_information = {}
    
    r_text = get_raw_json(x)

    json_load = json.loads(r_text)
    try:
        product_information['itemNumber'] = json_load['productData'][0]['identification']['itemNumber']
    except: 
        product_information['itemNumber'] = 'null'
    
    try:
        product_information['identification'] = json_load['identification'][0]
    except:
        product_information['identification'] = 'null'
    
    try:
        product_information['Cnet Enabled'] = json_load['productData'][0]['cnet']['isCNETProductFeaturesEnabled']
    except:
        product_information['Cnet Enabled'] = 'null'
        
    try:    
        product_information['collect plus'] = json_load['productData'][0]['collectPlus']
    except:
        product_information['collect plus'] = 'null'
        
    try:
        product_information['number of images'] = len(json_load['productData'][0]['images'])
    except:
        product_information['number of images'] = 0
        
    try: 
        product_information['description word count'] = len(var.split(json_load['productData'][0]['name']['longDescription']))
    except:
        product_information['description word count'] = 0
        
    try:    
        product_information['number of options'] = len(json_load['productData'][0]['options'])
    except:
        product_information['number of options'] = 0
            
    try:
        product_information['now from'] = json_load['productData'][0]['price']['nowFrom']
        product_information['now to price'] = json_load['productData'][0]['price']['nowToPrice']
        product_information['save from price'] = json_load['productData'][0]['price']['saveFromPrice']
        product_information['save to price'] = json_load['productData'][0]['price']['saveToPrice']
        product_information['was from'] = json_load['productData'][0]['price']['wasFrom']
        product_information['was to'] = json_load['productData'][0]['price']['wasTo']
    except:  
        product_information['now from'] = 0
        product_information['now to price'] = 0
        product_information['save from price'] = 0
        product_information['save to price'] = 0
        product_information['was from'] = 0
        product_information['was to'] = 0
    
    try:
        product_information['stars'] = json_load['productData'][0]['reviews']['stars']
        product_information['count of reviews'] = json_load['productData'][0]['reviews']['total']
    except:
        product_information['stars'] = 0
        product_information['count of reviews'] = 0


    
    series = pd.Series(product_information)
    product_info_df = product_info_df.append(series, ignore_index=True)
    
    bar.next()
    
product_info_df.to_csv('output1.csv')
    
bar.finish()