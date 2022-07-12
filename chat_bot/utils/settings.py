UPDATING_SETS: list[str] = ['HBG']
OLD_SETS: list[str] = ['SNC', 'NEO', 'DBL', 'VOW', 'MID', 'AFR', 'STX', 'KHM']
SETS: list[str] = UPDATING_SETS + OLD_SETS
START_DATE: str = '2019-01-01'
DEFAULT_FORMAT: str = 'PremierDraft'


FORMATS: dict[str, list[str]] = {
    'PremierDraft': ['bo1', 'premier', 'premierdraft'],
    'TradDraft': ['bo3', 'trad', 'traditional', 'traddraft', 'traditionaldraft'],
    'QuickDraft': ['qd', 'quick', 'quickdraft'],
    'Sealed': ['sealed', 'bo1sealed', 'sealedbo1'],
    'TradSealed': ['tradsealed', 'bo3sealed', 'sealedbo3'],
    'DraftChallenge': ['challenge', 'draftchallenge'],
}

FORMAT_MAPPINGS: dict[str, str] = {alias: name for name in FORMATS for alias in FORMATS[name]}

DATA_COMMANDS: dict[str, list[tuple[str, str, bool]]] = {
    'alsa': [('seen_count', '# Seen', True), ('avg_seen', 'ALSA', False)],
    'ata': [('pick_count', '# Taken', True), ('avg_pick', 'ATA', False)],
    'gp': [('game_count', '# GP', True), ('win_rate', 'GP WR', False)],
    'oh': [('opening_hand_game_count', '# OH', True), ('opening_hand_win_rate', 'OH WR', False)],
    'gd': [('drawn_game_count', '# GD', True), ('drawn_win_rate', 'GD WR', False)],
    'gih': [('ever_drawn_game_count', '# GIH', True), ('ever_drawn_win_rate', 'GIH WR', False)],
    'gnd': [('never_drawn_game_count', '# GND', True), ('never_drawn_win_rate', 'GND WR', False)],
    'iwd': [('drawn_improvement_win_rate', 'IWD', False)]
}
DATA_COMMANDS['drafts'] = DATA_COMMANDS['alsa'] + DATA_COMMANDS['ata']
DATA_COMMANDS['games'] = DATA_COMMANDS['gp'] + DATA_COMMANDS['oh'] + DATA_COMMANDS['gd'] + DATA_COMMANDS['gih'] + \
                         DATA_COMMANDS['gnd'] + DATA_COMMANDS['iwd']
DATA_COMMANDS['data'] = DATA_COMMANDS['drafts'] + DATA_COMMANDS['games']
