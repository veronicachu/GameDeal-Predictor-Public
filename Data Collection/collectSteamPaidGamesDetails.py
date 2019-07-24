# -*- coding: utf-8 -*-
"""
Get all paid games and their game details from Steam
Also creates lists of free games' appIDs, non-games' appIDs, and broken appIDs

**Note: Takes a while to run from scratch because there are 80,000 app IDs 
and Steam will rate limit requests (1/sec)

----
Last updated: 2019-07-24
Last run: 2019-06-18
"""
#%%
import utils
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
# parameters needed to collect game details from Steam
#------------------------------------------------------------------------------
# get proxies from https://www.us-proxy.org/ - automate this one day
proxies = ["https://3.212.104.192:80",
           "https://173.54.193.242:50200",
           "https://63.249.67.70:53281",
           "https://138.197.108.5:3128",
           "https://96.65.221.1:34088"]

# request rate - determine best number for the site
numRequestperSec = 1 

# range of appIDs to check
minIDInd = 78000
maxIDInd = 80000

#%%
#------------------------------------------------------------------------------
# load previously pickled items or create empty lists for new run
#------------------------------------------------------------------------------
try:
    # load pickled dictionary of appIDs {appID:appName}
    appIDDict = utils.load_pickleObject('steamapplist_appID')
    
    # get keys list
    keysList = list(appIDDict.keys())   # get keys in appIDDict
except:
    print ("Need steamapplist_appID.pkl file in dataobjects folder. Run getSteamAppsList.py")

# get previous lists or create empty ones
paidIDList = utils.load_savedLists(1)
freeIDList = utils.load_savedLists(2)
nongameIDList = utils.load_savedLists(3)
brokenIDList = utils.load_savedLists(4)
unformattedIDList = utils.load_savedLists(5)
emptyIDList = utils.load_savedLists(6)

# get previous failed ID list - all
try:
    failedIDList = utils.load_pickleObject('failedSteamIDsList')
except:
    failedIDList = brokenIDList + unformattedIDList + emptyIDList

# get game details dataframe
try:
    gameDetails = utils.load_pickleObject('SteamGamesDetails')
except:
    # initialize pandas dataframe
    columns = ['Game Title','Steam ID','Developers','Publishers','Release Data','Genres',
               'Total Reviews','Initial Price','Final Price','Metacritic Score','Metacritic URL']
    gameDetails = pd.DataFrame(columns=columns)

#%%
#------------------------------------------------------------------------------
# function to get game details for all paid games and collect lists of other Steam ID types
#------------------------------------------------------------------------------
columns = ['Game Title','Steam ID','Developers','Publishers','Release Data','Genres',
               'Total Reviews','Initial Price','Final Price','Metacritic Score','Metacritic URL']
tempDF = pd.DataFrame(columns=columns)

keysListSubset = keysList[minIDInd:maxIDInd]
for ID in keysListSubset:
    if ID not in paidIDList and ID not in freeIDList and ID not in nongameIDList and ID not in failedIDList:
        
        # settings to prevent being blocked by website
        session = requests.Session()
        currentProxy = utils.set_proxy(session, proxies)
        
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
                            print("Added paid game: ID#", ID, sep='')
                    except: 
                        print("Unable to add to dataframe: appID#", ID, sep='')
                        pass
                    
                    # if free game
                    if apptype == 'game' and appfree == True:
                        freeIDList.append(ID)
                        print("Added free game: ID#", ID, sep='')
                    
                    # if non-game
                    if apptype != 'game':
                        nongameIDList.append(ID)
                        print("Added non-game: ID#", ID, sep='')
                except:
                    unformattedIDList.append(ID)
                    print('JSON file not formatted as expected...Page may have failed to load: appID#', ID, sep='')
                    pass
            except:
                emptyIDList.append(ID)
                print('Nothing in JSON file: appID#', ID, sep='')
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

#%% add temp dataframe to gameDetails dataframe
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
utils.save_pickleObject(brokenIDList,'brokenSteamIDsList') # broken app IDs list
utils.save_pickleObject(paidIDList,'paidSteamIDsList') # paid games ID list
utils.save_pickleObject(freeIDList,'freeSteamIDsList') # free games ID list
utils.save_pickleObject(nongameIDList,'nongameSteamIDsList') # non-game app ID list
utils.save_pickleObject(emptyIDList,'emptySteamIDsList') # empty app ID list
utils.save_pickleObject(unformattedIDList,'unformattedSteamIDsList') # unformatted app ID list
utils.save_pickleObject(failedIDList,'failedSteamIDsList') # failed app ID list


gameDetails.to_pickle("../data/SteamGamesDetails.pkl")

gameTitles = list(gameDetails['Game Title'])
utils.save_pickleObject(gameTitles, 'SteamGameTitles')





