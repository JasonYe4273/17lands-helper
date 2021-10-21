import numpy as np
import pandas as pd

from global_vals.WUBRG import COLOR_GROUPS, COLORS, get_color_identity
import data_fetch
from global_vals.structs import *
import global_vals.settings as settings
import data_handling.data_cache as cache


# region Pandas Filters
def min_play_filter(df: pd.DataFrame, p: float) -> pd.DataFrame:
    """
    Filters out cards that have a number of games played less than p% of # GP.
    :param df: The DataFrame to filter
    :param p: The percent of #GP to act as the threshold. (1 = 1.00%)
    :return: Cards that meet the minimum number of games played.
    """
    min_game = df['# GP'].sum() * (p / 100)
    return df[df['# GP'] >= min_game]


def color_id_filter(df: pd.DataFrame, color_string: str) -> pd.DataFrame:
    """
    Filters out cards that don't fall within the colour identity.
    :param df: The DataFrame to filter
    :param color_string: The colour string to filter on
    :return: Cards that meet the colour criteria.
    """
    if color_string is not None and color_string != '':
        return df[df['Color'].apply(lambda x: set(x) <= set(color_string))]
    else:
        return df


def rarity_filter(df: pd.DataFrame, rarity: str) -> pd.DataFrame:
    """
    Filters out cards that aren't in the given rarities.
    :param df: The DataFrame to filter
    :param rarity: The rarities to filter on
    :return: Cards that match the given rarities.
    """
    if rarity is not None and rarity != '':
        return df[df['Rarity'].apply(lambda x: set(x) <= set(rarity))]
    else:
        return df
# endregion Pandas Filters


def get_top(df: pd.DataFrame, stat: str, n: int = 5,
            card_colors: str = None, card_rarity: str = None, min_thresh: float = 1,
            reverse: bool = False, columns: list[str] = None) -> pd.DataFrame:
    """
    Find the top/bottom x cards by stat, with the ability to filter by colour, games played and rarity.
    :param df: The DataFrame to filter
    :param stat: The column to filter on
    :param n: The number of card to return
    :param card_colors: The colour string to filter on
    :param card_rarity: The rarities to filter on
    :param min_thresh: The percent of #GP to act as the threshold. (1 = 1.00%)
    :param reverse: Sort by lowest or last picked
    :param columns: The columns to include in the output.
    If none include all columns in df.
    :return: A dataframe which contains the top (or bottom) n cards by stat,
    filtered on various criteria.
    """

    # If the DataFrame doesn't exist or is empty, return an empty DataFrame.
    if df is None or df.empty:
        return pd.DataFrame()

    # If columns is none, get the columns which currently exist in the DataFrame
    if columns is None:
        columns = list(df)

    # Apply the filters
    filtered = color_id_filter(df, card_colors)
    filtered = rarity_filter(filtered, card_rarity)
    filtered = min_play_filter(filtered, min_thresh)

    # If we're getting card pick info, we need to invert the ordering,
    # as the smallest numbers are the top-picked.
    smallest = (stat == "ALSA" or stat == "ATA")

    # If reverse is true, we need to find the lowest value, so invert the ordering.
    smallest = reverse != smallest  # != is a functional XOR.

    # Filter by smallest or largest
    if smallest:
        filtered = filtered.nsmallest(n, stat)
    else:
        filtered = filtered.nlargest(n, stat)

    # And set the title base on the reverse flag.
    if reverse:
        filtered.columns.name = f"'Top {n} by {stat}'"
    else:
        filtered.columns.name = f"'Bottom {n} by {stat}'"

    # TODO: Give a clearer idea of the restrictions on the data in the DataFrame.
    # c_filter = f"\r\nColours: '{card_colors}'" if card_colors is not None else ""
    # r_filter = f"\r\nRarities: '{card_rarity}'" if card_colors is not None else ""

    # filtered.columns.name = title + c_filter + r_filter

    # Filter the DataFrame on columns
    filtered = filtered[columns]
    return filtered


# Gets a dataframe for the card, where the deck colours are the indexes.
def get_card_frame(s, f, card_name):
    """
    Creates a DataFrame for a card, where the colours are the indexes.
    :param s: The set name
    :param f: The format name
    :param card_name: The card name
    :return: A DataFrame with info about card_name
    """

    # TODO: Rework this with the query_frames function for safety.
    columns = list(cache.PANDAS_CACHE[s][f][''])
    card_df = pd.DataFrame(columns=columns)

    for c in cache.PANDAS_CACHE[s][f]:
        df = cache.PANDAS_CACHE[s][f][c]
        if c == '':
            c = 'Overall'
        if df.empty or card_name not in df.index:
            data_df = pd.DataFrame(np.nan, index=[c], columns=columns)
        else:
            series = df.loc[card_name]
            data_df = series.to_frame(name=c).transpose()
        card_df = card_df.append(data_df)

    return card_df


# Card Metagame Functions
def color_game_counts(s: str, f: str, c: str, color_filter: str = None) -> tuple:
    """
    Returns a tuple with winrate, games won, and games played
    :param s: The set name
    :param f: The format name
    :param c: The colour identity
    :param color_filter: The colour string to filter on
    :return: tuple with winrate, games won, and games played
    """
    # Get the DataFrame from the cache, and make sure it is valid.
    df = cache.query_frames_cache(s, f, c)
    if not isinstance(df, pd.DataFrame):
        print("WARNING: DataFrame not found.")
        df = pd.DataFrame()

    # If the frame is empty, return NaNs.
    if df.empty:
        return tuple((np.nan, np.nan, np.nan))

    # Filter by colour
    df = color_id_filter(df, color_filter)

    try:
        # Check to make sure the appropriate columns exist.
        # TODO: Check that this fails if the columns don't exist.
        df = df[['# GP', 'GP WR']]

        # Calculate the data to return.
        games_played = df['# GP'].sum()
        games_won = (df['# GP'] * (df['GP WR'] * 0.01)).sum().round()
        percent_won = ((games_won * 100) / games_played).round(2)
        return tuple((percent_won, games_won, games_played))
    except:
        # If something goes wrong, return NaNs.
        # TODO: Narrow the exception catching.
        print("WARNING: DataFrame does not contain both '# GP' and 'GP WR'.")
        return tuple((np.nan, np.nan, np.nan))


# Populates WINRATES with data.
def get_color_winrates():
    # TODO: Make this populate an object in data_cache, and use that to handle data.
    win_rates = cache.get_set_tree_struct()
    for s in settings.SETS:
        for f in settings.FORMATS:
            for c in COLOR_GROUPS:
                win_rates[s][f][c] = color_game_counts(s, f, c)
    return win_rates


# Get metagame data for a given colour group.
def get_color_group_metadata(s, f, colors, n=5, stat='GIH WR', columns=None):
    # Set up the data.
    c = get_color_identity(colors)
    metagame_data = gen_metadata_dict_struct()

    # Get the frame, and handle column filtering.
    df = cache.PANDAS_CACHE[s][f][c]
    if columns is None:
        columns = list(df)

    # Get the overall stats, and the stats for the colour group.
    overall_games = color_game_counts(s, f, '')
    color_games = color_game_counts(s, f, c)

    # Use those stats to get high-level stats for the colours.
    metagame_data['Winrate'] = color_games[0]
    metagame_data['Winrate Delta'] = (color_games[0] - overall_games[0]).round(2)
    metagame_data['Games Played'] = color_games[2]
    metagame_data['Metagame Share'] = ((color_games[2] / overall_games[2]) * 100).round(2)

    # Get top commons and uncommons for the colour group.
    metagame_data['Top Commons'] = get_top(df, stat, n=n, card_rarity='C', columns=columns)
    metagame_data['Top Uncommons'] = get_top(df, stat, n=n, card_rarity='U', columns=columns)

    return metagame_data


# Gets a suite of data about the given colour's position in the metagame.
def get_single_color_overview(s, f, main_color, stat='GIH WR', columns=None):
    # Set up the data.
    metagame_dict = dict()
    metagame_data = gen_metadata_dict_struct()
    metagame_dict[main_color] = metagame_data

    # Get the frame, and handle column filtering.
    df = cache.PANDAS_CACHE[s][f]['']
    if columns is None:
        columns = list(df)

    # Get the overall stats, and the stats filtered on the main_colour.
    overall_games = color_game_counts(s, f, '')
    color_games = color_game_counts(s, f, '', main_color)

    # Use those stats to get high-level stats for the colours.
    metagame_data['Winrate'] = color_games[0]
    metagame_data['Winrate Delta'] = (color_games[0] - overall_games[0]).round(2)
    metagame_data['Games Played'] = color_games[2]
    metagame_data['Metagame Share'] = ((color_games[2] / overall_games[2]) * 100).round(2)

    # Get top commons and uncommons for the main_colour
    metagame_data['Top Commons'] = get_top(df, stat, n=10, card_colors=main_color, card_rarity='C', columns=columns)
    metagame_data['Top Uncommons'] = get_top(df, stat, n=10, card_colors=main_color, card_rarity='U', columns=columns)

    # Get the metagame data for all colour pairs that contain 'color'.
    color_pairs = [main_color + x for x in COLORS if x != main_color]
    for col in color_pairs:
        c = get_color_identity(col)
        metagame_dict[c] = get_color_group_metadata(s, f, c, stat=stat, columns=columns)

    # TODO: Add in a fun fact here.

    return metagame_dict


# Gets an overview of the metagame data and saves it to METAGAME_REPORT
def get_format_metagame_data(s, f, stat='GIH WR', columns=None):
    if columns is None:
        columns = settings.DEFAULT_COLUMNS

    report = dict()
    for c in COLORS:
        report[c] = get_single_color_overview(s, f, c, stat=stat, columns=columns)
    return report


# Gets an overview of the metagame data and saves it to METAGAME_REPORT
def get_all_metagame_data(stat='GIH WR', columns=None):
    if columns is None:
        columns = settings.DEFAULT_COLUMNS

    report = dict()
    for s in settings.SETS:
        report[s] = dict()
        for f in settings.FORMATS:
            report[s][f] = dict()
            for c in COLORS:
                report[s][f][c] = get_single_color_overview(s, f, c, stat=stat, columns=columns)
    return report


data_fetch.WINRATES = get_color_winrates()
