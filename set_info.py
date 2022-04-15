import os
import json
import requests
from time import sleep
from datetime import date, time, datetime, timedelta
from WUBRG import MAIN_COLOUR_GROUPS

# TODO: Make this a json object which is routinely checked.
# This will enable format updates without having to completely recompile the bot.
SET_CONFIG = {
    "VOW": {
        "PremierDraft": {
            "Updating": True,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "TradDraft": {
            "Updating": True,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "QuickDraft": {
            "Updating": True,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "Sealed": {
            "Updating": True,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "TradSealed": {
            "Updating": True,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "DraftChallenge": {
            "Updating": False,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        }
    },
    "MID": {
        "PremierDraft": {
            "Updating": False,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "TradDraft": {
            "Updating": False,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "QuickDraft": {
            "Updating": False,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "Sealed": {
            "Updating": False,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "TradSealed": {
            "Updating": False,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "DraftChallenge": {
            "Updating": False,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        }
        # TODO: Consider adding in a list of key archetypes to reduce data footprint.
        # "KeyArchetypes" : ["U", "B", "WU", "WB", "UB", "UG", ""]
    },
    "AFR": {
        "PremierDraft": {
            "Updating": False,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "TradDraft": {
            "Updating": False,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "QuickDraft": {
            "Updating": False,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "Sealed": {
            "Updating": False,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "TradSealed": {
            "Updating": False,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        },
        "DraftChallenge": {
            "Updating": False,
            "StartDate": "yyyy-mm-dd",
            "EndDate": "yyyy-mm-dd"
        }
    }
}

SETS = ['MID', 'AFR']
FORMATS = ['PremierDraft', 'TradDraft', 'QuickDraft', 'Sealed', 'TradSealed', 'DraftChallenge']
SET_TREE = dict()
for s in SETS:
    SET_TREE[s] = dict()
    for f in FORMATS:
        SET_TREE[s][f] = None

START_DATE = '2021-01-01'
DATA_DIR = os.path.join(os.getcwd(), "17_lands_data")
FILENAME = '{0}_{1}.json'  # '{set}_{format}.json'
STAT_NAMES = [
    "seen_count",
    "avg_seen",
    "pick_count",
    "avg_pick",
    "game_count",
    "win_rate",
    "sideboard_game_count",
    "sideboard_win_rate",
    "opening_hand_game_count",
    "opening_hand_win_rate",
    "drawn_game_count",
    "drawn_win_rate",
    "ever_drawn_game_count",
    "ever_drawn_win_rate",
    "never_drawn_game_count",
    "never_drawn_win_rate",
    "drawn_improvement_win_rate"]

DATA_CACHE = dict()


def fetch_bot_data():
    # TODO: Fill this out to pull .config data to update the bot on the fly.
    pass


# - JSON Management
# Reads the json file for a given set and returns a dict which represent the cards.
def read_set_data(set_name, format_name):
    format_dict = {c: dict() for c in MAIN_COLOUR_GROUPS}
    filename = FILENAME.format(set_name, format_name)
    filepath = os.path.join(DATA_DIR, filename)
    print(f'Parsing {filename}...')

    try:
        with open(filepath, 'r') as format_name:
            json_str = format_name.read()
            format_name.close()

        format_dict = json.loads(json_str)
    except Exception:
        print(f'Error reading json file {filename}')

    return format_dict


# Automatically gets the overall data for cards, and the data for 1, 2 and 3 colour decks.
def save_set_data(set_name, format_name):
    json_out = dict()
    filename = FILENAME.format(set_name, format_name)

    # Query 17 lands for each colour filter.
    for c in MAIN_COLOUR_GROUPS:
        json_colour = fetch_format_data(set_name, format_name, c)
        json_out[c] = json_colour
        sleep(3)

    # Convert the aggregate dictionary into a .json file, and save it.
    try:
        filepath = os.path.join(DATA_DIR, filename)
        file = open(filepath, 'w')
        file.write(json.dumps(json_out))
        file.close()

        print(f'File {filename} created.')
    except Exception:
        print(f'Error creating {filename}!')


# - 17 Lands Querying
# Returns true is the data for a set format should be updated.
def to_update(set_name, format_name):
    # If the format is live,
    if SET_CONFIG[set_name][format_name]['Updating']:
        time_range_start = time(0, 55)
        time_range_end = time(2, 0)
        cur_date = datetime.utcnow()
        cur_time = cur_date.time()

        # And the current time is between 12:55am and 2:00am,
        if time_range_start <= cur_time <= time_range_end:
            # Signal for an update.
            print(f"{set_name} {format_name} is live, and new data should exist. Signaling update...")
            return True

        try:
            edit_date = datetime.fromtimestamp(os.path.getmtime(
                os.path.join(DATA_DIR, FILENAME.format(set_name, format_name)))
            )
        except Exception:
            # Should update if can't find file
            return True
        edit_diff = cur_date - edit_date
        # If the file is over 24hrs old, update it.
        if edit_diff >= timedelta(days=1):
            # Signal for an update.
            print(f"{set_name} {format_name} is over 24hrs old. Signaling update...")
            return True

    # Or if the format is dead, but the data doesn't exist.
    if not os.path.isfile(os.path.join(DATA_DIR, FILENAME.format(set_name, format_name))):
        # Signal for an update.
        print(f"{set_name} {format_name} doesn't exist. Signaling update...")
        return True

    # Skip the update.
    return False


# Fetches all the data for a given set and format, using an optional colour filter.
def fetch_format_data(set_name, format_name, c='None', start_date=None, end_date=None):
    success = False
    count = 0

    if c is None or c == 'None':
        c = 'No Filter'

    if start_date is None:
        start_date = START_DATE
    if end_date is None:
        end_date = date.today()

    url_base = 'https://www.17lands.com/card_ratings/data?'
    url_append = f'expansion={set_name}&format={format_name}&start_date={start_date}&end_date={end_date}'
    colour_filter = ''
    if c != 'No Filter':
        colour_filter = f'&colors={c}'
    url = url_base + url_append + colour_filter

    while not success:
        count += 1
        try:
            print(f'Fetching data for {set_name} {format_name} "{c}"...')
            response = requests.get(url)
            success = True
            print('Success!')
        except Exception:
            if count < 5:
                print('Failed; trying again in 30s')
                sleep(30)
                continue
            else:
                print(f'Failed to get data after 5 attempts. Could not get data for {url}')
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


# Fetch all the data for sets and formats, controlled by SET_CONFIG
def fetch_all_data():
    print(f'Checking for new format data...')
    update_dict = dict(SET_TREE)

    for set_name in SETS:
        for format_name in FORMATS:
            if to_update(set_name, format_name):
                update_dict[set_name][format_name] = True
                save_set_data(set_name, format_name)
                sleep(60)
            else:
                update_dict[set_name][format_name] = False
                print(f'{set_name} {format_name} data is up to date!')

    print(f'Done checking for new format data.\r\n')
    return update_dict


# - Cache Management
# Creates an empty cache structure for the card data.
def blank_cache():
    global DATA_CACHE
    new_cache = dict(SET_TREE)
    for set_name in SETS:
        for format_name in FORMATS:
            new_cache[set_name][format_name] = dict()

    DATA_CACHE = new_cache


# Updates the cards data cache with data from the .json files.
def update_cache(update_dict):
    print(f'Checking for cache updates...')

    global DATA_CACHE
    # Create a copy of the current cache to modify/
    new_cache = dict(DATA_CACHE)

    # For each format in the set, check for a go-ahead to refresh the data.
    for set_name in SETS:
        for format_name in FORMATS:
            if update_dict[set_name][format_name]:
                # If allowed, get the data from the json file, and add it to the temp cache.
                format_dict = read_set_data(set_name, format_name)
                new_cache[set_name][format_name] = format_dict
                print(f'{set_name} {format_name} added to DATA_CACHE!')

    # Overwrite the main cache with the temp cache.
    DATA_CACHE = new_cache
    print(f'Done checking for cache updates.\r\n')


def init_cache():
    # Update all data.
    fetch_all_data()

    # Create a blank cache.
    blank_cache()

    # Create an update dict which update the entire cache.
    update_dict = dict(SET_TREE)
    for set_name in SETS:
        for format_name in FORMATS:
            update_dict[set_name][format_name] = True

    # And update the cache.
    update_cache(update_dict)


def query_cache(_set, _format, color_filter, card_name):
    if _set not in DATA_CACHE:
        return None
    if _format not in DATA_CACHE[_set]:
        return None
    if color_filter not in DATA_CACHE[_set][_format]:
        return None
    if card_name not in DATA_CACHE[_set][_format][color_filter]:
        return None
    return DATA_CACHE[_set][_format][color_filter][card_name]


if __name__ == "__main__":
    init_cache()
    pass
