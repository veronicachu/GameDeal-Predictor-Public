# -*- coding: utf-8 -*-
"""
Pulls the list of Steam apps and store as dictionary
Output: in folder "dataobjects"
    -pickle file "steamapplist_appID = dictionary {appID:appName}
    -pickle file "steamapplist_appName = dictionary {appName:appID}

----
Last updated: 2019-06-06
Last run: 2019-06-06 12:35PM PST
"""
#%%
import requests
import json
import generalFunctions

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
for key, value in dict.items(jsondata["applist"]):
    applist = {key:value}

#------------------------------------------------------------------------------
# transform games list into a string for parsing
#------------------------------------------------------------------------------
appsString = json.dumps(applist["apps"])
# appsString[1:100]

#------------------------------------------------------------------------------
# split game data into a list of strings
#------------------------------------------------------------------------------
appid = appsString[2:].split("}, {")

#for i in range(10):
#    print(appid[i])
#print("total games", len(appid))

#------------------------------------------------------------------------------
# parse out appid# and appname
# place into a dictionary {appid:appname}
#------------------------------------------------------------------------------
keystart = '"appid": '
keyend = ','

appIDDict = dict()
for line in appid:
  key = (line.split(keystart))[1].split(keyend)[0]
  value = (line.split('"'))[5] # will break if the number of quotations or order change
  appIDDict[int(key)] = value

#appIDDict[992050] # should be 'Oik 5'

#------------------------------------------------------------------------------
# parse out appid# and appname
# place into a dictionary {appname:appid}
#------------------------------------------------------------------------------
keystart = '"appid": '
keyend = ','

appNameDict = dict()
for line in appid:
  key = (line.split(keystart))[1].split(keyend)[0]
  value = (line.split('"'))[5] # will break if the number of quotations or order change
  appNameDict[value] = key

#appNameDict['Oik 5'] # should be 992050

#%%
#------------------------------------------------------------------------------
# pickle {appid:appname} dictionary
#------------------------------------------------------------------------------
generalFunctions.save_pickleObject(appIDDict,'steamapplist_appID')

#------------------------------------------------------------------------------
# pickle {appname:appid} dictionary
#------------------------------------------------------------------------------
generalFunctions.save_pickleObject(appNameDict,'steamapplist_appName')

