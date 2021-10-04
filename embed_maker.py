import discord
import time
from datetime import date

from WUBRG import *
from utils import *
from settings import *
from data_core import *


### Help Embeds ###

# Returns an emebed object, stylized for help calls
def new_help_embed(title, description = ""):
    embed = discord.Embed(title=title, description=description, color=discord.Color.red())
    return embed

# Returns an embed which lists all of the strings which can be parsed into color strings.
def supported_color_strings():
    ret = new_help_embed(
        title="Available Colour Strings",
        description="Accepted colours are a mix of 'W', 'U', 'B', 'R', 'G', and 'C', or the keywords below.",
        )
    
    for d_key in COLOR_ALIASES_SUPPORT:
        d = COLOR_ALIASES_SUPPORT[d_key]
        msg = ""
        for s in d:
            color_string = get_color_string(s)
            color_id = emojify_color_id(color_string)
            
            msg +=color_id + ' - ' + s + '\r\n'
        ret.add_field(name=d_key, value=msg, inline=True)
    return ret



### Data Embeds ###

# Returns an emebed object, stylized for data queries.
def new_data_embed(title, description = "", url = ""):
    embed = discord.Embed(title=title, description=description, color=discord.Color.blue(), url=url)
    # NOTE: Adding in a thumbnail sqiushes the formatting of the embed, which seems to have little way to control it.
    #embed.set_thumbnail(url="https://c1.scryfall.com/file/scryfall-cards/normal/front/b/6/b615facd-6276-4896-bdf6-e5c006f55c5f.jpg?1632163002")
    footer = "Draft data provided by 17Lands.com | Card info provided by Scryfall.com"
    embed.set_footer(text=footer)
    return embed

# Returns an embed which displays the game stats about a particular card.
def gen_card_embed(card, set_code, data, formats, fields, start_date, end_date, color_filter = None):
    mana_cost = card['mana_cost']
    name = card['name']
    stored_name = card['stored_name']

    
    title = name + " " + emojify_mana_cost(mana_cost)
    embed = new_data_embed(title, url="https://www.17lands.com/card_ratings")

    # Generate a field to show the scope of the data.
    date_range = f"Date Range:\t\t {start_date} to {end_date}"  + '\r\n'

    filt_emojis = emojify_color_id(color_filter)
    if filt_emojis == "":
        filt_emojis = "*None*"
    filt = "Colour filter: \t\t" + filt_emojis + '\r\n'
    # TODO: fetch color winrate from 17lands
    color_winrate = ""#"Avg. " + emojify_color_id(color_filter) + " Winrate: \t" + "%00.00" + '\r\n'
    embed.add_field(name="Data Info", value=date_range + filt + color_winrate, inline=False)
  

    # Generate a field which acts as the labels for the data.
    # SET = get_emoji("ELD") # TODO: Find and add set emojis to the sever to use with WUBRG.py
    formats_column = "\r\n".join([f'*{FORMAT_NICKNAMES[f]}*' for f in formats])
    embed.add_field(name=f" - {set_code} - ", value=formats_column, inline=True)

    # Generate a field which is populated with a 'table' of card data.
    FORMAT_STRING = "`{:^6}`"
    fields_strs = [FORMAT_STRING.format(f) for (_, f) in fields]
    data_strs = "\r\n".join([" ".join([FORMAT_STRING.format(format_data(data[f][stored_name][field])) for (field, _) in fields]) for f in formats])
    embed.add_field(name=" ".join(fields_strs), value=data_strs, inline=True)


    return embed


# Returns an embed which displays the game stats about a particular card.
def gen_card_embeds_V2(call_struct, start_date=None, end_date=None):
        
    
    card = call_struct['CARD']
    s = call_struct['SET']
    formats = call_struct['FORMATS']
    color_filters = call_struct['COLORS']
    columns = call_struct['COLUMNS']

    def remove(col):
        if col in columns:
            columns.remove(col)
    remove('Color')
    remove('Rarity')

    # TODO: Remove colour and rarity from columns.
            
    mana_cost = card['mana_cost']
    name = card['name']
    stored_name = card['stored_name']

##    # Generate a field to show the scope of the data.
##    if start_date is None:
##        default = SET_CONFIG[s][formats[0]]['StartDate']
##        start_date = default if default is not None else DEFAULT_START_DATE
##    if end_date is None:
##        default = SET_CONFIG[s][formats[0]]['EndDate']
##        end_date = default if default is not None else date.today()
##    date_range = f"Date Range:\t\t {start_date} to {end_date}"  + '\r\n'


    # TODO: fetch color winrate from 17lands
        
    title = name + " " + emojify_mana_cost(mana_cost)
    #avreage_winrate = "Avg. Overall Winrate: \t" + "%00.00" + '\r\n'
    #color_winrate = "Avg. " + emojify_color_id(card['color_identity']) + " Winrate: \t" + "%00.00" + '\r\n'
    description = ""
    embed = new_data_embed(title, description, url=card['url'])
##    embed.add_field(name="avreage_winrate + color_winrate", value="", inline=False)
  

    # Generate a field which acts as the labels for the data.
    # SET = get_emoji("ELD") # TODO: Find and add set emojis to the sever to use with WUBRG.py
    format_temp = []
    color_temp = []
    for x in formats:
        for y in color_filters:
            format_temp.append(x)
            color_temp.append(y)

    FORMAT_STRING = "`{:^7}`"
    formats_column = "\r\n".join([FORMAT_STRING.format(FORMAT_NICKNAMES[f]) for f in format_temp])
    embed.add_field(name=f"Format", value=formats_column, inline=True)

    # Generate a field which acts as the labels for the data.
    # SET = get_emoji("ELD") # TODO: Find and add set emojis to the sever to use with WUBRG.py
    colors_column = "\r\n".join([f'` `**NONE**' if not c else f'` `{emojify_color_id(c)}' for c in color_temp])
    embed.add_field(name=f"` `Colors", value=colors_column, inline=True)

    # Generate a field which is populated with a 'table' of card data.
    FORMAT_STRING = "`{:^6}`"
    fields_strs = [FORMAT_STRING.format(cols) for cols in columns]

    data_strs = ""
    for x in range(0, len(format_temp)):
        # TODO: Create a map to use to determine formating, based on column name.
        data = PANDAS_CACHE[s][format_temp[x]][color_temp[x]][columns].loc[stored_name]
        data_strs += " ".join([FORMAT_STRING.format(format_data(d)) for d in data]) + '\r\n'

    embed.add_field(name=" ".join(fields_strs), value=data_strs, inline=True)


    return embed


# Returns an embed which shows the win rates diffenet colours of decks.
# NOTE: Unfinished. Needs to be populated with real data.
def gen_colour_rating_embed():
    embed = new_data_embed(title="Colour Rankings", url="https://www.17lands.com/color_ratings")

    # TODO: Modufy this so it orders the results by win rate, rather than colour identity.
    
    for d_key in COLOUR_GROUPINGS:
        d = COLOUR_GROUPINGS[d_key]
        msg = ""
        for s in d:
            color_string = get_color_string(s)
            color_id = emojify_color_id(color_string)

            # TODO: Populate with real data.
            msg +=  color_id + ': ' + "`% 00.00`" + '\r\n'
        embed.add_field(name=d_key, value=msg, inline=True)

    return embed
    

