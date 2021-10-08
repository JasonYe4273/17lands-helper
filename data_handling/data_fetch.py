import os
import requests
from time import sleep
from datetime import date, time, datetime, timedelta
import pandas as pd

from global_vals import settings
from global_vals.settings import DATA_DIR, CARD_DATA_FILENAME, RARITY_ALIASES, STAT_NAMES
from global_vals.WUBRG import *
from global_vals.utils import *
from global_vals.structs import *
import data_handling.data_cache as cache


# Make an HTTP request to a given url for json data.
# 'tries' limits the number of attempts made to get data.
# 'delay' sets the number of seconds before retrying on a fail.
# On success returns a json object, otherwise None
def fetch(url, tries=5, delay=60):
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


# region Deck Level Data
def fetch_deck_data():
    print(f'WARNING: fetch_deck_data not yet implemented.')
    pass
# endregion Deck Level Data


# region Card Level Data
# Query scryfall to get information on a card based on its name.
def get_scryfall_data(raw_cardname):
    card_info = gen_card_info_struct()
    
    try:
        response = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={raw_cardname}').json()
        if response['object'] == 'error':
            if response['details'][:20] == 'Too many cards match':
                card_info['err_msg'] = f'Error: Multiple card matches for "{raw_cardname}"'
            else:
                card_info['err_msg'] = f'Error: Cannot find card "{raw_cardname}"'
        elif response['object'] != 'card':
            card_info['err_msg'] = f'Error: "{raw_cardname}" returned non-card'
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
        card_info['err_msg'] = f'Error querying Scryfall for {raw_cardname}'

    return card_info


# Query 17 lands for data about a particular colour group for a set and format.
def fetch_card_data_by_colour(s, f, c = ''):
    # Manage params
    start_date = settings.SET_CONFIG[s][f]['StartDate']
    if start_date is None:
        start_date = settings.DEFAULT_START_DATE
        
    end_date = settings.SET_CONFIG[s][f]['EndDate']
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


# Query 17 lands for all data about a particular set and format.
def fetch_card_data(s, f, delay = 5):
    card_data = dict()

    # Query 17 lands for each colour filter.
    for c in COLOR_GROUPS:
        card_data[c] = fetch_card_data_by_colour(s, f, c)
        sleep(delay)

    print(f"Fetched card data for {s} {f}!")
    return card_data


# Convert the dictionary of card data into a .json file, and save it.
def save_card_data(s, f):
    card_data = fetch_card_data(s, f)
    filename = CARD_DATA_FILENAME.format(s, f)
    return save_json_file(DATA_DIR, filename, card_data)


# Load the dictionary of card data from a .json file, and parse it.
def load_card_data(s: str, f: str) -> bool:
    """
    Attempts to read card data from a saved file, and load it into the cache.
    :param s: The set name
    :param f: The format name
    :return: Whether the load was successful.
    """
    filename = CARD_DATA_FILENAME.format(s, f)
    card_dict = load_json_file(DATA_DIR, filename)
    if card_dict is not None:
        cache.set_cache(card_dict, s, f)
        for c in COLOR_GROUPS:
            cache.set_frames(panadafy_dict(card_dict[c]), s, f, c)
        return True
    else:
        return False


# Attempt to update card data for a set and format.
# Will only update the data under certain conditions to reduce load on
# the 17-lands website.
# Can optionally force the data to update.
def update_card_data(s, f, force = False):
    def allow_update():
        filepath = os.path.join(DATA_DIR, CARD_DATA_FILENAME.format(s, f))
        
        # If the data doesn't exist,
        if not os.path.isfile(filepath):
            # Signal for an update.
            print(f"{s} {f} doesn't exist. Signaling update...")
            return True
        
        # Or, if the format is live,
        # TODO: Manage set config so it's more fail-safe.
        if settings.SET_CONFIG[s][f]['Updating']:
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

    if force or allow_update():
        return save_card_data(s, f)
    else:
        return False
# endregion Card Level Data


### Metagame Level Data ###

def fetch_meta_data():
    print(f'WARNING: fetch_meta_data not yet implemented.')    
    pass



### Master Functions ###

def refresh_deck_level_data(force=False):
    print(f'WARNING: refresh_deck_level_data not yet implemented.')  
    pass


# Attempts to update the card-level data for all sets and formats.
# Can optionally force an update, but this should almost never be done.
# TODO: Rename to update_all_card_level_data
def refresh_card_level_data(force=False):
    updated = cache.get_set_tree_struct()
    for s in settings.SETS:
        for f in settings.FORMATS:
            updated[s][f] = False
            success = update_card_data(s, f, force)
            if success or not cache.query_frames(s, f):
                updated[s][f] = load_card_data(s, f)
    return updated


def refresh_meta_level_data(force=False):
    print(f'WARNING: refresh_meta_level_data not yet implemented.')  
    pass


# Update all data surround a format from a specific set.
# Can optionally force an update, but this should almost never be done.
def update_format_data(s, f, force=False):
    #fetch_deck_data()
    update_card_data(s, f, force)
    #fetch_meta_data()


# Update all data surrounding limited formats.
# Can optionally force an update, but this should likely never be done.
def update_all_data(force=False):
    for s in settings.SETS:
        for f in settings.FORMATS:
            update_format_data(s, f, force)


# Loads data for a specific set and format into the cache.
def load_format_data(s, f):
    # Load deck-level data.
    load_card_data(s, f)
    # Load meta-level data.


# Loads all data from saved files into the cache.
def load_all_data():
    for s in settings.SETS:
        for f in settings.FORMATS:
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
