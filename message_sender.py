import discord

from settings import *
from message_parser import *

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

async def handle_message_actions(actions):
    for action in actions:
        if not action["CHANNELS"]:
            continue # Can't send a message to no channels
        elif not action["MSG"] and not action["EMBED"]:
            continue # Can't send a message with no content
        else:
           await send(action["CHANNELS"], action["MSG"], action["EMBED"])


def gen_message_action_struct():
    msg_action = {
        "CHANNELS" : None,
        "MSG" : None,
        "EMBED" : None
    }
    return msg_action


def command_response(command_info, channel):
    msg_action = gen_message_action_struct()
    msg_action["CHANNELS"] = [channel]

    
    if command_str in ['colors', 'colours']:
        msg_action["EMBED"] = supported_color_strings()
    elif command_str in ['h', 'help']:
        msg_action["MSG"] = 'Read the README here: <https://github.com/JasonYe4273/17lands-helper>'
    elif command_str == 'code':
        msg_action["MSG"] = '<https://github.com/JasonYe4273/17lands-helper>'
    elif command_str in ['color_rank', 'colour_rank', 'rank']:
        msg_action["EMBED"] = gen_colour_rating_embed()


    return msg_action


def card_call_response(card_info, options, channel):
    msg_action = gen_message_action_struct()
    msg_action["CHANNELS"] = [channel]

    # TODO: Generate embed for card based on data.
    if card_info['err_msg'] is not None:
        msg_action["MSG"] = card_info['err_msg']
    else:
        msg_action["EMBED"] = gen_card_embeds_V2(card_info)
        
    return msg_action



async def send_response(message):
    msg_actions = list()
    msg = message.content
    user = message.author
    channel = message.channel
    
    if msg.startswith(COMMAND_STR):
        # TODO: Split string on spaces, remove first element.
        print(msg)
        command_info = parse_command_call(msg)
        print(command_info)
        action = parse_command_call(command_info, channel)
        print(action)
        msg_actions.append(action)
    else:
        card_infos = parse_card_calls(msg, user)
        for card_info in card_infos:
            print(card_info)
            action = card_call_response(card_info, None, channel)
            print(action)
            msg_actions.append(action)

    await handle_message_actions(msg_actions)




def init():
    global BROADCAST_CHANNELS
    BROADCAST_CHANNELS = list()
    for channel_name in BROADCAST_CHANNEL_IDS:
         BROADCAST_CHANNELS.append(get_channel(BROADCAST_CHANNEL_IDS[channel_name]))

    global LOGGING_CHANNELS
    LOGGING_CHANNELS = list()
    for channel_name in LOGGING_CHANNEL_IDS:
         LOGGING_CHANNELS.append(get_channel(LOGGING_CHANNEL_IDS[channel_name]))


         
