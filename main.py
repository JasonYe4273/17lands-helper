import discord
import requests
import time
from datetime import date
from discord.ext import tasks
from settings import COMMAND_STR, DEFAULT_FORMAT, START_DATE, TOKEN
from settings import DATA_QUERY_L, DATA_QUERY_R, DATA_QUERY_MID

client = discord.Client()

UPDATING_SETS = ['MID']
OLD_SETS = [] # ['AFR', 'STX', 'KHM']
SETS = UPDATING_SETS + OLD_SETS

FORMATS = {
    'PremierDraft': ['bo1', 'premier', 'premierdraft'],
    # 'TradDraft': ['bo3', 'trad', 'traditional', 'traddraft', 'traditionaldraft'],
    # 'QuickDraft': ['qd', 'quick', 'quickdraft'],
    # 'Sealed': ['sealed', 'bo1sealed', 'sealedbo1'],
    # 'TradSealed': ['tradsealed', 'bo3sealed', 'sealedbo3'],
    # 'DraftChallenge': ['challenge', 'draftchallenge'],
}
FORMAT_MAPPING = {}
for f in FORMATS:
    for s in FORMATS[f]:
        FORMAT_MAPPING[s] = f

cache = {s: {f: {} for f in FORMATS} for s in SETS}

DATA_COMMANDS = {
    'alsa': [('seen_count', '# Seen', True), ('avg_seen', 'ALSA', False)],
    'ata': [('pick_count', '# Taken', True), ('avg_pick', 'ATA', False)],
    'gp': [('game_count', '# GP', True), ('win_rate', 'GP WR', False)],
    'gnp': [('sideboard_game_count', '# GNP', True), ('sideboard_win_rate', 'GNP WR', False)],
    'oh': [('opening_hand_game_count', '# OH', True), ('opening_hand_win_rate', 'OH WR', False)],
    'gd': [('drawn_game_count', '# GD', True), ('drawn_win_rate', 'GD WR', False)],
    'gih': [('ever_drawn_game_count', '# GIH', True), ('ever_drawn_win_rate', 'GIH WR', False)],
    'gnd': [('never_drawn_game_count', '# GND', True), ('never_drawn_win_rate', 'GND WR', False)],
    'iwd': [('drawn_improvement_win_rate', 'IWD', False)]
}
DATA_COMMANDS['drafts'] = DATA_COMMANDS['alsa'] + DATA_COMMANDS['ata']
DATA_COMMANDS['games'] = DATA_COMMANDS['gp'] + DATA_COMMANDS['gnp'] + DATA_COMMANDS['oh'] + DATA_COMMANDS['gd'] + DATA_COMMANDS['gih'] + DATA_COMMANDS['gnd'] + DATA_COMMANDS['iwd']
DATA_COMMANDS['data'] = DATA_COMMANDS['drafts'] + DATA_COMMANDS['games']

async def send_message(channel, message):
    print(f'Sending message to channel {channel}: {message}')
    await channel.send(message)

@client.event
async def on_ready():
    fetch_data(OLD_SETS)
    print('Logged in as {0.user}'.format(client))

def format_data(data):
    if type(data) != float:
        return str(data)
    elif data < 1:
        return "{:.1f}%".format(data * 100)
    else:
        return "{:.2f}".format(data)

async def data_query(query, channel):
    print(f'Handling data query {query}')
    separator = query.find(DATA_QUERY_MID)
    card_query = query.strip() if separator == -1 else query[:separator].strip()
    options_query = '' if separator == -1 else query[separator+1:].strip()

    # Parse cardnames to the left of separator
    cardnames = []
    rest = card_query
    while rest != '':
        # Parse cardname, allowing spaces inside quotes
        if rest[0] in ['"', "'"] and rest.find(rest[0], 1) != -1:
            end = rest.find(rest[0], 1)
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
        try:
            response = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={raw_cardname}').json()
            if response['object'] == 'error':
                if response['details'][:20] == 'Too many cards match':
                    await send_message(channel, f'Error: multiple card matches for "{raw_cardname}"')
                else:
                    await send_message(channel, f'Error: cannot find card "{raw_cardname}"')
            else:
                cardnames.append(response['name'])
        except:
            await send_message(channel, f'Error querying Scryfall for {raw_cardname}')

    options = options_query.split(' ')

    # Parse options for formats, sets, and data to query to the right of separator
    formats = []
    sets = []
    data_commands = []
    verbose = False
    for o in options:
        if o.lower() in FORMAT_MAPPING:
            formats.append(FORMAT_MAPPING[o.lower()])
        if o.upper() in SETS:
            sets.append(o.upper())
        if o.lower() in DATA_COMMANDS:
            data_commands += DATA_COMMANDS[o.lower()]
        if o.lower() == 'verbose' or o.lower == '-v':
            verbose = True

    if len(formats) == 0:
        formats = [DEFAULT_FORMAT]
    if len(sets) == 0:
        sets = SETS
    print(formats)
    print(sets)
    print(data_commands)

    tables = []
    for c in cardnames:
        found = False
        for s in sets:
            if c in cache[s][formats[0]]:
                header = [s] + [f for f in formats]
                table = [[dc_name] + [
                    format_data(cache[s][f][c][dc]) for f in formats
                ] for (dc, dc_name, v) in data_commands if not v or verbose]
                tables.append((c, [header] + table))
                found = True
                break
        if not found:
            await send_message(channel, f'Cannot find {c} in 17lands data')

    result = ''
    for (c, t) in tables:
        result += f'Data for {c}\n'
        result += '```'
        column_lengths = [0 for _ in t[0]]
        for r in range(len(t)):
            for c in range(len(t[0])):
                column_lengths[c] = max(column_lengths[c], len(t[r][c]))

        for c in range(len(t[0])):
            result += t[0][c] + (column_lengths[c]+1-len(t[0][c]))*' ' + '| '
        result += '\n'

        result += '-' * (sum(column_lengths) + 2*len(column_lengths)) + '\n'

        for r in range(1, len(t)):
            for c in range(len(t[0])):
                result += t[r][c] + (column_lengths[c]+1-len(t[r][c]))*' ' + '| '
            result += '\n'
        result += '```\n'

    await send_message(channel, result)


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

    # Old data commands
    if command in DATA_COMMANDS:
        # Parse cardname, allowing spaces inside quotes
        if rest[0] in ['"', "'"] and rest.find(rest[0], 1) != -1:
            cardname = rest[1:rest.find(rest[0], 1)]
            rest = rest[rest.find(rest[0], 1)+1:].strip()
        else:
            cardname = rest[:rest.find(' ')]
            rest = rest[rest.find(' ')+1:].strip()

        # Try get unique card from Scryfall
        try:
            response = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={cardname}').json()
            if response['object'] == 'error':
                if response['details'][:20] == 'Too many cards match':
                    await send_message(message.channel, f'Error: multiple card matches for "{cardname}"')
                else:
                    await send_message(message.channel, f'Error: cannot find card "{cardname}"')
                return
            else:
                cardname = response['name']
        except:
            await send_message(message.channel, 'Error querying Scryfall')
            return

        tokens = rest.split(' ')

        # See if any format names were passed in
        formatname = None
        for t in tokens:
            if t.lower() in FORMAT_MAPPING:
                formatname = FORMAT_MAPPING[t.lower()]
                break
        if formatname is None:
            formatname = DEFAULT_FORMAT

        # See if any set names were passed in
        setname = None
        for t in tokens:
            if t.upper() in SETS:
                setname = t.upper()
                break
        if setname is not None and cardname not in cache[setname][formatname]:
            # Set name was passed in but no matching card in that set
            await send_message(message.channel, f'Cannot find {cardname} in 17lands data for {setname}')
            return

        # If no set names were passed in, try to find a set with the cardname
        if setname is None:
            for s in SETS:
                if cardname in cache[s][formatname]:
                    setname = s
        if setname is None:
            # No card found in any 17lands data
            await send_message(message.channel, f'Cannot find {cardname} in 17lands data')
            return

        data = cache[setname][formatname][cardname]

        result = f'Data for {cardname} in {setname} {formatname}:'
        result += f'\n----------------------------------------------'
        for (column, name) in DATA_COMMANDS[command]:
            # Add a line for each data point requested
            result += f'\n{name}: {data[column]}'
        await send_message(message.channel, result)


@tasks.loop(hours=12)
async def refresh_data():
    fetch_data(UPDATING_SETS)

def fetch_data(sets):
    for s in sets:
        for f in FORMATS:
            success = False
            while not success:
                try:
                    print(f'Fetching data for {s} {f}...')
                    response = requests.get(
                        'https://www.17lands.com/card_ratings/data?' +
                        f'expansion={s}&format={f}&start_date={START_DATE}&end_date={date.today()}'
                    )
                    for c in response.json():
                        cache[s][f][c['name']] = c
                    success = True
                    print('Success!')
                    time.sleep(10)
                except:
                    print('Failed; trying again in 30s')
                    time.sleep(30)


refresh_data.start()
client.run(TOKEN)