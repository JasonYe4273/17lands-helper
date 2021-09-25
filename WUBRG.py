import discord

MANAMOJIS = []
def cache_manamojis(client):
    global MANAMOJIS
    MANAMOJIS = [emo for emo in client.emojis if emo.name.startswith('mana')]
    # TODO: Add in support for set symbols.
    #SETMOJIS = [emo for emo in client.emojis if emo.name.startswith('set')]
    print(f'{len(MANAMOJIS)} manamojis found!')

### Colour Mapping ###
# Groupings of colour-sets supported.
COLOR_ALIASES_SUPPORT = {
    'Colors': {
        'White' : "W",
         'Blue' : "U",
         'Black' : "B",
         'Red' : "R",
         'Green' : "G"
    },
    'Guilds' : {
        'Azorius' : "WU", 
         'Orzhov' : "WB", 
         'Boros' : "WR",
         'Selesnya' : "WG",
         'Dimir' : "UB",
         'Izzet' : "UR",
         'Simic' : "UG",
         'Rakdos' : "BR",
         'Golgari' : "BG",
         'Gruul' : "RG"
    },
    'Colleges' : {
        'Silverquill' : "WB", 
         'Lorehold' : "WR",
         'Prismari' : "UR",
         'Quandrix' : "UG",
         'Witherbloom' : "BG"
    },
    'Wedges' : {
        'Jeksai' : "WUR",
         'Mardu' : "WBR",
         'Abzan' : "WBG",
         'Sultai' : "UBG",
         'Temur' : "URG"
    },
    'Triomes' : {
        'Raugrin' : "WUR",
         'Savai' : "WBR",
         'Indatha' : "WBG",
         'Zagoth' : "UBG",
         'Ketria' : "URG"
    },
    'Shards' : {
        'Esper' : "WUB",
         'Bant' : "WUG",
         'Naya' : "WRG",
         'Grixis' : "UBR",
         'Jund' : "BRG"
    }
}

COLOUR_GROUPINGS = {
    'Mono-Color': ['White', 'Blue', 'Black', 'Red', 'Green'],
    'Two-Color': ['Azorius', 'Orzhov', 'Boros', 'Selesnya', 'Dimir', 'Izzet', 'Simic', 'Rakdos', 'Golgari', 'Gruul'],
    'Three-Color': ['Jeksai', 'Mardu', 'Abzan', 'Sultai', 'Temur', 'Esper', 'Bant', 'Naya', 'Grixis', 'Jund']
}


# Merging all of the supported colour-sets.
COLOR_ALIASES = {'All' : "WUBRGC", 'None' : ""}
for d in COLOR_ALIASES_SUPPORT:
    COLOR_ALIASES = COLOR_ALIASES | COLOR_ALIASES_SUPPORT[d]


def get_color_string(s):
    s = s.upper()

    if s.title() in COLOR_ALIASES:
        s = COLOR_ALIASES[s.title()]

    #validate the string
    valid_chars = set(COLOR_ALIASES['All'])
    char_set = set(s)
    remainder = char_set - valid_chars

    if (len(remainder) > 0):
        print(f'Invalid color string provded: {s}. Converting to "WUBRGC"')
        s = "WUBRGC"
    
    return s


def get_color_map(color_str):
    s = get_color_string(color_str)
    colors_exist = {'W': False,
                    'U': False,
                    'B': False,
                    'R': False,
                    'G': False,
                    'C': False}

    for c in s:
        colors_exist[c] = True

    return colors_exist



### Emojis ###
# To automatically grab server emojis installed from
# https://github.com/scryfall/manamoji-discord/tree/main/emojis
def get_emoji(emoji_str):
    # Format and convert the emoji trying to be found.
    # EG: 'W' gets converted to 'w', and then 'manaw'.
    emoji_str = emoji_str.lower()
    
    manamoji_str = emoji_str
    if not manamoji_str.startswith('mana'):
        manamoji_str = 'mana' + manamoji_str

    setmoji_str = emoji_str
    if not setmoji_str.startswith('set'):
        setmoji_str = 'set' + setmoji_str
        
    
    manamojis = [emo for emo in MANAMOJIS if emo.name == manamoji_str]

    if (len(manamojis) != 1):
        print(f'Found {len(manamojis)} for string: {emoji_str}')
        return ''
    else:
        return str(manamojis[0])

def parse_cost(mana_cost):
    # Parse the mana cost from the {1}{W}{B} format into a list of strings.
    return [char for char in mana_cost]
    pass

def emojify_mana_cost(mana_cost):
    mana_cost = parse_cost(mana_cost)
    cost = ""
    for sym in mana_cost:
        cost += get_emoji(sym)
    return cost

def emojify_color_id(mana_cost):
    mana_cost = parse_cost(mana_cost)
    pips = ['W', 'U', 'B', 'R', 'G', 'C']
    cost = ""
    for sym in pips:
        if sym not in mana_cost:
            continue
        cost += get_emoji(sym)
    return cost
