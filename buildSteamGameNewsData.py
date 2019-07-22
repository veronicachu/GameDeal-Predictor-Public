# -*- coding: utf-8 -*-
"""
Builds a dataset of Steam games news updates from Steam news webpage

Input: 
    appNames as (list of strings) - must have exact names as on it's Steam page

Output: 
    dataframe (news timestamp | news category)

----
Last updated: 2019-06-07
"""
import getSteamGameNews
import datetime
import pandas as pd

#appName = 'Grim Dawn'
#appName = 'DiRT Rally'

def buildSteamNewsData(appName):
#------------------------------------------------------------------------------
# create empty dataframe of appName x time filled with zeros
#------------------------------------------------------------------------------
    # set time range
    firstday = datetime.date(2003,9,11) # Steam platform release date 09-11-2003
    currentday = datetime.date.today()
    
    # create time samples - sampling rate in days
    # create day intervals from start date to end date
    timeSamples = []
    delta = currentday - firstday
    for i in range(delta.days + 1):
        temp = firstday + datetime.timedelta(days=i)
        temp = datetime.datetime(temp.year, temp.month, temp.day)
        timeSamples.append(temp)
    
    # convert day intervals to timestamp values
    timestamps = []
    for date in timeSamples:
        timestamps.append(datetime.datetime.timestamp(date))
    
    # create empty table with timestamps as columns
    newsdf = pd.DataFrame(index=timestamps, columns=list({appName}))
    newsdf = newsdf.fillna(0) # with 0s rather than NaNs
    
    newsdf.index.name = 'timestamps'
    newsdf = newsdf.reset_index()


#------------------------------------------------------------------------------
# get each game's news and aggregate into single dataframe
#------------------------------------------------------------------------------
    gamenews = getSteamGameNews.getNewsUpdates(appName)
            
    for i in range(len(gamenews.postDate)):
            # make sure there is a news item present
            if gamenews.postDate[i]:
                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], appName] =  1
    #            # channel updates
    #            if gamenews.iloc[i][1] == "Announcement":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  1
    #                print(1)
    #            if gamenews.iloc[i][1] == "Client Update":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  2
    #            if gamenews.iloc[i][1] == "Press Release":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  3
    #            if gamenews.iloc[i][1] == "Product Release":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  4
    #            if gamenews.iloc[i][1] == "Product Update":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  5
    #            if gamenews.iloc[i][1] == "Steam Blog":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  6
    #            
    #            # syndicated updates
    #            if gamenews.iloc[i][1] == "Eurogamer":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  7
    #            if gamenews.iloc[i][1] == "Kotaku":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  8
    #            if gamenews.iloc[i][1] == "L4D Blog":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  9
    #            if gamenews.iloc[i][1] == "PC Gamer":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  10
    #            if gamenews.iloc[i][1] == "Portal 2 Blog":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  11
    #            if gamenews.iloc[i][1] == "Rock, Paper, Shotgun":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  12
    #            if gamenews.iloc[i][1] == "Shacknews":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  13
    #            if gamenews.iloc[i][1] == "Community Announcements":
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  14
    #            if gamenews.iloc[i][1] == "TF2 Blog":
    #                #newsdf.loc[gamenews.postDate[i], newsdf['appName'] == name] =  15
    #                newsdf.loc[newsdf['timestamps'] == gamenews.postDate[i], name] =  15

    return newsdf













