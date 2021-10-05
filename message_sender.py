import discord

from settings import *

CLIENT = discord.Client()
BROADCAST_CHANNELS = []
LOGGING_CHANNELS = []

# returns a channel
def get_channel(channel_info):
    guild_id = channel_info['guild_id']
    channel_id = channel_info['channel_id']
    return CLIENT.get_guild(guild_id).get_channel(channel_id)

# returns a channel
def get_private_chat(user):
    #TODO: Figure out how to dm a user.
    pass

async def send(channels, message="", embed=None):
    for channel in channels:
        await channel.send(message, embed=embed)

async def send_message(channel, message, embed=None):
    await send([channel], message, embed=embed)

async def send_broadcast(message, embed=None):
    await send(BROADCAST_CHANNELS, message, embed=embed)

async def log(message, embed=None):
    await send(LOGGING_CHANNELS, message, embed=embed)





def command_response(command_lst):
    pass


def card_call_response(card_info, options):
    pass



def init():
    global BROADCAST_CHANNELS
    BROADCAST_CHANNELS = list()
    for channel_name in BROADCAST_CHANNEL_IDS:
         BROADCAST_CHANNELS.append(get_channel(BROADCAST_CHANNEL_IDS[channel_name]))

    global LOGGING_CHANNELS
    LOGGING_CHANNELS = list()
    for channel_name in LOGGING_CHANNEL_IDS:
         LOGGING_CHANNELS.append(get_channel(LOGGING_CHANNEL_IDS[channel_name]))


         
