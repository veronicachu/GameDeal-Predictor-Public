# -*- coding: utf-8 -*-
"""
Get game reviews from app's Steam appdetails API
**Still under development**

----
Last updated: 2019-06-11
Last run: 2019-06-11
"""

import generalFunctions
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import pandas as pd

#------------------------------------------------------------------------------
# load unfiltered pickled dictionary {appID:appName}
#------------------------------------------------------------------------------
try:
    paidIDList = generalFunctions.load_pickleObject('paidSteamIDsList')
except:
    print ("Need paidSteamIDsList.pkl file in dataobjects folder. Run collectSteamPaidGamesDetails.py")

#------------------------------------------------------------------------------
# 
#------------------------------------------------------------------------------
appID = paidIDList[0]
offset = 0

apikey = [line.rstrip('\n') for line in open('steam_api_key.txt')]
url = "https://store.steampowered.com/appreviews/" + appID + "?json=1&filter=recent&start_offset=" + offset
page = requests.get()
jsondata = json.loads(page.text)

# loads all 20 reviews
reviewDetails = jsondata['reviews']

i = 0
timestamp = reviewDetails[i]['timestamp_created']
vote = reviewDetails[i]['voted_up']
helpful = reviewDetails[i]['votes_up']
funny = reviewDetails[i]['votes_funny']
weightedscore = reviewDetails[i]['weighted_vote_score'] # no idea where this value comes from, but its there