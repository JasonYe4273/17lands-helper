def gen_card_info_struct():
    return {
        'name': None,
        'stored_name': None,
        'mana_cost': None,
        'cmc': None,
        'color_identity': None,
        'set': None,
        'formats': None,
        'columns': None,
        'colors': None,
        'id': None,
        'url': None,
        'err_msg': None
    }


def gen_metadata_dict_struct():
    ret = {
        'Winrate': None,
        'Winrate Delta': None,
        'Games Played': None,
        'Metagame Share': None,
        'Top Commons': None,
        'Top Uncommons': None
    }
    return ret


def gen_card_call_struct():
    ret = {
        'CARD': gen_card_info_struct(),
        'SET': None,
        'FORMATS': None,
        'COLORS': None,
        'COLUMNS': None,
        'ERR': None,
        'EXTRA': None
    }
    return ret


def gen_msg_response_struct():
    ret = {
        'TYPE': None,  # 'MSG', 'EMBED', 'FILE'
        'CONTENT': None,
        'CALLBACK': None,
        'PM': None,
        'BROADCAST': None
    }
    return ret


def gen_user_config_struct():
    ret = {
        "Formats": {
            "PremierDraft": False,
            "TradDraft": False,
            "QuickDraft": False
        }
    }
    return ret
