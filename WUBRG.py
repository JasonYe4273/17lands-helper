# Used to populate the emojis which represent mana costs and set symbols.
# Note, not calling this means no emojis will be found, and embeds will be emoji-less.
MANAMOJIS: list = []
SETMOJIS: list = []


def cache_manamojis(client) -> None:
    global MANAMOJIS
    MANAMOJIS = [emo for emo in client.emojis if emo.name.startswith('mana')]
    print(f'{len(MANAMOJIS)} manamojis found!')

    # TODO: Add in support for set symbols.
    # global SETMOJIS
    # SETMOJIS = [emo for emo in client.emojis if emo.name.startswith('set')]
    # print(f'{len(SETMOJIS)} setmojis found!')


# - Colour Mapping ###
# Groupings of colour-sets supported.
COLOR_ALIASES_SUPPORT: dict[str, dict[str, str]] = {
    'Colors': {
        'White': "W",
        'Blue': "U",
        'Black': "B",
        'Red': "R",
        'Green': "G"
    },
    'Guilds': {
        'Azorius': "WU",
        'Orzhov': "WB",
        'Boros': "WR",
        'Selesnya': "WG",
        'Dimir': "UB",
        'Izzet': "UR",
        'Simic': "UG",
        'Rakdos': "BR",
        'Golgari': "BG",
        'Gruul': "RG"
    },
    'Colleges': {
        'Silverquill': "WB",
        'Lorehold': "WR",
        'Prismari': "UR",
        'Quandrix': "UG",
        'Witherbloom': "BG"
    },
    'Wedges': {
        'Jeskai': "WUR",
        'Mardu': "WBR",
        'Abzan': "WBG",
        'Sultai': "UBG",
        'Temur': "URG"
    },
    'Triomes': {
        'Raugrin': "WUR",
        'Savai': "WBR",
        'Indatha': "WBG",
        'Zagoth': "UBG",
        'Ketria': "URG"
    },
    'Shards': {
        'Esper': "WUB",
        'Bant': "WUG",
        'Naya': "WRG",
        'Grixis': "UBR",
        'Jund': "BRG"
    },
    'Families': {
        'Obscura': "WUB",
        'Brokers': "WUG",
        'Cabaretti': "WRG",
        'Maestros': "UBR",
        'Riveteers': "BRG"
    }
}

# Merging all of the supported colour-sets.
COLOR_ALIASES: dict[str, str] = {'5-Color': "WUBRG", 'All': "WUBRGC", 'None': "None"}
for d in COLOR_ALIASES_SUPPORT:
    COLOR_ALIASES = COLOR_ALIASES | COLOR_ALIASES_SUPPORT[d]

# Lists of alias based on the number of colours.
COLOUR_GROUPINGS: dict[str, list[str]] = {
    'Mono-Color': ['White', 'Blue', 'Black', 'Red', 'Green'],
    'Two-Color': ['Azorius', 'Orzhov', 'Boros', 'Selesnya', 'Dimir', 'Izzet', 'Simic', 'Rakdos', 'Golgari', 'Gruul'],
    'Three-Color': ['Jeskai', 'Mardu', 'Abzan', 'Sultai', 'Temur', 'Esper', 'Bant', 'Naya', 'Grixis', 'Jund']
}

MAIN_COLOUR_GROUPS = ["", "WU", "WB", "WR", "WG", "UB", "UR"," UG", "BR", "BG", "RG"]


def get_color_string(s: str) -> str:
    """
    Takes in a string, and attempts to convert it to a color string.
    If the string is invalid, returns 'WUBRGC'.
    :param s: The string to get colours from
    :return: 'WUBRGC' or a subset of 'WUBRG'
    """
    s = s.upper()

    if s.title() in COLOR_ALIASES:
        s = COLOR_ALIASES[s.title()]

    # Validate the string by using the set difference
    valid_chars = set(COLOR_ALIASES['All'])
    char_set = set(s)
    remainder = char_set - valid_chars

    if len(remainder) > 0:
        print(f'Invalid color string provided: {s}. Converting to "WUBRGC"')
        s = "WUBRGC"

    return s


# TODO: Remove this
# Takes in a valid colour string, or colour string alias,
# and then returns a dictionary of booleans.
def get_color_map(color_str: str) -> dict[str, bool]:
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


# - Emojis
# To automatically grab server emojis installed from
# https://github.com/scryfall/manamoji-discord/tree/main/emojis
def get_emoji(emoji_str: str) -> str:
    """
    Format and convert the emoji trying to be found.
    EG: 'W' gets converted to 'w', and then 'manaw'.
    :param emoji_str: The emoji to find.
    :return: Best guess at the emoji being requested.
    """

    emoji_str = emoji_str.lower()

    manamoji_str = emoji_str
    if not manamoji_str.startswith('mana'):
        manamoji_str = 'mana' + manamoji_str

    setmoji_str = emoji_str
    if not setmoji_str.startswith('set'):
        # setmoji_str = 'set' + setmoji_str
        pass

    manamojis = [emo for emo in MANAMOJIS if emo.name == manamoji_str]

    if len(manamojis) > 0:
        return str(manamojis[0])
    else:
        return ""


# NOTE: Incomplete
# Parses a string mana cost into a list of mana 'elements', while converting
# from 'curly-brace' format or plain-text format to our list format.
# Eg. {10}{G}{G} would return ['10', 'G', 'G']
# Eg. 10GG would return ['1', '0', 'G', 'G'], which is likely not what's wanted.
def parse_cost(mana_cost: str) -> list[str]:
    # TODO: Parse the mana cost from the {1}{W}{B} format into a list of strings.
    return [char for char in mana_cost]
    pass


# Takes a mana cost and attempts to return a string of emojis which
# represent that mana cost, as it would look on the card.
def emojify_mana_cost(mana_cost: str) -> str:
    """
    Converts human-like message with emoji to a discord usable message.
    :param mana_cost: The mana cost to add emojis to.
    :return: A string which will display properly when sent.
    """
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
def emojify_color_id(mana_cost: str) -> str:
    """
    Converts human-like message with emoji to a discord usable message.
    :param mana_cost: The mana cost to add emojis to.
    :return: A string which will display properly when sent.
    """
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
