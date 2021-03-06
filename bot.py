import os 
import logging
import random
import urllib.request
import urllib.parse
import re

import discord 
from discord.ext import commands

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get('TOKEN') 

client = commands.Bot(command_prefix = ".")

youtube_url = "https://www.youtube.com/watch?v="
youtube_search = "https://www.youtube.com/kepowob/search?"

# Events is a piece of code happens when the bot detects a 
# specific activity has happened
@client.event
async def on_ready():
    GAMES = ['Minecraft', 'Anything but Fortnite', 'Lucid Dream']
    is_playing = random.choice(GAMES)
    await client.change_presence(status=discord.Status.idle,
            activity=discord.Game(is_playing))
    print('Bot is ready')

@client.event
async def on_member_join(member):
    print(f'{member} has joined a server.')

@client.event
async def on_command_error(ctx, error):
    """ The event will be triggered for all functions
        if using commands.MissingRequiredArgument
    """ 
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'Invalid command used. To get a lists of commands type `.help`')
    
@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=2):
    """ Takes as an argument a number of messages to be deleted.
    """
    await ctx.channel.purge(limit=amount)        

@client.command()
async def youtube(ctx, *, args, amount=1):
    """ Searches for kevins videos on a given topic. 
    """
    params = urllib.parse.urlencode({'query': args}) 
    search = f'{youtube_search}{params}'
    html = urllib.request.urlopen(search)
    content = html.read().decode()
    video_ids = re.findall(r"watch\?v=(\S{11})", content)
    for video in video_ids[:amount]:
        await ctx.send(f'{youtube_url}{video}')

@client.command()
async def ping(ctx): 
    """ By default, the name of the function is the name of the command
    """
    await ctx.send(f'Pong! {round(client.latency * 1000)} ms')

# Custom check
def is_it_user(ctx):
    return ctx.author.id == 542770113443528705 

#@commands.check(is_it_user) # will run if the custom check returns true
@client.command(aliases=['toss'])
async def coinflip(ctx, *, question):
    """ aliases takes a list of strings. You can have +1 aliases.
        * allows for multiple arguments to be passed
    """
    responses = ['heads', 'tails']
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}\n@{ctx.author}')

@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)

@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    
@client.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user 

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user) 
            await ctx.send(f'Unbanned {user.name}')
            return

# Specifying errors directly to each command
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Please specify an amount of messages to delete')

if __name__ == "__main__":
    try:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                client.load_extension(f'cogs.{filename[:-3]}')
    except Exception as ex:
        print(f'{ex}')
    client.run(TOKEN)
