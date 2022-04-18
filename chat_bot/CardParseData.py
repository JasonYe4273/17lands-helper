from typing import Optional
import re
from datetime import date, timedelta

from WUBRG import FAILSAFE, get_color_identity
from chat_bot.utils.settings import FORMAT_MAPPINGS


class CardParseData:
    def __init__(self):

        pass

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
            self.handle_verbose()

            self.START_DATE: Optional[date] = None
            self.END_DATE: Optional[date] = None
            self.handle_date_range()

            self.COLORS: Optional[list[str]] = None
            self.handle_color_filter()

            self.FORMATS: Optional[list[str]] = None
            self.handle_format_filter()

            self.SET: Optional[str] = None
            self.handle_set_override()

        def handle_verbose(self):
            """ Handles self.VERBOSE """
            # Find the flag for verbose.
            verbose_match = self.verbose_re.search(self._options_text)
            self.VERBOSE = verbose_match is not None
            if self.VERBOSE:
                print("Verbose Mode enabled.")

        def handle_date_range(self):
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
                # Initialize default date values,
                self.START_DATE = date(2020, 1, 1)
                self.END_DATE = date.today()
                # And overwrite with found values
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

        def handle_color_filter(self):
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

        def handle_format_filter(self):
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

        def handle_set_override(self):
            # Get the set to pull data from, if it exists.
            set_match = self.set_re.search(self._options_text)

            if self.VERBOSE:
                print(f"set_match: {set_match is not None}")

            if set_match:
                self.SET = set_match.group(2).upper()


if __name__ == "__main__":
    opt = CardParseData.CardParseOptions("-v -c=r,w,b,wubrg -w=2 set=KHM")
    print(opt.__dict__)
