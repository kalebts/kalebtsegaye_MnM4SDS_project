#import necessary libraries
# import nbimporter
import requests
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import re
import spotify_functions as spf
import songkick_functions as skf
import spotipy
import teetool as tt

api_key = "fCnCRQ1S6LDAS7zQ"
client_id = 'f5a0fe76389c42c0b85c832f1de66cf7'
client_secret = 'e9d4fc0874f345b2b636a6e307384bb7'

#maybe remove festivals - songkick
# maybe market - spotify

def point_analysis(artist):
    artists = spf.related_artists(artname = 'aster aweke')

    gl = []

    for a in artists:
        an = skf.get_artist_id(a[0].replace(' ', '+')) if not (a[0]+' ').isspace() else print('need artist!')    
        if an != -1:
            req = requests.get("https://api.songkick.com/api/3.0/artists/"+ an +"/gigography.json?apikey="+ api_key + '&per_page=20&order=desc')
            gdfs = skf.make_points(req.json())
            gl.append(gdfs[0])
    
    rdf = gpd.GeoDataFrame(pd.concat(gl, ignore_index=True))
    print(rdf)

    plt.figure(figsize=(10, 12))

    world = gpd.read_file('Countries_WGS84/Countries_WGS84.shp') #open file

    fig, ax = plt.subplots(figsize=(15,15))
    # ax = world[world.continent == 'North America'].plot(
    world.plot(ax=ax, color='white', edgecolor='black')

    # ax.set_xlim(-130, -65)
    # ax.set_ylim(24, 50)

    # We can now plot our ``GeoDataFrame``.
    rdf.plot(ax=ax, color='blue')

    # plot_line(ax, line)

    # plt.tight_layout()

    plt.show()