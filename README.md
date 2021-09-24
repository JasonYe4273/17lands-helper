# 17lands-helper
Discord bot for scraping 17lands data

## Status
The bot is currently in development, and is not yet hosted anywhere, so does not work unless I am running it in my testing environment.

## How to use
Go to [this link](https://discord.com/api/oauth2/authorize?client_id=890628197664817203&permissions=380104920128&scope=bot) to invite the bot to your server.

The bot currently responds to the following commands:
- Data queries:
    - The bot will respond to messages that include substring(s) like `{{[cardnames] | [options]}}`. Everything is case-insensitive.
    - `[cardnames]` is a list of names of cards you want to query data for, separated by spaces. This uses Scryfall's fuzzy match to find the card, so slight misspellings and incomplete names are often okay. A name with spaces must be enclosed by quotes, otherwise it will be interpreted as multiple names. For example: `{{jadar "gisa resurrector"}}` will query for the cards Jadar, Ghoulcaller of Nephalia and Gisa, Glorious Resurrector.
    - `[options]` is a list of options to modify the query. Ommitting options entirely (in a query like `{{[cardname]}}` for example) will just use the default options. Available options include:
        - You can specify which sets to search for the card(s) in by providing set codes as options. If no sets are provided, all sets available on 17lands will be searched. Data returned will always be from the most recent set the card is found in. For example, `{{"return to nature" | m21}}` would specifically query for Return to Nature's data in Core Set 2021, while `{{"return to nature"}}` would query for its data in Innistrad: Midnight Hunt (as that is the most recent printing as of September 2021)
        - You can specify which Arena formats to query data for. These will appear as individual columns in the response table. Available formats, and keywords to use to specify them, are as follows:
            - PremierDraft: `bo1`, `premier`, `premierdraft`
            - TradDraft: `bo3`, `trad`, `traditional`, `traddraft`, `traditionaldraft`
            - QuickDraft: `qd`, `quick`, `quickdraft`
            - Sealed: `sealed`, `bo1sealed`, `sealedbo1`
            - TradSealed: `tradsealed`, `bo3sealed`, `sealedbo3`
            - DraftChallenge: `challenge`, `draftchallenge`
        - You can specify which data points to query. Available data points are:
            - `alsa`: Average Last Seen At
            - `ata`: Average Taken At
            - `gp`: Games Played
            - `gd`: Games Drawn
            - `gih`: Games in Hand
            - `gnd`: Games Not Drawn
            - `iwd`: Improvement When Drawn
            - `drafts`: ALSA and ATA
            - `games`: GP, GD, GIH, GND, and IWD
            - `data`: all of the above
        - You can specify a time period to query data from. Note that this will result in a slower query, as the data will not be cached, and will need to be fetched from 17lands.
            - `-e=[end]` or `end=[end]` will set the end date to `[end]`. `[end]` must be given in the format `MM-DD-YYYY`. If `[end]` is not specified, it will default to the current day.
            - `-d=[days]` or `days=[days]` will set the number of days in the time period. If the length of the time period is not specified, it will default to querying over all 17lands data.
                - `-w=[weeks]`, `weeks=[weeks]`, `-m=[months]`, and `months=[months]` function similarly, except a week is 7 days and a month is 30 days. Using multiple flags is additive; `-d=5 -w=1 -m=1` is equivalent to `-d=42`.
        - Adding `-v` or `verbose` as an option will cause the query to also return data counts (things like # Games Played) in addition to winrates.
    - Examples
        - `{{jadar "gisa resurrector"}}` will give all data for Jadar, Ghoulcaller of Nephalia and Gisa, Glorious Resurrector.
    	- `{{jadar "gisa resurrector" | drafts gih}}` will give ALSA, ATA, and GIH data for Jadar, Ghoulcaller of Nephalia and Gisa, Glorious Resurrector.
        - `{{jadar "gisa resurrector" | drafts gih -w=2 -e=09-21-2021}}` will give ALSA, ATA, and GIH data for Jadar, Ghoulcaller of Nephalia and Gisa, Glorious Resurrector in the time period of 9/7/2021 to 9/21/2021