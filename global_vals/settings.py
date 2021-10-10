from global_vals.utils import *
from global_vals.structs import *
from global_vals.consts import *

SETS = ['MID']
DEFAULT_SET = SETS[0]
FORMATS = ['PremierDraft', 'TradDraft', 'QuickDraft']
DEFAULT_FORMAT = FORMATS[0]
FORMAT_MAPPINGS = dict()
DEFAULT_COLUMNS = ["Color", "Rarity", "ALSA", "ATA", "# GP", "GP WR", "# GIH", "GIH WR", "IWD"]
DEFAULT_START_DATE = '2019-01-01'
SET_CONFIG = dict()
BROADCAST_CHANNEL_IDS = dict()
LOGGING_CHANNEL_IDS = dict()
USER_CONFIG = dict()


def load_defaults_config():
    """
    Reads the defaults.config file and update many of the golbal variables.
    Most importantly are the SETS and FORMATS
    """
    config_data = load_json_file(CONFIG_DIR, "defaults.config")

    global SETS
    SETS = config_data['SETS']
    print(f"'SETS': {SETS}")

    global DEFAULT_SET
    DEFAULT_SET = SETS[0]
    print(f"'DEFAULT_SET': {DEFAULT_SET}")

    global FORMATS
    FORMATS = config_data['FORMATS']
    print(f"'FORMATS': {FORMATS}")

    global DEFAULT_FORMAT
    DEFAULT_FORMAT = FORMATS[0]
    print(f"'DEFAULT_FORMAT': {DEFAULT_FORMAT}")

    global DEFAULT_COLUMNS
    DEFAULT_COLUMNS = config_data['DEFAULT_COLUMNS']

    global DEFAULT_START_DATE
    DEFAULT_START_DATE = config_data['DEFAULT_START_DATE']
    print(f"'DEFAULT_START_DATE': {DEFAULT_START_DATE}")

    global BROADCAST_CHANNEL_IDS
    BROADCAST_CHANNEL_IDS = config_data['BROADCAST_CHANNELS']
    print(f"'BROADCAST_CHANNEL_IDS': {BROADCAST_CHANNEL_IDS}")

    global LOGGING_CHANNEL_IDS
    LOGGING_CHANNEL_IDS = config_data['LOGGING_CHANNELS']
    print(f"'LOGGING_CHANNEL_IDS': {LOGGING_CHANNEL_IDS}")


def load_set_config():
    """
    Reads the sets.config file and updates the SET_CONFIG
    object for extra set information.
    """
    config_data = load_json_file(CONFIG_DIR, "sets.config")
    global SET_CONFIG
    SET_CONFIG = config_data['SET_CONFIG']
    print(f"'SET_CONFIG': {[x for x in SET_CONFIG]}")


def save_set_config() -> bool:
    """
    Saves the SET_CONFIG object to the sets.config file.
    :return: Whether the save was successful.
    """
    success = save_json_file(CONFIG_DIR, "sets.config", SET_CONFIG)
    return success


def update_set_config():
    print("update_set_config not currently implemented.")


def load_user_config():
    """
    Reads the users.config file and updates the USER_CONFIG
    object with extra user information.
    """
    config_data = load_json_file(CONFIG_DIR, "users.config")
    global USER_CONFIG
    USER_CONFIG = config_data


def save_user_config() -> bool:
    """
    Saves the user USER_CONFIG object to the users.config file.
    :return: Whether the save was successful.
    """
    success = save_json_file(CONFIG_DIR, "users.config", USER_CONFIG)
    return success


def get_user_formats(username) -> list[str]:
    """
    Gets the default formats a user uses from the USER_CONFIG object.
    If the user doesn't exist, automatically adds them to the USER_CONFIG,
    using the DEFAULT_FORMAT as format of choice, and saves the config.
    :param username: The username of the user.
    :return: A list of format strings, defaulting to the DEFAULT_FORMAT.
    """
    formats = []

    # Get the formats the use cares about, if they exist in the config.
    if username in USER_CONFIG:
        for f in USER_CONFIG[username]['Formats']:
            if USER_CONFIG[username]['Formats'][f]:
                formats.append(f)
    else:
        config_struct = gen_user_config_struct()
        config_struct['Formats'][DEFAULT_FORMAT] = True
        USER_CONFIG[username] = config_struct
        save_user_config()

    # If no formats are in the format list, add the default one.
    if len(formats) == 0:
        formats.append(DEFAULT_FORMAT)
    
    return formats


def update_user_formats(username: str, formats: list[str]) -> str:
    """
    Update the USER_CONFIG for the user based on the formats handed in.
    :param username: The use to change th data for
    :param formats: The formats to change
    :return: A string to use as a response to the user.
    """

    raise NotImplementedError("'update_user_formats' is not currently finished.")
    # TODO: Consider having this reset formats, rather than invert the provided ones.
    to_change = formats
    if formats in FORMAT_MAPPINGS:
        to_change = FORMAT_MAPPINGS[formats]

    # Get the formats the use cares about, if they exist in the config.
    if username in USER_CONFIG:
        config_struct = USER_CONFIG[username]['Formats']
    else:
        config_struct = gen_user_config_struct()

    if to_change in USER_CONFIG[username]['Formats']:
        val = USER_CONFIG[username]['Formats'][to_change]
        USER_CONFIG[username]['Formats'][to_change] = not val
        USER_CONFIG[username] = config_struct
        if save_user_config():
            return f"{to_change} updated to '{not val}'."
        else:
            return f"Failed to update user config!"
    else:
        return f"No format found for value '{formats}'."


load_defaults_config()
load_set_config()
load_user_config()
