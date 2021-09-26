import discord
import time
from datetime import date
import WUBRG
from WUBRG import COLOR_ALIASES_SUPPORT, COLOR_ALIASES, COLOUR_GROUPINGS, MANAMOJIS
from utils import format_data


FORMAT_NICKNAMES = {
    'PremierDraft': 'Bo1',
    'TradDraft': 'Bo3',
    'QuickDraft': 'Quick',
    'Sealed': 'Seal',
    'TradSealed': 'Bo3Seal',
    'DraftChallenge': 'Chal.',
}

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

    
    title = name + " " + WUBRG.emojify_mana_cost(mana_cost)
    embed = new_data_embed(title, url="https://www.17lands.com/card_ratings")

    # Generate a field to show the scope of the data.
    date_range = f"Date Range:\t\t {start_date} to {end_date}"  + '\r\n'

    filt_emojis = WUBRG.emojify_color_id(color_filter)
    if filt_emojis == "":
        filt_emojis = "*None*"
    filt = "Colour filter: \t\t" + filt_emojis + '\r\n'
    # TODO: fetch color winrate from 17lands
    color_winrate = ""#"Avg. " + WUBRG.emojify_color_id(color_filter) + " Winrate: \t" + "%00.00" + '\r\n'
    embed.add_field(name="Data Info", value=date_range + filt + color_winrate, inline=False)
  

    # Generate a field which acts as the labels for the data.
    # SET = WUBRG.get_emoji("ELD") # TODO: Find and add set emojis to the sever to use with WUBRG.py
    formats_column = "\r\n".join([f'*{FORMAT_NICKNAMES[f]}*' for f in formats])
    embed.add_field(name=f" - {set_code} - ", value=formats_column, inline=True)

    # Generate a field which is populated with a 'table' of card data.
    FORMAT_STRING = "`{:^6}`"
    fields_strs = [FORMAT_STRING.format(f) for (_, f) in fields]
    data_strs = "\r\n".join([" ".join([FORMAT_STRING.format(format_data(data[f][name][field])) for (field, _) in fields]) for f in formats])
    embed.add_field(name=" ".join(fields_strs), value=data_strs, inline=True)


    return embed

# Returns an embed which shows the win rates diffenet colours of decks.
# NOTE: Unfinished. Needs to be populated with real data.
def gen_colour_rating_embed():
    embed = new_data_embed(title="Colour Rankings", url="https://www.17lands.com/color_ratings")

    for d_key in COLOUR_GROUPINGS:
        d = COLOUR_GROUPINGS[d_key]
        msg = ""
        for s in d:
            color_string = WUBRG.get_color_string(s)
            color_id = WUBRG.emojify_color_id(color_string)

            # TODO: Populate with real data.
            msg +=  color_id + ': ' + "`% 00.00`" + '\r\n'
        embed.add_field(name=d_key, value=msg, inline=True)

    return embed
    


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
            color_string = WUBRG.get_color_string(s)
            color_id = WUBRG.emojify_color_id(color_string)
            
            msg +=color_id + ' - ' + s + '\r\n'
        ret.add_field(name=d_key, value=msg, inline=True)
    return ret
