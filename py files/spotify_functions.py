#import necessary libraries
import requests
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import re
import spotipy
import base64
import teetool as tt

api_key = "fCnCRQ1S6LDAS7zQ"
client_id = 'f5a0fe76389c42c0b85c832f1de66cf7'
client_secret = 'e9d4fc0874f345b2b636a6e307384bb7'

#maybe remove festivals - songkick
# maybe market - spotify

#spotipy playground
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlists = sp.user_playlists('spotify')

"https://api.spotify.com/v1/search?q=year%3A2001&type=artist&market=US"

# se = sp.search(q = 'year:0000-9999', limit = 1, offset = 9999, type = 'artist', market = 'US')

# se = sp.search(q = 'tag:hipster ', limit = 1, offset = 5678, type = 'album', market = 'US')

# se = sp.search(q = 'berhana', limit = 1, type = 'artist')

# spotify function definitions

# given a name/id or genre, will provide a list of 
# artists that exist in relation and also are within the follower limit

# custom function used to sort by num of shared genres
def custom_sort(x):
    return x[2]

query_count = 0

# handles counting the genres for related artists
def ra_help(artid, genres):
    global query_count
    alist = []
    if query_count < 10:
        for a in sp.artist_related_artists(artid)['artists']:
            gc = 0
            for g in a['genres']:    
                if g in genres:
                    gc += 1
            if gc > 0 and ([item for item in alist if item[1] == a['id']] == []):
                alist.append((a['name'], a['id'], gc))
        return sorted(alist, key = custom_sort, reverse = True)
                    
# used to faciliate recursive calls - 
# allows me to find the related artists in each level of separation from the root
# before moving on to the root artist
def ra_rec(lst, genres, followers, lessthan):
    global query_count
    lst2 = []
    for a in lst:
        if query_count < 10:
            lst2+=(ra_help(a[1], genres))
            query_count += 1
#         print("ra_rec ra_help" + str(query_count))
    if query_count < 10:
        lst2 += (ra_rec((sorted(lst2, key = custom_sort)), genres, followers, lessthan))    
    
    return sorted(lst2, key = custom_sort, reverse = True)

def related_artists(artname='', artid='', genre='', followers=-1, lessthan = True):
    if (artname == '' and artid == '' and genre == ''):
        print('please include name, id, or genre')
        return
    else:
        global query_count
        query_count = 0
        alist = []
        if (artname != ''):
            se = sp.search(q = artname, limit = 1, type = 'artist')
            query_count += 1
            print("related_artists search " + str(query_count))
            if (se['artists']['total'] > 0):
                artist = se['artists']['items'][0]
                artid = artist['id']
                genres = artist['genres']
        elif (artid != ''):
            artist = sp.artist(artid)
            genres = artist['genres']

        lst = ra_help(artid, genres)
#         print(lst)
        query_count += 1
        print("related_artists ra_help " + str(query_count))
                
        if query_count < 10:
            lst+=(ra_rec(lst, genres, followers, lessthan))
          
        print(len(lst))
        
        print(len(sorted(list(set(lst)), key = custom_sort)))
    
    return sorted(list(set(lst)), key = custom_sort, reverse = True) 

# related_artists(artid = '0WjtdWS6su0f3jrW9aqEHl')   
