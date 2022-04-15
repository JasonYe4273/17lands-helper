from typing import Union


def format_data(data: Union[float, int, str]) -> str:
    """
    Automatically formats data to the correct number of characters for display in embeds.
    Also automatically changes values less than 1 to percentages.
    :param data: The data to format.
    :return: The formatted data as a string.
    """
    if type(data) != float:
        return str(data)
    # TODO: Make this a range from -1/0 to 1.
    elif data < 1:
        return "{:.1f}%".format(data * 100)
    else:
        return "{:.2f}".format(data)


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
