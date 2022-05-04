from discord import Client
from discord.emoji import Emoji

from WUBRG import parse_cost, get_color_string


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

    @classmethod
    def emojify_mana_cost(cls, mana_cost: str) -> str:
        """
        Converts a card/human-like mana cost to a set of emoji-based symbols.
        :param mana_cost: The mana cost to convert.
        :return: A string which will display properly when sent.
        """
        if mana_cost is None:
            return ""
        mana_cost = parse_cost(mana_cost)
        cost = ""
        for sym in mana_cost:
            cost += cls.get_emoji(sym)
        return cost

    @classmethod
    def emojify_color_string(cls, color_string: str) -> str:
        """
        Converts a color string into its set of mana symbols.
        :param color_string: The color string to convert.
        :return: A string which will display properly when sent.
        """
        color_string = get_color_string(color_string)
        cost = ""
        for sym in color_string:
            emoji = cls.get_emoji(sym)
            cost += emoji
        return cost


