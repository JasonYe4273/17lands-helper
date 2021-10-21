import pandas as pd

from global_vals import settings
from global_vals.WUBRG import *


def get_set_tree_struct() -> dict:
    """
    Generates a dictionary tree of the sets, formats, and colour groups
    :return: A tree structure of the sets.
    """
    set_tree = dict()
    for s in settings.SETS:
        set_tree[s] = dict()
        for f in settings.FORMATS:
            set_tree[s][f] = dict()
            for c in COLOR_GROUPS:
                set_tree[s][f][c] = None
    return set_tree


def get_card_list_cache_struct() -> dict:
    """
    Generates a dictionary tree of the sets, formats, and colour groups
    :return: A tree structure of the sets.
    """
    set_tree = dict()
    for s in settings.SETS:
        set_tree[s] = set()
    return set_tree


PANDAS_CACHE = get_set_tree_struct()
DICT_CACHE = get_set_tree_struct()
WIN_RATES = get_set_tree_struct()
# TODO: Create a structure for time-based pulls.

CARD_LIST_CACHE = get_card_list_cache_struct()


# region DATA_CACHE
def query_dict_cache(s: str, f: str = None, c: str = None, card_name: str = None) -> dict or None:
    """
    Attempts to return a structure located in the DATA_CACHE.
    :param s: The set name
    :param f: The format name
    :param c: The colour identity
    :param card_name: The card name
    :return: The structure if it exists, None otherwise.
    """
    global DICT_CACHE
    if DICT_CACHE is None:
        return None
    if s not in DICT_CACHE:
        return None
    if f is None:
        return DICT_CACHE[s]

    if DICT_CACHE[s] is None:
        return None
    if f not in DICT_CACHE[s]:
        return None
    if c is None:
        return DICT_CACHE[s][f]

    if DICT_CACHE[s][f] is None:
        return None
    if c not in DICT_CACHE[s][f]:
        return None
    if card_name is None:
        return DICT_CACHE[s][f][c]

    if DICT_CACHE[s][f][c] is None:
        return None
    if card_name not in DICT_CACHE[s][f][c]:
        return None
    return DICT_CACHE[s][f][c][card_name]


def expand_dict_cache(s: str, f: str = None, c: str = None):
    """
    Attempts to fill in gaps the tree structure of the DATA_CACHE.
    This happens when a new set or format is added in the config.
    :param s: The set name
    :param f: The format name
    :param c: The colour identity
    """
    global DICT_CACHE

    if DICT_CACHE is None:
        DICT_CACHE = dict()
    if s is not None and query_dict_cache(s) is None:
        DICT_CACHE[s] = dict()
    if f is not None and query_dict_cache(s, f) is None:
        DICT_CACHE[s][f] = dict()
    if c is not None and query_dict_cache(s, f, c) is None:
        DICT_CACHE[s][f][c] = dict()


def set_dict_cache_value(val: object, s: str, f: str = None, c: str = None):
    """
    Adds a value to the position in the DATA_CACHE, while automatically
    creating any missing bits of structure needed.
    :param val: The value to add
    :param s: The set name
    :param f: The format name
    :param c: The colour identity
    """
    global DICT_CACHE
    expand_dict_cache(s, f, c)

    if f is None:
        DICT_CACHE[s] = val
    elif c is None:
        DICT_CACHE[s][f] = val
    else:
        DICT_CACHE[s][f][c] = val
# endregion DATA_CACHE


# region PANDAS_CACHE
def query_frames_cache(s: str, f: str = None, c: str = None, card_name: str = None) -> object:
    """
    Attempts to return a structure located in the PANDAS_CACHE.
    :param s: The set name
    :param f: The format name
    :param c: The colour identity
    :param card_name: The card name
    :return: The structure if it exists, None otherwise.
    """
    global PANDAS_CACHE
    if PANDAS_CACHE is None:
        return None
    if s not in PANDAS_CACHE:
        return None
    if f is None:
        return PANDAS_CACHE[s]  # Returns a dict()

    if PANDAS_CACHE[s] is None:
        return None
    if f not in PANDAS_CACHE[s]:
        return None
    if c is None:
        return PANDAS_CACHE[s][f]  # Returns a dict()

    if PANDAS_CACHE[s][f] is None:
        return None
    if c not in PANDAS_CACHE[s][f]:
        return None
    if card_name is None:
        return PANDAS_CACHE[s][f][c]  # Returns a pd.DataFrame

    if PANDAS_CACHE[s][f][c] is None:
        return None
    if card_name not in PANDAS_CACHE[s][f][c].index:
        return None
    return PANDAS_CACHE[s][f][c].loc[card_name]  # Returns a np.array


def expand_frames_cache(s: str, f: str = None, c: str = None):
    """
    Attempts to fill in gaps the tree structure of the PANDAS_CACHE.
    This happens when a new set or format is added in the config.
    :param s: The set name
    :param f: The format name
    :param c: The colour identity
    """
    global PANDAS_CACHE

    if PANDAS_CACHE is None:
        PANDAS_CACHE = dict()
    if s is not None and query_frames_cache(s) is None:
        PANDAS_CACHE[s] = dict()
    if f is not None and query_frames_cache(s, f) is None:
        PANDAS_CACHE[s][f] = dict()
    if c is not None and query_frames_cache(s, f, c) is None:
        PANDAS_CACHE[s][f][c] = dict()


def set_frames_cache_value(val: object, s: str, f: str = None, c: str = None):
    """
    Adds a value to the position in the PANDAS_CACHE, while automatically
    creating any missing bits of structure needed.
    :param val: The value to add
    :param s: The set name
    :param f: The format name
    :param c: The colour identity
    """
    global PANDAS_CACHE
    expand_frames_cache(s, f, c)

    if f is None:
        PANDAS_CACHE[s] = val
    elif c is None:
        PANDAS_CACHE[s][f] = val
    else:
        PANDAS_CACHE[s][f][c] = val
# endregion PANDAS_CACHE


# region CARD_LIST_CACHE
def query_card_list_cache(card_name: str) -> str or None:
    """
    Gets the most recent set a card has appeared in.
    :param card_name: The card name
    :return: The set code if it exists, None otherwise.
    """
    global CARD_LIST_CACHE
    for s in CARD_LIST_CACHE:
        if card_name in CARD_LIST_CACHE[s]:
            return s
    return None


def set_card_list_cache_value(val: set, s: str):
    """
    Adds a value to the position in the CARD_LIST_CACHE, while automatically
    creating any missing bits of structure needed.
    :param val: The set of card names to add
    :param s: The set name
    """
    global CARD_LIST_CACHE

    if CARD_LIST_CACHE is None:
        CARD_LIST_CACHE = dict()

    CARD_LIST_CACHE[s] = val
# endregion CARD_LIST_CACHE
