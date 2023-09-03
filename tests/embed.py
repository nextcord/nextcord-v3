from nextcord.types.embed import Embed, EmbedFooter, EmbedProvider

embed = Embed(
    title="The title", description="The description", footer=EmbedFooter(text="hey", icon_url="https://discord.com/")
)
embed._provider = EmbedProvider(name="Discord", url="https://discord.com/")

data = embed.to_dict()
print(data)
embed2 = Embed.from_dict(data)
print(embed2, dir(embed2))
for a in dir(embed2):
    if not a.startswith("__"):
        print(a, getattr(embed2, a))

data2 = embed2.to_dict()

print(data2)
assert data == data2
