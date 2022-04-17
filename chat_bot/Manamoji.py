from discord import Client
from discord.emoji import Emoji


class Manamoji:
    MANAMOJIS: list[Emoji] = []
    SETMOJIS: list[Emoji] = []
    MISSING: str = "<:question:965285494982336592>"

    @classmethod
    def cache_manamojis(cls, client: Client) -> None:
        cls.MANAMOJIS = [emo for emo in client.emojis if emo.name.startswith('mana')]
        print(f'{len(cls.MANAMOJIS)} manamojis found!')

        cls.SETMOJIS = [emo for emo in client.emojis if emo.name.startswith('set')]
        print(f'{len(cls.SETMOJIS)} setmojis found!')

    # To automatically grab server emojis installed from
    # https://github.com/scryfall/manamoji-discord/tree/main/emojis
    @classmethod
    def get_manamoji(cls, emoji_str: str) -> str:
        """
        Format and convert the emoji trying to be found.
        EG: 'W' gets converted to 'w', and then 'manaw'.
        :param emoji_str: The emoji to find.
        :return: Best guess at the emoji being requested.
        """
        manamoji_str = emoji_str.lower()
        if not manamoji_str.startswith('mana'):
            manamoji_str = 'mana' + manamoji_str

        manamojis = [emo for emo in cls.MANAMOJIS if emo.name == manamoji_str]

        if len(manamojis) > 0:
            return str(manamojis[0])
        else:
            return cls.MISSING

    @classmethod
    def get_setmoji(cls, emoji_str: str) -> str:
        """
        Format and convert the emoji trying to be found.
        EG: 'W' gets converted to 'w', and then 'manaw'.
        :param emoji_str: The emoji to find.
        :return: Best guess at the emoji being requested.
        """
        setmoji_str = emoji_str.lower()
        if not setmoji_str.startswith('set'):
            setmoji_str = 'set' + setmoji_str
            pass

        setmojis = [emo for emo in cls.SETMOJIS if emo.name == setmoji_str]
        if len(setmojis) > 0:
            return str(setmojis[0])
        else:
            return cls.MISSING

    @classmethod
    def get_emoji(cls, emoji_str: str) -> str:
        """
        Format and convert the emoji trying to be found.
        EG: 'W' gets converted to 'w', and then 'manaw'.
        :param emoji_str: The emoji to find.
        :return: Best guess at the emoji being requested.
        """

        manamoji = cls.get_manamoji(emoji_str)
        if manamoji != cls.MISSING:
            return manamoji

        setmoji = cls.get_setmoji(emoji_str)
        if setmoji != cls.MISSING:
            return setmoji

        return cls.MISSING


    # NOTE: Incomplete
    # Parses a string mana cost into a list of mana 'elements', while converting
    # from 'curly-brace' format or plain-text format to our list format.
    # Eg. {10}{G}{G} would return ['10', 'G', 'G']
    # Eg. 10GG would return ['1', '0', 'G', 'G'], which is likely not what's wanted.
    @classmethod
    # TODO: Move to WUBRG
    def parse_cost(cls, mana_cost: str) -> list[str]:
        # TODO: Parse the mana cost from the {1}{W}{B} format into a list of strings.
        return [char for char in mana_cost]
        pass

    # Takes a mana cost and attempts to return a string of emojis which
    # represent that mana cost, as it would look on the card.
    @classmethod
    def emojify_mana_cost(cls, mana_cost: str) -> str:
        """
        Converts human-like message with emoji to a discord usable message.
        :param mana_cost: The mana cost to add emojis to.
        :return: A string which will display properly when sent.
        """
        if mana_cost is None:
            return ""
        mana_cost = cls.parse_cost(mana_cost)
        cost = ""
        for sym in mana_cost:
            cost += cls.get_emoji(sym)
        return cost

    # Takes a mana cost and attempts to return a string of emojis which
    # represent that teh colours contained in that card.
    # NOTE: Not a true colour_id, potentially worth renaming.
    @classmethod
    def emojify_color_id(cls, mana_cost: str) -> str:
        """
        Converts human-like message with emoji to a discord usable message.
        :param mana_cost: The mana cost to add emojis to.
        :return: A string which will display properly when sent.
        """
        if mana_cost is None:
            return ""
        mana_cost = cls.parse_cost(mana_cost)
        pips = ['W', 'U', 'B', 'R', 'G', 'C']
        cost = ""
        for sym in pips:
            if sym not in mana_cost:
                continue
            cost += cls.get_emoji(sym)
        return cost
