import os
import json
import requests
from time import sleep
from datetime import date, time, datetime, timedelta
import numpy as np
import pandas as pd
import WUBRG
from WUBRG import COLOUR_GROUPS, COLORS
import data_fetch
import data_crunch



DATA_CACHE = data_fetch.get_set_tree()
PANDAS_CACHE = data_fetch.get_set_tree()
WINRATES = data_fetch.get_set_tree()


def init_cache():
    # Update and load all data.
    data_fetch.update_all_data()
    data_fetch.load_all_data()

    global DATA_CACHE
    DATA_CACHE = data_fetch.DATA_CACHE

    global PANDAS_CACHE
    PANDAS_CACHE = data_fetch.PANDAS_CACHE

    #global WINRATES
    #WINRATES = data_fetch.WINRATES


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



if __name__ == "__main__":
    init_cache()
    pass
