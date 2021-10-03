import os
import json

def format_data(data):  
    if type(data) != float:
        return str(data)
    elif data < 1:
        return "{:.2f}%".format(data * 100)
    elif data == round(data, 0):
        return str(int(data))
    else:
        return "{:.2f}".format(data)

# Get 17lands-compatible card name given Scryfall card object
def get_card_name(card):
    name = card['name']
    split = name.find('/')
    if split == -1:
        return name
    else:
        print(name[:split].strip())
        return name[:split].strip()


def load_json_file(folder, filename):
    filepath = os.path.join(folder, filename)
    print(f'Parsing {filename}...')

    try:
        json_str = ''
        with open(filepath, 'r') as f:
            json_str = f.read()
            f.close()
        
            return json.loads(json_str)
    except Exception as ex:
        print(f'Error reading json file {filename}')
        print(ex)
        return None


def save_json_file(folder, filename, data):
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
