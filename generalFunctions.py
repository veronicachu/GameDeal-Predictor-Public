# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 12:28:26 2019

@author: User
"""
#%%
import pickle

# save pickle object
def save_pickleObject(obj, name ):
    with open('dataobjects/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

# load pickle object
def load_pickleObject(name ):
    with open('dataobjects/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

#%%
#------------------------------------------------------------------------------
# load saved pickled lists
#------------------------------------------------------------------------------
def load_savedLists(num):
    # 1 - get saved paid games ID list
    if num == 1:
        try:
            loadedList = load_pickleObject('paidSteamIDslist')
        except:
            loadedList = []
    
    # 2 - get saved free games ID list
    if num == 2:
        try:
            loadedList = load_pickleObject('freeSteamIDsList')
        except:
            loadedList = []
    
    # 3 - get saved non-game ID list
    if num == 3:
        try:
            loadedList = load_pickleObject('nongameSteamIDsList')
        except:
            loadedList = []
    
    # 4 - get saved failed ID list - request error
    if num == 4:
        try:
            loadedList = load_pickleObject('brokenSteamIDsList')
        except:
            loadedList = []
        
    # 5 - get saved failed ID list - unformatted JSON error
    if num == 5:
        try:
            loadedList = load_pickleObject('unformattedSteamIDsList')
        except:
            loadedList = []
        
    # 6 - get saved failed ID list - empty JSON error
    if num == 6:
        try:
            loadedList = load_pickleObject('emptySteamIDsList')
        except:
            loadedList = []
    
    return loadedList

#%%
#------------------------------------------------------------------------------
# randomly choose from list of proxies and verify proxy
# https://codereview.stackexchange.com/questions/194977/using-rotation-of-proxies-within-a-python-script
#------------------------------------------------------------------------------
from random import choice
#from urllib.parse import urlparse

def set_proxy(session, proxy_candidates, verify=False):
    """
    Configure the session to use one of the proxy_candidates.  If verify is
    True, then the proxy will have been verified to work.
    """
#    while True:
    chosen_proxy = choice(proxy_candidates)
    proxy = {"https": chosen_proxy}
#        session.proxies = {urlparse(proxy).scheme: proxy}
#        if not verify:
#            return
#        try:
#            print(session.get('https://httpbin.org/ip').json())
#            return
#        except Exception:
#            pass
    return proxy #session.proxies


