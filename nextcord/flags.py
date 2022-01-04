from .types.base_flag import IntFlags, flag_value


class Intents(IntFlags):
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
        "GUILD_SCHEDULED_EVENTS"
    )

    @flag_value(0)
    def GUILDS(self):
        ...

    @flag_value(1)
    def GUILD_MEMBERS(self):
        ...

    @flag_value(2)
    def GUILD_BANS(self):
        ...

    @flag_value(3)
    def GUILD_EMOJIS_AND_STICKERS(self):
        ...

    @flag_value(4)
    def GUILD_INTEGRATIONS(self):
        ...

    @flag_value(5)
    def GUILD_WEBHOOKS(self):
        ...

    @flag_value(6)
    def GUILD_INVITES(self):
        ...

    @flag_value(7)
    def GUILD_VOICE_STATES(self):
        ...

    @flag_value(8)
    def GUILD_PRESENCES(self):
        ...

    @flag_value(9)
    def GUILD_MESSAGES(self):
        ...

    @flag_value(10)
    def GUILD_MESSAGE_REACTIONS(self):
        ...

    @flag_value(11)
    def GUILD_MESSAGE_TYPING(self):
        ...

    @flag_value(12)
    def DIRECT_MESSAGES(self):
        ...

    @flag_value(13)
    def DIRECT_MESSAGE_REACTIONS(self):
        ...

    @flag_value(14)
    def DIRECT_MESSAGE_TYPING(self):
        ...

    @flag_value(16)
    def GUILD_SCHEDULED_EVENTS(self):
        ...
