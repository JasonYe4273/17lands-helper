from discord import Client, Message
from discord.ext import tasks

from chat_bot.settings import COMMAND_STR, DATA_QUERY_L, DATA_QUERY_R, UPDATING_SETS, OLD_SETS, SETS, FORMATS, START_DATE
from chat_bot.Manamoji import Manamoji
from chat_bot.message_maker import handle_card_request, handle_command

import requests
import time
from datetime import date

client: Client = Client()

cache: dict = {s: {f: {} for f in FORMATS} for s in SETS}


@client.event
async def on_message(message: Message) -> None:
    """
    Automatically handles what the bot should do when a user sends a message.
    :param message: The sent message.
    """
    # Don't parse own messages
    if message.author == client.user:
        return

    # Handle data queries of the form {{query}}
    if message.content.contains(DATA_QUERY_L) and message.content.contains(DATA_QUERY_R):
        await handle_card_request(message.content, message.channel)

    # Only parse messages that start with command string
    if message.content.startswith(COMMAND_STR):
        await handle_command(message.content, message.channel)


@tasks.loop(hours=12)
async def refresh_data() -> None:
    """
    Refreshes data about the set on a loop.
    """
    fetch_data(UPDATING_SETS)
    ##for s in UPDATING_SETS:
    ##    mgr = SetManager(s, True, False)
    ##    mgr.check_for_updates()


@client.event
async def on_ready() -> None:
    """
    Set up for the bot, which happens when it is first loaded.
    """
    Manamoji.cache_manamojis(client)
    fetch_data(OLD_SETS)
    ##for s in OLD_SETS:
    ##    mgr = SetManager(s, True, False)
    ##    mgr.check_for_updates()
    print('Logged in as {0.user}'.format(client))


def fetch_data(sets: list[str]) -> None:
    """
    Gets the data the bot uses.
    :param sets: The list of sets to get data for.
    """
    for s in sets:
        cache[s] = {f: {} for f in FORMATS}
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
                except Exception:
                    print('Failed; trying again in 30s')
                    time.sleep(30)


def main():
    # refresh_data.start()
    try:
        import os
        client.run(os.environ['TOKEN'])
    except KeyError:
        # print("Critical Error! Could not load token from operating system.")
        # Temporarily let this run locally with my bot token, so I can
        # check that everything compiles properly. I'll make sure to
        # remove this later.
        #    -ZacharyN
        from LocalToken import TOKEN
        client.run(TOKEN)


if __name__ == "__main__":
    main()
