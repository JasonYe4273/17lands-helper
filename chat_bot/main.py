from discord import Client, Message
from discord.ext import tasks

from chat_bot.utils.consts import COMMAND_STR, DATA_QUERY_L, DATA_QUERY_R
from chat_bot.utils.settings import UPDATING_SETS, OLD_SETS
from chat_bot.Manamoji import Manamoji
from chat_bot.message_maker import handle_card_request_v2, handle_command
from chat_bot.DataCache import DataCache

client: Client = Client()


@client.event
async def on_message(message: Message) -> None:
    """
    Automatically handles what the bot should do when a user sends a message.
    :param message: The sent message.
    """
    # Don't parse own messages
    if message.author == client.user:
        return

    # Handle data queries of the form '{{query | options}}'
    if (DATA_QUERY_L in message.content) and (DATA_QUERY_R in message.content):
        await handle_card_request_v2(message.content, message.channel)

    # Only parse messages that start with command string '17!'
    if message.content.startswith(COMMAND_STR):
        await handle_command(message.content, message.channel)


@tasks.loop(hours=12)
async def refresh_data() -> None:
    """
    Refreshes data about the set on a loop.
    """
    DataCache.fetch_data(UPDATING_SETS)
    ##for s in UPDATING_SETS:
    ##    mgr = SetManager(s, True, False)
    ##    mgr.check_for_updates()


@client.event
async def on_ready() -> None:
    """
    Set up for the bot, which happens when it is first loaded.
    """
    Manamoji.cache_manamojis(client)
    DataCache.fetch_data(OLD_SETS)
    ##for s in OLD_SETS:
    ##    mgr = SetManager(s, True, False)
    ##    mgr.check_for_updates()
    print('Logged in as {0.user}'.format(client))


def main():
    refresh_data.start()
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
