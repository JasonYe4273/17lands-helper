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
    If the string is invalid, returns ''.
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
        print(f'Invalid color string provided: {s}. Converting to ""')
        s = ""

    return s


def get_color_identity(color_string: str) -> str:
    """
    Takes in a color string, and attempts to convert it to a
    color identity string.
    :param color_string: The color string to convert.
    :return: A color identity string, a subset of 'WUBRG'.
    """
    char_set = set(get_color_string(color_string))
    s = ''
    for c in "WUBRG":
        if c in char_set:
            s += c
    return s


# NOTE: Incomplete
# Parses a string mana cost into a list of mana 'elements', while converting
# from 'curly-brace' format or plain-text format to our list format.
# Eg. {10}{G}{G} would return ['10', 'G', 'G']
# Eg. 10GG would return ['1', '0', 'G', 'G'], which is likely not what's wanted.
def parse_cost(mana_cost: str) -> list[str]:
    # TODO: Parse the mana cost from the {1}{W}{B} format into a list of strings.
    return [char for char in mana_cost]
    pass
