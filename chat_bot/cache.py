import requests
import time
from datetime import date

from chat_bot.utils.settings import SETS, FORMATS, START_DATE


cache: dict = {s: {f: {} for f in FORMATS} for s in SETS}


def fetch_data(sets: list[str]) -> None:
    """
    Gets the data the bot uses.
    :param sets: The list of sets to get data for.
    """
    for s in sets:
        cache[s] = {f: {} for f in FORMATS}
        for f in FORMATS:
            success = False
            while not success:
                try:
                    print(f'Fetching data for {s} {f}...')
                    response = requests.get(
                        'https://www.17lands.com/card_ratings/data?' +
                        f'expansion={s}&format={f}&start_date={START_DATE}&end_date={date.today()}'
                    )
                    for c in response.json():
                        cache[s][f][c['name']] = c
                    success = True
                    print('Success!')
                except Exception:
                    print('Failed; trying again in 30s')
                    time.sleep(30)
