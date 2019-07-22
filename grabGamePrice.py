# -*- coding: utf-8 -*-
"""
Get current price on Steam to appear in the results page of webapp

Input: Steam app ID

Output: saved game image in local file

----
Last updated: 2019-06-21
"""
#%%
import generalFunctions
import requests
from bs4 import BeautifulSoup, SoupStrainer

#%%
#gameName = 'Stardew Valley'
gameName = 'Steep'
def grabGamePrice(gameName):
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
        
        # check if game currently on sale
        try:
            finalpriceStrain = SoupStrainer(class_="discount_final_price")
            originalpriceStrain = SoupStrainer(class_="discount_original_price")
            
            finalpriceSoup = BeautifulSoup(page.content, 'html.parser', parse_only=finalpriceStrain)
            originalpriceSoup = BeautifulSoup(page.content, 'html.parser', parse_only=originalpriceStrain)
            
            discountprice = list(finalpriceSoup)[0].string
            originalprice = list(originalpriceSoup)[1].string
            
            priceoutput = list([discountprice, originalprice])
        # if not on sale, grab game price from webpage
        except:
            priceStrain = SoupStrainer(class_="game_purchase_price price")
            priceSoup = BeautifulSoup(page.content, 'html.parser', parse_only=priceStrain)
            price = list(priceSoup)[0].text
            price = price[price.index('$'):]
            price = price[:price.index('\t')]
            
            priceoutput = list([price])
            
    except:
        priceoutput = []
        
    return priceoutput