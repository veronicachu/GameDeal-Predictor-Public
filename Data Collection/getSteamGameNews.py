# -*- coding: utf-8 -*-
"""
Pulls an individual Steam game's news updates from Steam news webpage

Input: 
    appName as (string) - must be exact name on it's Steam page

Output: 
    dataframe (news timestamp | news category)

----
Last updated: 2019-06-10
"""
#%%
import utils
import requests
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime
import pandas as pd

#%%
def getNewsUpdates(appName):
#------------------------------------------------------------------------------
# load pickled dictionary {appName:appID}
#------------------------------------------------------------------------------
    try:
        appNameDict = utils.load_pickleObject('steamapplist_appName')
    except:
        print ("Need steamapplist_appName.pkl file in dataobjects folder. Run getSteamAppsList.py")


#------------------------------------------------------------------------------
# access game's Steam news webpage's HTML
#------------------------------------------------------------------------------
    appID = appNameDict[appName]
    url = "https://store.steampowered.com/news/?appids=" + appID + "&headlines=1"
    page = requests.get(url) #, timeout = 1)
    
    # print download status
    # if output 200 (or starts with 2), then download successful; if starts with 4 or 5, then unsuccessful
    #page.status_code 


#------------------------------------------------------------------------------
# grab category type of news items from webpage
#------------------------------------------------------------------------------
    # parse webpage's HTML, straining for "feed" class items only
    newscategoryStrain = SoupStrainer(class_="feed")
    newscategorySoup = BeautifulSoup(page.content, 'html.parser', parse_only=newscategoryStrain)
    
    # convert soup item to string
    newscategory = str(newscategorySoup)
    
    # split date into a list of strings
    categories = newscategory.split('<div class="feed">')
    
    # remove </div> from each string list item
    cleanCategories = []
    for text in categories:
      cleanCategories.append(text.replace("</div>",""))
    
    cleanCategories = cleanCategories[1:] # remove first item, which is just an empty ''
    cleanCategories

#------------------------------------------------------------------------------
#!! work in progress !!
#------------------------------------------------------------------------------
    ## grab news type of news items from webpage
    #newstitleStrain = SoupStrainer(class_="title") # class_ options: "feed", "title", "date"
    #newstitleSoup = BeautifulSoup(page.content, 'html.parser', parse_only=newstitleStrain)
    #
    ## convert soup item to string
    #newstitle = str(newstitleSoup)
    #newstitle
    #
    ## split date into a list of strings
    #titles = newstitle.split('return false;">')
    #
    ## remove </div> from each string list item
    #cleanTitles = []
    #for text in titles:
    #  cleanTitles.append(text.replace("</div>",""))
    #
    #cleanTitles = cleanTitles[1:] # remove first item, which is just an empty ''
    #cleanTitles


#------------------------------------------------------------------------------
# grab posted dates of news items from webpage and convert to timestamps
#------------------------------------------------------------------------------
    # parse webpage's HTML, straining for "date" class items only
    newsdateStrain = SoupStrainer(class_="date")
    newsdateSoup = BeautifulSoup(page.content, 'html.parser', parse_only=newsdateStrain)
    
    # convert soup item to string
    newsdate = str(newsdateSoup)
    
    # split each date item into a list of strings
    dates = newsdate.split('<div class="date">')
    
    # remove </div> from each string list item
    cleanDates = []
    for text in dates:
      cleanDates.append(text.replace("</div>",""))
    
    # remove first item, which is just an empty ''
    cleanDates = cleanDates[1:]
    #cleanDates
    
    # add comma and year to dates that occured this year because Steam does not include
    #!! need to include exception for current day posts (only gives time of post) !!
    cleanDates2 = []
    for text in cleanDates:
      if not "," in text:
        cleanDates2.append(text + ", " + str(datetime.now().year))
      if "," in text:
        cleanDates2.append(text)
    #cleanDates2

    # convert string date to datetime object
    dateTime = []
    for date in cleanDates2:
      dateTime.append(datetime.strptime(date, '%b %d, %Y'))
    #dateTime

    # convert datetime object to timestamp value
    dateTimestamp = []
    for date in dateTime:
      dateTimestamp.append(datetime.timestamp(date))
    #dateTimestamp

#------------------------------------------------------------------------------
# create dataframe with timestamp and categories
#------------------------------------------------------------------------------
    gamenewsDF = pd.DataFrame(
        {'postDate': dateTimestamp,
         'postCategory': cleanCategories,
        })
    return gamenewsDF













