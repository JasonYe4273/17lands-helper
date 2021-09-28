import os
import json
import requests
from time import sleep
from datetime import date, time, datetime, timedelta
import numpy as np
import pandas as pd
import WUBRG
from WUBRG import COLOUR_GROUPS

# TODO: Make this a json object which is routinely checked.
# This will enable format updates without having to completely recompile the bot.
SET_CONFIG = {
    "MID" : {
        "PremierDraft": {
            "Updating" : True,
            "StartDate" : "yyyy-mm-dd",
            "EndDate" : "yyyy-mm-dd"
        },
        "TradDraft": {
            "Updating" : True,
            "StartDate" : "yyyy-mm-dd",
            "EndDate" : "yyyy-mm-dd"
        },
        "QuickDraft": {
            "Updating" : False,
            "StartDate" : "yyyy-mm-dd",
            "EndDate" : "yyyy-mm-dd"
        },
        "Sealed": {
            "Updating" : False,
            "StartDate" : "yyyy-mm-dd",
            "EndDate" : "yyyy-mm-dd"
        },
        "TradSealed": {
            "Updating" : False,
            "StartDate" : "yyyy-mm-dd",
            "EndDate" : "yyyy-mm-dd"
        },
        "DraftChallenge": {
            "Updating" : False,
            "StartDate" : "yyyy-mm-dd",
            "EndDate" : "yyyy-mm-dd"
        }
        # TODO: Consider adding in a list of key archetypes to reduce data footprint.
        #"KeyArchetypes" : ["U", "B", "WU", "WB", "UB", "UG", ""]
    },
    "AFR" : {
        "PremierDraft": {
            "Updating" : False,
            "StartDate" : "yyyy-mm-dd",
            "EndDate" : "yyyy-mm-dd"
        },
        "TradDraft": {
            "Updating" : False,
            "StartDate" : "yyyy-mm-dd",
            "EndDate" : "yyyy-mm-dd"
        },
        "QuickDraft": {
            "Updating" : False,
            "StartDate" : "yyyy-mm-dd",
            "EndDate" : "yyyy-mm-dd"
        },
        "Sealed": {
            "Updating" : False,
            "StartDate" : "yyyy-mm-dd",
            "EndDate" : "yyyy-mm-dd"
        },
        "TradSealed": {
            "Updating" : False,
            "StartDate" : "yyyy-mm-dd",
            "EndDate" : "yyyy-mm-dd"
        },
        "DraftChallenge": {
            "Updating" : False,
            "StartDate" : "yyyy-mm-dd",
            "EndDate" : "yyyy-mm-dd"
        }
    }
}

##SETS = ['MID', 'AFR']
SETS = ['MID']
FORMATS = ['PremierDraft', 'TradDraft']
#FORMATS = ['PremierDraft', 'TradDraft', 'QuickDraft', 'Sealed', 'TradSealed', 'DraftChallenge

def get_set_tree():
    SET_TREE = dict()
    for s in SETS:
        SET_TREE[s] = dict()
        for f in FORMATS:
            SET_TREE[s][f] = dict()
            for c in COLOUR_GROUPS:
                SET_TREE[s][f][c] = None
    return SET_TREE


START_DATE = '2021-01-01'
DATA_DIR = os.path.join(os.getcwd(), "17_lands_data")
FILENAME = '{0}_{1}.json'  #'{set}_{format}.json'



STAT_NAMES = {
## "name",
 "color" : "Color",
 "rarity" : "Rarity",
 "seen_count" : "# Seen", 
 "avg_seen" : "ALSA", 
 "pick_count" : "# Picked", 
 "avg_pick" : "ATA", 
 "game_count" : "# GP", 
 "win_rate" : "GP WR", 
## "sideboard_game_count" : "Sideboard Games", 
## "sideboard_win_rate" : "SWR", 
 "opening_hand_game_count" : "# OH", 
 "opening_hand_win_rate" : "OH WR", 
 "drawn_game_count" : "# GD", 
 "drawn_win_rate" : "GD WR", 
 "ever_drawn_game_count" : "# GIH", 
 "ever_drawn_win_rate" : "GIH WR", 
 "never_drawn_game_count" : "# GND", 
 "never_drawn_win_rate" : "GND WR", 
 "drawn_improvement_win_rate" : "IWD"
## "url",
## "url_back",
}
PERCENTS = ["GP WR", "OH WR", "GD WR", "GIH WR", "GND WR", "IWD"]

RARITY_ALIASES = {
    'common': "C",
    'uncommon': "U",
    'rare': "R",
    'mythic': "M"
}




DATA_CACHE = get_set_tree()
##{
##"SET" : {
##    "FORMAT" : {
##        "COLOURS" : {
##            "CARD" : {
##                "STAT_1" : None,
##                "STAT_2" : None,
##                "STAT_3" : None ...
##                }
##            }
##        }
##    }
##}

PANDAS_CACHE = get_set_tree()
##{
##"SET" : {
##    "FORMAT" : {
##        "COLOURS" : <pandas.DataFrame>
##        }
##    }
##}

def fetch_bot_data():
    # TODO: Fill this out to pull .config data to update the bot on the fly.
    pass



### Pandas Helpers ###

# Converts a dict of cards stats into a a DataFrame
def panadafy_dict(d):
    frame = pd.DataFrame.from_dict(d, orient='index')
    frame = frame.rename(columns=STAT_NAMES)
    
    # If there's no data, make a blank frame and return it.
    if len(d) == 0:
        return frame
    
    for col in PERCENTS:
        frame[col] = frame[col] * 100
    
    frame['Rarity'] = frame['Rarity'].map(RARITY_ALIASES)
    frame = frame.round(3)
    return frame


# Creates a copy of the cache, except using DataFrames instead of dicts for card data.
def pandafy_cache():
    global PANDAS_CACHE
    PANDAS_CACHE = get_set_tree()
    for s in SETS:
        for f in FORMATS:
            for c in COLOUR_GROUPS:
                #print(f"Framing {s} {f} {c}'s {str(len(DATA_CACHE[s][f][c]))} cards...")
                frame = panadafy_dict(DATA_CACHE[s][f][c])
                PANDAS_CACHE[s][f][c] = frame


# Filters out cards that have a number of games played less than p% of # GP.
def min_play_filter(df, p):
    min_game = df['# GP'].mean() * (p/100)
    return df[df['# GP'] >= min_game]


# Filters out cards that don't fall within the colour identy.
def color_id_filter(df, color_string):
    if color_string is not None and color_string != '':
        return df[df['Color'].apply(lambda x: set(x) <= set(color_string))]
    else:
        return df


# Filters out cards that aren't in the given rarities.
def rarity_filter(df, rarity):
    if rarity is not None and rarity != '':
        return df[df['Rarity'].apply(lambda x: set(x) <= set(rarity))]
    else:
        return df


# Gets the top n cards, based on a particular stat column.
# Can filter based on card colours, rarity.
# Can get the bottom n cards with 'reverse=True'
def get_top(df, col, n=5, card_colors=None, card_rarity=None, min_thresh=10, reverse=False):
    filtered = min_play_filter(df, min_thresh)
    filtered = color_id_filter(filtered, card_colors)
    filtered = rarity_filter(filtered, card_rarity)

    # Functional XOR.
    reverse = reverse != (col == "ALSA" or col == "ATA")
    
    # Return the smallest values if we're dealing with pick orders
    if reverse != (col == "ALSA" or col == "ATA"):
        return filtered.nsmallest(n, col)
    else:
        return filtered.nlargest(n, col)


# Gets a suite of data about the given colour's position in the metagame.
def get_color_metadata(s, f, color, stat='GIH WR', columns=None):
    df = PANDAS_CACHE[s][f]['']
    if columns == None:
        columns = list(df)
    
    top_commons = get_top(df, stat, n=10, card_colors=color, card_rarity='C')
    top_commons.columns.name = f'Top 10 {color} Commons'
    top_commons = top_commons[columns]
    top_uncommons = get_top(df, stat, n=10, card_colors=color, card_rarity='U')
    top_uncommons.columns.name = f'Top 10 {color} Uncommons'
    top_uncommons = top_uncommons[columns]
    
    color_pairs = [color + x for x in COLORS if x != color]
    color_pair_dfs = dict()
    
    for col in color_pairs:
        c = WUBRG.get_color_identity(col)
        commons = get_top(PANDAS_CACHE[s][f][c], stat, n=5, card_rarity='C')
        uncommons = get_top(PANDAS_CACHE[s][f][c], stat, n=5, card_rarity='U')
        df = pd.concat([commons, uncommons])
        df.columns.name = f'{col} Top Cards'
        df = df[columns]
        color_pair_dfs[c] = df
        
    # TODO: Add in a fun fact here.
        
    return (top_commons, top_uncommons, color_pair_dfs)



### JSON Management ###

# Reads the json file for a given set and returns a dict which represent the cards.
def read_set_data(s, f):
    format_dict = { c : dict() for c in COLOUR_GROUPS }
    filename = FILENAME.format(s, f)
    filepath = os.path.join(DATA_DIR, filename)
    print(f'Parsing {filename}...')

    try:
        json_str = ''
        with open(filepath, 'r') as f:
            json_str = f.read()
            f.close()
        
        format_dict = json.loads(json_str)
    except:
        print(f'Error reading json file {filename}')

    return format_dict


# Automatically gets the overall data for cards, and the data for 1, 2 and 3 colour decks.
def save_set_data(s, f):
    json_out = dict()
    filename = FILENAME.format(s, f)

    # Query 17 lands for each colour filter.
    for c in COLOUR_GROUPS:
        success = False
        count = 0
        
        json_colour = fetch_format_data(s, f, c)
        json_out[c] = json_colour
        sleep(3)


    # Convert the aggreate dictionary into a .json file, and save it.       
    try:
        filepath = os.path.join(DATA_DIR, filename)
        file = open(filepath, 'w')
        file.write(json.dumps(json_out))
        file.close()
        
        print(f'File {filename} created.')
    except Exception as ex:
        print(f'Error creating {filename}!')



### 17 Lands Querying ###

# Returns true is the data for a set format should be updated.
def to_update(s, f):
    # If the data doesn't exist,
    if not os.path.isfile(os.path.join(DATA_DIR, FILENAME.format(s, f))):
        # Signal for an update.
        print(f"{s} {f} doesn't exist. Signaling update...")
        return True
    
    # Or, if the format is live,
    if SET_CONFIG[s][f]['Updating']:
        time_range_start = time(0, 55)
        time_range_end = time(2, 0)
        cur_date = datetime.utcnow()
        cur_time = cur_date.time()

        # And the current time is between 12:55am and 2:00am,
        if time_range_start <= cur_time <= time_range_end:
            # Signal for an update.
            print(f"{s} {f} is live, and new data should exist. Signaling update...")
            return True

        try:
            edit_date = datetime.fromtimestamp(os.path.getmtime(os.path.join(DATA_DIR, FILENAME.format(s, f))))
        except:
            # Should update if can't find file
            return True
        edit_diff = cur_date - edit_date
        # Or, if the file is over 24hrs old, update it.
        if edit_diff >= timedelta(days=1):
            # Signal for an update.
            print(f"{s} {f} is over 24hrs old. Signaling update...")
            return True

    # Otherwise, skip the update.
    return False


# Fetches all the data for a given set and format, using an optional colour filter.
def fetch_format_data(s, f, c = 'None', start_date = None, end_date = None):
    success = False
    count = 0

    if c is None or c == 'None' or c == "":
        c = 'No Filter'

    if start_date is None:
        start_date = START_DATE
    if end_date is None:
        end_date = date.today()
    
    while not success:
        count += 1
        response = None
        
        try:
            url_base = 'https://www.17lands.com/card_ratings/data?'
            url_append = f'expansion={s}&format={f}&start_date={start_date}&end_date={end_date}'
            colour_filter = ''
            if c != 'No Filter':
                colour_filter = f'&colors={c}'
            url = url_base + url_append + colour_filter
            print(f'Fetching data for {s} {f} "{c}"...')
            response = requests.get(url)
            
            success = True
            print('Success!')
        except:
            if count < 5:
                print('Failed; trying again in 30s')
                sleep(30)
                continue
            else:
                print(f'Failed to get data after 5 attempts. File {filename} not created')
                return dict()

        # Pump the query results into a dict, tagged with the colour filter,
        # trimming data like image, name etc.
        json_colour = dict()
        for card in response.json():
            card_info = dict()
            for stat in STAT_NAMES:
                card_info[stat] = card[stat]
            json_colour[card['name']] = card_info
        return json_colour
    

# Fetch all the data for sets and fomats, controlled by SET_CONFIG
def fetch_all_data():
    print(f'Checking for new format data...')
    update_dict = get_set_tree()
    
    for s in SETS:
        for f in FORMATS:
            if to_update(s, f):
                update_dict[s][f] = True
                save_set_data(s, f)
                sleep(60)
            else:
                update_dict[s][f] = False
                print(f'{s} {f} data is up to date!')

    print(f'Done checking for new format data.\r\n')
    return update_dict



### Cache Management ###

# Creates an empty cache structure for the card data.
def blank_cache():
    global DATA_CACHE
    new_cache = get_set_tree()
    for s in SETS:
        for f in FORMATS:
            new_cache[s][f] = dict()
        
    DATA_CACHE = new_cache


# Updates the cards data cache with data from the .json files.
def update_cache(update_dict):
    global DATA_CACHE
    print(f'Checking for cache updates...')
    
    # Create a copy of the current cache to modify.

    new_cache = dict(DATA_CACHE)

    # For each format in the set, check for a go-ahead to refresh the data.
    for s in SETS:
        for f in FORMATS:
            if update_dict[s][f]:
                # If allowed, get the data from the json file, and add it to the temp chache.
                new_cache[s][f] = read_set_data(s, f)
                print(f'{s} {f} added to DATA_CACHE!')

    # Overwite the main cache with the temp cache.
    DATA_CACHE = new_cache
    print(f'Done checking for cache updates.\r\n')
    pandafy_cache()



def init_cache():
    # Update all data.
    fetch_all_data()

    # Create a blank cache.
    blank_cache()

    # Create an update dict which update the entire cache.
    update_dict = get_set_tree()
    for s in SETS:
        for f in FORMATS:
            update_dict[s][f] = True

    # And update the cache.
    update_cache(update_dict)


def query_cache(_set, _format, color_filter, cardname):
    if _set not in DATA_CACHE:
        return None
    if _format not in DATA_CACHE[_set]:
        return None
    if color_filter not in DATA_CACHE[_set][_format]:
        return None
    if cardname not in DATA_CACHE[_set][_format][color_filter]:
        return None
    return DATA_CACHE[_set][_format][color_filter][cardname]

### Data Analysis ###



if __name__ == "__main__":
    init_cache()
    pass
