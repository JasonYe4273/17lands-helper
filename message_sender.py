import discord

from settings import *

CLIENT = discord.Client()
  

# returns a channel
def get_channel(channel_info):
    guild_id = channel_info['guild_id']
    channel_id = channel_info['channel_id']
    return client.get_guild(guild_id).get_channel(channel_id)

# returns a channel
def get_private_chat(user):
    #TODO: Figure out how to dm a user.
    pass

def send_msg(channels, message, embed):
    for channel in channels:
        await channel.send(message, embed=embed)

async def send_embed_message(channel, embed):
    await channel.send(embed=embed)

async def send_message(channel, message):
    await channel.send(message)

async def send_embed_broadcast(embed):
    for channel_name in BROADCAST_CHANNELS:
        await send_embed_message(get_channel(BROADCAST_CHANNELS[channel_name]), embed)

async def send_broadcast(message):
    for channel_name in BROADCAST_CHANNELS:
        await send_message(get_channel(BROADCAST_CHANNELS[channel_name]), message)

async def log(message):
    for channel_name in LOGGING_CHANNELS:
        await send_message(get_channel(LOGGING_CHANNELS[channel_name]), message)






def init():
    global BROADCAST_CHANNELS
    BROADCAST_CHANNELS = list()
    for channel_name in BROADCAST_CHANNEL_IDS:
         BROADCAST_CHANNELS.append(get_channel(channel_info[channel_name]))

    global LOGGING_CHANNELS
    LOGGING_CHANNELS = list()
    for channel_name in LOGGING_CHANNEL_IDS:
         LOGGING_CHANNELS.append(get_channel(channel_info[channel_name]))


         
