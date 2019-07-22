# -*- coding: utf-8 -*-
"""
Validate the ouputs from the price prediction model

----
Last updated: 2019-06-25
"""
#%%
import pandas as pd
import numpy as np
from retrieveSimilarPriceHistories import retrievePriceHistories
from predictNextDeal import predictNextDeal
import random

#%%
def validateUserTargetsPrediction(gameDetailsDF, targetName):
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
    is_similar_initial = gameDetailsDF['Initial Price'] >= (targetGameInitial-targetGameInitial/2)
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
    
#------------------------------------------------------------------------------
# get relevant price histories (target game, similar publisher games, similar 
# genre games)
#------------------------------------------------------------------------------
    # retrieve price histories of target game and similar games
    histories = retrievePriceHistories(targetName, publisherGameDetails, genreGameDetails)
    filledHistories = histories[0]
    
#------------------------------------------------------------------------------
# get model prediction of a price given a wait time that already happened 
#------------------------------------------------------------------------------
    # outputs: list([probDealTomorrow, nextHighProbDay, testDuration])
    dealPredictionOutput = predictNextDeal(targetGameDetails, publisherGameDetails, genreGameDetails,
                    filledHistories, validate=True)
    
    return dealPredictionOutput

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

#------------------------------------------------------------------------------
# select random sample of games to validate on
#------------------------------------------------------------------------------
# Filter for price and Metacritic score (>= 70)
gameFilter = (gameDetailsDF['Initial Price'] >= 4999) & (gameDetailsDF['Initial Price'] < 7999) & (gameDetailsDF['Metacritic Score'] >= 70)
filteredGameDetailsDF = gameDetailsDF[gameFilter]

nGameSamples = len(filteredGameDetailsDF)
sample = random.sample(list(filteredGameDetailsDF['Game Title']), nGameSamples)

#%%
#------------------------------------------------------------------------------
# run model and collect errors
#------------------------------------------------------------------------------
# run prediction with validation settings on
probDealTomorrow = np.zeros(nGameSamples)
nextHighProbDay = np.zeros(nGameSamples)
testDuration = np.zeros(nGameSamples)
error_sq = np.zeros(nGameSamples)
for i in range(len(sample)):
    targetPredictionOutput = validateUserTargetsPrediction(filteredGameDetailsDF, sample[i])
    
    # parse predictUserTargets output
    probDealTomorrow[i] = targetPredictionOutput[0]
    nextHighProbDay[i] = targetPredictionOutput[1]
    testDuration[i] = targetPredictionOutput[2]
    
#%%
# combine actual and predicted prices into single matrix
dealpredictionMatrix = np.vstack((testDuration, nextHighProbDay)).T
dealpredictionDF = pd.DataFrame(dealpredictionMatrix, columns=list(('actual','predicted')))
dealpredictionDF = dealpredictionDF.dropna()

# calculate percent error
error = (dealpredictionDF['predicted'] - dealpredictionDF['actual']) / dealpredictionDF['actual']
error_pct = error*100
np.mean(error_pct)
#np.mean(error_pct.drop([14,100,114]))


# calculate squared error for price
deal_prediction_error_sq = np.power(dealpredictionDF['predicted'] - dealpredictionDF['actual'], 2)
#deal_prediction_error_sq = deal_prediction_error_sq.drop([14,100,114])

# calculate mean squared error
error_sq_sum = np.sum(deal_prediction_error_sq)/len(deal_prediction_error_sq)
error_rms = np.power(error_sq_sum, 1/2)

# -135.80%; 61.45 rms (n=65)

dealpredictionDF.to_pickle("dataobjects/DealPrediction_60usd-70meta-0.1thres.pkl")

# threshold < 0.30 (run #1) --> mean pct change = -93.42, rms = 85.43
# threshold < 0.30 (run #2) --> mean pct change = -67.14, rms = 74.73

# threshold < 0.2 --> mean pct change = -65.76, rms = 78.39
# threshold < 0.1 --> mean pct change = -28.12, rms = 63.63




