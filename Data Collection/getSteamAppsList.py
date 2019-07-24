# -*- coding: utf-8 -*-
"""
Pulls the list of Steam apps and store as dictionary
Output: in folder "dataobjects"
    -pickle file "steamapplist_appID = dictionary {appID:appName}
    -pickle file "steamapplist_appName = dictionary {appName:appID}

----
Last updated: 2019-07-24
Last run: 2019-06-06 12:35PM PST
"""
#%%
import requests
import json
import utils

#%%
#------------------------------------------------------------------------------
# access webpage with Steam games list
#------------------------------------------------------------------------------
url = 'http://api.steampowered.com/ISteamApps/GetAppList/v2'
apidata = requests.get(url=url)

#%%
#------------------------------------------------------------------------------
# get json file of Steam games list
#------------------------------------------------------------------------------
jsondata = json.loads(apidata.text)

#------------------------------------------------------------------------------
# move down json hierarchy
#------------------------------------------------------------------------------
applist = dict()
for title, apps in dict.items(jsondata["applist"]):
    applist = {title:apps}

#------------------------------------------------------------------------------
# loop through list of apps
# place into a dictionary {appid:appname}
#------------------------------------------------------------------------------
appIDDict = dict()
for ind in range(len(apps)):
    key = apps[ind]['appid']
    value = apps[ind]['name']
    appIDDict[key] = value

#------------------------------------------------------------------------------
# loop through list of apps
# place into a dictionary {appname:appid}
#------------------------------------------------------------------------------
appNameDict = dict()
for ind in range(len(apps)):
    key = apps[ind]['name']
    value = apps[ind]['appid']
    appNameDict[key] = value

#appNameDict['Oik 5'] # should be 992050

#%%
# if there is already a saved file, make another file that lists the new entries 
# and overwrite old file
# if there is not already a saved file, save dict

#------------------------------------------------------------------------------
# pickle {appid:appname} dictionary
#------------------------------------------------------------------------------
try:
    # load old dictionary
    oldappID = utils.load_pickleObject('steamapplist_appID')
    
    # create list of the new items
    oldkeys = list(oldappID.keys())
    newkeys = list(appIDDict.keys())
    newList = list(set(newkeys) - set(oldkeys))
    
    # save new items list
    utils.save_pickleObject(newList,'steamapplist_newIDs')
    
    # save new dictionary
    utils.save_pickleObject(appIDDict,'steamapplist_appID')
    
except:
    utils.save_pickleObject(appIDDict,'steamapplist_appID')

#------------------------------------------------------------------------------
# pickle {appname:appid} dictionary
#------------------------------------------------------------------------------
try:
    # load old dictionary
    oldappName = utils.load_pickleObject('steamapplist_appName')
    
    # create list of the new items
    oldNames = list(oldappName.keys())
    newNames = list(appNameDict.keys())
    newList = list(set(newNames) - set(oldNames))
    
    # save new items list
    utils.save_pickleObject(newList,'steamapplist_newNames')
    
    # save new dictionary
    utils.save_pickleObject(appNameDict,'steamapplist_appID')
    
except:
    utils.save_pickleObject(appNameDict,'steamapplist_appID')


