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
from predictInputs import predictUserTargets
import random

#%%
def validateUserTargetsPrediction(gameDetailsDF, targetName, userWaitMonths):
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
    scatterHistories = histories[1]
    
#------------------------------------------------------------------------------
# get model prediction of a price given a wait time that already happened 
#------------------------------------------------------------------------------
    # outputs: list([predictedInputPriceOutput, predictedNextDealPriceOutput, historicalLow, testPrice, userWaitMonths])
    targetPredictionOutput = predictUserTargets(targetGameDetails, publisherGameDetails, genreGameDetails, 
                       scatterHistories, userWaitMonths, nextHighProbDay=0,
                       validate=True)
    
    return targetPredictionOutput

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
nGameSamples = 65

# Filter for price and Metacritic score (>= 70)
gameFilter = (gameDetailsDF['Initial Price'] >= 4999) & (gameDetailsDF['Initial Price'] < 7999) & (gameDetailsDF['Metacritic Score'] >= 70)
filteredGameDetailsDF = gameDetailsDF[gameFilter]

sample = random.sample(list(filteredGameDetailsDF['Game Title']), nGameSamples)

#%%
#------------------------------------------------------------------------------
# run model and collect errors
#------------------------------------------------------------------------------
userWaitMonths = 4

# run prediction with validation settings on
predictedPriceOutput = np.zeros(nGameSamples)
predictedMonthOutput = np.zeros(nGameSamples)
actualPrice = np.zeros(nGameSamples)
testWaitMonths = np.zeros(nGameSamples)
error_sq = np.zeros(nGameSamples)
for i in range(len(sample)):
    targetPredictionOutput = validateUserTargetsPrediction(filteredGameDetailsDF, sample[i], userWaitMonths)
    
    # parse predictUserTargets output
    predictedPriceOutput[i] = targetPredictionOutput[0]
    actualPrice[i] = targetPredictionOutput[3]
    testWaitMonths[i] = targetPredictionOutput[4]
    
#%%
# combine actual and predicted prices into single matrix
pricepredictionMatrix = np.vstack((actualPrice, predictedPriceOutput)).T
pricepredictionDF = pd.DataFrame(pricepredictionMatrix, columns=list(('actual','predicted')))
pricepredictionDF = pricepredictionDF.dropna()

# calculate percent error
error = (pricepredictionDF['predicted'] - pricepredictionDF['actual']) / pricepredictionDF['actual']
error_pct = error*100
np.mean(error_pct)
#np.mean(error_pct.drop([29,61]))


# calculate squared error for price
price_prediction_error_sq = np.power(pricepredictionDF['predicted'] - pricepredictionDF['actual'], 2)
#price_prediction_error_sq = price_prediction_error_sq.drop([29,61])

# calculate mean squared error
error_sq_sum = np.sum(price_prediction_error_sq)/len(price_prediction_error_sq)
error_rms = np.power(error_sq_sum, 1/2)

# 3.53 (n=5)
# 18.28 (n=65) n-2 outliers Vampyr and Monster Hunter

#pricepredictionDF.to_pickle("dataobjects/PricePrediction_60usd-70meta.pkl")







