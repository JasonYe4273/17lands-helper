from typing import Optional
import re
from datetime import date, timedelta

from WUBRG import FAILSAFE, get_color_identity, get_color_supersets
from chat_bot.utils.settings import FORMAT_MAPPINGS, DEFAULT_FORMAT
from chat_bot.message_maker import query_scryfall


class CardParseOptions:
    # If this is in the opt_str, then use verbose.
    verbose_re = re.compile(r'([Vv]erbose ?|-[Vv])')

    # There should only be one of each of these.
    start_re = re.compile(r'([Ss]tart|-[Ss])=([0-9][0-9]-[0-9][0-9]-[0-9][0-9])')
    end_re = re.compile(r'([Ee]nd|-[Ee])=([0-9][0-9]-[0-9][0-9]-[0-9][0-9])')

    # There should likely only be one of any of these.
    month_re = re.compile(r'([Mm]onths?|-[Mm])=([0-9]*)')
    week_re = re.compile(r'([Ww]eeks?|-[Ww])=([0-9]*)')
    day_re = re.compile(r'([Dd]ays?|-[Dd])=([0-9]*)')

    # This could happen more than once, and could be a comma separated list of colour aliases
    color_re = re.compile(r'([Cc]olou?rs?|-[Cc])=([A-Za-z,]*)')

    # This could happen more than once, and could be a comma separated list of format aliases
    format_re = re.compile(r'([Ff]ormats?|-[Ff])=([a-zA-Z0-9,]*)')

    # This should happen once, and be a 3 character string of letters and numbers.
    set_re = re.compile(r'([Ss]et=([a-zA-Z0-9]{3}))')

    def __init__(self, options: str = ''):
        self._options_text = options
        self.VERBOSE: bool = False
        self.START_DATE: Optional[date] = None
        self.END_DATE: Optional[date] = None
        self.COLORS: Optional[list[str]] = None
        self.FORMATS: Optional[list[str]] = None
        self.SET: Optional[str] = None

        self._handle_verbose()
        self._handle_date_range()
        self._handle_color_filter()
        self._handle_format_filter()
        self._handle_set_override()

    def _handle_verbose(self):
        """ Handles self.VERBOSE """
        # Find the flag for verbose.
        verbose_match = self.verbose_re.search(self._options_text)
        self.VERBOSE = verbose_match is not None
        if self.VERBOSE:
            print("Verbose Mode enabled.")

    def _handle_date_range(self):
        """ Handles self.START_DATE and self.END_DATE"""
        # Find the flags for start and end dates.
        start_match = self.start_re.search(self._options_text)
        end_match = self.end_re.search(self._options_text)

        if self.VERBOSE:
            print(f"start_match: {start_match is not None}")
            print(f"end_match: {end_match is not None}")

        # If both a start or end date exists, use them for the range.
        # TODO: Convert these to date objects.
        if start_match or end_match:
            # Set found values
            if start_match:
                self.START_DATE = start_match.group(2)
            if end_match:
                self.END_DATE = end_match.group(2)
        # If neither exist, check for a time offset flag.
        else:
            self.handle_time_offset()

    def handle_time_offset(self) -> None:
        """ Handles self.START_DATE and self.END_DATE """
        # Find the flags for day, week or month offsets.
        day_match = self.day_re.search(self._options_text)
        week_match = self.week_re.search(self._options_text)
        month_match = self.month_re.search(self._options_text)

        if self.VERBOSE:
            print(f"day_match: {day_match is not None}")
            print(f"week_match: {week_match is not None}")
            print(f"month_match: {month_match is not None}")

        # There are any matches, set the date range.
        if day_match or week_match or month_match:
            self.END_DATE = date.today()

            # Use the first time period found, and base the start date on that.
            if day_match:
                days = int(day_match.group(2))
                self.START_DATE = self.END_DATE - timedelta(days=days)
            elif week_match:
                weeks = int(week_match.group(2))
                self.START_DATE = self.END_DATE - timedelta(weeks=weeks)
            elif month_match:
                months = int(month_match.group(2))
                self.START_DATE = self.END_DATE - timedelta(days=months * 30)

    def _handle_color_filter(self):
        # Get the list of colours to display stats for, if it exists.
        color_match = self.color_re.search(self._options_text)

        if self.VERBOSE:
            print(f"color_match: {color_match is not None}")

        # If the flag is found,
        if color_match:
            # Initialize a list for COLORS, and split the found values.
            self.COLORS = list()
            colors = color_match.group(2).split(',')
            if self.VERBOSE:
                print(f"colors: {colors is not None}")

            # For each value,
            for c in colors:
                # Clean the value,
                c_id = get_color_identity(c)
                # And if it is new and valid, append it to the list.
                if c_id != FAILSAFE and c_id not in self.COLORS:
                    self.COLORS.append(c_id)

    def _handle_format_filter(self):
        # Get the list of formats to display stats for, if it exists.
        format_match = self.format_re.search(self._options_text)

        if self.VERBOSE:
            print(f"format_match: {format_match is not None}")

        if format_match:
            # Initialize a list for FORMATS, and split the found values.
            self.FORMATS = list()
            formats = format_match.group(2).lower().split(',')
            if self.VERBOSE:
                print(f"formats: {formats is not None}")

            # For each value,
            for f in formats:
                # If the alias is found in FORMAT_MAPPING get the name,
                if f in FORMAT_MAPPINGS:
                    format_name = FORMAT_MAPPINGS[f]
                    # And if it is a new item, add it to the list.
                    if format_name not in self.FORMATS:
                        self.FORMATS.append(format_name)

    def _handle_set_override(self):
        # Get the set to pull data from, if it exists.
        set_match = self.set_re.search(self._options_text)

        if self.VERBOSE:
            print(f"set_match: {set_match is not None}")

        if set_match:
            self.SET = set_match.group(2).upper()


class CardParseData:
    def __init__(self, card: dict, options: CardParseOptions):
        self.OPTIONS = options
        self.CARD_DATA = card
        self._fill_missing_options()

    def _fill_missing_options(self):
        # info['columns'] = settings.DEFAULT_COLUMNS

        if not self.OPTIONS.COLORS:
            self.OPTIONS.COLORS = [''] + get_color_supersets(self.CARD_DATA['color_identity'], 2)

        if not self.OPTIONS.FORMATS:
            # info['formats'] = settings.get_user_formats(username)
            self.OPTIONS.FORMATS = [DEFAULT_FORMAT]

        if not self.OPTIONS.SET:
            # TODO: Search through the sets and find the most recent set in which the card was printed.
            self.OPTIONS.SET = 'NEO'

        if not self.OPTIONS.START_DATE:
            if self.OPTIONS.SET:
                # TODO: Set this to the start of the set.
                self.OPTIONS.START_DATE = date(2020, 1, 1)

        if not self.OPTIONS.END_DATE:
            self.OPTIONS.END_DATE = date.today()


class MessageParseData:
    multi_card_re = re.compile(r'(?:"(.*?)")+')
    single_card_re = re.compile(r'{{(.*?) ?(?:\||}})')
    options_re = re.compile(r'\| ?(.*?)?}}')

    def __init__(self, cmd_str: str):
        """ :param cmd_str: The {{card_name | options}} style string. """
        self._cmd_str = cmd_str
        self._options_text = None
        self._card_name_list = []
        self.OPTIONS = None
        self.CARDS = []
        self.CARD_CALLS = []

        self._parse_options()
        self._parse_cards()
        self._gen_card_calls()

    def _parse_options(self):
        # Attempt to find the options in the string.
        options_match = self.options_re.search(self._cmd_str)

        # If found, use the options, otherwise use the empty string.
        if options_match:
            self._options_text = options_match[1]
        else:
            self._options_text = ''
        self.OPTIONS = CardParseOptions(self._options_text)

        if self.OPTIONS.VERBOSE:
            print(f'cmd_str: {self._cmd_str}')
            print(f'options_text: {self._options_text}')

    def _parse_cards(self):
        # Attempt to find multiple card names in the query, separated by quotes.
        self._card_name_list = self.multi_card_re.findall(self._cmd_str)

        # If no names were found, attempt to parse query as a single card name.
        if not self._card_name_list:
            self._card_name_list = self.single_card_re.findall(self._cmd_str)

        if self.OPTIONS.VERBOSE:
            print(f'card_name_list: {self._card_name_list}')

        # For each card name found, get the card from scryfall.
        for name in self._card_name_list:
            card = query_scryfall(name)
            if 'error' not in card:
                self.CARDS.append(card)

    def _gen_card_calls(self):
        for card in self.CARDS:
            # TODO: Make a deep copy of options here.
            options_copy = self.OPTIONS
            card_call = CardParseData(card, options_copy)
            self.CARD_CALLS.append(card_call)


if __name__ == "__main__":
    test_strings = list()
    test_strings.append('{{"Virus Beetle | -v -c=r,w,b,wubrg -w=2 set=KHM}}')
    for string in test_strings:
        card_parse = MessageParseData(string)
        for card_call in card_parse.CARD_CALLS:
            print(card_call.__dict__)
            print(card_call.OPTIONS.__dict__)
