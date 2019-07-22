# -*- coding: utf-8 -*-
"""
Builds a dataset of game price history from IsThereAnyDeal.com

Input: 
    gameName as (list of strings) - must have exact names as on it's Steam page

Output: 
    dataframe (timestamp | price)

----
Last updated: 2019-07-16
"""
#%%
import getPriceHistory
import datetime
import pandas as pd

#%%
#gameName = 'Grim Dawn'
#gameName = 'Dirt Rally'
gameName = "Call of Duty: WWII" # 5999 initial

def buildPriceHistoryData(gameName):
#%%
    df = getPriceHistory.getPriceHistory(gameName)

#------------------------------------------------------------------------------
# create empty dataframe of appName x time filled with zeros
#------------------------------------------------------------------------------
    if not df.empty:
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
        pricedf = pd.DataFrame(index=timestamps, columns = {gameName})
        pricedf.index.name = 'timestamps'
        pricedf = pricedf.reset_index()
    
    #------------------------------------------------------------------------------
    # create empty dataframe of appName x time filled with zeros
    #------------------------------------------------------------------------------
        steamPrices = df[df.dealShopName == ("Steam" or "Amazon")] # filter dealshops for Steam only
        
        dateList = steamPrices.dealDate.tolist()
        priceList = steamPrices.dealNewPrice.tolist()
        
        for i in range(len(dateList)):
            pricedf.loc[pricedf['timestamps'] == dateList[i], gameName] = priceList[i]
        
        # if 'fill' input true, fill NaNs with previous price data
        pricedf_filled = pricedf.fillna(method='ffill')
    else:
        print('no price history for' + gameName)
        pricedf_filled = []
        pricedf = []

    return list([pricedf_filled, pricedf])
#%%
#------------------------------------------------------------------------------
# plot price history
#------------------------------------------------------------------------------
#import matplotlib.pyplot as plt
#x = timeSamples
#y = pricedf.loc[:, gameName]
#
#plt.figure()
#plt.scatter(x,y)
#plt.title("Price History for " + gameName, fontsize=50)
#plt.xlabel("Time", fontsize=30)
#plt.ylabel("Prices", fontsize=30)
#
#ax = plt.gca()
#ax.tick_params(axis = 'both', which = 'major', labelsize = 24)
#ax.tick_params(axis = 'both', which = 'minor', labelsize = 16)
#
#ax.set_xlim([datetime.date(2017,1,1), currentday])




























