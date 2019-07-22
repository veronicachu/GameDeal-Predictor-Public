# -*- coding: utf-8 -*-
"""
Get all paid games and their game details from app's Steam appdetails API
Also creates lists of free games' appIDs, non-games' appIDs, and broken appIDs

*Note: Takes a while to run from scratch
----
Last updated: 2019-06-18
Last run: 2019-06-18
"""
#%%
import generalFunctions
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
from buildSteamGameDetailsData import buildSteamGameDetailsData
import sys
import pandas as pd
import time

#%%
#------------------------------------------------------------------------------
# load unfiltered pickled dictionary {appID:appName}
#------------------------------------------------------------------------------
try:
    appIDDict = generalFunctions.load_pickleObject('steamapplist_appID')
except:
    print ("Need steamapplist_appID.pkl file in dataobjects folder. Run getSteamAppsList.py")

#%%
#------------------------------------------------------------------------------
# load previously pickled items or create empty lists for new run
#------------------------------------------------------------------------------
# get keys list
try:
    keysList = generalFunctions.load_pickleObject('keysList')
except:
    keysList = list(appIDDict.keys())   # get keys in appIDDict

# get previous lists or create empty ones
paidIDList = generalFunctions.load_savedLists(1)
freeIDList = generalFunctions.load_savedLists(2)
nongameIDList = generalFunctions.load_savedLists(3)
brokenIDList = generalFunctions.load_savedLists(4)
unformattedIDList = generalFunctions.load_savedLists(5)
emptyIDList = generalFunctions.load_savedLists(6)

# get previous failed ID list - all
try:
    failedIDList = generalFunctions.load_pickleObject('failedSteamIDsList')
except:
    failedIDList = brokenIDList + unformattedIDList + emptyIDList

# get game details dataframe
try:
    gameDetails = generalFunctions.load_pickleObject('SteamGamesDetails')
except:
    # initialize pandas dataframe
    columns = ['Game Title','Steam ID','Developers','Publishers','Release Data','Genres',
               'Total Reviews','Initial Price','Final Price','Metacritic Score','Metacritic URL']
    gameDetails = pd.DataFrame(columns=columns)

#%%
#------------------------------------------------------------------------------
# parameters needed to collect game details from Steam
#------------------------------------------------------------------------------
# get proxies from https://www.us-proxy.org/
proxies = ["https://74.84.255.88:53281",
           "https://66.229.52.101:8080",
           "https://159.203.186.40:8080",
           "https://50.233.228.147:8080",
           "https://45.63.66.17:8080"]

numRequestperSec = 1 # determine best number for the site
keysListSubset = keysList[70000:73000]

#%%
#------------------------------------------------------------------------------
# function to get game details for all paid games and collect lists of other Steam ID types
#------------------------------------------------------------------------------
columns = ['Game Title','Steam ID','Developers','Publishers','Release Data','Genres',
               'Total Reviews','Initial Price','Final Price','Metacritic Score','Metacritic URL']
tempDF = pd.DataFrame(columns=columns)

for ID in keysListSubset:
    if ID not in paidIDList and ID not in freeIDList and ID not in nongameIDList and ID not in failedIDList:
        
        # settings to prevent being blocked by website
        session = requests.Session()
        currentProxy = generalFunctions.set_proxy(session, proxies)
        
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.max_redirects = 3
        
        try:
            url = "https://store.steampowered.com/api/appdetails?appids=" + str(ID)
            page = session.get(url, proxies=currentProxy)
            
            # get JSON file
            try:
                jsondata = json.loads(page.text)
                
                # get info about app type and if free
                try:
                    appdata = jsondata[str(ID)]['data']
                    apptype = appdata['type'] # only want 'game'
                    appfree = appdata['is_free'] # only want False
                    
                    try:
                        # if paid games
                        if apptype == 'game' and appfree == False:
                            tempDF = buildSteamGameDetailsData(appIDDict, ID, appdata, tempDF)
                            
                            paidIDList.append(ID)
                            print("Added paid game from ID#", ID, sep='')
                    except: 
                        print("Unable to add to dataframe for appID#", ID, sep='')
                        pass
                    
                    # if free game
                    if apptype == 'game' and appfree == True:
                        freeIDList.append(ID)
                        print("Added free game from ID#", ID, sep='')
                    
                    # if non-game
                    if apptype != 'game':
                        nongameIDList.append(ID)
                        print("Added non-game from ID#", ID, sep='')
                except:
                    unformattedIDList.append(ID)
                    print('JSON file not formatted as expected...Page may have failed to load for appID#', ID, sep='')
                    pass
            except:
                emptyIDList.append(ID)
                print('Nothing in JSON file for appID#', ID, sep='')
                pass
        except requests.exceptions.RequestException as e:
            brokenIDList.append(ID)
            print(e, ID, sep="AppID#")
            print("Proxy ", str(currentProxy), " does not work or may have been blocked...", sep="")
            print("Removing proxy from list...")
            proxies.remove(currentProxy['https'])
            
            if len(proxies) < 1:
                sys.exit()
            else:
                pass
        time.sleep(1/numRequestperSec)

print("Done with batch! Append temp dataframe just collected to your dataframe.")

#%%
# add temp dataframe to gameDetails dataframe
gameDetails = gameDetails.append(tempDF)

#%%
#------------------------------------------------------------------------------
# check numbers and combine all types of failed requests
#------------------------------------------------------------------------------
numApps = len(paidIDList) + len(freeIDList) + len(nongameIDList)
numErrors = len(brokenIDList) + len(unformattedIDList) + len(emptyIDList)
print("number of apps", numApps, sep=": ")
print("number of errors", numErrors, sep=": ")
print("total apps ran", numApps + numErrors, sep=": ")

# remove any duplicates in list
brokenIDList2 = list(set(brokenIDList) - set(paidIDList + freeIDList + nongameIDList))
unformattedIDList2 = list(set(unformattedIDList) - set(paidIDList + freeIDList + nongameIDList))
emptyIDList2 = list(set(emptyIDList) - set(paidIDList + freeIDList + nongameIDList))

failedIDList = brokenIDList2 + unformattedIDList2 + emptyIDList

# check if any duplicates in dataframe        
print(any(gameDetails['Steam ID'].duplicated()))

#%%
#------------------------------------------------------------------------------
# pickle the data
#------------------------------------------------------------------------------
generalFunctions.save_pickleObject(keysList,'keysList') # all app IDs list
generalFunctions.save_pickleObject(brokenIDList,'brokenSteamIDsList') # broken app IDs list
generalFunctions.save_pickleObject(paidIDList,'paidSteamIDsList') # paid games ID list
generalFunctions.save_pickleObject(freeIDList,'freeSteamIDsList') # free games ID list
generalFunctions.save_pickleObject(nongameIDList,'nongameSteamIDsList') # non-game app ID list
generalFunctions.save_pickleObject(emptyIDList,'emptySteamIDsList') # empty app ID list
generalFunctions.save_pickleObject(unformattedIDList,'unformattedSteamIDsList') # unformatted app ID list
generalFunctions.save_pickleObject(failedIDList,'failedSteamIDsList') # failed app ID list


gameDetails.to_pickle("dataobjects/SteamGamesDetails.pkl")

gameTitles = list(gameDetails['Game Title'])
generalFunctions.save_pickleObject(gameTitles, 'SteamGameTitles')





