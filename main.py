import re
import os
import discord
from discord.ext import commands
import random
from pprint import pprint
import json
from shikimori_api import Shikimori
try:
    import bot_data as DATA
except ImportError:
    import bot_local as DATA
    
            

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

shiki_request_prev = []
shiki_is_active = False


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)
    
@bot.command()
async def shiki(ctx, search: str, *args):
    from shikimori_api import Shikimori
    import requests
    import aiofiles.os
    
    global shiki_request_prev
    global shiki_is_active
    
    try:
        int(search)
    except:
        shiki_is_active = False
    
   
    session = Shikimori()
    api = session.get_api()
    
    if shiki_is_active:
        anime = shiki_request_prev[int(search)-1]
        anime_text = f'''**{'['+anime['kind'].upper()+']' if anime['kind'] else ''} {anime['name']} | {anime['aired_on'].split('-')[0]}**
```js
RUS: {anime['russian']}
Score: {anime['score']}
Episodes: {f"{anime['episodes_aired']}/{anime['episodes']} [{anime['status']}]" if anime['status']=='ongoing' else f"{anime['episodes']} [{anime['status']}]"}
```
---
*url: <https://shikimori.one{anime['url']}>*
'''
        
        image_original = anime['image']['original'].split('?')
        cover_filename = '{}.jpg'.format(image_original[1])
        resp = requests.get('http://shikimori.one'+image_original[0], headers={'User-Agent': 'Mozilla/5.0'})
        
        if resp.status_code == 200:
            with open(cover_filename, 'wb') as cover_img:
                cover_img.write(resp.content)
            with open(cover_filename, 'rb') as file:
                await ctx.send(
                    content=anime_text,
                    files=[discord.File(file)])
                shiki_is_active = False
                
            if os.path.exists(cover_filename):
                await aiofiles.os.remove(cover_filename)
        else:
            print('http://shikimori.one'+image_original[0])
            print(resp.status_code)
            await ctx.send(
                    content=anime_text + '\nPIC ERROR')
        
    elif not shiki_is_active:
        anime_list = ''
        counter = 1
        
        if args:
            search += ' '+' '.join(args)
        
        request = api.animes.GET(search=search,limit=10)

        if request != []:
            anime_list += '```'
            
            for anime in request:
                anime_list = anime_list+f"{counter}. {anime['name']} {'['+anime['kind'].upper()+']' if anime['kind'] else ''}\n"
                counter+=1
            
            anime_list += '```'
            await ctx.send(content=anime_list)
            
            shiki_request_prev = request
            shiki_is_active = True
            
        else: 
            await ctx.send(content='wtf?')

@bot.command()
async def horny(ctx):
    from hentai import Hentai, Format, Utils
    import aiofiles.os
    import requests
    
    doujin = Utils.get_random_hentai()
    title = doujin.title(Format.Pretty)
    tags = ", ".join(tag.name for tag in doujin.tag)
    url = doujin.url
    cover = doujin.cover
    cover_filename = '{}.jpg'.format(doujin.id)
    
    resp = requests.get(cover)
    if resp.status_code == 200:
        with open(cover_filename, 'wb') as cover_img:
            cover_img.write(resp.content)

    with open(cover_filename, 'rb') as file:
        await ctx.send(
            content=f'''Title: {title}
Tags: `{tags}`
_<{url}>_''',
            files=[discord.File(file)])
        
    if os.path.exists(cover_filename):
        await aiofiles.os.remove(cover_filename)

@bot.command()
async def dem(ctx):
    import aiofiles.os    
    from simpledemotivators import Demotivator
    
    if(ctx.message.attachments != [] and ctx.message.content != '?dem'):
        top_text, bottom_text = ctx.message.content.split('?dem ')[1].split('/')
        dem = Demotivator(top_text, bottom_text) 
        dem.create(ctx.message.attachments[0].url, use_url=True, delete_file=True)
        
        with open('demresult.jpg', 'rb') as file:
            await ctx.send(files=[discord.File(file)])
            
        if os.path.exists('demresult.jpg'):
            await aiofiles.os.remove('demresult.jpg')
    else:
        await ctx.send(
            content=f'''Погоди... 
Ты должен прикрепить пикчу и написать текст в формате `?dem [верхняя строка]/[нижняя строка]`, где "/" - это разделитель
''')
    
    
@bot.command()
async def avatar(ctx, member:discord.Member):
    await ctx.send(member.avatar_url)  
    

@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)

@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))

@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await ctx.send(content)

@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send('{0.name} joined in {0.joined_at}'.format(member))
    


@bot.group()
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('No, {0.subcommand_passed} is not cool'.format(ctx))

@cool.command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')


bot.run(DATA.TOKEN)
