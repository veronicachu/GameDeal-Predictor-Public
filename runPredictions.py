# -*- coding: utf-8 -*-
"""
Run predictions given user inputs and when next game deal will occur

----
Last updated: 2019-06-25
"""
#%%
import pandas as pd
import numpy as np
from retrieveSimilarPriceHistories import retrievePriceHistories
from predictNextDeal import predictNextDeal
from predictInputs import predictUserTargets
import string

#%%
#targetName = "Assassin's Creed Odyssey" # 5999 initial
#targetName = 'Watch_Dogs'
targetName = "Call of Duty: WWII" # 5999 initial
#targetPrice = 20
userWaitMonths = 4

#%%
def predict_gamedeal(targetName, userWaitMonths):
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
    targetName2 = targetName.replace(":", "") # remove punctuation
    try:
        histories = pd.read_pickle("dataobjects/PriceHistory_" + targetName2 + ".pkl")
    except:
        histories = retrievePriceHistories(targetName, publisherGameDetails, genreGameDetails)
    
    # parse retrieved price history types
    filledHistories = histories[0]
    scatterHistories = histories[1]
    
#%%
#------------------------------------------------------------------------------
# run model to get probability there will be a deal tomorrow and when next day 
# there is a high probability of a deal
#------------------------------------------------------------------------------
    # outputs: list([probDealTomorrow, nextHighProbDay])
    dealPredictionOutput = predictNextDeal(targetGameDetails, publisherGameDetails, genreGameDetails,
                    filledHistories)
    
    # parse predictNextDeal output
    probDealTomorrow = dealPredictionOutput[0]
    nextHighProbDay = dealPredictionOutput[1]
    
#%%
#------------------------------------------------------------------------------
# run model to predict when target price will occur and what price will be when 
# given user wait time
#------------------------------------------------------------------------------
    # outputs: list([predictedInputPriceOutput, predictedNextDealPriceOutput, historicalLow, testPrice, userWaitMonths])
    targetPredictionOutput = predictUserTargets(targetGameDetails, publisherGameDetails, genreGameDetails, 
                       scatterHistories, userWaitMonths, nextHighProbDay,
                       validate=False)
    
    # parse predictUserTargets output
    predictedInputPriceOutput = targetPredictionOutput[0]
    predictedNextDealPriceOutput = targetPredictionOutput[1]
    historicalLow = targetPredictionOutput[2]
    
#%%
#------------------------------------------------------------------------------
# polish predictNextDeal output to send to webapp
#------------------------------------------------------------------------------
    probDealTomorrow = (str(round(probDealTomorrow*100, 1)) + '%')
#    nextHighProbDay = (str(round(nextHighProbDay/30, 1)) + ' months')
    
    if predictedNextDealPriceOutput < 0:
        predictedNextDealPriceOutput = '(Not enough data to make an accurate prediction)'
    else:
        predictedNextDealPriceOutput = ('$' + str(predictedNextDealPriceOutput))
    
#%%
#------------------------------------------------------------------------------
# polish predictUserTargets output to send to webapp
#------------------------------------------------------------------------------
    # if negative, then prediction is not accurate - need negative exponential model
    if predictedInputPriceOutput < 0:
        predictedInputPriceOutput = 'Not enough data to make an accurate prediction'
    else:
        predictedInputPriceOutput = ('$' + str(predictedInputPriceOutput))
    
    
#%%
    targetResults = list([predictedInputPriceOutput, historicalLow,
                          probDealTomorrow, nextHighProbDay, predictedNextDealPriceOutput])
    
    return targetResults

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    