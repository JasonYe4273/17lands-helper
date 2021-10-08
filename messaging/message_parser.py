import re

from messaging.embed_maker import *


# region Card Call Parsing
# TODO: Move this into message sender.
# Parsing the card call into a card info object makes sense,
# but for the command calls, functions will need to be called
# meaning trying to return a function pointer and list of arguments.s


def parse_options(opt_str):
    option_keys = ['verbose', '-v', 'start=', '-s=', 'end=', '-e=', 'months=', '-m=', 'weeks=', '-w=', 'days=', '-c=', 'colors=', '-f=', 'formats=', 'set=']

    pass


def parse_card_call(card_name, opt_str, username):
    info = get_scryfall_data(card_name)

    if info['err_msg'] is not None:
        return info

    info['formats'] = settings.get_user_formats(username)
    info['columns'] = settings.DEFAULT_COLUMNS

    # Get all of the 2-colour combinations which contains the card colour.
    color_sets = get_color_supersets(info['color_identity'], 2)
    info['colors'] = [''] + (color_sets if color_sets else [info['color_identity']])
    
    # If there are options to use, parse them and modify the info.
    if opt_str != '':
        options = parse_options(opt_str)

        # TODO: Allow override in options
        #set_override = ""
        #info['set'] = set_override]

        # TODO: Allow override in options
        #color_override = []
        #info['colors'] = [''] + color_override

    # Validate the data
    if info['set'] not in settings.SETS:
        info['err_msg'] = f"Data on '{info['name']}' in set '{info['set']}' not available."
        return info


    return info


# '"?(.*?)"? ?' finds a singular card name, ignoring quotes and a trailing space.
# '(?:\| ?(.*?))?' finds the options, without the bar, if they exist.
re_card_str = r'({{"?(.*?)"? ?(?:\| ?(.*?))?}})'
re_comp = re.compile(re_card_str)

def parse_card_calls(msg, user):
    card_infos = []
    
    card_calls = re_comp.findall(msg)
    for call in card_calls:
        print(f"Card: '{call[1]}', Options: '{call[2]}'")
        card_info = parse_card_call(call[1], call[2], user)
        card_infos.append(card_info)

    return card_infos
# endregion Card Call Parsing



### Command Parsing ###

def gen_command_info_struct():
    command_info = {
        "COMMAND" : None,
        "OPTIONS" : None
    }
    return command_info

def parse_command_call(command_str):
    info = gen_command_info_struct()
    lst = command_str.split(' ')

    # Remove the '17!' from the start.
    lst.pop(0)

    # Remove the command from the start, and log it.
    info["COMMAND"] = lst.pop(0)

    # Add the rest of the options.
    info["OPTIONS"] = lst

    return info

