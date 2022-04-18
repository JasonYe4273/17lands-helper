import requests


# Get 17lands-compatible card name given Scryfall card object
def get_card_name(card: dict) -> str:
    """
    Gets a usable card name from card data.
    :param card: The json object of the card.
    :return: The simple card name.
    """
    name = card['name']
    split = name.find('/')
    if split == -1:
        return name
    else:
        print(name[:split].strip())
        return name[:split].strip()


def query_scryfall(raw_card_name: str) -> dict:
    # Try get unique card from Scryfall
    try:
        response = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={raw_card_name}').json()
        if response['object'] == 'error':
            if response['details'][:20] == 'Too many cards match':
                return {'error': f'Error: multiple card matches for "{raw_card_name}"'}
            else:
                return {'error': f'Error: cannot find card "{raw_card_name}"'}
        else:
            return response
    except Exception:
        return {'error': f'Error querying Scryfall for {raw_card_name}'}
