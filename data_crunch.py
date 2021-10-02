import numpy as np
import pandas as pd

import WUBRG
from WUBRG import COLOUR_GROUPS, COLORS
import data_fetch
from settings import *

PANDAS_CACHE = data_fetch.PANDAS_CACHE

### Pandas Filters ###

# Filters out cards that have a number of games played less than p% of # GP.
def min_play_filter(df, p):
    min_game = df['# GP'].sum() * (p/100)
    return df[df['# GP'] >= min_game]


# Filters out cards that don't fall within the colour identy.
def color_id_filter(df, color_string):
    if color_string is not None and color_string != '':
        return df[df['Color'].apply(lambda x: set(x) <= set(color_string))]
    else:
        return df


# Filters out cards that aren't in the given rarities.
def rarity_filter(df, rarity):
    if rarity is not None and rarity != '':
        return df[df['Rarity'].apply(lambda x: set(x) <= set(rarity))]
    else:
        return df


# Gets the top n cards, based on a particular stat column.
# Can filter based on card colours, rarity.
# Can get the bottom n cards with 'reverse=True'
def get_top(df, stat, n=5, card_colors=None, card_rarity=None, min_thresh=1, reverse=False, columns=None):
    if df.empty:
        return df

    if columns == None:
        columns = list(df)
    
    filtered = color_id_filter(df, card_colors)
    filtered = rarity_filter(filtered, card_rarity)
    filtered = min_play_filter(filtered, min_thresh)

    # If reverse is true, we need to invert the ordering.
    # If we're getting card pick info, we also need to invert the ordering.
    smallest = reverse != (stat == "ALSA" or stat == "ATA")  # != is a functional XOR.
    
    # Return the smallest values if we're dealing with pick orders
    if smallest:
        filtered = filtered.nsmallest(n, stat)
    else:
        filtered = filtered.nlargest(n, stat)


    if reverse:
        filtered.columns.name = f"'Top {n} by {stat}'"
    else:
        filtered.columns.name = f"'Bottom {n} by {stat}'"

    
    # TODO: Give a clearer idea of the restrictions on the data in the DataFrame.
    #c_filter = f"\r\nColours: '{card_colors}'" if card_colors is not None else ""
    #r_filter = f"\r\nRarities: '{card_rarity}'" if card_colors is not None else ""
    
    #filtered.columns.name = title + c_filter + r_filter
    filtered = filtered[columns]
    return filtered


# Gets a dataframe for the card, where the deck colours are the indexes.
def get_card_frame(s, f, card_name):
    columns = list(PANDAS_CACHE[s][f][''])
    card_df = pd.DataFrame(columns=columns)
    
    for c in PANDAS_CACHE[s][f]:
        df = PANDAS_CACHE[s][f][c]
        if c == '':
            c = 'Overall'
        data_df = None
        if df.empty or card_name not in df.index:
            data_df = pd.DataFrame(np.nan, index=[c], columns=columns)
        else:
            series = df.loc[card_name]
            data_df = series.to_frame(name=c).transpose()
        card_df = card_df.append(data_df)
    
    return card_df



### Card Metagame Functions ###

# Returns a tuple with winrate, games won, and games played
def color_game_counts(s, f, c, color_filter = None):
    df = PANDAS_CACHE[s][f][c]
    if df is None or df.empty:
        return (np.nan, np.nan, np.nan)
    
    df = color_id_filter(df, color_filter)
    df = df[['# GP','GP WR']]
    games_played = df['# GP'].sum()
    games_won = (df['# GP'] * (df['GP WR'] * 0.01)).sum().round()
    percent_won = ((games_won  * 100)/ games_played).round(2)
    return (percent_won, games_won, games_played)


# Populates WINRATES with data.
def get_color_win_rates():
    win_rates = data_fetch.get_set_tree()
    for s in SETS:
        for f in FORMATS:
            for c in COLOUR_GROUPS:
                win_rates[s][f][c] = color_game_counts(s,f,c)
    return win_rates


# Get metagame data for a given colour group.
def get_color_group_metadata(s, f, colors, n=5, stat='GIH WR', columns=None):
    # Set up the data.
    c = WUBRG.get_color_identity(colors)
    metagame_data = gen_metadata_dict_struct()
    
    # Get the frame, and handle column filtering.
    df = PANDAS_CACHE[s][f][c]
    if columns == None:
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
def get_color_overview(s, f, main_color, stat='GIH WR', columns=None):
    # Set up the data.
    metagame_dict = dict()
    metagame_data = gen_metadata_dict_struct()
    metagame_dict[main_color] = metagame_data
    
    # Get the frame, and handle column filtering.
    df = PANDAS_CACHE[s][f]['']    
    if columns == None:
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
        c = WUBRG.get_color_identity(col)
        metagame_dict[c] = get_color_group_metadata(s, f, c, stat=stat, columns=columns)
        
    # TODO: Add in a fun fact here.
        
    return metagame_dict


# Gets an overview of the metagame data and saves it to METAGAME_REPORT
def get_format_metagame_data(s, f, stat='GIH WR', columns=None):
    if columns is None:
        columns = DEFAULT_COLUMNS
    
    report = dict()
    for s in SETS:
        report[s] = dict()
        for f in FORMATS:
            report[s][f] = dict()
            for c in COLORS:
                report[s][f][c] = get_color_overview(s, f, c, stat=stat, columns=columns)
    return report




data_fetch.WINRATES = get_color_win_rates()

