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


PANDAS_CACHE = get_set_tree_struct()
DATA_CACHE = get_set_tree_struct()
WIN_RATES = get_set_tree_struct()
# TODO: Create a structure for time-based pulls.


# region DATA_CACHE
def query_cache(s: str, f: str = None, c: str = None, card_name: str = None) -> object:
    """
    Attempts to return a structure located in the DATA_CACHE.
    :param s: The set name
    :param f: The format name
    :param c: The colour identity
    :param card_name: The card name
    :return: The structure if it exists, None otherwise.
    """
    global DATA_CACHE
    if DATA_CACHE is None:
        return None
    if s not in DATA_CACHE:
        return None
    if f is None:
        return DATA_CACHE[s]

    if DATA_CACHE[s] is None:
        return None
    if f not in DATA_CACHE[s]:
        return None
    if c is None:
        return DATA_CACHE[s][f]

    if DATA_CACHE[s][f] is None:
        return None
    if c not in DATA_CACHE[s][f]:
        return None
    if card_name is None:
        return DATA_CACHE[s][f][c]

    if DATA_CACHE[s][f][c] is None:
        return None
    if card_name not in DATA_CACHE[s][f][c]:
        return None
    return DATA_CACHE[s][f][c][card_name]


def expand_cache(s: str, f: str = None, c: str = None):
    """
    Attempts to fill in gaps the tree structure of the DATA_CACHE.
    This happens when a new set or format is added in the config.
    :param s: The set name
    :param f: The format name
    :param c: The colour identity
    """
    global DATA_CACHE

    if DATA_CACHE is None:
        DATA_CACHE = dict()
    if s is not None and query_cache(s) is None:
        DATA_CACHE[s] = dict()
    if f is not None and query_cache(s, f) is None:
        DATA_CACHE[s][f] = dict()
    if c is not None and query_cache(s, f, c) is None:
        DATA_CACHE[s][f][c] = dict()


def set_cache(val: object, s: str, f: str = None, c: str = None):
    """
    Adds a value to the position in the DATA_CACHE, while automatically
    creating any missing bits of structure needed.
    :param val: The value to add
    :param s: The set name
    :param f: The format name
    :param c: The colour identity
    """
    global DATA_CACHE
    expand_cache(s, f, c)

    if f is None:
        DATA_CACHE[s] = val
    elif c is None:
        DATA_CACHE[s][f] = val
    else:
        DATA_CACHE[s][f][c] = val
# endregion DATA_CACHE


# region PANDAS_CACHE
def query_frames(s: str, f: str = None, c: str = None, card_name: str = None) -> object:
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


def expand_frames(s: str, f: str = None, c: str = None):
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
    if s is not None and query_frames(s) is None:
        PANDAS_CACHE[s] = dict()
    if f is not None and query_frames(s, f) is None:
        PANDAS_CACHE[s][f] = dict()
    if c is not None and query_frames(s, f, c) is None:
        PANDAS_CACHE[s][f][c] = dict()


def set_frames(val: object, s: str, f: str = None, c: str = None):
    """
    Adds a value to the position in the PANDAS_CACHE, while automatically
    creating any missing bits of structure needed.
    :param val: The value to add
    :param s: The set name
    :param f: The format name
    :param c: The colour identity
    """
    global PANDAS_CACHE
    expand_frames(s, f, c)

    if f is None:
        PANDAS_CACHE[s] = val
    elif c is None:
        PANDAS_CACHE[s][f] = val
    else:
        PANDAS_CACHE[s][f][c] = val
# endregion PANDAS_CACHE
