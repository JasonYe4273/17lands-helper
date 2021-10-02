import discord
from discord.ext import tasks
import os
import requests
import time
from datetime import date, datetime, timedelta

from settings import *
import WUBRG
from WUBRG import COLOR_ALIASES_SUPPORT, COLOR_ALIASES, COLOUR_GROUPINGS, MANAMOJIS
from embed_maker import gen_card_embed, supported_color_strings
from utils import format_data, get_card_name
import data_core

client = discord.Client()


##SETS = settings.SETS
##FORMATS = settings.FORMATS
##FORMAT_MAPPING = settings.FORMAT_MAPPING
##DATA_COMMANDS = settings.DATA_COMMANDS
##SET_CONFIG = settings.SET_CONFIG
##DEFAULT_START_DATE = settings.DEFAULT_START_DATE
##DATA_DIR = settings.DATA_DIR
##CONFIG_DIR = settings.SET_CONFIG
##CARD_FILENAME = settings.CARD_DATA_FILENAME  #'{set}_{format}.json'
##BROADCAST_CHANNELS = settings.BROADCAST_CHANNELS

DATA_CACHE = None


def get_channel(channel_info):
    guild_id = channel_info['guild_id']
    channel_id = channel_info['channel_id']
    return client.get_guild(guild_id).get_channel(channel_id)

async def send_embed_message(channel, embed):
    print(f"Sending embedded message to channel '#{channel}'")
    await channel.send(embed=embed)

async def send_message(channel, message):
    print(f"Sending message to channel '#{channel}': {message}")
    await channel.send(message)

async def send_embed_broadcast(embed):
    for channel_name in BROADCAST_CHANNELS:
        await send_embed_message(get_channel(BROADCAST_CHANNELS[channel_name]), embed)

async def send_broadcast(message):
    for channel in BROADCAST_CHANNELS:
        await send_message(get_channel(BROADCAST_CHANNELS[channel_name]), message)

async def log(message):
    await send_message(LOG_CHANNEL, message)


def update_data():
    data_core.init_cache()
    global DATA_CACHE
    DATA_CACHE = data_core.DATA_CACHE


@tasks.loop(hours=12)
async def refresh_data():
    update_data()
    print(f"Data cache char len: '{len(str(DATA_CACHE))}'")


@client.event
async def on_ready():
    refresh_data.start()
    WUBRG.cache_manamojis(client)
    #update_data()
    print('Logged in as {0.user}'.format(client))
    print(get_channel(BROADCAST_CHANNELS["CrossComputer"]))



async def data_query(query, channel):
    print(f'Handling data query {query}')
    separator = query.find(DATA_QUERY_MID)
    card_query = query.strip() if separator == -1 else query[:separator].strip()
    options_query = '' if separator == -1 else query[separator+1:].strip()

    # Parse cardnames to the left of separator
    scryfall_cards = []
    rest = card_query
    old_rest = None
    sets = []

    while rest != '':
        if rest == old_rest:
            await send_message(channel, 'Error: infinite loop while parsing cardnames')
            break
        else:
            old_rest = rest
        # Parse cardname, allowing spaces inside quotes
        if rest[0] in QUOTE_PAIRS and rest.find(QUOTE_PAIRS[rest[0]], 1) != -1:
            end = rest.find(QUOTE_PAIRS[rest[0]], 1)
            raw_cardname = rest[1:end]
            rest = rest[end+1:].strip()
        else:
            end = rest.find(' ')
            if end == -1:
                raw_cardname = rest
                rest = ''
            else:
                raw_cardname = rest[:end]
                rest = rest[end:].strip()

        # Try get unique card from Scryfall
        card_response = data_core.query_scryfall(raw_cardname)
        if card_response['err_msg'] != None:
           await send_message(channel, card_response['err_msg'])
        else:
            
            s = card_response['card_info']['set']
            if s in SETS:
                scryfall_cards.append(card_response['card_info'])
                sets.append(s)
            else:
               await send_message(channel, f"No data for '{s}'. Cannot display info for '{card_response['card_info']['name']}'.")
        

    options = options_query.split(' ')

    # Parse options to the right of separator
    formats = []
    data_commands = {}
    verbose = False
    start_date = None
    end_date = None
    days = 0
    colors = None
    can_use_cache = True
    for o in options:
        ol = o.lower()
        ou = o.upper()
        # Format
        if ol in FORMAT_MAPPING:
            formats.append(FORMAT_MAPPING[ol])

        # Sets
        elif ou in SETS:
            sets.append(ou)

        # Data commands
        elif ol in DATA_COMMANDS:
            for dc in DATA_COMMANDS[ol]:
                data_commands[dc[0]] = dc

        # Verbose (whether to show # in addition to WR)
        elif ol == 'verbose' or ol == '-v':
            verbose = True

        # Time period to search
        elif end_date is None and (ol.startswith('end=') or ol.startswith('-e=')):
            try:
                end_date = datetime.strptime(ol[ol.find('=')+1:], '%m-%d-%Y').date()
            except:
                pass
        elif ol.startswith('months=') or ol.startswith('-m='):
            try:
                days += int(ol[ol.find('=')+1:])*30
            except:
                pass
        elif ol.startswith('weeks=') or ol.startswith('-w='):
            try:
                days += int(ol[ol.find('=')+1:])*7
            except:
                pass
        elif ol.startswith('days=') or ol.startswith('-d='):
            try:
                days += int(ol[ol.find('=')+1:])
            except:
                pass

        # Deck colors to search
        elif ol.startswith('-c=') or ol.startswith('colors='):
            if colors is None:
                colors = WUBRG.get_color_identity(ol[ol.find('=')+1:])
                if colors is not None and colors != 'all' or colors != '':
                    can_use_cache = False


    # Set defaults if no options specified
    if len(formats) == 0:
        formats = [DEFAULT_FORMAT]
    if len(sets) == 0:
        sets = SETS
    if len(data_commands) == 0:
        for dc in DATA_COMMANDS['data']:
            data_commands[dc[0]] = dc
    
    # Calculate start and end date
    result_description = ''
    if end_date is None:
        end_date = date.today()
        result_description = f' to today'
    if end_date != date.today():
        can_use_cache = False
        result_description = f' to {end_date}'

    if days > 0:
        start_date = end_date - timedelta(days=days)
        can_use_cache = False
        result_description = f' from {start_date}{result_description}'
    else:
        start_date = START_DATE
        result_description = f' up{result_description}'

    # Calculate 17lands query string
    query_str = f'&start_date={start_date}&end_date={end_date}'
    if colors is not None and colors != 'all':
        result_description = f' in {colors} decks{result_description}'
        query_str += f'&colors={colors}'


    print('pre: sent = []')
    sent = []
    for s in sets:
        data_to_use = {}
        for f in formats:
            # Use data from the cache if possible
            if can_use_cache:
                #data_to_use[f] = DATA_CACHE[s][f][colors]
                data_to_use[f] = DATA_CACHE[s][f]['']
                print('Using main cache')
            elif f'{f}{query_str}' in DATA_CACHE[s]:
                data_to_use[f] = DATA_CACHE[s][f'{f}{query_str}']
                print('Using query cache')
            else:
                #data_to_use[f] = fetch_format_data(s, f, colors, start_date, end_date)
                try:
                    # Otherwise, query from 17lands and add the result to the cache
                    data_to_use[f] = {}
                    cache[s][f'{f}{query_str}'] = {}
                    print(f'Fetching data for {s} {f}...')
                    response = requests.get(
                        'https://www.17lands.com/card_ratings/data?' +
                        f'expansion={s}&format={f}{query_str}'
                    )
                    for c in response.json():
                        data_to_use[f][c['name']] = c
                        DATA_CACHE[s][f'{f}{query_str}'][c['name']] = c
                    print('Success!')
                except:
                    await send_message(channel, f'Failed to fetch data for {s} {f} from 17lands')

        for card in scryfall_cards:
            cardname = get_card_name(card)
            print(cardname)
            if cardname not in data_to_use[formats[0]]:
                print(f'{cardname} not found in data_to_use')
            elif cardname in sent:
                print(f'{cardname} already sent')
            else:
                sent.append(cardname)
                print(f'Generating embed for {cardname}')
                await send_embed_message(channel, gen_card_embed(
                    card=card,
                    set_code=s,
                    data=data_to_use,
                    formats=formats,
                    fields=[(dc, dc_name) for (dc, dc_name, v) in data_commands.values() if not v],
                    start_date=start_date,
                    end_date=end_date,
                    color_filter=(None if colors == 'all' else colors)
                ))


@client.event
async def on_message(message):
    # Don't parse own messages
    if message.author == client.user:
        return

    # Handle data queries of the form {{query}}
    next_data_query = message.content.find(DATA_QUERY_L)
    while next_data_query != -1:
        start = next_data_query + len(DATA_QUERY_L)
        end = message.content.find(DATA_QUERY_R, start)
        if end == -1:
            break
        await data_query(message.content[start:end], message.channel)
        next_data_query = message.content.find(DATA_QUERY_L, end)

    # Only parse messages that start with command string
    if not message.content.startswith(COMMAND_STR):
        return

    print(f'Parsing message: {message.content}')
    rest = message.content[len(COMMAND_STR):]

    # Get command
    command = rest.split(' ')[0]
    rest = rest[len(command):].strip()

    if command == 'colors':
        await send_embed_message(message.channel, supported_color_strings())
    elif command == 'help':
        await send_message(message.channel, 'Read the README here: <https://github.com/JasonYe4273/17lands-helper>')
    elif command == 'code':
        await send_message(message.channel, '<https://github.com/JasonYe4273/17lands-helper>')



try:
    client.run(os.environ['TOKEN'])
except:
    # Temporarily let this run locally with my bot token, so I can
    # check that everything compiles properly. I'll make sure to
    # remove this later.
    #    -ZacharyN
    from LocalToken import TOKEN
    client.run(TOKEN)
