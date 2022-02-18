import discord
import spacer
from discord.ext import commands

client = discord.Bot()

spacer.client = client


@spacer.commandWithSpaces()
@commands.guild_only()
async def do_something_again(ctx):
    await ctx.respond("Success, you just used the do_something_again function")

@spacer.commandWithSpaces()
@commands.commandWithSpaces()
async def do_something_twice(ctx):
    await ctx.respond("Success, you just used the do_something_twice function")

@client.event
async def on_ready():
    print("Bot is online")

spacer.finish()
client.run("TOKEN")
