from multiprocessing import Value
from discord.ext import commands
import discord


bot_token = 'bot_token'
channel_id = 1223750722164883596
admins = []
with open('admins.txt', 'r') as a:
    content = a.readlines()
    for line in content:
        admins.append(int(line.split('\n')[0]))
avail_tags = []
with open('tags.txt', 'r') as t:
    content = t.readlines()
    for line in content:
        avail_tags.append(line.split('\n')[0])

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
#Sends an alert to the command prompt that the bot is ready.
async def on_ready():
    print('Hello!')

@bot.command()
#Allows users to thank the bot.
async def thanks(ctx):
    with open('thanks.txt', 'r') as t:
        num = int(t.readline(1)) + 1
    with open('thanks.txt', 'w') as t:
        t.write(str(num))
    await ctx.send(f"You're very welcome. I have been thanked {num} times!'")

@bot.command()
#Allows users to add seeds to the database. No permissions reqiured.
async def addSeed(ctx, seed=None, desc=None, tag_1=None, tag_2=None, tag_3=None):
    added = False
    length = False
    verif = True
    tags_verif = True
    if seed is None:
        verif = False
        await ctx.send('You need to input a seed, description, and tag(s).')
    elif desc is None and verif:
        verif = False
        await ctx.send('You need to input a seed description and tag(s).')
    elif tag_1 is None and verif:
        verif = False
        await ctx.send('You need to input at least one tag.')
    if tag_1 not in avail_tags:
        tags_verif = False
        await ctx.send(f"{tag_1.lower()} is not a legal tag. Please enter a different tag. To see the available tags, type !tags.")
    elif tag_2 is not None and tag_2 not in avail_tags:
        tags_verif = False
        await ctx.send(f"{tag_2.lower()} is not a legal tag. Please enter a different tag. To see the available tags, type !tags.")
    elif tag_3 is not None and tag_3 not in avail_tags:
        tags_verif = False
        await ctx.send(f"{tag_3.lower()} is not a legal tag. Please enter a different tag. To see the available tags, type !tags.")
    if verif and tags_verif:
        with open('seeds.txt', 'r') as f:
            content = f.readlines()
            for line in content:
                if line.split(':')[0] == seed.upper():
                    added = True
                    await ctx.send(f"I seem to already have the seed `{seed.upper()}`.")
            if len(seed) > 8:
                legnth = True
                await ctx.send('That seed is too long.')
            if not added:
                f_string = f'{seed.upper()}: {desc.lower()}\n{tag_1.lower()}'
                if tag_2 is None and tag_3 is None:
                    f_string += '\n'
                elif tag_2 is not None and tag_3 is None:
                    f_string += f', {tag_2.lower()}\n'
                elif tag_2 is not None and tag_3 is not None:
                    f_string += f', {tag_2.lower()}, {tag_3.lower()}\n'
                content.append(f_string)
        with open('seeds.txt', 'w') as f:
            for line in content:
                f.write(line)
            if not added and not length:
                await ctx.send('Seed successfully added!')
    
@bot.command()
#Allows users to remove seeds from the database. Admin required.
async def removeSeed(ctx, seed=None):
    user_id = ctx.author.id
    verif = True
    if seed is None:
        verif = False
        await ctx.send('You need to input a seed.')
    if user_id in admins and verif:
        delete_next_line = False
        with open('seeds.txt', 'r') as f:
            content = f.readlines()
            original = len(content)
        with open('seeds.txt', 'w') as f:
            for line in content:
                if line.split(':')[0] != seed.upper() and not delete_next_line:
                    f.write(line)
                elif delete_next_line:
                    delete_next_line = False
                else:
                    delete_next_line = True
        with open('seeds.txt', 'r') as f:
            content = f.readlines()
            new = len(content)
        if original == new:
            await ctx.send(f"I couldn't seem to find the seed `{seed.upper()}`.")
        else:
            await ctx.send('Seed successfully deleted!')
    elif verif:
        await ctx.send("You don't have the required permissions to do that.")
        
@bot.command()
#Allows users to add admins. Admin required.
async def addAdmin(ctx, member):
    user_id = ctx.author.id
    user = discord.utils.get(bot.users, name=member)
    verif = True
    added = False
    try:
        id = user.id
    except AttributeError:
        verif = False
        id = None
        await ctx.send(f'{member} is not a valid Discord username.')
    if user_id in admins and verif:
        with open('admins.txt', 'r') as a:
            content = a.readlines()
        for line in content:
            if int(line.split('\n')[0]) == id:
                added = True
                await ctx.send(f'`{member}` already has admin permissions.')
        with open('admins.txt', 'w') as a:
            for line in content:
                a.write(line)
            if not added:
                a.write(f'{id}\n')
                admins.append(int(id))
                await ctx.send('Admin permissions successfully added!')
    elif verif:
        await ctx.send("You don't have the required permissions to do that.")
       
@bot.command()
#Allows users to remove admins. Admin required.
async def removeAdmin(ctx, member):
    user_id = ctx.author.id
    user = discord.utils.get(bot.users, name=member)
    verif = True
    added = True
    try:
        id = user.id
    except AttributeError:
        verif = False
        id = None
        await ctx.send(f'{member} is not a valid Discord username.')
    if user_id in admins and user_id != id and verif:
        with open('admins.txt', 'r') as a:
            content = a.readlines()
        with open('admins.txt', 'w') as a:
            try:
                content.remove(f'{id}\n')
            except ValueError:
                added = False
                await ctx.send(f'`{member}` does not have admin permissions.')
            for line in content:
                a.write(line)
        if added:
            admins.remove(id)
            await ctx.send('Admin permissions successfully removed!')
    elif user_id in admins and user_id == id and verif:
        await ctx.send("You can't remove yourself from the admin list.")
    elif verif:
        await ctx.send("You don't have the required permissions to do that.")

@bot.command()
#Allows users to add a tag. Admin required.
async def addTag(ctx, tag=None):
    user_id = ctx.author.id
    verif = True
    added = False
    if tag is None:
        verif = False
        await ctx.send('You need to input a tag.')
    if user_id in admins and verif:
        with open('tags.txt', 'r') as t:
            content = t.readlines()
            for line in content:
                if line.split('\n')[0] == tag.lower():
                    added = True
                    await ctx.send(f"I seem to already have the tag `{tag.lower()}`.")
            if not added:
                content.append(f'{tag.lower()}\n')
        with open('tags.txt', 'w') as t:
            for line in content:
                t.write(line)
            if not added:
                avail_tags.append(tag.lower())
                await ctx.send('Tag successfully added!')
    elif verif:
        await ctx.send("You don't have the required permissions to do that.")

@bot.command()
#Allows users to remove a tag. Admin required.
async def removeTag(ctx, tag=None):
    user_id = ctx.author.id
    verif = True
    added = True
    if tag is None:
        verif = False
        await ctx.send('You need to input a tag.')
    if user_id in admins and verif:
        with open('tags.txt', 'r') as t:
            content = t.readlines()
        with open('tags.txt', 'w') as t:
            try:
                content.remove(f'{tag.lower()}\n')
            except ValueError:
                added = False
                await ctx.send(f"I couldn't seem to find the tag `{tag.lower()}`.")
            for line in content:
                t.write(line)
        if added:
            avail_tags.remove(tag.lower())
            await ctx.send('Tag successfully removed!')
    elif verif:
        await ctx.send("You don't have the required permissions to do that.")

@bot.command()
#Allows users to see the list of available tags.
async def tags(ctx):
    with open('tags.txt', 'r') as t:
        content = t.readlines()
    f_string = f"Sure! Here are the available tags:\n"
    for line in content:
        f_string += f'-{line}'
    await ctx.send(f_string)
        
@bot.command()
#Prints a list of commands that the bot has.
async def guide(ctx):
    await ctx.send('This Discord bot is used to create and access a database of Balatro seeds. You can add seeds yourself, or simply search for seeds. Quotation marks are needed for any input that is multiple words (ex. "my name is bob").\n\n!addSeed (seed) "(description)" "(tags)" - Adds a seed to the database, along with a description and tag(s). Only 1 tag is required.\n!removeSeed (seed) - Removes a seed from the database. Admin required.\n!addAdmin (user) - Adds a user to the admin list. Admin required.\n!removeAdmin (user) - Removes a user from the admin list. Admin required.\n!addTag "(tag)" - Adds a tag to the list of tags. Admin required.\n!removeTag "(tag)" - Removes a tag from the list of tags. Admin required.\n!tags - Shows the list of available tags.\n!thanks - Allows you to thank the bot, and the people that made it!\n!guide - Shows this list of commands.')
    
bot.run(bot_token)
