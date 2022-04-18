COMMAND_STR: str = '17!'
DATA_QUERY_L: str = '{{'
DATA_QUERY_R: str = '}}'
DATA_QUERY_MID: str = '|'
QUOTE_PAIRS: dict[str, str] = {'"': '"', '“': '”'}

FORMAT_NICKNAMES: dict[str, str] = {
    'PremierDraft': 'Bo1',
    'TradDraft': 'Bo3',
    'QuickDraft': 'Quick',
    'Sealed': 'Seal',
    'TradSealed': 'Bo3Seal',
    'DraftChallenge': 'Chal.',
}

STAT_FORMAT_STRINGS = {
    "Name": "`{:<20}`",
    "Color": "`{:^6}`",
    "Rarity": "`{:^6}`",
    "# Seen": "`{:>6.0f}`",
    "ALSA": "`{:^6.2f}`",
    "# Picked": "`{:>6.0f}`",
    "ATA": "`{:^6.2f}`",
    "# GP": "`{:>6.0f}`",
    "GP WR": "`{:5.2f}%`",
    "# OH": "`{:>6.0f}`",
    "OH WR": "`{:5.2f}%`",
    "# GD": "`{:>6.0f}`",
    "GD WR": "`{:5.2f}%`",
    "# GIH": "`{:>6.0f}`",
    "GIH WR": "`{:5.2f}%`",
    "# GND": "`{:>6.0f}`",
    "GND WR": "`{:5.2f}%`",
    "IWD": "`{:5.2f}%`"
}

STAT_ALIASES: dict[str, str] = {
    # 17Lands variable mapping
    "name": "Name",
    "color": "Color",
    "rarity": "Rarity",
    "seen_count": "# Seen",
    "avg_seen": "ALSA",
    "pick_count": "# Picked",
    "avg_pick": "ATA",
    "game_count": "# GP",
    "win_rate": "GP WR",
    "opening_hand_game_count": "# OH",
    "opening_hand_win_rate": "OH WR",
    "drawn_game_count": "# GD",
    "drawn_win_rate": "GD WR",
    "ever_drawn_game_count": "# GIH",
    "ever_drawn_win_rate": "GIH WR",
    "never_drawn_game_count": "# GND",
    "never_drawn_win_rate": "GND WR",
    "drawn_improvement_win_rate": "IWD",

    # 17Lands variable shorthand mapping
    "games": "# GP",
    "winrate": "GP WR",
    "opening_hand": "OH WR",
    "drawn": "GD WR",
    "ever_drawn": "GIH WR",
    "never_drawn": "GND WR",
    "drawn_improvement": "IWD",

    # Lowercase mapping
    "# seen": "# Seen",
    "alsa": "ALSA",
    "# picked": "# Picked",
    "ata": "ATA",
    "# gp": "# GP",
    "gp wr": "GP WR",
    "# oh": "# OH",
    "oh wr": "OH WR",
    "# gd": "# GD",
    "gd wr": "GD WR",
    "# gih": "# GIH",
    "gih wr": "GIH WR",
    "# gnd": "# GND",
    "gnd wr": "GND WR",
    "iwd": "IWD",

    # Shorthand mapping
    "seen": "# Seen",
    "picked": "# Picked",
    "gp": "GP WR",
    "oh": "OH WR",
    "gd": "GD WR",
    "gih": "GIH WR",
    "gnd": "GND WR",
}
