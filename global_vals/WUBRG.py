try:
    import discord
except ImportError as ex:
    print("WARNING: 'discord' failed to import. Emoji support unavailable")

# Used to populate the emojis which represent mana costs and set symbols.
# Note, not calling this means no emojis will be found, and embeds will be emojiless.
MANAMOJIS = []
SETMOJIS = []


def cache_manamojis(client):
    """
    Uses a discord client to go through available emojis and creates a
    lookup table of them for future use when displaying information.
    :param client: An active instance of a discord.Client()
    """

    # TODO: See if this can be converted into .svgs, so it can operate
    # without servers having the emojis.
    global MANAMOJIS
    MANAMOJIS = [emo for emo in client.emojis if emo.name.startswith('mana')]
    print(f'{len(MANAMOJIS)} manamojis found!')

    # TODO: Add in support for set symbols.
    # global SETMOJIS
    # SETMOJIS = [emo for emo in client.emojis if emo.name.startswith('set')]
    # print(f'{len(SETMOJIS)} setmojis found!')


# Colour Mapping
COLORS = "WUBRG"

# Groupings of colour-sets supported.
COLOR_ALIASES_SUPPORT = {
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
    'Nephillim': {
        'Yore': "WUBR",
        'Witch': "WUBG",
        'Ink': "WURG",
        'Dune': "WBRG",
        'Glint': "UBRG"
    }
}

# Merging all of the supported colour-sets.
COLOR_ALIASES = {
    '5-Color': "WUBRG",
    'All': "WUBRGC",
    'None': ""
}

for d in COLOR_ALIASES_SUPPORT:
    # COLOR_ALIASES = COLOR_ALIASES | COLOR_ALIASES_SUPPORT[d]
    COLOR_ALIASES = {**COLOR_ALIASES, **COLOR_ALIASES_SUPPORT[d]}

# Lists of aliases based on the number of colours.
COLOUR_GROUPINGS = {
    'Mono-Color': COLOR_ALIASES_SUPPORT['Colors'],
    'Two-Color': COLOR_ALIASES_SUPPORT['Guilds'],
    # 'Three-Color': COLOR_ALIASES_SUPPORT['Wedges'] | COLOR_ALIASES_SUPPORT['Shards'],
    'Three-Color': {**COLOR_ALIASES_SUPPORT['Wedges'], **COLOR_ALIASES_SUPPORT['Shards']},
    'Four-Color': COLOR_ALIASES_SUPPORT['Nephillim'],
}


def get_color_string(s: str) -> str:
    """
    Takes in a string, and attempts to convert it to a color string.
    If the string is invalid, returns 'WUBRGC'.
    This function will attempt to convert common names into their colours.
    Eg. 'Bant' -> 'WUG'
    :param s: The string to convert.
    :return: A color string, which contains only characters found in 'WUBRGC'.
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


def get_color_identity(color_string: str) -> str:
    """
    Takes in a color string, and attempts to convert it to a
    color identity string.
    :param color_string: The color string to convert.
    :return: A color identity string, a subset of 'WUBRGC'.
    """
    char_set = set(get_color_string(color_string))
    s = ''
    for c in COLOR_ALIASES['All']:
        if c in char_set:
            s += c
    return s


def get_color_alias(color_string: str) -> str:
    """
    Takes in a colour string and attempts to return a more
    common name for the colors. Eg. 'WUR' -> 'Jeskai'
    :param color_string: The color string to convert.
    :return: A common name which represents the colours in color_string.
    """
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


COLOR_GROUPS = [''] + [get_color_string(y) for x in COLOUR_GROUPINGS for y in COLOUR_GROUPINGS[x]] + ['WUBRG']


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


def get_color_supersets(color_id: str, l: int = 5) -> list[str]:
    """
    Gets all possible permutations of WUBRG which contain the color_id.
    Can limit the length of the permutations returned with l.
    :param color_id: The colours to look for in the permutations.
    :param l: The max length of the permutations. Default: 5
    :return: A list of color ids.
    """
    color_ids = list()

    cis = set(get_color_string(color_id))
    for c in COLOR_GROUPS:
        if len(c) <= l and cis < set(c):
            color_ids.append(c)

    return color_ids


def get_color_subsets(color_id: str, l: int = 1) -> list[str]:
    """
    Gets all possible permutations of WUBRG which are contained in color_id.
    Can limit the length of the permutations returned with l.
    :param color_id: The colours to look for in the permutations.
    :param l: The min length of the permutations. Default: 1
    :return: A list of color ids.
    """
    colour_ids = list()

    cis = set(get_color_string(color_id))
    for c in COLOR_GROUPS:
        if len(c) >= l and cis > set(c):
            colour_ids.append(c)

    return colour_ids


# Emojis

# To automatically grab server emojis installed from
# https://github.com/scryfall/manamoji-discord/tree/main/emojis
def get_emoji(emoji_str: str) -> str:
    """
    Attempts to convert the commonly used emoji string into the
    raw representation used by discord.
    Eg. ':manab:' -> '<:manab:890942873632120903>'
    Eg. 'W' -> '<:manaw:890942874089312296>'
    :param emoji_str: The string name of the emoji
    :return: The discord reference to the emoji.
    """
    emoji_str = emoji_str.lower()
    if emoji_str.startswith(':') and emoji_str.endswith(':'):
        emoji_str = emoji_str[1:-1]

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


def parse_cost(mana_cost: str) -> list[str]:
    """
    Parses a mana cost into a list of mona pips. If a mana cost with curly
    braces is provided, the braces are stripped in the output.
    Eg. {10}{G}{G} would return ['10', 'G', 'G']
    Eg. 10GG would return ['1', '0', 'G', 'G'], which is likely not what's wanted.
    :param mana_cost: The mana cost of the card. Can be in the form '1WW' or '{1}{W}{W}'
    :return: A list of strings, which represent the different pips.
    """
    # TODO: Properly parse the mana cost from the {1}{W}{B} format into a list of strings.
    # TODO: Better parse unusual symbols
    # TODO: Better parse non-brace numeric costs
    return [char for char in mana_cost if char not in set('{}')]
    pass


def emojify_mana_cost(mana_cost: str) -> str:
    """
    Attempts to convert a mana cost into a series of emojis which show
    the card's mana cost, as it would look on the card.
    :param mana_cost: The mana cost of the card. Can be in the form '1WW' or '{1}{W}{W}'
    :return: A string containing emoji references.
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
    Attempts to convert a mana cost into a series of emojis which show
    the card's color id. (NOTE: If using the cost only, it may not be a true color id.)
    :param mana_cost: The mana cost of the card. Can be in the form '1WW' or '{1}{W}{W}'
    :return: A string containing emoji references.
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
