def format_data(data):
    if type(data) != float:
        return str(data)
    elif data < 1:
        return "{:.1f}%".format(data * 100)
    else:
        return "{:.2f}".format(data)

# Get 17lands-compatible card name given Scryfall card object
def get_card_name(card):
    name = card['name']
    split = name.find('/')
    if split == -1:
        return name
    else:
        return name[:split].trim()