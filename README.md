# 17lands-helper
Discord bot for scraping 17lands data

## Status
The bot is currently in development, and is not yet hosted anywhere, so does not work unless I am running it in my testing environment.

## How to use
Go to [this link](https://discord.com/api/oauth2/authorize?client_id=890628197664817203&permissions=380104920128&scope=bot) to invite the bot to your server.

The bot currently responds to the following commands:
- Data queries:
    - Formatted like `![data_command] [cardname] [options]`, with spaces between options. Everything is case-insensitive.
    - \[data_command\] determines which 17lands data point you're querying; available data commands are:
        - !alsa: Average Last Seen At
        - !ata: Average Taken At
        - !drafts: ALSA and ATA
        - !gp: Games Played
        - !gd: Games Drawn
        - !gih: Games in Hand
        - !gnd: Games Not Drawn
        - !iwd: Improvement When Drawn
        - !games: GP, GD, GIH, GND, and IWD
        - !data: all of the above
    - \[cardname\] is the name of the card you're querying. This uses Scryfall's fuzzy match to find the card, so misspells are okay. Must enclose in quotes to use spaces
    - \[options\] can include:
    	- Set code (e.g. 'mid' for Innistrad: Midnight Hunt) to disambiguate between two sets a card is in
    	- Format to specify which format to query from (default Premier Draft). Valid options for formats include:
    		- PremierDraft': ['bo1', 'premier', 'premierdraft']
    		- TradDraft': ['bo3', 'trad', 'traditional', 'traddraft', 'traditionaldraft']
    		- QuickDraft': ['qd', 'quick', 'quickdraft']
    		- Sealed': ['sealed', 'bo1sealed', 'sealedbo1']
    		- TradSealed': ['tradsealed', 'bo3sealed', 'sealedbo3']
    		- DraftChallenge': ['challenge', 'draftchallenge']
    - Examples
    	- `!alsa "first day"` returns the ALSA data for First Day of Class in STX Premier Draft
    	- `!gih jaspera sealed` returns the GIH data for Jaspera Sentinel in KHM Sealed
    	- `!data "rev drowned" mid bo3` returns all data for Revenge of the Drowned in MID Traditional Draft