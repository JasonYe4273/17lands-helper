import re

from global_vals.settings import *
from global_vals.consts import *
from global_vals.WUBRG import get_color_identity

from messaging.embed_maker import *
from datetime import date, timedelta


# region Card Call Parsing
# If this is in the opt_str, then use verbose.
verbose_re = re.compile(r'([Vv]erbose ?|-[Vv])')

# There should only be one of each of these.
start_re = re.compile(r'([Ss]tart|-[Ss])=([0-9][0-9]-[0-9][0-9]-[0-9][0-9])')
end_re = re.compile(r'([Ee]nd|-[Ee])=([0-9][0-9]-[0-9][0-9]-[0-9][0-9])')

# There should likely only be one of any of these.
month_re = re.compile(r'([Mm]onths?|-[Mm])=([0-9]*)')
week_re = re.compile(r'([Ww]eeks?|-[Ww])=([0-9]*)')
day_re = re.compile(r'([Dd]ays?|-[Dd])=([0-9]*)')

# This could happen more than once, and could be a comma separated list of colour aliases
color_re = re.compile(r'([Cc]olou?rs?|-[Cc])=([A-Za-z,]*)')

# This could happen more than once, and could be a comma separated list of format aliases
format_re = re.compile(r'([Ff]ormats?|-[Ff])=([a-zA-Z0-9,]*)')

# This should happen once, and be a 3 character string of letters and numbers.
set_re = re.compile(r'([Ss]et=([a-zA-Z0-9]{3}))')


def parse_options(opt_str):
    """
    Parses the options that can accompany a card call into a series
    of usable values.
    :param opt_str: The list of options to parse
    :return: An options call struct.
    """

    ret = gen_options_call_struct()
    ret["start"] = DEFAULT_START_DATE
    ret["end"] = str(date.today())

    verbose_match = verbose_re.search(opt_str)
    if verbose_match is not None:
        ret['verbose'] = True

    # Handle the start and end date if either exists.
    start_match = start_re.search(opt_str)
    end_match = end_re.search(opt_str)
    if start_match is not None:
        ret['start'] = start_match.group(2)
    if end_match is not None:
        ret['end'] = end_match.group(2)

    # If a defined start or end date doesn't exist, look for time periods.
    if start_match is None and end_match is None:
        day_match = day_re.search(opt_str)
        week_match = week_re.search(opt_str)
        month_match = month_re.search(opt_str)
        today = date.today()

        # Use the first time period found, and base the start date on that.
        if day_match is not None:
            days = int(day_match.group(2))
            ret['start'] = str(today - timedelta(days=days))
        elif week_match is not None:
            weeks = int(week_match.group(2))
            ret['start'] = str(today - timedelta(weeks=weeks))
        elif month_match is not None:
            months = int(month_match.group(2))
            ret['start'] = str(today - timedelta(days=months*30))

    # Get the list of colours to display stats for, if it exists.
    color_match = color_re.search(opt_str)
    if color_match is not None:
        color_str = color_match.group(2)
        colors = color_str.split(',')
        for c in colors:
            c_id = get_color_identity(c)
            if c_id == 'WUBRGC':
                continue
            if c_id not in ret['colors']:
                ret['colors'].append(c_id)

    # Get the list of formats to display stats for, if it exists.
    format_match = format_re.search(opt_str)
    if format_match is not None:
        format_str = format_match.group(2).lower()
        formats = format_str.split(',')
        for f in formats:
            if f not in FORMAT_MAPPINGS:
                continue
            if FORMAT_MAPPINGS[f] not in ret['formats']:
                ret['formats'].append(FORMAT_MAPPINGS[f])

    # Get the set to pull data from, if it exists.
    set_match = set_re.search(opt_str)
    if set_match is not None:
        ret['set'] = set_match.group(2).upper()

    return ret


def parse_card_call(card_name, opt_str, username):
    info = get_scryfall_card_data(card_name)

    if info['err_msg'] is not None:
        return info

    info['formats'] = settings.get_user_formats(username)
    info['columns'] = settings.DEFAULT_COLUMNS

    # Get all of the 2-colour combinations which contains the card colour.
    color_sets = get_color_supersets(info['color_identity'], 2)
    info['colors'] = [''] + (color_sets if color_sets else [info['color_identity']])
    
    # If there are options to use, parse them and modify the info.
    if opt_str:
        options = parse_options(opt_str)

        # Override the colours, if they are provided.
        if options['colors']:
            info['colors'] = [''] + options['colors']

        # Override the formats, if they are provided.
        if options['formats']:
            info['formats'] = options['formats']

        # Override the set, if one is provided.
        if options['set']:
            info['set'] = options['set']

    # Validate the data
    if info['set'] not in settings.SETS:
        info['err_msg'] = f"Data on '{info['name']}' in set '{info['set']}' not available."
        return info

    return info


# '"?(.*?)"? ?' finds a singular card name, ignoring quotes and a trailing space.
# '(?:\| ?(.*?))?' finds the options, without the bar, if they exist.
re_comp = re.compile(r'(\{"?(.*?)"? ?(?:\| ?(.*?))?\})')


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
        "command": None,
        "params": None
    }
    return command_info


def parse_command_call(command_str):
    info = gen_command_info_struct()
    lst = command_str.split(' ')

    # Remove the '17!' from the start.
    lst.pop(0)

    # Remove the command from the start, and log it.
    info["command"] = lst.pop(0)

    # Add the rest of the options.
    info["params"] = lst

    return info

