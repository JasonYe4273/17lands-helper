import os
import json

from global_vals.consts import STAT_FORMAT_STRINGS


def format_data(data):

    # TODO: Flesh out with the STAT_FORMAT_STRINGS mapping,
    # while adding in some extra handling for potential missing data.
    if type(data) != float:
        return str(data)
    elif data < 1:
        return "{:.2f}%".format(data * 100)
    elif data == round(data, 0):
        return str(int(data))
    else:
        return "{:.2f}".format(data)


def get_card_name(card: object) -> str:
    """
    Get a 17-lands compatible name from the card struct.
    :param card: The card struct.
    :return: The name of the card in the 17-lands data.
    """
    name = card['name']
    split = name.find('/')
    if split == -1:
        return name
    else:
        print(name[:split].strip())
        return name[:split].strip()


def load_json_file(folder, filename):
    """
    Loads and returns the data from a json file.
    :param folder: The folder the json file is in.
    :param filename: The name of the json file (including filetype).
    :return: An object contain the json data.
    """
    filepath = os.path.join(folder, filename)
    print(f'Reading {filename}...')

    try:
        with open(filepath, 'r') as f:
            json_str = f.read()
            f.close()
        
            return json.loads(json_str)
    except Exception as ex:
        print(f'Error reading json file {filename}')
        print(ex)
        return None


def save_json_file(folder, filename, data):
    """
    Saves provided data into the specified json file.
    :param folder: The folder the json file is in.
    :param filename: The name of the json file (including filetype).
    :param data: The object to be saved as json.
    :return: Whether the save operation was successful.
    """
    filepath = os.path.join(folder, filename)
    print(f'Parsing {filename}...')

    try:
        with open(filepath, 'w') as f:
            f.write(json.dumps(data, indent=4))
            f.close()
        
        print(f'File {filename} written to.')
        return True
    except Exception as ex:
        print(f'Error writing to json file {filename}')
        print(ex)
        return False
