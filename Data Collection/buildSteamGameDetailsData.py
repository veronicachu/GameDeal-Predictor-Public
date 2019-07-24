# -*- coding: utf-8 -*-
"""
Format data from json file read from Steam's app details page into a DataFrame
with target details

Input: 
    appIDDict = Steam app ID to Name dictionary
    appID = target's Steam app ID number
    json_appdata = json data
    gameDetailsDF = empty dataframe or existing dataframe game's info is being being added to

Output: 
    dataframe (game title | app ID | developer | publisher | release date | genres | total reviews | ...
               initial price | final price | metacritic score | metacritic url)
    
----
Created: 2019-06-12
Last updated: 2019-07-22
- Updated description
"""

def buildSteamGameDetailsData(appIDDict, appID, json_appdata, gameDetailsDF):
    title = appIDDict[appID]
    steamid = appID
    
    try:
        developer = json_appdata['developers']
    except:
        developer = 'nan'
    
    try:
        publisher = json_appdata['publishers']
    except:
        publisher = 'nan'
    
    try:
        release_date = json_appdata['release_date']['date']
    except:
        release_date = 'nan'
    
    try:
        genres = json_appdata['genres']
    except:
        genres = 'nan'
    
    try:
        total_reviews = json_appdata['recommendations']['total']
    except:
        total_reviews = 'nan'
    
    try:
        initial_price = json_appdata['price_overview']['initial']
    except:
        initial_price = 'nan'
    
    try:
        final_price = json_appdata['price_overview']['final']
    except:
        final_price = 'nan'
                                
    try:
        metacritic_score = json_appdata['metacritic']['score']
    except:
        metacritic_score = 'nan'
                                
    try:
        metacritic_url = json_appdata['metacritic']['url']
    except:
        metacritic_url = 'nan'
    
    # place into pandas dataframe
    gameDetailsDF = gameDetailsDF.append(
                        {'Game Title': title,
                       'Steam ID': steamid, 
                       'Developers': developer,
                       'Publishers': publisher,
                       'Release Data': release_date,
                       'Genres': genres,
                       'Total Reviews': total_reviews,
                       'Initial Price': initial_price,
                       'Final Price': final_price,
                       'Metacritic Score': metacritic_score,
                       'Metacritic URL': metacritic_url}, ignore_index=True)
    return gameDetailsDF


