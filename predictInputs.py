# -*- coding: utf-8 -*-
"""
Prediction of the price the target game will drop down to and the price
of the game within the wait time period using price histories of other similar 
games by the same publisher or games of the same genre; "similar" defined as 
close in initial price to the target game

Inputs: targetGameDetails, publisherGameDetails, genreGameDetails, 
        scatterHistories, targetPrice, userWaitMonths

Outputs: list([predictedPriceOutput, predictedMonthOutput, historicalLow, targetPrice, userWaitMonths])
 - predictedPriceOutpu and predictedMonthOutput are strings
 - historicalLow is a float
 - targetPrice and userWaitMonths are used for validation (will change from input if input validate=True)

----
Last updated: 2019-06-25
"""
#%%
import datetime
from dateutil.parser import parse
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
from scipy.optimize import curve_fit
import random
import math
import statistics

#%%
def func(x, a, b, c, d):
    return a * np.exp(-b * (x - c)) + d

#%%
def predictUserTargets(targetGameDetails, publisherGameDetails, genreGameDetails, 
                       scatterHistories, userWaitMonths, nextHighProbDay,
                       validate=False):
#%%
#------------------------------------------------------------------------------
# parse inputs for needed data formats
#------------------------------------------------------------------------------
    # get target game information
    ind = targetGameDetails.index.tolist()
    targetName = targetGameDetails['Game Title'][ind[0]]
    targetReleaseDate = targetGameDetails['Release Data'][ind[0]]
    
    # get price history information
    targetHistory = scatterHistories[0]
    publisherHistory = scatterHistories[1]
    genreHistory = scatterHistories[2]
    
#%%
#------------------------------------------------------------------------------
# feature engineering: target price history
# 1) transform dates to days since release
# 2) keep only first instance of each unique price value
#------------------------------------------------------------------------------
    try:
        targetfirstdayDT = datetime.datetime.strptime(targetReleaseDate, '%b %d, %Y').date()
    except:
        targetfirstdayDT = parse(targetReleaseDate, ignoretz=True).date()
    
    if len(targetHistory) > 0:
        # convert timestamps to dates 
        targetGameDates = []
        for ts in targetHistory['timestamps']:
            targetGameDates.append(datetime.datetime.fromtimestamp(ts).date())
        
        # convert dates --> days since release
        # transform specific dates to time deltas (in days) from release date
        # i.e days from release_date to timepoint1, release_date to timepoint2, etc.
        targetDaysSinceRelease = []
        
        for i in range(len(targetGameDates)):
            delta = targetGameDates[i] - targetfirstdayDT
            targetDaysSinceRelease.append(delta.days)
        
        ## visualize target price history x days since release
#        plt.figure()
#        plt.scatter(targetDaysSinceRelease, targetHistory[targetName], s=100)
#        plt.title("Price History " + targetName, fontsize=50)
#        plt.xlabel("Days Since Release", fontsize=30)
#        plt.ylabel("Price", fontsize=30)
#        ax = plt.gca()
#        ax.xaxis.set_label_coords(0.5,-.07)
#        ax.yaxis.set_label_coords(-.05,0.5)
#        ax.tick_params(axis = 'both', which = 'major', labelsize = 20)
#        ax.tick_params(axis = 'both', which = 'minor', labelsize = 12)
        
        # grab first instance in time of each unique price value
        target_FirstUniquePrices = np.zeros(shape=[1,2])
        target_UniquePrices = np.unique(list(targetHistory[targetName]))
        tempPriceHistory = list(targetHistory[targetName])
        for price in list(target_UniquePrices):
                tempIndex = (next(index for index in range(len(targetHistory)) if tempPriceHistory[index] == price))
                temp = np.array([targetDaysSinceRelease[tempIndex], price])
                target_FirstUniquePrices = np.vstack((target_FirstUniquePrices, temp))
        # remove first row (initiliziation values)
        target_FirstUniquePrices = target_FirstUniquePrices[1:,:]
        # sort by days since release
        target_FirstUniquePrices = target_FirstUniquePrices[np.argsort(target_FirstUniquePrices[:,0])]
    else:
        target_FirstUniquePrices = np.empty(2)

#%%
#------------------------------------------------------------------------------
# feature engineering: publisher price history
# 1) transform dates to days since release
# 2) keep only first instance of each unique price value
#------------------------------------------------------------------------------
    # convert dates --> days since release
    # transform specific dates to time deltas (in days) from release date
    # i.e days from release_date to timepoint1, release_date to timepoint2, etc.
    publisherDaysSinceRelease = []
    # make sure there are still other publisher games
    if len(publisherHistory) > 0:
        publisherGameTitles = []
        
        for ind in range((len(publisherHistory))):
            dealDates = []
            for ts in publisherHistory[ind]['timestamps']:
                        dealDates.append(datetime.datetime.fromtimestamp(ts).date())
            
            # get first day
            columnnames = list(publisherHistory[ind].columns.values)
            ind2 = publisherGameDetails.loc[publisherGameDetails['Game Title'] == columnnames[1]].index.tolist()
            firstday = publisherGameDetails['Release Data'][ind2[0]]
            try:
                firstdayDT = datetime.datetime.strptime(firstday, '%b %d, %Y').date()
            except:
                try:
                    firstdayDT = datetime.datetime.strptime(firstday, '%d %b, %Y').date()
                except:
                    try:
                        firstdayDT = datetime.datetime.strptime(firstday, '%B %dth, %Y').date()
                    except:
                        try:
                            firstdayDT = parse(firstday, ignoretz=True).date()
                        except:
                            pass
            
            # calculate time delta from release date
            gameDelta = []
            for i in range(len(dealDates)):
                timeDelta = dealDates[i] - firstdayDT
                gameDelta.append(timeDelta.days)
            publisherGameTitles.append(columnnames[1])
            publisherDaysSinceRelease.append(gameDelta)

    ## visualize publisher price history x days since release
#    for ind in range(len(publisherHistory)):
#        plt.scatter(publisherDaysSinceRelease[ind], publisherHistory[ind][publisherGameTitles[ind]], s=100)
##        plt.title("Price History for Ubisoft Games", fontsize=50)
#        plt.title("Price History for " + publisherGameTitles[ind], fontsize=50)
#        plt.xlabel("Days Since Release", fontsize=30)
#        plt.ylabel("Price", fontsize=30)
#        ax = plt.gca()
#        ax.xaxis.set_label_coords(0.5,-.07)
#        ax.yaxis.set_label_coords(-.05,0.5)
#        ax.tick_params(axis = 'both', which = 'major', labelsize = 20)
#        ax.tick_params(axis = 'both', which = 'minor', labelsize = 12)
    
    # grab first instance in time of each unique price value
    publisher_FirstUniquePrices = np.zeros(shape=[1,2])
    if len(publisherDaysSinceRelease) > 0:
        for ind in range(len(publisherDaysSinceRelease)):
            tempPriceHistory = list(publisherHistory[ind][publisherGameTitles[ind]])
            tempUniquePrices = np.unique(tempPriceHistory)
            
            # get indexes for first instance of each unique value
            for price in list(tempUniquePrices):
                tempIndex = (next(index for index in range(len(tempPriceHistory)) if tempPriceHistory[index] == price))
                temp = np.array([publisherDaysSinceRelease[ind][tempIndex], price])
                publisher_FirstUniquePrices = np.vstack((publisher_FirstUniquePrices, temp))
    # remove first row (initiliziation values)
    publisher_FirstUniquePrices = publisher_FirstUniquePrices[1:,:]
    # sort by days since release
    publisher_FirstUniquePrices = publisher_FirstUniquePrices[np.argsort(publisher_FirstUniquePrices[:,0])]

#%%
#------------------------------------------------------------------------------
# feature engineering: genre price history
# 1) transform dates to days since release
# 2) keep only first instance of each unique price value
#------------------------------------------------------------------------------
    # convert dates --> days since release
    # transform specific dates to time deltas (in days) from release date
    # i.e days from release_date to timepoint1, release_date to timepoint2, etc.
    genreDaysSinceRelease = []
    # make sure there are still other genre games
    if len(genreHistory) > 0 and len(publisherHistory) < 1:
        genreGameTitles = []
        
        for ind in range((len(genreHistory))):
            dealDates = []
            for ts in genreHistory[ind]['timestamps']:
                        dealDates.append(datetime.datetime.fromtimestamp(ts).date())
            
            # get first day
            columnnames = list(genreHistory[ind].columns.values)
            ind2 = genreGameDetails.loc[genreGameDetails['Game Title'] == columnnames[1]].index.tolist()
            firstday = genreGameDetails['Release Data'][ind2[0]]
            try:
                firstdayDT = datetime.datetime.strptime(firstday, '%b %d, %Y').date()
            except:
                firstdayDT = parse(firstday, ignoretz=True).date()
            
            # calculate time delta from release date
            gameDelta = []
            for i in range(len(dealDates)):
                timeDelta = dealDates[i] - firstdayDT
                gameDelta.append(timeDelta.days)
            genreGameTitles.append(columnnames[1])
            genreDaysSinceRelease.append(gameDelta)
    
    ## visualize genre price history x days since release
#    for ind in range(len(genreHistory)):
#        plt.scatter(genreDaysSinceRelease[ind], genreHistory[ind][genreGameTitles[ind]])
#        plt.title("Price History for Same Genre Games", fontsize=50)
#        plt.xlabel("Days Since Release", fontsize=30)
#        plt.ylabel("Price", fontsize=30)
#        ax = plt.gca()
#        ax.tick_params(axis = 'both', which = 'major', labelsize = 20)
#        ax.tick_params(axis = 'both', which = 'minor', labelsize = 12)
    
    # grab first instance in time of each unique price value
    genre_FirstUniquePrices = np.zeros(shape=[1,2])
    if len(genreDaysSinceRelease) > 0 and len(publisherHistory) < 1:
        for ind in range(len(genreDaysSinceRelease)):
            tempPriceHistory = list(genreHistory[ind][genreGameTitles[ind]])
            tempUniquePrices = np.unique(tempPriceHistory)
            
            # get indexes for first instance of each unique value
            for price in list(tempUniquePrices):
                tempIndex = (next(index for index in range(len(tempPriceHistory)) if tempPriceHistory[index] == price))
                temp = np.array([genreDaysSinceRelease[ind][tempIndex], price])
                genre_FirstUniquePrices = np.vstack((genre_FirstUniquePrices, temp))
    # remove first row (initiliziation values)
    genre_FirstUniquePrices = genre_FirstUniquePrices[1:,:]
    # sort by days since release
    genre_FirstUniquePrices = genre_FirstUniquePrices[np.argsort(genre_FirstUniquePrices[:,0])]

#%%
#------------------------------------------------------------------------------
# machine learning: target game pricing model
#------------------------------------------------------------------------------
    if validate is True and len(targetHistory) > 0:
        if len(target_UniquePrices) >= 2:
            # choose random target price that has already occurred
#            testPrice = random.choice(target_UniquePrices)
            # choose last target price that has already occurred
            testPrice = target_UniquePrices[-1]
            
            # get row index of target price in target unique price matrix
            ind = np.where(target_FirstUniquePrices == testPrice)[0][0]
            
            # get time target price occurred to use as input into prediction
            userWaitMonths = target_FirstUniquePrices[ind][0]
            
            # remove target price
            tempTargetUniqueTime = np.delete(target_FirstUniquePrices[:,0], np.s_[ind]) #:len(target_FirstUniquePrices)])
            tempTargetUniquePrice = np.delete(target_FirstUniquePrices[:,1], np.s_[ind]) #:len(target_FirstUniquePrices)])
            
            # combine matrix back together
            target_FirstUniquePrices = np.array((tempTargetUniqueTime, tempTargetUniquePrice)).T
        else:
            testPrice = np.NaN
    else:
        testPrice = np.NaN
    
    # create weights - weight target price history highest, publisher price history second, and genre price history lowest
#    if len(targetHistory) > 0:
#        arrayLen = len(target_FirstUniquePrices) + len(publisher_FirstUniquePrices) + len(genre_FirstUniquePrices)
#    else:
#        arrayLen = len(publisher_FirstUniquePrices) + len(genre_FirstUniquePrices)
#    
#    model_weights = np.zeros(arrayLen)
#    for i in range(len(target_FirstUniquePrices)):
#        model_weights[i] = 4
#    for i in range(len(target_FirstUniquePrices), len(target_FirstUniquePrices)+len(publisher_FirstUniquePrices)):
#        model_weights[i] = 2
#    for i in range(len(target_FirstUniquePrices)+len(publisher_FirstUniquePrices), len(target_FirstUniquePrices)+len(publisher_FirstUniquePrices)+len(genre_FirstUniquePrices)):
#        model_weights[i] = 1
    
    # combine all data points into single matrix
    all_FirstUniquePrices = np.vstack((target_FirstUniquePrices, publisher_FirstUniquePrices, genre_FirstUniquePrices))
    
    # scipy curve_fit
    # fit curve
    init_vals = [50,0,90,63]
    all_FirstUniquePrices = all_FirstUniquePrices[np.argsort(all_FirstUniquePrices[:,0])]
    
    # futher clean data
    tempprices = all_FirstUniquePrices[:,1]
    ind = targetGameDetails.index.tolist()
    rowtodelete = []
    for i in range(2,len(tempprices)):
        temp = tempprices[:i]
        mintemp = statistics.median(temp)
        
        # remove if current price greater than median so far
        if temp[i-1] > mintemp:
            rowtodelete.append(i)
        # remove if current price greater than initial value
        elif temp[i-1] > (targetGameDetails['Initial Price'][ind[0]]/100):
            rowtodelete.append(i)
            
    
    all_FirstUniquePrices = np.delete(all_FirstUniquePrices, (rowtodelete), axis=0)
    xdata = all_FirstUniquePrices[:,0]
    ydata = all_FirstUniquePrices[:,1]
    
    # fit your data and getting fit parameters
    popt, pcov = curve_fit(func, xdata, ydata, p0=init_vals, bounds=([0,0,90,0], [1000, 0.1, 200, 200]))
#    
    # visualize data that model is being fitted to
#    plt.figure()
#    plt.scatter(target_FirstUniquePrices[:,0], target_FirstUniquePrices[:,1],  color='black', s=100)
#    plt.scatter(publisher_FirstUniquePrices[:,0], publisher_FirstUniquePrices[:,1], color='blue', s=100)
#    plt.scatter(genre_FirstUniquePrices[:,0], genre_FirstUniquePrices[:,1], color='grey')
#    plt.title("Price History for Activision Games", fontsize=50)
#    plt.xlabel("Days Since Release", fontsize=30)
#    plt.ylabel("Price", fontsize=30)
#    ax = plt.gca()
#    ax.xaxis.set_label_coords(0.5,-.07)
#    ax.yaxis.set_label_coords(-.05,0.5)
#    ax.tick_params(axis = 'both', which = 'major', labelsize = 20)
#    ax.tick_params(axis = 'both', which = 'minor', labelsize = 12)
#        
#    # plot fit
#    plt.plot(xdata, func(xdata, *popt), '-', label='fit', linewidth=3.3)
    
    
#    # scikit learn - linear regression
#    # create linear regression model
#    lm = linear_model.LinearRegression()
#    lm.fit(all_FirstUniquePrices[:,0].reshape(-1,1), all_FirstUniquePrices[:,1].reshape(-1,1), sample_weight=model_weights)
    
#%%
#------------------------------------------------------------------------------
# prepare output results
#------------------------------------------------------------------------------
    # user input days + number of days already since release
    currentday = datetime.date.today()
    days_release_to_today = currentday - targetfirstdayDT
    userWaitDays = userWaitMonths * 30
    userDaysSince = (days_release_to_today + datetime.timedelta(days=userWaitDays)).days
    
    # calculate predicted price for input target day
    # predict new data based on your fit
    predictedInputPrice = func(userDaysSince, *popt) # using scipy curve_fit model
    predictedInputPriceOutput = math.ceil(predictedInputPrice)
#    predictedPrice = lm.coef_*userDaysSince + lm.intercept_ # using scikit linear regression model
#    predictedPriceOutput = math.ceil(predictedPrice[0][0])
    
    
    if validate is False:
        # next high prob deal days + number of days already since release
        days_release_to_today = currentday - targetfirstdayDT
        nextDealWaitDays = nextHighProbDay
        nextDealDaysSince = (days_release_to_today + datetime.timedelta(days=nextDealWaitDays)).days
        
        # calculate predicted price for input target day
        # predict new data based on your fit
        predictedNextDealPrice = func(nextDealDaysSince, *popt) # using scipy curve_fit model
        predictedNextDealPriceOutput = math.ceil(predictedNextDealPrice)
    #    predictedPrice = lm.coef_*nextDealDaysSince + lm.intercept_ # using scikit linear regression model
    #    predictedPriceOutput = math.ceil(predictedPrice[0][0])
    elif validate is True:
        predictedNextDealPriceOutput = np.NaN
    
    
    # get historical low
    if len(target_FirstUniquePrices) > 1 and len(targetHistory) > 1:
        historicalLow = min(target_FirstUniquePrices[:,1]) # use as check
    else:
        historicalLow = np.NaN
    
    
    return list([predictedInputPriceOutput, predictedNextDealPriceOutput, historicalLow, testPrice, userWaitMonths])










