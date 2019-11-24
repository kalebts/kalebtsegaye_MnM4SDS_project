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

# function definitions
def make_points(json_str):
    df = pd.DataFrame(
    {'City': [],
     'State/Province': [],
     'Country': [],
     'Longitude': [],
     'Latitude': []})

    i = 0

    for p in json_str['resultsPage']['results']['event']:
        #     print(p['popularity'])
        lng = p['location']['lng']
        lat = p['location']['lat']
        city = p['location']['city']
        state = 'N/A'
        csplit = city.split(',')
        country = csplit[1]
        
        if (len(csplit) == 3):
            if not ('Washington' == csplit[0] and 'DC' == csplit[1]):
                city = csplit[0]
                state = csplit[1]
                country = csplit[2]
            else:
                city = csplit[0] + ', ' + csplit[1]
                state = 'N/A'
                country = csplit[2]
            
        
        df.loc[i] = [city] + [state] + [country] + [lat] +[lng]

        i+=1
    #convert to gdf to plot
    gdf = gpd.GeoDataFrame(
        df, geometry=[Point(x, y) for y, x in zip(df['Longitude'], df['Latitude'])])

    gdf2 = gdf
    gdf2 = gdf2.drop(list(range(1, len(gdf))))
    gdf3 = gdf
    gdf3 = gdf3.drop(list(range(0, len(gdf)-1)))
    
    return(gdf, gdf2, gdf3)

def run_plot(req):
    gdfs = make_points(req.json())

    points_gdf = gdfs[0]
    print(points_gdf)
    start_gdf = gdfs[1]
    stop_gdf = gdfs[2]

    #current us basemap
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # fig, ax = plt.subplots(figsize=(15,15))
    ax = world[world.continent == 'North America'].plot(
#     ax = world.plot(
        color='white', edgecolor='black')

    ax.set_xlim(-130, -65)
    ax.set_ylim(24, 50)

    # We can now plot our ``GeoDataFrame``.
    points_gdf.plot(ax=ax, color='blue')

    start_gdf.plot(ax=ax, color='green')
    stop_gdf.plot(ax=ax, color='red')

    points = []

    linedf = pd.DataFrame(
        {'Line': []})

    for i in range(len(points_gdf)):
        points.append(points_gdf.iloc[i].loc["geometry"])

    line = LineString(points)

    def plot_line(ax, ob):
        x, y = ob.xy
        ax.plot(x, y, color='grey', alpha=0.7, linewidth=1, solid_capstyle='round', zorder=2)

    plot_line(ax, line)

    plt.tight_layout()

    plt.show()
    
def get_artist_id(artist_name):
    json_str = requests.get("https://api.songkick.com/api/3.0/search/artists.json?apikey=" + api_key + "&query=" + artist_name).json()
    return (str(json_str['resultsPage']['results']['artist'][0]['id']) if json_str['resultsPage']['totalEntries'] != 0 else -1)

def req_input():
    print("Welcome")
    while (True):
        past = True
        is_venue = True
        
        cmd = input("Venue search (0) or event search (1)?")
        
        if (cmd == 1):
            is_venue = False
            
        if (is_venue == False):
            cmd = input("Past events (0), upcoming events (1): ")
        
            if (cmd == 1):
                past = False
            
            cmd = input("Please type the parameters: [artist_name, min_date, max_date.] Separate with commas."
                       + "\nIf no input, just add a comma and skip.\n")
        
            if (cmd == 'quit'):
                return
        
            cs = cmd.split(',')
            an = get_artist_id(cs[0].replace(' ', '+')) if not (cs[0]+' ').isspace() else print('need artist!')
            if (cs[0]+' ').isspace():
                continue
            mind = "&min_date=" + cs[1].replace(' ', '') if (re.search("\d{4}-\d{2}-\d{2}", cs[1])) else ''
            maxd = "&max_date=" + cs[2].replace(' ', '') if (re.search("\d{4}-\d{2}-\d{2}", cs[2])) else ''
            
            if (past == True):
                r = requests.get("https://api.songkick.com/api/3.0/artists/"+ an +"/gigography.json?apikey="+ api_key 
                              + mind + maxd)
                run_plot(r)
            else:
                r = requests.get("https://api.songkick.com/api/3.0/events.json?apikey="+ api_key 
                    + an + loc + mind + maxd)
                print(r.json())
                run_plot(r)
        else:
            cmd = input("Past venues (0), upcoming venues (1): ")
        
            if (cmd == 1):
                past = False
            
        cmd = input("Please type the parameters: [artist_name, min_date, max_date.] Separate with commas."
                   + "\nIf no input, just add a comma and skip.\n")
        
        if (cmd == 'quit'):
            return
        
        cs = cmd.split(',')
        an = get_artist_id(cs[0].replace(' ', '+')) if not (cs[0]+' ').isspace() else print('need artist!')
        if (cs[0]+' ').isspace():
            continue
        mind = "&min_date=" + cs[1].replace(' ', '') if (re.search("\d{4}-\d{2}-\d{2}", cs[1])) else ''
        maxd = "&max_date=" + cs[2].replace(' ', '') if (re.search("\d{4}-\d{2}-\d{2}", cs[2])) else ''
        
        if (past == True):
            r = requests.get("https://api.songkick.com/api/3.0/artists/"+ an +"/gigography.json?apikey="+ api_key 
                              + mind + maxd)
            run_plot(r)
        else:
            r = requests.get("https://api.songkick.com/api/3.0/events.json?apikey="+ api_key 
                + an + loc + mind + maxd)
            print(r.json())
            run_plot(r)
            