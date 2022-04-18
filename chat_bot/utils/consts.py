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
