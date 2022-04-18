import re
from re import Pattern

mana_symbol_re: Pattern = re.compile(r'{(.*?)}')

FAILSAFE: str = ''

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

MAIN_COLOUR_GROUPS: list[str] = ["", "WU", "WB", "WR", "WG", "UB", "UR", " UG", "BR", "BG", "RG"]
COLOR_COMBINATIONS: list[str] = ['', 'W', 'U', 'B', 'R', 'G',
                                 'WU', 'WB', 'WR', 'WG', 'UB', 'UR', 'UG', 'BR', 'BG', 'RG',
                                 'WUR', 'WBR', 'WBG', 'UBG', 'URG', 'WUB', 'WUG', 'WRG', 'UBR', 'BRG',
                                 'WUBR', 'WUBG', 'WURG', 'WBRG', 'UBRG', 'WUBRG']

BASE_MANA_SYMBOLS: set[str] = {"W", "U", "B", "R", "G", "C"}
NUMERIC_MANA_SYMBOLS: set[str] = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                                  "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"}
HYBRID_MANA_SYMBOLS: set[str] = {"W/U", "W/B", "B/R", "B/G", "U/B", "U/R", "R/G", "R/W", "G/W", "G/U"}
PHYREXIAN_MANA_SYMBOLS: set[str] = {"W/P", "U/P", "B/P", "R/P", "G/P"}
HYBRID_PHYREXIAN_MANA_SYMBOLS: set[str] = {"B/G/P", "B/R/P", "G/U/P", "G/W/P", "R/G/P",
                                           "R/W/P", "U/B/P", "U/R/P", "W/B/P", "W/U/P"}
COLORLESS_HYBRID_MANA_SYMBOLS: set[str] = {"2/W", "2/U", "2/B", "2/R", "2/G"}
SPECIAL_MANA_SYMBOLS: set[str] = {"A", "X", "Y", "Z", "S"}
COST_SYMBOLS: set[str] = {"T", "Q", "E"}
MANA_SYMBOLS: set[str] = BASE_MANA_SYMBOLS | NUMERIC_MANA_SYMBOLS | HYBRID_MANA_SYMBOLS | PHYREXIAN_MANA_SYMBOLS \
                         | HYBRID_PHYREXIAN_MANA_SYMBOLS | COLORLESS_HYBRID_MANA_SYMBOLS | SPECIAL_MANA_SYMBOLS \
                         | COST_SYMBOLS


def get_color_string(s: str) -> str:
    """
    Takes in a string, and attempts to convert it to a color string.
    If the string is invalid, returns ''.
    :param s: The string to get colours from
    :return: 'WUBRGC' or a subset of 'WUBRG'
    """
    if s is None:
        return FAILSAFE
    s = s.strip().upper()

    if s.title() in COLOR_ALIASES:
        s = COLOR_ALIASES[s.title()]

    # Validate the string by using the set difference
    valid_chars = set(COLOR_ALIASES['All'])
    char_set = set(s)
    remainder = char_set - valid_chars

    if len(remainder) > 0:
        print(f"Invalid color string provided: {s}. Converting to '{FAILSAFE}'")
        s = FAILSAFE

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


def get_color_supersets(color_id: str, max_len: int = 5, strict: bool = False) -> list[str]:
    """
    Gets all possible permutations of WUBRG which contain the color_id.
    Can limit the length of the permutations returned with l.
    :param color_id: The colours to look for in the permutations.
    :param max_len: The max length of the permutations. Default: 5
    :param strict: Whether the subset should be strict
    :return: A list of color ids.
    """
    color_ids = list()

    cis = set(get_color_identity(color_id))

    for c in COLOR_COMBINATIONS:
        if strict:
            if len(c) < max_len and cis < set(c):
                color_ids.append(c)
        else:
            if len(c) <= max_len and cis <= set(c):
                color_ids.append(c)

    return color_ids


def parse_cost(mana_cost: str) -> list[str]:
    """
    Converts the typically used mana cost to a list of strings to more easily iterate over.
    Eg. {10}{G}{G} would return ['10', 'G', 'G']
    :param mana_cost: A mana cost, in the form of {W}{U}{B}{R}{G}.
    :return: A list of mana symbols as strings.
    """
    sym_left = '{'
    sym_right = '}'
    default = ['A']

    # If the parenthesis don't match, return a dummy value.
    if mana_cost.count(sym_left) != mana_cost.count(sym_right):
        return default

    # Find anything like {.} in the string,
    costs = mana_symbol_re.findall(mana_cost)
    # And for the contents of each element,
    for cost in costs:
        # Make sure it is a valid mana symbol.
        if cost not in MANA_SYMBOLS:
            # If not, return a dummy value.
            return default

    # If all check passed, return the found values.
    return costs
