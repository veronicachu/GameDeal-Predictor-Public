# -*- coding: utf-8 -*-
"""
Input: target game title

Output: prediction of the time period of next upcoming deal and price

----
Last updated: 2019-07-16
"""
#%%
import datetime
from dateutil.parser import parse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines import CoxPHFitter
import random

#%%
def predictNextDeal(targetGameDetails, publisherGameDetails, genreGameDetails,
                    filledHistories, validate=False):
#%%
#------------------------------------------------------------------------------
# parse inputs for needed data formats
#------------------------------------------------------------------------------
    # get target game information
    ind = targetGameDetails.index.tolist()
    targetReleaseDate = targetGameDetails['Release Data'][ind[0]]
    
    # get price history information
    targetHistory = filledHistories[0]
    publisherHistory = filledHistories[1]
    genreHistory = filledHistories[2]
    
#%%
#------------------------------------------------------------------------------
# feature engineering: target price history
# 1) transform dates to days since release
# 2) find time when deals occur and duration from last deal's end to current deal's start
#------------------------------------------------------------------------------
    target_dur_until_deal = []
    targetDaysSinceRelease = []
    if len(targetHistory) > 0:
        # Part 1 - transform dates to days since release
        # convert timestamps to dates 
        targetGameDates = []
        for ts in targetHistory['timestamps']:
            targetGameDates.append(datetime.datetime.fromtimestamp(ts).date())
        
        # convert dates --> days since release
        # transform specific dates to time deltas (in days) from release date
        # i.e days from release_date to timepoint1, release_date to timepoint2, etc.
        try:
            targetfirstdayDT = datetime.datetime.strptime(targetReleaseDate, '%b %d, %Y').date()
        except:
            try:
                targetfirstdayDT = datetime.datetime.strptime(targetReleaseDate, '%b %Y').date()
            except:
                targetfirstdayDT = parse(targetReleaseDate, ignoretz=True).date()
        
        for i in range(len(targetGameDates)):
            delta = targetGameDates[i] - targetfirstdayDT
            targetDaysSinceRelease.append(delta.days)
        
#        plt.figure()
#        plt.scatter(targetDaysSinceRelease, targetHistory.iloc[:,1])
#        plt.title("Price History " + targetName, fontsize=50)
#        plt.xlabel("Days Since Release", fontsize=30)
#        plt.ylabel("Price", fontsize=30)
#        ax = plt.gca()
#        ax.tick_params(axis = 'both', which = 'major', labelsize = 20)
#        ax.tick_params(axis = 'both', which = 'minor', labelsize = 12)
        
        # Part 2 - find time when deals occur and the duration from last deal's end
        # find change in target price history time series
        targetPriceDiff = targetHistory.iloc[:,1].diff()
        
        # combine days since release and price history change into a matrix
        targetPriceChanges = np.zeros([len(targetPriceDiff), 2])
        for i in range(len(targetPriceChanges)):
            tempDate = targetDaysSinceRelease[i]
            tempPrice = targetPriceDiff.iloc[i]
            targetPriceChanges[i,:] = [tempDate, tempPrice]
        
        # remove first row with nan
        priceChanges = targetPriceChanges[1:,:]
        
        # remove rows with zeros
        priceChanges = priceChanges[~(priceChanges==0).any(1),:]
        
        # markers for when deals start
        targetDealStart = priceChanges[(priceChanges<0).any(1),:]
        
        # markers for when deals end
        targetDealEnd = priceChanges[~(priceChanges<0).any(1),:]
        firstRow = targetPriceChanges[0,:]
        targetDealEnd = np.vstack([firstRow, targetDealEnd])
        
        # find duration between deals
        for i in range(len(targetDealStart[:,0])):
            # find index of day for current deal
            dealDay = targetDealStart[i, 0]
            daysColumn = targetPriceChanges[:,0]
            dealDayInd = np.where(daysColumn == dealDay)[0][0]
            
            # find day for when last normal price began
            temp = targetPriceChanges[:int(dealDayInd),:]
            previousNonZero = temp[(temp[:,1]!=0),:]
            originDay = previousNonZero[-1][0]
            
            # find time elapsed since last deal ended
            duration = dealDay - originDay
            
            target_dur_until_deal = np.hstack([target_dur_until_deal, duration])
        
        # remove first row with zero initialization
        target_dur_until_deal = target_dur_until_deal[1:]
    
#%%
#------------------------------------------------------------------------------
# feature engineering: publisher price history
# 1) transform dates to days since release
# 2) find time when deals occur and duration from last deal's end to current deal's start
#------------------------------------------------------------------------------
    # Part 1 - transform dates to days since release
    # convert dates --> days since release
    # transform specific dates to time deltas (in days) from release date
    # i.e days from release_date to timepoint1, release_date to timepoint2, etc.
    publisherDaysSinceRelease = []
    # make sure there are still other publisher games
    if len(publisherHistory) > 0:
        publisherGameTitles = []
        
        for ind in range(len(publisherHistory)):
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
                            firstdayDT = datetime.datetime.strptime(firstday, '%b %Y').date()
                        except:
                            firstdayDT = parse(firstday, ignoretz=True).date()
            
            # calculate time delta from release date
            gameDelta = []
            for i in range(len(dealDates)):
                timeDelta = dealDates[i] - firstdayDT
                gameDelta.append(timeDelta.days)
            publisherGameTitles.append(columnnames[1])
            publisherDaysSinceRelease.append(gameDelta)

    # visualize publisher price history x days since release
#    for ind in range(len(publisherHistory)):
#        plt.scatter(publisherDaysSinceRelease[ind], publisherHistory[ind][publisherGameTitles[ind]])
##        plt.title("Price History for Ubisoft Games", fontsize=50)
#        plt.title("Price History for " + publisherGameTitles[ind], fontsize=50)
#        plt.xlabel("Days Since Release", fontsize=30)
#        plt.ylabel("Price", fontsize=30)
#        ax = plt.gca()
#        ax.tick_params(axis = 'both', which = 'major', labelsize = 20)
#        ax.tick_params(axis = 'both', which = 'minor', labelsize = 12)
#        ax.set_ylim([0, 70])
    
    # Part 2 - find time when deals occur and the duration from last deal's end
    publisher_dur_until_deal = []
    if len(publisherHistory) > 0:
        
        for ind in range(len(publisherHistory)):
            # find change in publisher price history time series
            publisherPriceDiff = publisherHistory[ind].iloc[:,1].diff()
            
            # combine days since release and price history change into a matrix
            publisherPriceChanges = np.zeros([len(publisherPriceDiff), 2])
            for i in range(len(publisherPriceChanges)):
                tempDate = publisherDaysSinceRelease[ind][i]
                tempPrice = publisherPriceDiff.iloc[i]
                publisherPriceChanges[i,:] = [tempDate, tempPrice]
    
            # remove first row with nan
            priceChanges = publisherPriceChanges[1:,:]
    
            # remove rows with zeros
            priceChanges = priceChanges[~(priceChanges==0).any(1),:]
    
            # markers for when deals start
            publisherDealStart = priceChanges[(priceChanges<0).any(1),:]
    
            # markers for when deals end
            publisherDealEnd = priceChanges[~(priceChanges<0).any(1),:]
            firstRow = publisherPriceChanges[0,:]
            publisherDealEnd = np.vstack([firstRow, publisherDealEnd])
    
            # find duration between deals
            temp_dur_until_deal = np.zeros(1)
            for i in range(len(publisherDealStart[:,0])):
                # find index of day for current deal
                dealDay = publisherDealStart[i, 0]
                daysColumn = publisherPriceChanges[:,0]
                dealDayInd = np.where(daysColumn == dealDay)[0][0]
                
                # find day for when last normal price began
                temp = publisherPriceChanges[:int(dealDayInd),:]
                previousNonZero = temp[(temp[:,1]!=0),:]
                originDay = previousNonZero[-1][0]
                
                # find time elapsed since last deal ended
                duration = dealDay - originDay
                
                temp_dur_until_deal = np.hstack([temp_dur_until_deal, duration])
    
            # remove first row with zero initialization
            temp_dur_until_deal = temp_dur_until_deal[1:]
            
            # stack publisher durations in matrix
            publisher_dur_until_deal.append(temp_dur_until_deal)
    
#%%
#------------------------------------------------------------------------------
# feature engineering: genre price history
# 1) transform dates to days since release
# 2) find time when deals occur and duration from last deal's end to current deal's start
#------------------------------------------------------------------------------
    # Part 1 - transform dates to days since release
    # convert dates --> days since release
    # transform specific dates to time deltas (in days) from release date
    # i.e days from release_date to timepoint1, release_date to timepoint2, etc.
    genreDaysSinceRelease = []
    # make sure there are still other publisher games
    if len(genreHistory) > 0 and len(publisherHistory) < 1:
        genreGameTitles = []
        
        for ind in range(len(genreHistory)):
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
                try:
                    firstdayDT = datetime.datetime.strptime(firstday, '%d %b, %Y').date()
                except:
                    try:
                        firstdayDT = datetime.datetime.strptime(firstday, '%B %dth, %Y').date()
                    except:
                        try:
                            firstdayDT = datetime.datetime.strptime(firstday, '%b %Y').date()
                        except:
                            firstdayDT = parse(firstday, ignoretz=True).date()
            
            # calculate time delta from release date
            gameDelta = []
            for i in range(len(dealDates)):
                timeDelta = dealDates[i] - firstdayDT
                gameDelta.append(timeDelta.days)
            genreGameTitles.append(columnnames[1])
            genreDaysSinceRelease.append(gameDelta)

    ## visualize publisher price history x days since release
#    for ind in range(len(publisherHistory)):
#        plt.scatter(publisherDaysSinceRelease[ind], publisherHistory[ind][publisherGameTitles[ind]])
#        plt.title("Price History for Ubisoft Games", fontsize=50)
#        plt.xlabel("Days Since Release", fontsize=30)
#        plt.ylabel("Price", fontsize=30)
#        ax = plt.gca()
#        ax.tick_params(axis = 'both', which = 'major', labelsize = 20)
#        ax.tick_params(axis = 'both', which = 'minor', labelsize = 12)
    
    # Part 2 - find time when deals occur and the duration from last deal's end
    genre_dur_until_deal = []
    if len(genreHistory) > 0 and len(publisherHistory) < 1:
        for ind in range(len(genreHistory)):
            # find change in publisher price history time series
            genrePriceDiff = genreHistory[ind].iloc[:,1].diff()
            
            # combine days since release and price history change into a matrix
            genrePriceChanges = np.zeros([len(genrePriceDiff), 2])
            for i in range(len(genrePriceChanges)):
                tempDate = genreDaysSinceRelease[ind][i]
                tempPrice = genrePriceDiff.iloc[i]
                genrePriceChanges[i,:] = [tempDate, tempPrice]
    
            # remove first row with nan
            priceChanges = genrePriceChanges[1:,:]
    
            # remove rows with zeros
            priceChanges = priceChanges[~(priceChanges==0).any(1),:]
    
            # markers for when deals start
            genreDealStart = priceChanges[(priceChanges<0).any(1),:]
    
            # markers for when deals end
            genreDealEnd = priceChanges[~(priceChanges<0).any(1),:]
            firstRow = genrePriceChanges[0,:]
            genreDealEnd = np.vstack([firstRow, genreDealEnd])
    
            # find duration between deals
            temp_dur_until_deal = np.zeros(1)
            for i in range(len(genreDealStart[:,0])):
                # find index of day for current deal
                dealDay = genreDealStart[i, 0]
                daysColumn = genrePriceChanges[:,0]
                dealDayInd = np.where(daysColumn == dealDay)[0][0]
                
                # find day for when last normal price began
                temp = genrePriceChanges[:int(dealDayInd),:]
                previousNonZero = temp[(temp[:,1]!=0),:]
                originDay = previousNonZero[-1][0]
                
                # find time elapsed since last deal ended
                duration = dealDay - originDay
                
                temp_dur_until_deal = np.hstack([temp_dur_until_deal, duration])
    
            # remove first row with zero initialization
            temp_dur_until_deal = temp_dur_until_deal[1:]
            
            # stack publisher durations in matrix
            genre_dur_until_deal.append(temp_dur_until_deal)
    
#%%
#------------------------------------------------------------------------------
# machine learning: probability of deal
#------------------------------------------------------------------------------
    if validate is True and len(targetHistory) > 0:
        if len(target_dur_until_deal) > 1:
            # choose random target deal that has already occurred
#            testDuration = random.choice(target_dur_until_deal)
            # choose last target deal that has already occurred
            testDuration = target_dur_until_deal[-1]
            
            # get row index of target price in target unique price matrix
            ind = np.where(target_dur_until_deal == testDuration)[0][0]
            
            # remove target price and prices after it
            target_dur_until_deal = np.delete(target_dur_until_deal, np.s_[ind])
        else:
            testDuration = np.NaN
    else:
        testDuration = np.NaN
    
    
    # combine all data points into single array
    all_dur_until_deal = np.zeros(1) # initialize array
    if len(target_dur_until_deal) > 0:
        all_dur_until_deal = target_dur_until_deal
    
    if len(publisher_dur_until_deal) > 0:
        for ind in range(len(publisher_dur_until_deal)):
            all_dur_until_deal = np.hstack((all_dur_until_deal, publisher_dur_until_deal[ind]))
    
    if len(genre_dur_until_deal) > 0:
        for ind in range(len(genre_dur_until_deal)):
            all_dur_until_deal = np.hstack((all_dur_until_deal, genre_dur_until_deal[ind]))
    
    # create event array
    all_event = np.ones(all_dur_until_deal.shape)
    
    # get days since last target deal
    if len(targetDaysSinceRelease) > 0:
        censoredNextDealDur = targetDaysSinceRelease[-1] - targetDealEnd[-1][0]
    else:
        censoredNextDealDur = 0
    
    # add days since last target deal to duration and event matrices
    all_dur_until_deal = np.append(all_dur_until_deal, censoredNextDealDur)
    all_event = np.append(all_event, 0)
    
    # transform to Pandas dataframe for fitting
    tempmat = np.vstack((all_dur_until_deal, all_event)).T
    columns = ['Duration', 'Event']
    duration = pd.DataFrame(tempmat, columns=columns)
    
    # estimate survival function using Kaplan-Meier estimator
    kmf = KaplanMeierFitter()
    kmf.fit(duration['Duration'], event_observed=duration['Event'])
    
    # visualize probability of deals
#    kmf.survival_function_.plot(linewidth=3.3)
#    plt.title('Survival Function of No Deals (Activision Games)', fontsize=50)
#    plt.xlabel("Days Since Last Deal", fontsize=30)
#    plt.ylabel("Probability No Deal Tomorrow", fontsize=30)
#    ax = plt.gca()
#    ax.xaxis.set_label_coords(0.5,-.07)
#    ax.yaxis.set_label_coords(-.05,0.5)
#    ax.tick_params(axis = 'both', which = 'major', labelsize = 20)
#    ax.tick_params(axis = 'both', which = 'minor', labelsize = 12)
#    ax.set_xlim([0, 160])
    
    # probability a deal will occur tomorrow
    probDealTomorrow = 1 - kmf.predict(censoredNextDealDur)
    
    # when high probability (0.80) deal will occur tomorrow
    try:
        kmf_survival = kmf.survival_function_
        threshold = kmf_survival[kmf_survival['KM_estimate'] < .10]
        nextHighProbDay = threshold.index[0]
        nextHighProbDay = nextHighProbDay - censoredNextDealDur
    except:
        nextHighProbDay = np.NaN
    
    # Cox Proportional Hazard Model (regression model for future)
#    cph = CoxPHFitter()
#    cph.fit(duration, duration_col=0, show_progress=True)
#    cph.print_summary()  # access the results using cph.summary
#    
#    cph.predict_partial_hazard(duration)
#    cph.predict_survival_function(duration, times=[5., 25., 50.])
#    cph.predict_median(duration)
    
#%%
    return list([probDealTomorrow, nextHighProbDay, testDuration])
    
    
    
    
    
    
    
    
    
    
    
    
    
