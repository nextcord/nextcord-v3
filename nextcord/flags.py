from .types.base_flag import IntFlags, flag_value


class Intents(IntFlags):
    """
    The intents you can connect to the gateway with.

    .. note::
        See the `documentation <https://discord.dev/topics/gateway#gateway-intents>`_
    """

    flags = (
        "GUILDS",
        "GUILD_MEMBERS",
        "GUILD_BANS",
        "GUILD_EMOJIS_AND_STICKERS",
        "GUILD_INTERACTIONS",
        "GUILD_WEBHOOKS",
        "GUILD_INVITES",
        "GUILD_VOICE_STATES",
        "GUILD_PRESENCES",
        "GUILD_MESSAGES",
        "GUILD_MESSAGE_REACTIONS",
        "GUILD_MESSAGE_TYPING",
        "DIRECT_MESSAGES",
        "DIRECT_MESSAGE_REACTIONS",
        "DIRECT_MESSAGE_TYPING",
        "MESSAGE_CONTENT",
        "GUILD_SCHEDULED_EVENTS",
    )

    GUILDS = flag_value(1 << 0)
    GUILD_MEMBERS = flag_value(1 << 1)
    GUILD_BANS = flag_value(1 << 2)
    GUILD_EMOJIS_AND_STICKERS = flag_value(1 << 3)
    GUILD_INTEGRATIONS = flag_value(1 << 4)
    GUILD_WEBHOOKS = flag_value(1 << 5)
    GUILD_INVITES = flag_value(1 << 6)
    GUILD_VOICE_STATES = flag_value(1 << 7)
    GUILD_PRESENCES = flag_value(1 << 8)
    GUILD_MESSAGES = flag_value(1 << 9)
    GUILD_MESSAGE_REACTIONS = flag_value(1 << 10)
    GUILD_MESSAGE_TYPING = flag_value(1 << 11)
    DIRECT_MESSAGES = flag_value(1 << 12)
    DIRECT_MESSAGE_REACTIONS = flag_value(1 << 13)
    DIRECT_MESSAGE_TYPING = flag_value(1 << 14)
    MESSAGE_CONTENT = flag_value(1 << 15)
    GUILD_SCHEDULED_EVENTS = flag_value(1 << 16)
