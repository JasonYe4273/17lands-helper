### Parsing Consts ###
COMMAND_STR = '17!'
DATA_QUERY_L = '{{'
DATA_QUERY_R = '}}'
DATA_QUERY_MID = '|'
DEFAULT_FORMAT = 'PremierDraft'
START_DATE = '2019-01-01'
QUOTE_PAIRS = {'"': '"', '“': '”'}



### File Consts ###
DATA_DIR = os.path.join(os.getcwd(), "17_lands_data")
CONFIG_DIR = os.path.join(os.getcwd(), "config")
CARD_DATA_FILENAME  = '{0}_{1}.json'



### Set Consts ###
FORMAT_NICKNAMES = {
    'PremierDraft': 'Bo1',
    'TradDraft': 'Bo3',
    'QuickDraft': 'Quick',
    'Sealed': 'Seal',
    'TradSealed': 'Bo3Seal',
    'DraftChallenge': 'Chal.',
}

FORMATS = {
    'PremierDraft': ['bo1', 'premier', 'premierdraft'],
    'TradDraft': ['bo3', 'trad', 'traditional', 'traddraft', 'traditionaldraft'],
    'QuickDraft': ['qd', 'quick', 'quickdraft'],
    'Sealed': ['sealed', 'bo1sealed', 'sealedbo1'],
    'TradSealed': ['tradsealed', 'bo3sealed', 'sealedbo3'],
    'DraftChallenge': ['challenge', 'draftchallenge'],
}






### Card Consts ###
RARITY_ALIASES = {
    'common': "C",
    'uncommon': "U",
    'rare': "R",
    'mythic': "M"
}




### Stat Consts ###
DATA_COMMANDS = {
    'alsa': [('seen_count', '# Seen', True), ('avg_seen', 'ALSA', False)],
    'ata': [('pick_count', '# Taken', True), ('avg_pick', 'ATA', False)],
    'gp': [('game_count', '# GP', True), ('win_rate', 'GP WR', False)],
    'oh': [('opening_hand_game_count', '# OH', True), ('opening_hand_win_rate', 'OH WR', False)],
    'gd': [('drawn_game_count', '# GD', True), ('drawn_win_rate', 'GD WR', False)],
    'gih': [('ever_drawn_game_count', '# GIH', True), ('ever_drawn_win_rate', 'GIH WR', False)],
    'gnd': [('never_drawn_game_count', '# GND', True), ('never_drawn_win_rate', 'GND WR', False)],
    'iwd': [('drawn_improvement_win_rate', 'IWD', False)]
}
DATA_COMMANDS['drafts'] = DATA_COMMANDS['alsa'] + DATA_COMMANDS['ata']
DATA_COMMANDS['games'] = DATA_COMMANDS['gp'] + DATA_COMMANDS['oh'] + DATA_COMMANDS['gd'] + DATA_COMMANDS['gih'] + DATA_COMMANDS['gnd'] + DATA_COMMANDS['iwd']
DATA_COMMANDS['data'] = DATA_COMMANDS['drafts'] + DATA_COMMANDS['games']

FORMAT_MAPPING = {}
for f in FORMATS:
    for s in FORMATS[f]:
        FORMAT_MAPPING[s] = f


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
COLUMNS_TRUNC = ["Color", "Rarity", "ALSA", "# GP", "GP WR", "# GIH", "GIH WR"]

