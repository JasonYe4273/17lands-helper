def gen_card_info_struct() -> dict:
    ret = {
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
    return ret


def gen_metadata_dict_struct() -> dict:
    ret = {
        'Winrate': None,
        'Winrate Delta': None,
        'Games Played': None,
        'Metagame Share': None,
        'Top Commons': None,
        'Top Uncommons': None
    }
    return ret


def gen_card_call_struct() -> dict:
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


def gen_msg_response_struct() -> dict:
    ret = {
        'TYPE': None,  # 'MSG', 'EMBED', 'FILE'
        'CONTENT': None,
        'CALLBACK': None,
        'PM': None,
        'BROADCAST': None
    }
    return ret


def gen_user_config_struct() -> dict:
    ret = {
        "Formats": {
            "PremierDraft": False,
            "TradDraft": False,
            "QuickDraft": False
        }
    }
    return ret
