import discord
try:
    import bot_data as DATA
except ImportError:
    import bot_local as DATA

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(guild_ids=[1052666851412418671])
async def hello(ctx):
    await ctx.respond("Hello!")
    
@bot.slash_command(guild_ids=[1052666851412418671], description="Sends the bot's latency.")
async def ping(ctx):
    await ctx.respond(f"Pong! Latency is {bot.latency}")

bot.run(DATA.TOKEN)