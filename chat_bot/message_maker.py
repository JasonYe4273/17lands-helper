from discord import TextChannel, Embed
import requests
from datetime import date, datetime, timedelta

from WUBRG import get_color_identity

from chat_bot.utils.consts import COMMAND_STR, DATA_QUERY_L, DATA_QUERY_R, DATA_QUERY_MID, QUOTE_PAIRS
from chat_bot.utils.settings import DEFAULT_FORMAT, START_DATE, DATA_COMMANDS, FORMAT_MAPPINGS, SETS
from chat_bot.utils.utils import get_card_name
from chat_bot.embed_maker import gen_card_embed, supported_color_strings
from chat_bot.DataCache import DataCache


async def send_embed_message(channel: TextChannel, embed: Embed) -> None:
    """
    Sends an embed to the specified channel.
    :param channel: The channel to send the message to.
    :param embed: The embed to send.
    """
    print(f"Sending embedded message to channel '#{channel}'")
    await channel.send(embed=embed)


async def send_message(channel: TextChannel, message: str) -> None:
    """
    Sends a message to the specified channel.
    :param channel: The channel to send the message to.
    :param message: The message to send.
    """
    print(f'Sending message to channel {channel}: {message}')
    await channel.send(message)


async def handle_command(message: str, channel: TextChannel):
    print(f'Parsing message: {message}')
    rest = message[len(COMMAND_STR):].strip()
    print(f'rest: {rest}')

    # Get command
    command = rest.split(' ')[0]
    print(f'command: {command}')
    # rest = rest[len(command):].strip()

    if command == 'colors':
        await send_embed_message(channel, supported_color_strings())
    elif command == 'help':
        await send_message(channel, 'Read the README here: <https://github.com/JasonYe4273/17lands-helper>')
    elif command == 'code':
        await send_message(channel, '<https://github.com/JasonYe4273/17lands-helper>')


# TODO: Restructure this
async def data_query(query: str, channel: TextChannel) -> None:
    """
    Handles a query for data sent by a user.
    :param query: The found query from the user.
    :param channel: The channel to send the query to.
    """
    print(f'Handling data query {query}')
    separator = query.find(DATA_QUERY_MID)
    card_query = query.strip() if separator == -1 else query[:separator].strip()
    options_query = '' if separator == -1 else query[separator + 1:].strip()

    # Parse card names to the left of separator
    requested_cards = []
    rest = card_query
    old_rest = None
    while rest != '':
        if rest == old_rest:
            await send_message(channel, 'Error: infinite loop while parsing card names')
            break
        else:
            old_rest = rest
        # Parse card name, allowing spaces inside quotes
        if rest[0] in QUOTE_PAIRS and rest.find(QUOTE_PAIRS[rest[0]], 1) != -1:
            end = rest.find(QUOTE_PAIRS[rest[0]], 1)
            raw_card_name = rest[1:end]
            rest = rest[end + 1:].strip()
        else:
            end = rest.find(' ')
            if end == -1:
                raw_card_name = rest
                rest = ''
            else:
                raw_card_name = rest[:end]
                rest = rest[end:].strip()

        #card = CardManager.from_name(raw_card_name)
        #
        #if card is None:
        #    await send_message(channel, f'Error querying Scryfall for {raw_card_name}')
        #else:
        #    requested_cards.append(card)

        # Try get unique card from Scryfall
        try:
            response = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={raw_card_name}').json()
            if response['object'] == 'error':
                if response['details'][:20] == 'Too many cards match':
                    await send_message(channel, f'Error: multiple card matches for "{raw_card_name}"')
                else:
                    await send_message(channel, f'Error: cannot find card "{raw_card_name}"')
            else:
                requested_cards.append(response)
        except Exception:
            await send_message(channel, f'Error querying Scryfall for {raw_card_name}')

    options = options_query.split(' ')

    # Parse options to the right of separator
    formats = []
    sets = []
    data_commands = {}
    end_date = None
    days = 0
    colors = None
    can_use_cache = True
    for o in options:
        ol = o.lower()
        ou = o.upper()
        # Format
        if ol in FORMAT_MAPPINGS:
            formats.append(FORMAT_MAPPINGS[ol])

        # Sets
        elif ou in SETS:
            sets.append(ou)

        # Data commands
        elif ol in DATA_COMMANDS:
            for dc in DATA_COMMANDS[ol]:
                data_commands[dc[0]] = dc

        # # Verbose (whether to show # in addition to WR)
        # elif ol == 'verbose' or ol == '-v':
        #     verbose = True

        # Time period to search
        elif end_date is None and (ol.startswith('end=') or ol.startswith('-e=')):
            try:
                end_date = datetime.strptime(ol[ol.find('=') + 1:], '%m-%d-%Y').date()
            except Exception:
                pass
        elif ol.startswith('months=') or ol.startswith('-m='):
            try:
                days += int(ol[ol.find('=') + 1:]) * 30
            except Exception:
                pass
        elif ol.startswith('weeks=') or ol.startswith('-w='):
            try:
                days += int(ol[ol.find('=') + 1:]) * 7
            except Exception:
                pass
        elif ol.startswith('days=') or ol.startswith('-d='):
            try:
                days += int(ol[ol.find('=') + 1:])
            except Exception:
                pass

        # Deck colors to search
        elif ol.startswith('-c=') or ol.startswith('colors='):
            if colors is None:
                colors = get_color_identity(ol[ol.find('=') + 1:])
                if colors is not None and colors != '':
                    can_use_cache = False

    # Set defaults if no options specified
    if len(formats) == 0:
        formats = [DEFAULT_FORMAT]
    if len(sets) == 0:
        sets = SETS
    if len(data_commands) == 0:
        for dc in DATA_COMMANDS['data']:
            data_commands[dc[0]] = dc

    # Filter out irrelevant sets
    filtered_sets = []
    for s in sets:
        for c in requested_cards:
            if get_card_name(c) in DataCache[s][formats[0]]:
                filtered_sets.append(s)
                break
    sets = filtered_sets

    # Calculate start and end date
    # result_description = ''
    if end_date is None:
        end_date = date.today()
        # result_description = f' to today'
    if end_date != date.today():
        can_use_cache = False
        # result_description = f' to {end_date}'

    if days > 0:
        start_date = end_date - timedelta(days=days)
        can_use_cache = False
        # result_description = f' from {start_date}{result_description}'
    else:
        start_date = START_DATE
        # result_description = f' up{result_description}'

    # Calculate 17lands query string
    query_str = f'&start_date={start_date}&end_date={end_date}'
    if colors is not None and colors != 'all':
        # result_description = f' in {colors} decks{result_description}'
        query_str += f'&colors={colors}'

    sent = []
    for s in sets:
        data_to_use = {}
        for f in formats:
            # Use data from the cache if possible
            if can_use_cache:
                # data_to_use[f] = DATA_CACHE[s][f][colors]
                data_to_use[f] = DataCache[s][f]
            elif f'{f}{query_str}' in DataCache[s]:
                data_to_use[f] = DataCache[s][f'{f}{query_str}']
            else:
                # data_to_use[f] = fetch_format_data(s, f, colors, start_date, end_date)
                try:
                    # Otherwise, query from 17lands and add the result to the cache
                    data_to_use[f] = {}
                    DataCache[s][f'{f}{query_str}'] = {}
                    print(f'Fetching data for {s} {f}...')
                    response = requests.get(
                        'https://www.17lands.com/card_ratings/data?' +
                        f'expansion={s}&format={f}{query_str}'
                    )
                    for c in response.json():
                        data_to_use[f][c['name']] = c
                        DataCache[s][f'{f}{query_str}'][c['name']] = c
                    print('Success!')
                except Exception:
                    await send_message(channel, f'Failed to fetch data for {s} {f} from 17lands')
        for card in requested_cards:
            card_name = get_card_name(card)
            if card_name in data_to_use[formats[0]] and card_name not in sent:
                sent.append(card_name)

                await send_embed_message(channel, gen_card_embed(
                    card=card,
                    set_code=s,
                    data=data_to_use,
                    formats=formats,
                    fields=[(dc, dc_name) for (dc, dc_name, v) in data_commands.values() if not v],
                    start_date=start_date,
                    end_date=str(end_date),
                    color_filter=(None if colors == 'all' else colors)
                ))


async def handle_card_request(message: str, channel: TextChannel):
    next_data_query = message.find(DATA_QUERY_L)
    while next_data_query != -1:
        start = next_data_query + len(DATA_QUERY_L)
        end = message.find(DATA_QUERY_R, start)
        if end == -1:
            break
        await data_query(message[start:end], channel)
        next_data_query = message.find(DATA_QUERY_L, end)
