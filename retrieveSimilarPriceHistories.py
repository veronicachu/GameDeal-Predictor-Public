# -*- coding: utf-8 -*-
"""
Input: target game title

Output: retrieve target game price history, same publisher games' price 
histories, and same genre games' price histories

----
Last updated: 2019-07-16
"""
#%%
import buildPriceHistoryData
import numpy as np
import time

#%%
#targetName = "Total War: WARHAMMER" # 5999 initial
def retrievePriceHistories(targetName, publisherGameDetails, genreGameDetails):
#%%
#------------------------------------------------------------------------------
# get target game's price history
#------------------------------------------------------------------------------
    # target game price history dataframe
    targetHistory = buildPriceHistoryData.buildPriceHistoryData(targetName)
    
    # remove NaNs from filled target history
    targetHistory_filled = targetHistory[0].replace('nan', np.NaN)
    targetHistory_filled = targetHistory_filled.dropna()
    
    # remove NaNs from scatter target history
    targetHistory_scatter = targetHistory[1].replace('nan', np.NaN)
    targetHistory_scatter = targetHistory_scatter.dropna()

#%%
#------------------------------------------------------------------------------
# get similar publisher games' price history
#------------------------------------------------------------------------------
    # publisher games price history dataframe
    publisherHistory_filled = []
    publisherHistory_scatter = []
    
    numRequestperSec = 1 # determine best number for the site
    # make sure there are other publisher games
    if len(publisherGameDetails) > 0:
        # if publisher has too many games, take a sample of 10 games so function doesn't take too long to scrap data
        if len(publisherGameDetails) > 20:
            sample = publisherGameDetails.sample(n=20)
        else:
            sample = publisherGameDetails
        
        # list of selected publisher games' price history dataframes
        for game in sample['Game Title']:
            print(game)
            df = buildPriceHistoryData.buildPriceHistoryData(game)
            
            if len(df[0]) > 0:
                # remove NaNs from filled publisher history
                df_filled = df[0].replace('nan', np.NaN)
                df_filled = df_filled.dropna()
                
                # remove NaNs from scatter publisher history
                df_scatter = df[1].replace('nan', np.NaN)
                df_scatter = df_scatter.dropna()
                
                publisherHistory_filled.append(df_filled)
                publisherHistory_scatter.append(df_scatter)
            
            time.sleep(1/numRequestperSec)
        
    # remove empty publisher price histories
    publisherHistory_filled = [publisherHistory_filled[x] for x, _ in enumerate(publisherHistory_filled) if publisherHistory_filled[x].empty is False]
    publisherHistory_scatter = [publisherHistory_scatter[x] for x, _ in enumerate(publisherHistory_scatter) if publisherHistory_scatter[x].empty is False]
       
#%%
#------------------------------------------------------------------------------
# get and clean similar genre price history
# use genre history only if there is no publisher history available
#------------------------------------------------------------------------------
    # genre games price history dataframe
    genreHistory_filled = []
    genreHistory_scatter = []
    # make sure there are other genre games
    if len(genreGameDetails) > 0 and len(publisherHistory_filled) < 1:
        # if too many games with same genre, take a sample of 10 games so doesn't take too long
        if len(genreGameDetails) > 10:
            sample = genreGameDetails.sample(n=10)
        else:
            sample = genreGameDetails
        
        # list of selected publisher games' price history dataframes
        for game in sample['Game Title']:
            df = buildPriceHistoryData.buildPriceHistoryData(game)
            
            # remove NaNs from filled publisher history
            df_filled = df[0].replace('nan', np.NaN)
            df_filled = df_filled.dropna()
            
            # remove NaNs from scatter publisher history
            df_scatter = df[1].replace('nan', np.NaN)
            df_scatter = df_scatter.dropna()
            
            genreHistory_filled.append(df_filled)
            genreHistory_scatter.append(df_scatter)
        
    # remove empty publisher price histories
    genreHistory_filled = [genreHistory_filled[x] for x, _ in enumerate(genreHistory_filled) if genreHistory_filled[x].empty is False]
    genreHistory_scatter = [genreHistory_scatter[x] for x, _ in enumerate(genreHistory_scatter) if genreHistory_scatter[x].empty is False]
    
    # place price histories into lists for function return
    filledHistories = list([targetHistory_filled, publisherHistory_filled, genreHistory_filled])
    scatterHistories = list([targetHistory_scatter, publisherHistory_scatter,genreHistory_scatter])
    
#%%
    return list([filledHistories, scatterHistories])
    
    