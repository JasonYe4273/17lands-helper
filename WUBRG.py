try:
    import discord
except:
    print("WRANING: 'discord' failed to import. Emoji support unavailable")

# Used to populate the emojis which represent mana costs and set symbols.
# Note, not calling this means no emojis will be found, and embeds will be emojiless.
MANAMOJIS = []
SETMOJIS = []
def cache_manamojis(client):
    global MANAMOJIS
    MANAMOJIS = [emo for emo in client.emojis if emo.name.startswith('mana')]
    print(f'{len(MANAMOJIS)} manamojis found!')
    
    # TODO: Add in support for set symbols.
    #global SETMOJIS
    #SETMOJIS = [emo for emo in client.emojis if emo.name.startswith('set')]
    #print(f'{len(SETMOJIS)} setmojis found!')



### Colour Mapping ###
COLORS = "WUBRG"

    
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
    },
    'Nephillim' : {
        'Yore' : "WUBR",
         'Witch' : "WUBG",
         'Ink' : "WURG",
         'Dune' : "WBRG",
         'Glint' : "UBRG"
    }
}


# Merging all of the supported colour-sets.
COLOR_ALIASES = {
    '5-Color' : "WUBRG",
    'All' : "WUBRGC",
    'None' : ""
}

for d in COLOR_ALIASES_SUPPORT:
    #COLOR_ALIASES = COLOR_ALIASES | COLOR_ALIASES_SUPPORT[d]
    COLOR_ALIASES = {**COLOR_ALIASES, **COLOR_ALIASES_SUPPORT[d]}


# Lists of alais based on the number of colours.
COLOUR_GROUPINGS = {
    'Mono-Color': COLOR_ALIASES_SUPPORT['Colors'],
    'Two-Color': COLOR_ALIASES_SUPPORT['Guilds'],
    #'Three-Color': COLOR_ALIASES_SUPPORT['Wedges'] | COLOR_ALIASES_SUPPORT['Shards'],
    'Three-Color': {**COLOR_ALIASES_SUPPORT['Wedges'], **COLOR_ALIASES_SUPPORT['Shards']},
    'Four-Color': COLOR_ALIASES_SUPPORT['Nephillim'],
}


COLOUR_GROUPS = [''] # Filled below


# Takes in a string, and attempts to convert it to a color_string.
# If the string is invalid, returns 'WUBRGC'.
def get_color_string(s):
    s = s.upper()

    if s.title() in COLOR_ALIASES:
        s = COLOR_ALIASES[s.title()]

    # Validate the string by using the set difference
    valid_chars = set(COLOR_ALIASES['All'])
    char_set = set(s)
    remainder = char_set - valid_chars

    if (len(remainder) > 0):
        print(f'Invalid color string provded: {s}. Converting to "WUBRGC"')
        s = "WUBRGC"

    return s


def get_color_identity(color_string):
    char_set = set(color_string)
    s = ''
    for c in COLOR_ALIASES['All']:
        if c in char_set:
            s += c
    return s


def get_color_alias(color_string):
    color_identity = get_color_identity(color_string)
    if color_identity == 'WUBRG':
        return '5-Colour'
    elif color_identity == 'All':
        return ''

    
    for g in COLOUR_GROUPINGS:
        for c in COLOUR_GROUPINGS[g]:
            if color_identity == get_color_string(c):
                alias = c
                if len(color_identity) == 1:
                    alias = 'Mono-' + alias
                return alias
    
    

COLOUR_GROUPS = [''] + [get_color_string(y) for x in COLOUR_GROUPINGS for y in COLOUR_GROUPINGS[x]] + ['WUBRG']
    

# Takes in a valid colour string, or colour string alias,
# and then returns a dictionary of booleans.
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

    if len(manamojis) > 0:
        return str(manamojis[0])
    else:
        return ""

# NOTE: Imcomplete
# Parses a string mana cost into a list of mana 'elements', while converting
# from 'curly-brace' format or plain-text format to our list format.
# Eg. {10}{G}{G} would return ['10', 'G', 'G']
# Eg. 10GG would return ['1', '0', 'G', 'G'], which is likely not what's wanted.
def parse_cost(mana_cost):
    # TODO: Parse the mana cost from the {1}{W}{B} format into a list of strings.
    return [char for char in mana_cost]
    pass

# Takes a mana cost and attempts to return a string of emojis which
# represent that mana cost, as it would look on the card.
def emojify_mana_cost(mana_cost):
    if mana_cost is None:
        return ""
    mana_cost = parse_cost(mana_cost)
    cost = ""
    for sym in mana_cost:
        cost += get_emoji(sym)
    return cost

# Takes a mana cost and attempts to return a string of emojis which
# represent that teh colours contained in that card.
# NOTE: Not a true colour_id, potentially worth renaming.
def emojify_color_id(mana_cost):
    if mana_cost is None:
        return ""
    mana_cost = parse_cost(mana_cost)
    pips = ['W', 'U', 'B', 'R', 'G', 'C']
    cost = ""
    for sym in pips:
        if sym not in mana_cost:
            continue
        cost += get_emoji(sym)
    return cost
