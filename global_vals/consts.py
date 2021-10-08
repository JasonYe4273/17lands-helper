import os
import pathlib

root = pathlib.Path(__file__).parent.parent.resolve()

# File Consts
DATA_DIR = os.path.join(root, "17_lands_data")
print(f"'DATA_DIR': {DATA_DIR}")

CONFIG_DIR = os.path.join(root, "config")
print(f"'CONFIG_DIR': {CONFIG_DIR}")

CARD_DATA_FILENAME = 'CARD_DATA_{0}_{1}.json'
print(f"'CARD_DATA_FILENAME': {CARD_DATA_FILENAME}")

# Parsing Consts
COMMAND_STR = '17!'
DATA_QUERY_L = '{{'
DATA_QUERY_R = '}}'
DATA_QUERY_MID = '|'
QUOTE_PAIRS = {'"': '"', '“': '”'}

# Card Consts
RARITY_ALIASES = {
    'common': "C",
    'uncommon': "U",
    'rare': "R",
    'mythic': "M"
}

# Set Consts
FORMAT_NICKNAMES = {
    'PremierDraft': 'Bo1',
    'TradDraft': 'Bo3',
    'QuickDraft': 'Quick',
    'Sealed': 'Seal',
    'TradSealed': 'Bo3Seal',
    'DraftChallenge': 'Chal.',
}

FORMAT_ALIAS_LISTS = {
    "PremierDraft": ["bo1", "premier", "premierdraft"],
    "TradDraft": ["bo3", "trad", "traditional", "traddraft", "traditionaldraft"],
    "QuickDraft": ["qd", "quick", "quickdraft"],
    "Sealed": ["sealed", "bo1sealed", "sealedbo1"],
    "TradSealed": ["tradsealed", "bo3sealed", "sealedbo3"],
    "DraftChallenge": ["challenge", "draftchallenge"]
}

FORMAT_MAPPINGS = dict()
for f in FORMAT_ALIAS_LISTS:
    for s in FORMAT_ALIAS_LISTS[f]:
        FORMAT_MAPPINGS[s] = f

# Stat Consts
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
DATA_COMMANDS['games'] = DATA_COMMANDS['gp'] + DATA_COMMANDS['oh'] + DATA_COMMANDS['gd'] + DATA_COMMANDS['gih'] + \
                         DATA_COMMANDS['gnd'] + DATA_COMMANDS['iwd']
DATA_COMMANDS['data'] = DATA_COMMANDS['drafts'] + DATA_COMMANDS['games']

STAT_NAMES = {
    "color": "Color",
    "rarity": "Rarity",
    "seen_count": "# Seen",
    "avg_seen": "ALSA",
    "pick_count": "# Picked",
    "avg_pick": "ATA",
    "game_count": "# GP",
    "win_rate": "GP WR",
    "opening_hand_game_count": "# OH",
    "opening_hand_win_rate": "OH WR",
    "drawn_game_count": "# GD",
    "drawn_win_rate": "GD WR",
    "ever_drawn_game_count": "# GIH",
    "ever_drawn_win_rate": "GIH WR",
    "never_drawn_game_count": "# GND",
    "never_drawn_win_rate": "GND WR",
    "drawn_improvement_win_rate": "IWD"
}

STAT_FORMAT_STRINGS = {
    "Name": "`{:<20}`",
    "Color": "`{:^6}`",
    "Rarity": "`{:^6}`",
    "# Seen": "`{:>6.0f}`",
    "ALSA": "`{:^6.2f}`",
    "# Picked": "`{:>6.0f}`",
    "ATA": "`{:^6.2f}`",
    "# GP": "`{:>6.0f}`",
    "GP WR": "`{:5.2f}%`",
    "# OH": "`{:>6.0f}`",
    "OH WR": "`{:5.2f}%`",
    "# GD": "`{:>6.0f}`",
    "GD WR": "`{:5.2f}%`",
    "# GIH": "`{:>6.0f}`",
    "GIH WR": "`{:5.2f}%`",
    "# GND": "`{:>6.0f}`",
    "GND WR": "`{:5.2f}%`",
    "IWD": "`{:5.2f}%`"
}

PERCENT_COLUMNS = ["GP WR", "OH WR", "GD WR", "GIH WR", "GND WR", "IWD"]
