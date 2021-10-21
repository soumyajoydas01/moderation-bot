from inspect import EndOfBlock
import os
import discord
from discord import member
from discord import message
from discord import embeds
from discord import guild
from discord import user
from discord import client
from discord.colour import Color
from discord.enums import Status
import discord.ext.commands as commands
from discord.ext.commands.core import has_permissions
import dotenv
import json

intents = discord.Intents.default()
intents.members = True
dotenv.load_dotenv()

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)


def read_blacklisted_words(filename='blacklistedWords.json'):
    data = []
    with open(filename, 'r') as f:
        data = json.loads(f.read()).get("blacklistedWords", [])
    return data


def write_json(data, filename="blacklistedWords.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


@bot.event
async def on_ready():

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="servers as moderator"))

    print("I am Online")
    print("-----------------")


@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.mention}")


@bot.command(aliases=['c'])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=2):
    await ctx.channel.purge(limit=amount+1)


@bot.command(aliases=['k'])
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    if member == None or member == ctx.message.author:
        await ctx.channel.send("You cannot kick yourself")
        return
    if member.top_role > ctx.author.top_role:  # Check if the role is below the authors role
        await ctx.send("You can only kick users with a lower role!")
        return
    await member.send(f"You have been kicked from our Server {ctx.message.guild}, because of "+reason)
    await ctx.send(f"{member.mention} has been kicked from the server {ctx.guild.name}, Reason:"+reason)
    await member.kick(reason=reason)


@bot.command(aliases=['b'])
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    if member == None or member == ctx.message.author:
        await ctx.channel.send("You cannot ban yourself")
        return
    if member.top_role > ctx.author.top_role:  # Check if the role is below the authors role
        await ctx.send("You can only ban users with a lower role!")
        return
    await member.send(f"You have been banned from our Server {ctx.guild.name}, because of "+reason)
    embed = discord.Embed(
        title="User Banned!", description=f"{member.mention} has been banned from the server {ctx.guild.name}, because of "+reason)
    # await ctx.send(f"{member.mention} has been banned from the server {ctx.guild.name}, because of "+reason)
    await ctx.send(embed=embed)
    await member.ban(reason=reason)


@bot.command(aliases=['ub'])
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_disc = member.split('#')

    for banned_entry in banned_users:
        user = banned_entry.user

        if(user.name, user.discriminator) == (member_name, member_disc):
            await ctx.guild.unban(user)
            # await ctx.send(member_name+" has been unbanned!")
            embed = discord.Embed(title="User Unbanned!",
                                  description=member_name+" has been unbanned!")
            await ctx.send(embed=embed)
            return

    embed = discord.Embed(title="User Not Found",
                          description=f"{member} was not found")
    await ctx.send(embed=embed)
    # await ctx.send(member+" was not found")


@bot.command(aliases=['m'])
@commands.has_permissions(kick_members=True)
async def mute(ctx, member: discord.Member):
    if member == None or member == ctx.message.author:
        await ctx.channel.send("You cannot mute or unmute yourself")
        return
    if member.top_role > ctx.author.top_role:
        await ctx.send("You can only mute users with a lower role!")
        return
    muted_role = ctx.guild.get_role(900024798585954325)

    await member.add_roles(muted_role)
    embed = discord.Embed(title="User Muted!",
                          description=f"{member.mention} has been muted")
    await ctx.send(embed=embed)
    # await ctx.send(member.mention + " has been muted")


@bot.command(aliases=['um'])
@commands.has_permissions(kick_members=True)
async def unmute(ctx, member: discord.Member):
    if member == None or member == ctx.message.author:
        await ctx.channel.send("You cannot mute or unmute yourself")
        return
    muted_role = ctx.guild.get_role(900024798585954325)

    await member.remove_roles(muted_role)
    embed = discord.Embed(title="User Unmuted!",
                          description=f"{member.mention} has been unmuted")
    await ctx.send(embed=embed)
    # await ctx.send(member.mention + " has been unmuted")


@bot.event
async def on_message(message):
    for word in read_blacklisted_words():
        if word in message.content:
            await message.delete()
            embed = discord.Embed(
                title="Warning!", description=f"Warning!! {message.author.mention} you're using blacklisted Words!!")
            # await message.channel.send(f"Warning!! {message.author} you're using blacklisted Words!!")
            await message.channel.send(embed=embed)

    if str(message.channel) == "images-only" and message.content != "":
        await message.channel.purge(limit=1)

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("I'm gonna pretend you didn't say that because you're not a moderator ;-;")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You have not entered all the required arguments")
    else:
        print(error)


@bot.command(aliases=['info'])
@commands.has_permissions(kick_members=True)
async def user(ctx, member: discord.Member):
    embed = discord.Embed(
        title=member.name, description=member.mention, color=discord.Colour.red())
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(icon_url=ctx.author.avatar_url,
                     text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)


@bot.command(aliases=['bl'])
@commands.has_permissions(ban_members=True)
async def blacklist(ctx):
    blacklisted_words = read_blacklisted_words()
    embed = discord.Embed(title="Black Listed Words",
                          description=', '.join(blacklisted_words), color=discord.Colour.red())
    await ctx.channel.send(embed=embed)


@bot.command(aliases=['atb'])
@commands.has_permissions(ban_members=True)
async def addtoblacklist(ctx, *, word):
    with open("blacklistedWords.json") as json_file:
        data = json.load(json_file)
        temp = data["blacklistedWords"]
        temp.append(word)
    write_json(data)


@bot.command(aliases=['h'])
async def help(ctx):
    embed = discord.Embed(title=f"**Help Command**", description="*Hi, I'm PikaBot. I'm here to help you in moderating this server. I'm developed by Soumyajoy Das aka <@!583523069167927296>*\n\n**!clear N or !c N:**\t*Deletes N Messages*\n\n**!kick @user or !k @user:**\t*Kick users from server*\n\n**!ban @user or !b @user:**\t*Ban users from server*\n\n**!unban @user#id or !ub @user#id:**\t*Unban banned users*\n\n**!mute or !m:**\t*Mutes users by adding a mute role*\n\n**!umute or !um:**\t*Unmutes users by removing mute role*\n\n**!user or !info:**\t*Gives user info*\n\n**!blacklist or !bl:**\t*Displays Blacklisted Words*\n\n**!addtoblacklist str or !atb str:**\t*Add words to blacklist*\n\n\n**NOTE:**\t**These Commands can only be used by server Moderators**", color=discord.Colour.from_rgb(245, 158, 11))
    embed.set_footer(icon_url=ctx.author.avatar_url,
                     text=f"Help command requested by {ctx.author.name}")
    await ctx.send(embed=embed)



bot.run(os.getenv('TOKEN'))
