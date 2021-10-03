from data_fetch import *
from data_crunch import *


def init_cache():
    # Update and load all data.
    data_fetch.update_all_data()
    data_fetch.load_all_data()


def query_scryfall(card_name):
    return data_fetch.get_scryfall_data(card_name)
    

def query_cache(_set, _format, color_filter, cardname):
    if _set not in DATA_CACHE:
        return None
    if _format not in DATA_CACHE[_set]:
        return None
    if color_filter not in DATA_CACHE[_set][_format]:
        return None
    if cardname not in DATA_CACHE[_set][_format][color_filter]:
        return None
    return DATA_CACHE[_set][_format][color_filter][cardname]


def query_frames(_set, _format, color_filter, cardname):
    if _set not in PANDAS_CACHE:
        return None
    if _format not in PANDAS_CACHE[_set]:
        return None
    if color_filter not in PANDAS_CACHE[_set][_format]:
        return None
    if cardname not in PANDAS_CACHE[_set][_format][color_filter]:
        return None
    return PANDAS_CACHE[_set][_format][color_filter].loc[cardname]


if __name__ == "__main__":
    init_cache()
    pass
