import os
import json
import requests
from time import sleep
from datetime import date, time, datetime, timedelta
import numpy as np
import pandas as pd

from WUBRG import *
from settings  import *
from utils import *


RARITY_ALIASES = {
    'common': "C",
    'uncommon': "U",
    'rare': "R",
    'mythic': "M"
}


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


### Config ###
##SETS = settings.SETS
##FORMATS = settings.FORMATS
##SET_CONFIG = settings.SET_CONFIG
##DEFAULT_START_DATE = settings.DEFAULT_START_DATE
##DATA_DIR = settings.DATA_DIR
##CONFIG_DIR = settings.SET_CONFIG
##CARD_DATA_FILENAME = settings.CARD_DATA_FILENAME  #'{set}_{format}.json'



### 'Objects' ###

def get_set_tree():
    SET_TREE = dict()
    for s in SETS:
        SET_TREE[s] = dict()
        for f in FORMATS:
            SET_TREE[s][f] = dict()
            for c in COLOUR_GROUPS:
                SET_TREE[s][f][c] = None
    return SET_TREE


PANDAS_CACHE = get_set_tree()
DATA_CACHE = get_set_tree()
WINRATES = get_set_tree()
##"CARD" : {
##    "STAT_1" : None,
##    "STAT_2" : None,
##    "STAT_3" : None ...
##    }



### Helper Functions ###

# Make an HTTP request to a given url for json data.
# 'tries' limits the number of attempts made to get data.
# 'delay' sets the number of seconds before retrying on a fail.
# On sucess returns a json object, otherwise None
def fetch(url, tries = 5, delay = 60):
    success = False
    count = 0
    
    while not success:
        count += 1
        response = None
        
        try:
            response = requests.get(url)
            data = response.json()
            
            success = True
            print('Success!')
            return data
        except:
            if count < tries:
                print(f'Failed. Trying again in {delay} seconds.')
                sleep(delay)
                continue
            else:
                print(f'Failed to get data after 5 attempts.')
                return None


# Converts a dict of cards stats into a a DataFrame
def panadafy_dict(d):
    if d is None:
        print('Warning: Dict for pandafying is null.')
    
    frame = pd.DataFrame.from_dict(d, orient='index')
    frame = frame.rename(columns=STAT_NAMES)
    
    # If there's no data, make a blank frame and return it.
    if len(d) == 0:
        return frame
    
    for col in ["GP WR", "OH WR", "GD WR", "GIH WR", "GND WR", "IWD"]:
        frame[col] = frame[col] * 100
    
    frame['Rarity'] = frame['Rarity'].map(RARITY_ALIASES)
    frame = frame.round(3)
    return frame


### Deck Level Data ###
            
def fetch_deck_data():
    print(f'WARNING: fetch_deck_data not yet implemented.')
    pass



### Card Level Data ###

def get_scryfall_data(raw_cardname):
    card_info = gen_card_info_struct()
    ret = {'card_info': card_info, 'err_msg': None}
    
    try:
        response = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={raw_cardname}').json()
        if response['object'] == 'error':
            if response['details'][:20] == 'Too many cards match':
                ret['err_msg'] = f'Error: multiple card matches for "{raw_cardname}"'
            else:
                ret['err_msg'] = f'Error: cannot find card "{raw_cardname}"'
        elif response['object'] != 'card':
            ret['err_msg'] = f'Error: "{raw_cardname}" returned non-card'
        else:
            card = response
            card_info['name'] = card['name']
            card_info['stored_name'] = get_card_name(card)
            card_info['cmc'] = card['cmc']
            card_info['color_identity'] = get_color_identity(''.join(card['color_identity']))
            card_info['id'] = card['id']
            card_info['url'] = card['scryfall_uri']
            if card['set_type'] == 'promo':
                card_info['set'] = card['set'][1:].upper()
            else:
                card_info['set'] = card['set'].upper()

            if 'card_faces' in card:
                card_info['mana_cost'] = parse_cost(card['card_faces'][0]['mana_cost'])
                #card_info['colors'] = card['card_faces'][0]['colors'] + card['card_faces'][1]['colors']
            else:
                card_info['mana_cost'] = parse_cost(card['mana_cost'])
                #card_info['colors'] = WUBRG.get_color_identity(''.join(card['colors']))

    except Exception as ex:
        print(ex)
        ret['err_msg'] = f'Error querying Scryfall for {raw_cardname}'

    return ret


def fetch_card_data_by_colour(s, f, c = ''):
    # Manage params
    start_date = SET_CONFIG[s][f]['StartDate']
    if start_date is None:
        start_date = DEFAULT_START_DATE
        
    end_date = SET_CONFIG[s][f]['EndDate']
    if end_date is None:
        end_date = date.today()
    
    if c is None or c == '':
        c = 'No Filter'

    # Generate url
    url_base = 'https://www.17lands.com/card_ratings/data?'
    url_append = f'expansion={s}&format={f}&start_date={start_date}&end_date={end_date}'
    colour_filter = '' if c == 'No Filter' else f'&colors={c}'
    url = url_base + url_append + colour_filter
    print(f"Fetching data for {s} {f}, filter: '{c}'...")

    # Fetch card-lavel data.
    response = fetch(url)

    # Pump the query results into a dict, tagged with the colour filter,
    # trimming data like image, name etc.
    json_colour = dict()
    for card in response:
        card_info = dict()
        for stat in STAT_NAMES:
            card_info[stat] = card[stat]
        json_colour[card['name']] = card_info
    return json_colour
    
    pass


def fetch_card_data(s, f, delay = 5):
    # Automatically gets the overall data for cards, and the data for 1, 2 and 3 colour decks.
    card_data = dict()

    # Query 17 lands for each colour filter.
    for c in COLOUR_GROUPS:       
        card_data[c] = fetch_card_data_by_colour(s, f, c)
        sleep(delay)

    print(f"Fetched card data for {s} {f}!")
    return card_data


def save_card_data(s, f):
    # Convert the aggreate dictionary into a .json file, and save it.
    card_data = fetch_card_data(s, f)
    filename = CARD_DATA_FILENAME.format(s, f)
    save_json_file(DATA_DIR, filename, card_data)


def load_card_data(s, f):
    filename = CARD_DATA_FILENAME.format(s, f)
    return load_json_file(DATA_DIR, filename)
    print(f'Parsing {filename}...')


def update_card_data(s, f, force = False):
    def allow_update(s, f):
        filepath = os.path.join(DATA_DIR, CARD_DATA_FILENAME.format(s, f))
        
        # If the data doesn't exist,
        if not os.path.isfile(filepath):
            # Signal for an update.
            print(f"{s} {f} doesn't exist. Signaling update...")
            return True
        
        # Or, if the format is live,
        if SET_CONFIG[s][f]['Updating']:
            utc_time = datetime.utcnow().time()
            edit_date = datetime.fromtimestamp(os.path.getmtime(filepath))
            edit_diff = datetime.now() - edit_date

            # And the current time is between 12:55am and 2:00am,
            if time(0, 55) <= utc_time <= time(2, 0):
                # If the file is already updated, don't update it.
                if edit_diff < timedelta(hours=1):
                    print(f"{s} {f} is live, but data is already updated.")
                    return False
                # Otherwise, update the data.
                else:
                    print(f"{s} {f} is live, and new data should exist. Signaling update...")
                    return True


            # Or, if the file is over 24hrs old, update it.
            if edit_diff >= timedelta(days=1):
                # Signal for an update.
                print(f"{s} {f} is over 24hrs old. Signaling update...")
                return True

        # Otherwise, skip the update.
        return False


    if force or allow_update(s, f):
        save_card_data(s, f)



### Metagame Level Data ###

def fetch_meta_data():
    print(f'WARNING: fetch_meta_data not yet implemented.')    
    pass



### Master Functions ###

def update_format_data(s, f, force=False):
    #fetch_deck_data()
    update_card_data(s, f, force)
    #fetch_meta_data()


def update_all_data(force=False):
    for s in SETS:
        for f in FORMATS:
            update_format_data(s, f, force)


def load_format_data(s, f):
    # Load deck-level data.

    # Load card-level data.
    card_dict = load_card_data(s, f)
    if card_dict is not None:
        DATA_CACHE[s][f] = card_dict
        for c in COLOUR_GROUPS:
            PANDAS_CACHE[s][f][c] = panadafy_dict(card_dict[c])

    # Load meta-level data.


def load_all_data():
    for s in SETS:
        for f in FORMATS:
            load_format_data(s, f)



### File Init ###
def init():
    update_all_data()
    load_all_data()


init()
     
##s = SETS[0]
##f = FORMATS[0]
##            
##x = fetch_card_data_by_colour(s, f)
##update_all_data()
##
##x = load_card_data(s, f)
