import discord
import WUBRG
from WUBRG import COLOR_ALIASES_SUPPORT, COLOUR_GROUPINGS
from settings import FORMAT_NICKNAMES
from utils import format_data, get_card_name


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


def gen_card_embed(card: dict, set_code: str, data: dict, formats: list[str], fields: list[tuple[str, str]],
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

    title = name + " " + WUBRG.emojify_mana_cost(mana_cost)
    embed = new_data_embed(title, url="https://www.17lands.com/card_ratings")

    # Generate a field to show the scope of the data.
    date_range = f"Date Range:\t\t {start_date} to {end_date}" + '\r\n'

    filter_emojis = WUBRG.emojify_color_id(color_filter)
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
    fields_strings = [format_string.format(f) for (_, f) in fields]
    data_strings = "\r\n".join(
        [" ".join([format_string.format(format_data(data[f][stored_name][field])) for (field, _) in fields]) for f in
         formats])
    embed.add_field(name=" ".join(fields_strings), value=data_strings, inline=True)

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
            color_string = WUBRG.get_color_string(s)
            color_id = WUBRG.emojify_color_id(color_string)

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
            color_string = WUBRG.get_color_string(s)
            color_id = WUBRG.emojify_color_id(color_string)

            msg += color_id + ' - ' + s + '\r\n'
        ret.add_field(name=d_key, value=msg, inline=True)
    return ret
