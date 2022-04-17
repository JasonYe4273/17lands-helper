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
