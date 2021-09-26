import os
import json
import requests
import time
from datetime import date, datetime, timedelta
import WUBRG
from WUBRG import COLOUR_GROUPINGS

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

SETS = ['MID', 'AFR']
FORMATS = ['PremierDraft', 'TradDraft']
#FORMATS = ['PremierDraft', 'TradDraft', 'QuickDraft', 'Sealed', 'TradSealed', 'DraftChallenge']
START_DATE = '2021-01-01'
DATA_DIR = os.path.join(os.getcwd(), "17_lands_data")
FILENAME = '{0}_{1}.json'  #'{set}_{format}.json'
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

FORMAT_ALIASES = {
    'PremierDraft': ['bo1', 'premier', 'premierdraft'],
    'TradDraft': ['bo3', 'trad', 'traditional', 'traddraft', 'traditionaldraft']
    # 'QuickDraft': ['qd', 'quick', 'quickdraft'],
    # 'Sealed': ['sealed', 'bo1sealed', 'sealedbo1'],
    # 'TradSealed': ['tradsealed', 'bo3sealed', 'sealedbo3'],
    # 'DraftChallenge': ['challenge', 'draftchallenge'],
}

FORMAT_MAPPING = {}
for f in FORMATS:
    for s in FORMAT_ALIASES[f]:
        FORMAT_MAPPING[s] = f

DATA_COMMANDS = {
    'alsa': [('seen_count', '# Seen', True), ('avg_seen', 'ALSA', False)],
    'ata': [('pick_count', '# Taken', True), ('avg_pick', 'ATA', False)],
    'gp': [('game_count', '# GP', True), ('win_rate', 'GP WR', False)],
    'gnp': [('sideboard_game_count', '# GNP', True), ('sideboard_win_rate', 'GNP WR', False)],
    'oh': [('opening_hand_game_count', '# OH', True), ('opening_hand_win_rate', 'OH WR', False)],
    'gd': [('drawn_game_count', '# GD', True), ('drawn_win_rate', 'GD WR', False)],
    'gih': [('ever_drawn_game_count', '# GIH', True), ('ever_drawn_win_rate', 'GIH WR', False)],
    'gnd': [('never_drawn_game_count', '# GND', True), ('never_drawn_win_rate', 'GND WR', False)],
    'iwd': [('drawn_improvement_win_rate', 'IWD', False)]
}
DATA_COMMANDS['drafts'] = DATA_COMMANDS['alsa'] + DATA_COMMANDS['ata']
DATA_COMMANDS['games'] = DATA_COMMANDS['gp'] + DATA_COMMANDS['gnp'] + DATA_COMMANDS['oh'] + DATA_COMMANDS['gd'] + DATA_COMMANDS['gih'] + DATA_COMMANDS['gnd'] + DATA_COMMANDS['iwd']
DATA_COMMANDS['data'] = DATA_COMMANDS['drafts'] + DATA_COMMANDS['games']


def fetch_bot_data():
    # TODO: Fill this out to pull .config data to update the bot on the fly.
    pass


# Fetches all the data for a given set and format.
# NOTE: Automaticall gets the overall data for cards, and the data for 1, 2 and 3 colour decks.
def fetch_format_data(s, f):
    relevant_colour_groups = ['All'] + [WUBRG.get_color_string(y) for x in COLOUR_GROUPINGS for y in COLOUR_GROUPINGS[x]]
    json_out = dict()
    filename = FILENAME.format(s, f)

    # Query 17 lands for each colour filter.
    for c in relevant_colour_groups:
        success = False
        count = 0
        
        while not success:
            count += 1
            response = None
            
            try:
                url_base = 'https://www.17lands.com/card_ratings/data?'
                url_append = f'expansion={s}&format={f}&start_date={START_DATE}&end_date={date.today()}'
                colour_filter = ''
                if c != 'All':
                    colour_filter = f'&colors={c}'
                url = url_base + url_append + colour_filter
                print(f'Fetching data for {s} {f} {c}...')
                response = requests.get(url)
                
                success = True
                print('Success!')
            except:
                if count < 5:
                    print('Failed; trying again in 30s')
                    time.sleep(30)
                    continue
                else:
                    print(f'Failed to get data after 5 attempts. File {filename} not created')

            # Pump the query results into a dict, tagged with the colour filter,
            # trimming data like image, name etc.
            json_colour = dict()
            for card in response.json():
                card_info = dict()
                for stat in STAT_NAMES:
                    card_info[stat] = card[stat]
                json_colour[card['name']] = card_info
            json_out[c] = json_colour
            time.sleep(3)
            

    # Convert the aggreate dictionary into a .json file, and save it.       
    json_str = json.dumps(json_out)
    try:
        filepath = os.path.join(DATA_DIR, filename);
        file = open(filepath, 'w')
        file.write(json_str)
        file.close()
        
        print(f'File {filename} created.')
    except Exception as ex:
        print(f'Error creating {filename}!')
        return


def do_update(s, f):
    # Update if the format is live.
    if SET_CONFIG[s][f]['Updating']:
        # TODO: Add in validation so the data only updates once a
        # day, at around 1am UTC.
        return True

    # Update if the format is dead, but the data doesn't exist.
    if not os.path.isfile(os.path.join(DATA_DIR, FILENAME.format(s, f))):
        return True

    return False
    

# Fetch all the data for sets and fomats, controlled by SET_CONFIG
def fetch_all_data():    
    for s in SETS:
        for f in FORMATS:
            if do_update(s, f):
                fetch_format_data(s, f)
                time.sleep(10)
            else:
                print(f'{s} {f} data is up to date!')


if __name__ == "__main__":
    fetch_all_data()
##    end_date = datetime.utcnow()
##    print(end_date)
##    start_date = end_date - timedelta(days=2)
##    print(start_date)
##    if start_date < end_date:
##        print("Test")
    pass
