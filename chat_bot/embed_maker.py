from typing import Union
import discord

from WUBRG import get_color_string, COLOR_ALIASES_SUPPORT, COLOUR_GROUPINGS

from chat_bot.utils.consts import FORMAT_NICKNAMES, STAT_FORMAT_STRINGS, STAT_ALIASES
from chat_bot.utils.utils import get_card_name
from chat_bot.Manamoji import Manamoji


def format_data(data: Union[float, int, str]) -> str:
    """
    Automatically formats data to the correct number of characters for display in embeds.
    Also automatically changes values less than 1 to percentages.
    :param data: The data to format.
    :return: The formatted data as a string.
    """
    if not isinstance(data, float):
        return str(data)
    elif 0 < data < 1:
        return "{:.1f}%".format(data * 100)
    else:
        return "{:.2f}".format(data)


# - Data Embeds
def new_data_embed(title: str, description: str = "", url: str = "") -> discord.Embed:
    """
    Creates and returns a shell of an embed used as a response for data-related calls.
    :param title: The title of the embed.
    :param description: A description
    :param url: A url to send the user to on-click.
    :return: A pre-formatted embed.
    """
    embed = discord.Embed(title=title, description=description, color=discord.Color.blue(), url=url)
    # NOTE: Adding in a thumbnail squishes the formatting of the embed, which seems to have little way to control it.
    # embed.set_thumbnail(url="https://c1.scryfall.com/file/scryfall-cards/normal/front/b/6/b615facd-6276-4896-bdf6-e5c006f55c5f.jpg?1632163002")
    footer = "Draft data provided by 17Lands.com | Card info provided by Scryfall.com"
    embed.set_footer(text=footer)
    return embed


def gen_card_embed(card: dict, set_code: str, data: dict, formats: list[str], fields: list[str],
                   start_date: str, end_date: str, color_filter: str = None) -> discord.Embed:
    """
    Returns an embed which displays the game stats about a particular card.
    :param card: The json of the card.
    :param set_code: The three-letter set code.
    :param data: The dictionary of data to pull from.
    :param formats: The list of formats to display data from.
    :param fields: The list of fields to show data for.
    :param start_date: The start dat of the data.
    :param end_date: The end date of the data.
    :param color_filter: The colors to filter on.
    :return:
    """
    if 'mana_cost' in card:
        mana_cost = card['mana_cost']
    elif 'card_faces' in card:
        mana_cost = card['card_faces'][0]['mana_cost']
    else:
        mana_cost = "WUBRGC"
    name = card['name']
    stored_name = get_card_name(card)

    title = name + " " + Manamoji.emojify_mana_cost(mana_cost)
    embed = new_data_embed(title, url="https://www.17lands.com/card_ratings")

    # Generate a field to show the scope of the data.
    date_range = f"Date Range:\t\t {start_date} to {end_date}" + '\r\n'

    print(f"color_filter: {color_filter}")
    filter_emojis = Manamoji.emojify_color_string(color_filter)
    if filter_emojis == "":
        filter_emojis = "*None*"
    filter_str = "Colour filter: \t\t" + filter_emojis + '\r\n'
    # TODO: fetch color win_rate from 17lands
    color_win_rate = ""  # "Avg. " + WUBRG.emojify_color_id(color_filter) + " Win Rate: \t" + "%00.00" + '\r\n'
    embed.add_field(name="Data Info", value=date_range + filter_str + color_win_rate, inline=False)

    # Generate a field which acts as the labels for the data.
    # SET = WUBRG.get_emoji("ELD") # TODO: Find and add set emojis to the sever to use with WUBRG.py
    formats_column = "\r\n".join([f'*{FORMAT_NICKNAMES[f]}*' for f in formats])
    embed.add_field(name=f" - {set_code} - ", value=formats_column, inline=True)

    # Generate a field which is populated with a 'table' of card data.
    format_string = "`{:^6}`"
    fields_strings = [format_string.format(STAT_ALIASES[f]) for f in fields]
    data_strings = []
    for f in formats:
        data_string = " ".join([format_string.format(format_data(data[f][stored_name][field])) for field in fields])
        data_strings.append(data_string)
    embed.add_field(name=" ".join(fields_strings), value="\r\n".join(data_strings), inline=True)

    return embed


def gen_colour_rating_embed() -> discord.Embed:
    """
    Returns an embed which shows the win rates different colours of decks.
    :return: An embed with the archetype data.
    """
    embed = new_data_embed(title="Colour Rankings", url="https://www.17lands.com/color_ratings")

    for d_key in COLOUR_GROUPINGS:
        d = COLOUR_GROUPINGS[d_key]
        msg = ""
        for s in d:
            color_string = get_color_string(s)
            color_id = Manamoji.emojify_color_string(color_string)

            # TODO: Populate with real data.
            msg += color_id + ': ' + "`% 00.00`" + '\r\n'
        embed.add_field(name=d_key, value=msg, inline=True)

    return embed


# - Help Embeds
# Returns an embed object, stylized for help calls
def new_help_embed(title: str, description: str = "") -> discord.Embed:
    """
    Creates and returns a shell of an embed used as a response for help-related calls.
    :param title: The title of the embed.
    :param description: A description
    :return: A pre-formatted embed.
    """
    embed = discord.Embed(title=title, description=description, color=discord.Color.red())
    return embed


# Returns an embed which lists all of the strings which can be parsed into color strings.
def supported_color_strings() -> discord.Embed:
    """
    Generates a discord embed which outlines the colour aliases that are available to the user.
    """
    ret = new_help_embed(
        title="Available Colour Strings",
        description="Accepted colours are a mix of 'W', 'U', 'B', 'R', 'G', and 'C', or the keywords below.",
    )

    for d_key in COLOR_ALIASES_SUPPORT:
        d = COLOR_ALIASES_SUPPORT[d_key]
        msg = ""
        for s in d:
            color_string = get_color_string(s)
            color_id = Manamoji.emojify_color_string(color_string)

            msg += color_id + ' - ' + s + '\r\n'
        ret.add_field(name=d_key, value=msg, inline=True)
    return ret


# TODO: Test this and determine if it's worth keeping.
# Returns an embed which displays the game stats about a particular card.
def gen_card_embeds_v2(card_info, data, start_date=None, end_date=None):
    print(card_info)
    s = card_info['set']
    # formats = card_info['formats']
    formats = ['PremierDraft', 'TradDraft', 'QuickDraft']
    color_filters = card_info['colors']
    columns = card_info['columns']

    def remove(col):
        if col in columns:
            columns.remove(col)

    remove('Color')
    remove('Rarity')

    mana_cost = card_info['mana_cost']
    name = card_info['name']
    stored_name = card_info['stored_name']

    ##    # Generate a field to show the scope of the data.
    ##    if start_date is None:
    ##        default = SET_CONFIG[s][formats[0]]['StartDate']
    ##        start_date = default if default is not None else DEFAULT_START_DATE
    ##    if end_date is None:
    ##        default = SET_CONFIG[s][formats[0]]['EndDate']
    ##        end_date = default if default is not None else date.today()
    ##    date_range = f"Date Range:\t\t {start_date} to {end_date}"  + '\r\n'

    # TODO: fetch color winrate from 17lands

    title = name + " " + Manamoji.emojify_mana_cost(mana_cost)
    # avreage_winrate = "Avg. Overall Winrate: \t" + "%00.00" + '\r\n'
    # color_winrate = "Avg. " + emojify_color_id(card['color_identity']) + " Winrate: \t" + "%00.00" + '\r\n'
    description = ""  # TODO: Add in the average winrate of 17 lands users overall and in the card colours.
    embed = new_data_embed(title, description, url=card_info['url'])

    # Generate a list of format names and colour groupings in the order they need to be used.
    format_temp = []
    color_temp = []
    for x in formats:
        for y in color_filters:
            format_temp.append(x)
            color_temp.append(y)

    # Generate a column of colour groups
    colors_column = "\r\n".join([f'`   NONE   `' if not c else f'` {c} `{Manamoji.emojify_color_string(c)}' for c in color_temp])
    embed.add_field(name=f"`  Colors  `", value=colors_column, inline=True)

    # Generate a column of format names
    FORMAT_STRING = "`{:^9}`"
    formats_column = "\r\n".join([FORMAT_STRING.format(FORMAT_NICKNAMES[f]) for f in format_temp])
    embed.add_field(name=f"` Formats `", value=formats_column, inline=True)

    # Generate a table containing the card data
    FORMAT_STRING = "`{:^6}`"
    fields_strs = [FORMAT_STRING.format(cols) for cols in columns]
    data_strs = ""
    for x in range(0, len(format_temp)):
        data = data.query_frames_cache(s, format_temp[x], color_temp[x], stored_name)
        if data is not None:
            data = data[columns]
            # TODO: Better handle NaNs.
            data_strs += " ".join(
                [STAT_FORMAT_STRINGS[columns[i]].format(data[i]) for i in range(len(columns))]) + '\r\n'
        else:
            data_strs += " ".join([FORMAT_STRING.format('--') for i in range(len(columns))]) + '\r\n'

    embed.add_field(name=" ".join(fields_strs), value=data_strs, inline=True)

    return embed





