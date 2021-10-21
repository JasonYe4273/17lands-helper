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


def fetch(url: str, tries: int = 5, delay: int = 60) -> object:
    """
    Attempts to get json data from a url.
    :param url: The url to get data from
    :param tries: The maximum number of attempts to make
    :param delay: The delay to wait between failed tries
    :return: A json object or None
    """
    success = False
    count = 0
    
    while not success:
        count += 1

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
                print(f'Failed to get data after {tries} attempts.')
                return None


def get_scryfall_set_card_list(set_name: str) -> dict:
    # TODO: Get the list of cards in a set from scryfall
    pass


def update_card_list_cache(set_name: str) -> dict:
    # TODO: Populate the CARD_LIST_CACHE with set card lists.
    pass


def panadafy_dict(card_dict: dict) -> pd.DataFrame:
    """
    Turns a dictionary into a DataFrame, with some data cleaning applied.
    :param card_dict: The dictionary containing card data for a colour group
    :return: A DataFrame filled with the cleaned card data
    """
    if card_dict is None:
        print('Warning: Dict for pandafying is null.')
    
    frame = pd.DataFrame.from_dict(card_dict, orient='index')
    frame = frame.rename(columns=STAT_NAMES)
    
    # If there's no data, make a blank frame and return it.
    if len(card_dict) == 0:
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
def get_scryfall_card_data(raw_card_name: str) -> dict:
    """
    Gets card data from scryfall based on a name. Scryfall's fuzzy filter is
    used to handle imprecise queries and spelling errors.
    :param raw_card_name: The card name provided by a user
    :return: A card info struct which contains card data, and an error
    message if a problem occurred.
    """
    card_info = gen_card_info_struct()

    try:
        response = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={raw_card_name}').json()

        # If the response has an error use that error to generate a description of the problem.
        if response['object'] == 'error':
            if response['details'][:20] == 'Too many cards match':
                card_info['err_msg'] = f'Error: Multiple card matches for "{raw_card_name}"'
            else:
                card_info['err_msg'] = f'Error: Cannot find card "{raw_card_name}"'
        # If the search return a non-card, add that as the error message.
        elif response['object'] != 'card':
            card_info['err_msg'] = f'Error: "{raw_card_name}" returned non-card'
        # Otherwise, get the relevant card info and populate the card_info_struct
        else:
            card = response
            card_info['name'] = card['name']
            card_info['stored_name'] = get_card_name(card)
            card_info['cmc'] = card['cmc']
            card_info['color_identity'] = get_color_identity(''.join(card['color_identity']))
            card_info['id'] = card['id']
            card_info['url'] = card['scryfall_uri']
            # Ignore promo sets, changing them to the standard set.
            if card['set_type'] == 'promo':
                card_info['set'] = card['set'][1:].upper()
            else:
                card_info['set'] = card['set'].upper()

            # TODO: Determine the set from the CARD_LIST_CACHE
            # card_info['set'] = query_card_list_cache(card['name'])

            if 'card_faces' in card:
                card_info['mana_cost'] = parse_cost(card['card_faces'][0]['mana_cost'])
                # card_info['colors'] = card['card_faces'][0]['colors'] + card['card_faces'][1]['colors']
            else:
                card_info['mana_cost'] = parse_cost(card['mana_cost'])
                # card_info['colors'] = WUBRG.get_color_identity(''.join(card['colors']))
    # If and exception occurs, print it, and add an error massage to the struct.
    except Exception as ex:
        print(ex)
        card_info['err_msg'] = f'Error querying Scryfall for {raw_card_name}'

    return card_info


def fetch_card_data_by_colour(s: str, f: str, c: str = None, start_date: str = None, end_date: str = None) -> dict:
    """
    Queries 17Lands.com for data about card performance of a given set, format
    and colour group, with optional start and end date.
    :param s: The set name
    :param f: The format name
    :param c: The colour identity
    :param start_date: The start date of the data to get
    :param end_date: The end date of the data to get
    :return: A dictionary of card data.
    """
    # Manage params
    if start_date is None:
        start_date = settings.SET_CONFIG[s][f]['StartDate']
    if start_date is None:
        start_date = settings.DEFAULT_START_DATE

    if end_date is None:
        end_date = settings.SET_CONFIG[s][f]['EndDate']
    if end_date is None:
        end_date = date.today()
    
    if c is None or c == '':
        c = 'No Filter'

    # Generate the url
    url_base = 'https://www.17lands.com/card_ratings/data?'
    url_append = f'expansion={s}&format={f}&start_date={start_date}&end_date={end_date}'
    colour_filter = '' if c == 'No Filter' else f'&colors={c}'
    url = url_base + url_append + colour_filter
    print(f"Fetching data for {s} {f}, filter: '{c}'...")

    # Fetch card-level data.
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


def fetch_card_data(s: str, f: str, delay: int = 5) -> dict:
    """
    Queries 17Lands.com for data about card performance across a particular set and format
    :param s: The set name
    :param f: The format name
    :param delay: The delay between attempts to get data for a colour group
    :return: A dictionary of card data.
    """
    card_data = dict()

    # Query 17 lands for each colour filter.
    for c in COLOR_GROUPS:
        card_data[c] = fetch_card_data_by_colour(s, f, c)
        sleep(delay)

    print(f"Fetched card data for {s} {f}!")
    return card_data


def save_card_data(s: str, f: str) -> bool:
    """
    Convert the dictionary of card data into a .json file, and save it.
    :param s: The set name
    :param f: The format name
    :return: Whether the file save successfully
    """
    card_data = fetch_card_data(s, f)
    filename = CARD_DATA_FILENAME.format(s, f)
    return save_json_file(DATA_DIR, filename, card_data)


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
        cache.set_dict_cache_value(card_dict, s, f)
        for c in COLOR_GROUPS:
            cache.set_frames_cache_value(panadafy_dict(card_dict[c]), s, f, c)
        return True
    else:
        return False


def update_card_data(s, f, force=False):
    """
    Attempts to update the data for a particular set and format, but only if needed.
    Can forcibly update the data.
    :param s: The set name
    :param f: The format name
    :param force: Forcibly update the data
    :return: If the data updated successfully
    """
    def allow_update():
        """
        Performs various checks to determine if new data should be fetched.
        :return: Whether the format data should be updated.
        """
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


# Metagame Level Data

def fetch_meta_data():
    print(f'WARNING: fetch_meta_data not yet implemented.')    
    pass


# Master Functions
def refresh_deck_level_data(force=False):
    print(f'WARNING: refresh_deck_level_data not yet implemented.')  
    pass


# Attempts to update the card-level data for all sets and formats.
# Can optionally force an update, but this should almost never be done.
def update_all_card_level_data(force=False):
    updated = cache.get_set_tree_struct()
    for s in settings.SETS:
        for f in settings.FORMATS:
            updated[s][f] = False
            success = update_card_data(s, f, force)
            if success or not cache.query_frames_cache(s, f):
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


# File Init
def init():
    update_all_data()
    load_all_data()


init()
