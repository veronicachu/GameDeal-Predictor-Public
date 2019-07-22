# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 11:22:02 2019

@author: Veronica Chu
"""
import generalFunctions
import pandas as pd
import numpy as np
from retrieveSimilarPriceHistories import retrievePriceHistories
import string

#%%
#targetName = "Assassin's Creed Odyssey" # 5999 initial
targetName = "Call of Duty: WWII" # 5999 initial

#%%
#------------------------------------------------------------------------------
# load pickled paid games dataframe
#------------------------------------------------------------------------------
try:
    gameDetailsDF = pd.read_pickle("dataobjects/SteamGamesDetails.pkl")
    gameDetailsDF = gameDetailsDF.replace('nan', np.NaN)
    gameDetailsDF = gameDetailsDF.reset_index(drop=True)
except:
    print ("Need SteamGamesDetails.pkl file in dataobjects folder. Run collectSteamPaidGamesDetails.py")

#%%
#------------------------------------------------------------------------------
# get necessary details from game details dataframe about target game, other similarly
# priced publisher games, and other similarly priced same genre games
#------------------------------------------------------------------------------
# get details for target game
targetGameDetails = gameDetailsDF.loc[gameDetailsDF['Game Title'] == targetName]
ind = targetGameDetails.index.tolist()
targetPublisher = targetGameDetails['Publishers'][ind[0]]
targetGenres = targetGameDetails['Genres'][ind[0]]

# get games with similar initial price as target game
# buffer of target/2 less than target initial
targetGameInitial = targetGameDetails.loc[:,['Initial Price']].values[0][0]
is_similar_initial = gameDetailsDF['Initial Price'] >= (targetGameInitial/3)
similarInitialGameDetails = gameDetailsDF[is_similar_initial]

# get details for similar priced games that have same publisher as target game
filterPublishers = similarInitialGameDetails['Publishers'].apply(lambda x: targetPublisher[0] in x)
publisherGameDetails = similarInitialGameDetails[filterPublishers]
if len(publisherGameDetails) != 0:
    publisherGameDetails = publisherGameDetails.loc[publisherGameDetails['Game Title'] != targetName]

# get details for similar priced games that have same genres as target game
genreGames = []
for game in similarInitialGameDetails['Game Title']:
    tempIndex = similarInitialGameDetails.index[similarInitialGameDetails['Game Title'] == game]
    tempGenres = similarInitialGameDetails.loc[similarInitialGameDetails['Game Title'] == game, ['Genres']]
    tempGenres = tempGenres['Genres'][tempIndex[0]]
    
    try:
        for genres in range(len(tempGenres)):
            if tempGenres[genres]['description'] == targetGenres[0]['description']:
                genreGames.append(game)
    except:
        pass
genreFilter = similarInitialGameDetails['Game Title'].isin(genreGames)
genreGameDetails = similarInitialGameDetails[genreFilter]
genreGameDetails = genreGameDetails.loc[genreGameDetails['Game Title'] != targetName]
filterPublishers = genreGameDetails['Publishers'].apply(lambda x: targetPublisher[0] not in x)
genreGameDetails = genreGameDetails[filterPublishers]
    
#%%
#------------------------------------------------------------------------------
# get relevant price histories (target game, similar publisher games, similar 
# genre games)
#------------------------------------------------------------------------------
# retrieve price histories of target game and similar games
histories = retrievePriceHistories(targetName, publisherGameDetails, genreGameDetails)

targetName = targetName.translate(str.maketrans('','',string.punctuation)) # remove punctuation
generalFunctions.save_pickleObject(histories,('PriceHistory_' + targetName)) # failed app ID list







