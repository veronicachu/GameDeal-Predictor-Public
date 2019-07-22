# -*- coding: utf-8 -*-
"""
Get and save local copy of target game image used on Steam to appear in the 
results page of webapp

Input: Steam app ID

Output: saved game image in local file

----
Last updated: 2019-06-21
"""
#%%
import generalFunctions
import requests
from bs4 import BeautifulSoup, SoupStrainer
import urllib

#%%
#gameName = 'Stardew Valley'
gameName = 'Watch_Dogs'
def grabGameImage(gameName):
#------------------------------------------------------------------------------
# load unfiltered pickled dictionary {appName:appID}
#------------------------------------------------------------------------------
    try:
        appNameDict = generalFunctions.load_pickleObject('steamapplist_appName')
    except:
        print ("Need steamapplist_appName.pkl file in dataobjects folder. Run getSteamAppsList.py")
    
    # get appID for target game
    appID = appNameDict[gameName]
    
#------------------------------------------------------------------------------
# load unfiltered pickled dictionary {appName:appID}
#------------------------------------------------------------------------------
    try:
        # download webpage HTML
        cookies = {'birthtime': '568022401', 'mature_content': '1' } # bypass Steam age check
        url = "https://store.steampowered.com/app/" + str(appID)
        page = requests.get(url, cookies=cookies)
        
        # grab game image from webpage
        imageStrain = SoupStrainer(class_="game_header_image_full")
        imageSoup = BeautifulSoup(page.content, 'html.parser', parse_only=imageStrain)
        
        # get image source
        imageSrc = imageSoup.find('img')['src']
        
        # save image locally
        urllib.request.urlretrieve(imageSrc, ("static/img/" + gameName + ".jpg"))
        
    except:
        print("Request code: " + str(page.status_code))
        
    return url