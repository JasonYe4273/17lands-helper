import discord
import requests
import time
from datetime import date
from discord.ext import tasks
from settings import COMMAND_STR, DEFAULT_FORMAT, START_DATE, TOKEN

client = discord.Client()

UPDATING_SETS = ['MID']
OLD_SETS = [] # ['AFR', 'STX', 'KHM']
SETS = UPDATING_SETS + OLD_SETS

FORMATS = {
    'PremierDraft': ['bo1', 'premier', 'premierdraft'],
    'TradDraft': ['bo3', 'trad', 'traditional', 'traddraft', 'traditionaldraft'],
    'QuickDraft': ['qd', 'quick', 'quickdraft'],
    'Sealed': ['sealed', 'bo1sealed', 'sealedbo1'],
    'TradSealed': ['tradsealed', 'bo3sealed', 'sealedbo3'],
    'DraftChallenge': ['challenge', 'draftchallenge'],
}
FORMAT_MAPPING = {}
for f in FORMATS:
    for s in FORMATS[f]:
        FORMAT_MAPPING[s] = f

cache = {s: {f: {} for f in FORMATS} for s in SETS}

DATA_COMMANDS = {
    'alsa': [('seen_count', '# Seen'), ('avg_seen', 'Average Last Seen At')],
    'ata': [('pick_count', '# Taken'), ('avg_pick', 'Average Taken At')],
    'gp': [('game_count', '# Games Played'), ('win_rate', 'Games Played Winrate')],
    'gnp': [('sideboard_game_count', '# Games Not Played'), ('sideboard_win_rate', 'Games Not Played Winrate')],
    'oh': [('opening_hand_game_count', '# Opening Hands'), ('opening_hand_win_rate', 'Opening Hand Winrate')],
    'gd': [('drawn_game_count', '# Drawn'), ('drawn_win_rate', 'Drawn Winrate')],
    'gih': [('ever_drawn_game_count', '# In Hand'), ('ever_drawn_win_rate', 'In Hand Winrate')],
    'gnd': [('never_drawn_game_count', '# Not Drawn'), ('never_drawn_win_rate', 'Not Drawn Winrate')],
    'iwd': [('drawn_improvement_win_rate', 'Improvement When Drawn')]
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

@client.event
async def on_message(message):
    # Don't parse own messages
    if message.author == client.user:
        return

    # Only parse messages that start with command string
    if not message.content.startswith(COMMAND_STR):
        return

    print(f'Parsing message: {message.content}')
    rest = message.content[len(COMMAND_STR):]

    # Get command
    command = rest.split(' ')[0]
    rest = rest[len(command):].strip()
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