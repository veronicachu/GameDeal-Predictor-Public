# -*- coding: utf-8 -*-
"""
Pulls an individual Steam game's price history from data log on game's 
IsThereAnyDeal history webpage

Input: 
    gameName as (string) - 

Output: 
    dataframe (news timestamp | news category)

----
Last updated: 2019-06-10
"""
#%%
import string
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime
import pandas as pd
import numpy as np

#%%
def getPriceHistory(appName):
#------------------------------------------------------------------------------
# format input appName in acceptable way for the IsThereAnyDeal webpage link
#------------------------------------------------------------------------------
    appName2 = appName.replace(" ", "") # remove white space
    appName2 = appName2.replace("u2122","") # remove trademark symbol
    appName2 = appName2.translate(str.maketrans('','',string.punctuation)) # remove punctuation
    appName2 = appName2.lower()

#------------------------------------------------------------------------------
# download a webpage's HTML
#------------------------------------------------------------------------------
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.max_redirects = 3
    
    url = "https://isthereanydeal.com/game/" + appName2 + "/history/#/"
    try:
        page = requests.get(url) #, timeout = 1)
    
        # print download status
        # if output 200 (or starts with 2), then download successful; if starts with 4 or 5, then unsuccessful
#        print(page.status_code)
    
#------------------------------------------------------------------------------
# grab price history log from webpage
#------------------------------------------------------------------------------
        strainer = SoupStrainer(class_="lg2 game")
        soup = BeautifulSoup(page.content, 'html.parser', parse_only=strainer)
    
#------------------------------------------------------------------------------
# place each log's string entry into a list
#------------------------------------------------------------------------------
        log = [item.get_text() for item in list(soup.children)]
    
#------------------------------------------------------------------------------
# get date timestamp from log's list of strings
#------------------------------------------------------------------------------
        # get the part of the string that contains the date
        dateString = []
        for stringitem in log:
            dateString.append(stringitem.split()[0])
        
        # convert date string to datetime object
        dateTime = []
        for date in dateString:
            dateTime.append(datetime.strptime(date, '%Y-%m-%d'))
        
        # convert datetime object to timestamp value
        dateTimestamp = []
        for date in dateTime:
            try:
                dateTimestamp.append(datetime.timestamp(date))
            except:
                dateTimestamp.append(np.NaN)
    
#------------------------------------------------------------------------------
# get game shop name from log's list of strings
#------------------------------------------------------------------------------
        shopName = []
        for stringitem in log:
            temp = stringitem.split()[4]
            
            # some cases where original data contains "regular:" at end of shop name
            # because next item in string is "regular:%price"
            # remove "regular:" for these cases
            if "regular:" in temp:
                temp = temp.strip("regular:")
            try:
                shopName.append(temp)
            except:
                shopName.append(np.NaN)
    
#------------------------------------------------------------------------------
# get regular price from log's list of strings
#------------------------------------------------------------------------------
        regularPrice = []
        for stringitem in log:
            temp = stringitem.split('$')[1] # split on '$'
            temp = temp.split('-')[0] # split on '-'
            temp = temp.split('+')[0] # split on '+'
            try:
                regularPrice.append(float(temp))
            except:
                regularPrice.append(np.NaN)
    
#------------------------------------------------------------------------------
# get new price from log's list of strings
#------------------------------------------------------------------------------
        newPrice = []
        for stringitem in log:
            temp = stringitem.split('$')[-1] # split on '$' and take last element
            temp = temp.split('-')[0] # split off '-'
            temp = temp.split('+')[0] # split off '+'
            try:
                newPrice.append(float(temp))
            except:
                newPrice.append(np.NaN)
    
#------------------------------------------------------------------------------
# get percent price change for game shop from log's list of strings
#------------------------------------------------------------------------------
        priceChange = []
        for stringitem in log:
            temp = stringitem.split('$')[2] # split on '$'
            
            # if negative change
            try:
                temp = temp.split('-')[1] # split on '-'
                temp = "-" + temp[:-1] # remove percent symbol
            
            # if positive change
            except:
                temp = temp.split('+')[0] # split on '+'
                temp = "+" + temp[:-1] # remove percent symbol
                
            try:
                priceChange.append(float(temp))
            except:
    #            priceChange.append(0)
                priceChange.append(np.NaN)
    
#------------------------------------------------------------------------------
# create dataframe with timestamp and categories
#------------------------------------------------------------------------------
        pricehistoryDF = pd.DataFrame(
            {'dealDate': dateTimestamp,
             'dealShopName': shopName,
             'dealRegularPrice': regularPrice,
             'dealNewPrice': newPrice,
             'dealPercPriceChange': priceChange
            })
    except:
        pricehistoryDF = []
        print("unable to get price history for " + appName)
        
    return pricehistoryDF














