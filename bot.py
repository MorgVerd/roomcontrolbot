"""
    Discord Bot to control your physical room
    Copyright (C) 2020 MorgVerd

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
"""

import os, sys, random, time, datetime, subprocess, socket, json, io, textwrap, traceback, base64, contextlib, logging
import socket, errno
from utils import integrityCheck

# Check versions
version = sys.version_info
if (not (version[0] == 3)): print("[FATAL] You must run on Python 3"); sys.exit(0)
if (not (version[1] > 4)): print("[FATAL] You must run on Python 3.4+"); sys.exit(0)
pythonVersion = str(str(version[0]) + "." + str(version[1]))

def safe_download(packagename, dirpath, exitiferror=True):
    attempts = 0
    while True:
        attempts += 1
        if attempts >= 3:
            print(Fore.RED + "[LAUNCHER][SAFEDOWNLOAD][FATAL] Could not install: " + packagename)
            if exitiferror:
                sys.exit(0)
            else:
                return False

        if not ((pathlib.Path(dirpath)).exists()):
            attempts += 1
            os.system("sudo lxterminal -e sudo apt-get install -y " + packagename)

        else:
            print(Fore.GREEN + "[LAUNCHER][SAFEDOWNLOAD] '" + packagename + "' Installation verified." + Style.RESET_ALL)
            return True

def safe_import(module, override=False, command="", install_name="", dont_print=False):
    attempts = 0
    while True:
        attempts += 1
        try:
            __import__(module)
            if not dont_print: print("[LAUNCHER][SAFEIMPORT] " + module + " imported")
            return
        except ImportError:
            if not override:
                if not dont_print: print(Fore.YELLOW + "[LAUNCHER][SAFEIMPORT][ERROR] " + module + " doesnt exist, Trying to install" + Style.RESET_ALL)

                if not install_name == "":
                    module = install_name
                os.system("python3 -m pip install " + module)
            else:
                if not dont_print: print(Fore.YELLOW + "[LAUNCHER][SAFEIMPORT][ERROR] " + module + " doesnt exist, Trying to install. Override on" + Style.RESET_ALL)
                os.system(command)

        if attempts > 5:
            if not dont_print: print(Fore.RED + "[LAUNCHER][SAFEIMPORT][FATAL] Tried to install " + module + " 5 times and failed each time. Exiting" + Style.RESET_ALL)
            sys.exit(0)

# Make sure we have everything, If we dont install it
# Any new imports from any cogs go here

import pathlib, json
if not ((pathlib.Path("config.json")).exists()):
    if ((pathlib.Path("config.json.example")).exists()):
        print("[LAUNCHER][FATAL] Please rename 'config.json.example' to 'config.json' as outlined in the config guide here:\nhttps://github.com/morgverd/roomcontrolbot#configuration")
    else:
        print("[LAUNCHER][FATAL] Configuration file doesn't exist. Please follow the guide here:\nhttps://github.com/morgverd/roomcontrolbot#configuration")
    sys.exit(0)
if not ((pathlib.Path("presences.py")).exists()):
    if ((pathlib.Path("presences.py.example")).exists()):
        print("[LAUNCHER][FATAL] Please rename 'presences.py.example' to 'presences.py.example' as outlined in the config guide here:\nhttps://github.com/morgverd/roomcontrolbot#configuration")
    else:
        print("[LAUNCHER][FATAL] Presences file doesn't exist. Please follow the guide here:\nhttps://github.com/morgverd/roomcontrolbot#configuration")
    sys.exit(0)


with open("config.json", "r") as f:
    try:
        fileConfig = json.load(f)
    except json.decoder.JSONDecodeError as err:
        print("[LAUNCHER][FATAL] Configuration is not valid JSON. Are you missing any characters? Heres a helpfull message:\n" + str(err))
        sys.exit(0)

currentDir = str(fileConfig["rootpath"])

if (not (fileConfig["skipsafeimports"] == "TRUE")):
    print("[LAUNCHER] Doing Imports")

    safe_import("colorama", dont_print=True); import colorama; from colorama import Fore, Style
    safe_import("discord", install_name="discord.py")
    safe_import("asyncio")
    safe_import("pathlib")
    safe_import("json_pickle", install_name="jsonpickle")
    safe_import("urllib.request")
    safe_import("dhooks")
    safe_import("aiohttp")
    safe_import("pytz")
    safe_import("googletrans")
    safe_import("inspect")
    safe_import("lxml")
    safe_import("PIL", install_name="pillow")
    safe_import("urbandict")
    safe_import("bs4", override=True, command="sudo apt-get install -y python3-bs4")
    safe_import("requests")
    safe_import("numpy")
    safe_import("pornhub", override=True, command=f"sudo apt-get install -y git && sudo rm -r {currentDir}/pornhub-api || true && sudo git clone https://github.com/sskender/pornhub-api && sudo mv {currentDir}/pornhub-api/pornhub /usr/lib/python{pythonVersion}/pornhub")
    safe_import("aiosocks")
    safe_import("difflib")
    safe_import("gtts", install_name="gTTs")
    safe_import("ast")
    safe_import("pytube", install_name="pytube3")
    safe_import("pysubs2")
    safe_import("pyspeedtest")
    safe_import("alsaaudio", override=True, command="sudo apt-get install -y python-alsaaudio")
    
else:
    import colorama; from colorama import Fore, Style
    print("[LAUNCHER][CONFIG] Skipped import checks")


from utils.funcs import Funcs
from utils.generators import Generators
from utils.permissions import Permissions
from utils.filters import Filters
from utils.hooks import Hooks
import difflib
from discord.ext import commands
import discord, asyncio


print("[LAUNCHER][CONFIG] Got prefix: '" + fileConfig["prefix"] + "'")

bot = commands.Bot(command_prefix=fileConfig["prefix"], description="A bot I use to inact my ausitic rage")
bot.remove_command("help") # Remove the Help command to be set by our own one later

# Get file configuration and load into bot.config so it can be ran as bot.config["arg"]

bot.config = fileConfig

# Funcs defintion
bot.funcs = Funcs
bot.get_json = Funcs.get_json
bot.get_text = Funcs.get_text
bot.safe_delete = Funcs.safe_delete
bot.killmusic = Funcs.killmusic
bot.read_raw = Funcs.read_raw
bot.speak = Funcs.speak
bot.cleanString = Funcs.cleanString
bot.rawfromurl = Funcs.rawfromurl

# Setup hooks
bot.hook = Hooks

# Generators defintion
bot.generators = Generators
bot.generate_embed = Generators.generate_embed
bot.generate_error = Generators.generate_error
bot.generate_embedcolor = Generators.generate_embedcolor

# Permission Manager
bot.permissions = Permissions
bot.permissions_isowner = Permissions.permissions_isowner
bot.permissions_hasrole = Permissions.permissions_hasrole
bot.permissions_isallowed = Permissions.permissions_isallowed
bot.permissions_userchatmuted = Permissions.permissions_userchatmuted
bot.permissions_userlivebanned = Permissions.permissions_userlivebanned
bot.permissions_restrictedtime = Permissions.permissions_restrictedtime

# Filter Manager
bot.filter_check = Filters.filter_check
bot.filter_englishonly = Filters.filter_englishonly

bot.commandnames = None # For message error detecton
bot.blacklistedwords = []
bot.videoData = {}
bot.videoPlaying = False
bot.videoCurrentTimer = 0
bot.lastVolume = 0
bot.ismuted = False
bot.subtitlesexist = False
bot.header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"}
bot.commandsCache = []
bot.runningCustomVersion = False
bot.bannedFromChannels = []
bot.bannedFromChannelID = {}

bot.webSystem = {}
bot.webSystem["enabled"] = None
bot.webSystem["ip"] = str(bot.config["web"]["localIP"])
bot.webSystem["port"] = str(bot.config["web"]["port"])
bot.webSystem["location"] = str(f"http://{bot.webSystem['ip']}:{bot.webSystem['port']}/")

if (bot.config["web"]["enabled"] == "TRUE"):
    bot.webSystem["enabled"] = True
else:
    bot.webSystem["enabled"] = False

safe_download("vlc", "/usr/bin/vlc") # Core requirement
safe_download("alsa-utils", "/usr/bin/alsamixer") # Core requirement
if bot.webSystem["enabled"]: safe_download("php7.3", "/etc/php/7.3") # PHP for Web Server

os.system("sudo killall vlc") # VLC Player for music
if bot.webSystem["enabled"]: os.system("sudo killall php") # Stop any running webserver

if (bot.webSystem["enabled"]):
    # Setup web
    bot.webSystem["enabled"] = True
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((fileConfig["web"]["localIP"], int(fileConfig["web"]["port"])))
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            print(Fore.RED + "[LAUNCHER][WEB][FATAL] Port " + fileConfig["web"]["port"] + " is in use, Please change in config." + Style.RESET_ALL)
        else:
            print(Fore.RED + "[LAUNCHER][WEB][FATAL] " + str(e) + Style.RESET_ALL)
        print(Fore.RED + "[LAUNCHER][WEB][FATAL] Web is enabled and there is a fatal error. Please read the error above." + Style.RESET_ALL)
        print(Fore.RED + "[LAUNCHER][WEB][FATAL] If you cant fix this (you dont want to open a port), Please disable the web system in the config." + Style.RESET_ALL)
        sys.exit(0)

else:
    # Web has been disabled in config.json
    bot.webSystem["enabled"] = False

s.close()
if bot.webSystem["enabled"]: os.system("lxterminal -e sudo php -S " + bot.config["web"]["localIP"] + ":" + bot.config["web"]["port"] + " -t " + bot.config["rootpath"] + "/web")
os.system("lxterminal -e amixer set PCM -- 0%") # Set to default
print("[LAUNCHER] Set volume to 0%")

async def checkServerConnections():
    for server in bot.guilds:
        if not (int(server.id) == (bot.config["serverID"])):
            print("[LAUNCHER][CHECKSERVERCONNECTIONS] Bot is in " + str(server.name) + " (" + str(server.id) + "). This is not the serverID listed in Config.py. About to leave")
            try:
                await server.leave()
                print("[LAUNCHER][CHECKSERVERCONNECTIONS] Successfully left " + str(server.name) + " (" + str(server.id) + ")")
            except Exception:
                print(Fore.YELLOW + "[LAUNCHER][CHECKSERVERCONNECTIONS][ERROR] Couldn't leave " + str(server.name) + " (" + str(server.id) + ")" + Style.RESET_ALL)
    return

@bot.event
async def on_member_update(before, after):
    embed = None
    if not (((str(before.nick)).upper()) == ((str(after.nick)).upper())):
        # Nickname Change
        embed=discord.Embed(title=f"{after.name} Changed their Nickname from ``{before.nick}`` to ``{after.nick}``", color=(await bot.generate_embedcolor()))
    if not (((str(before.name)).upper()) == ((str(after.name)).upper())):
        # Nickname Change
        embed=discord.Embed(title=f"{after.name} Changed their Name from ``{before.nick}`` to ``{after.nick}``", color=(await bot.generate_embedcolor()))
    if not embed is None:
        channel = bot.get_channel(699287508688699392)
        await channel.send(embed=embed)
    return

@bot.event
async def on_ready():
    print("[LAUNCHER] on_ready() triggered. Bot active.")
    # Check this version to see if its the most up-to date
    localVersion = ((open(currentDir + "/data/version.txt")).read()).replace("\n", "")
    r = await bot.rawfromurl("https://raw.githubusercontent.com/MorgVerd/roomcontrolbot/master/data/version.txt?noCache=" + str(int(time.time())))
    r = r.replace("\n", "")
    print("[LAUNCHER][VERSIONCHECK] Local Version: " + localVersion)
    print("[LAUNCHER][VERSIONCHECK] Remote Version: " + r)

    # File integrity check
    supposedIntegrity = await bot.rawfromurl("https://raw.githubusercontent.com/MorgVerd/roomcontrolbot/master/data/integritykey.txt?noCache=" + str(int(time.time())))
    integrityKey = str(integrityCheck.getIntegrityKey(bot.config["rootpath"]))
    
    if not supposedIntegrity == integrityKey:
        bot.runningCustomVersion = True
        print(Fore.YELLOW + "[LAUNCHER][INTEGRITYCHECK] You are running an edited version to the one on GitHub." + Style.RESET_ALL)
        print(Fore.YELLOW + "[LAUNCHER][INTEGRITYCHECK] This means you edited some code, Or changed something in a core file." + Style.RESET_ALL)
        print(Fore.YELLOW + "[LAUNCHER][INTEGRITYCHECK] This could make this build unstable." + Style.RESET_ALL)
    else:
        bot.runningCustomVersion = False
        print(Fore.GREEN + "[LAUNCHER][INTEGRITYCHECK] You are running a stable, unedited build of this bot from GitHub." + Style.RESET_ALL)

    if localVersion == r:
        print("[LAUNCHER][VERSIONCHECK] Up-to date")
    else:
        # Not up-to date
        if not ((pathlib.Path("ignoreversion.txt")).exists()):
            print(Fore.RED + "[LAUNCHER][VERSIONCHECK] This bot is out of date. Please update by going to:\nhttps://github.com/morgverd/roomcontrolbot\nAnd re-installing it. Remember to keep the config.json file!\n\nTo ignore this warning and continue make a txt file called 'ignoreversion.txt' in the root of the bot and put '1' in it.\n\n" + Style.RESET_ALL)
            input(Fore.RED + "Press enter to exit..." + Style.RESET_ALL)
            sys.exit(0)
        else:
            print(Fore.RED + "[LAUNCHER][VERSIONCHECK] Out of date, However ignore file is present." + Style.RESET_ALL)

    print("[LAUNCHER] Checking for server connections.")
    await checkServerConnections()
    print(Fore.GREEN + "[LAUNCHER] Finished lancher. Comitting handoff to cogs." + Style.RESET_ALL)
    await bot.change_presence(activity=discord.Game(name='Initialising Bot...'))
    if (await bot.permissions_restrictedtime(bot)):
        await bot.speak(bot, "Initialising", isbot=True)
    else:
        print("[LAUNCHER][SPEAK] Couldn't speak as its a restricted time")

@bot.event
async def on_message(message):
    await bot.hook.messageSent(bot, message)
    if (((bot.config["token"]).upper()) in ((message.content).upper())):
        await bot.hook.tokenSent(bot, message)
        print(Fore.YELLOW + "[LAUNCHER][ONMESSAGE][WARNING] Token was mentioned in chat, Removing it" + Style.RESET_ALL)
        # Token is in message
        await bot.safe_delete(message)
        await message.channel.send(embed=(await bot.generate_error(message, f"The message sent by <@{message.author.id}> contains content that we consider to be sensitive. For this reason message was deleted.")), delete_after=20)
        return
    # Do a few checks
    if (bot.commandnames == None):
        cmds = (bot.commands)
        bot.commandsCache = cmds
        cmdList = []
        for cmd in cmds:
            cmdList.append((cmd.name).upper())
            if not (len(cmd.aliases) == 0):
                for alias in (cmd.aliases):
                    # alias's
                    cmdList.append(alias.upper())

        bot.commandnames = cmdList
        print("[LAUNCHER][ONMESSAGE] Initialised Command Error detection.")

    if message.author.id == bot.user.id: return
    if ((message.content).startswith(bot.config["prefix"])):

        strip_a = str(message.content).replace(bot.config["prefix"], "")
        if " " in strip_a:
            strip_b = (strip_a.split(" "))[0]
        else:
            strip_b = strip_a
        strip_b = strip_b.replace(" ", "")
    if message.guild is None:
        # In PM's
        if ((strip_b.upper()) == "HELP"):
            await bot.process_commands(message) # If its help
            return
        await bot.hook.messageInPMs(bot, message)
        await message.channel.send("Well. :eyes:  We aren't in a Discord Server! Im an exclusive guy. If you want me please talk to me in a Discord Server. I dont do PM's :rolling_eyes:")
        return
    else:

        if ((message.content).startswith(bot.config["prefix"])):
            if ((str(strip_b).upper()) == "HELP"):
                await message.channel.send(embed=(await bot.generate_error(bot, "Please run this command in our PM's, Since everyone's help commands are tailored to them.")), delete_after=20)
                return
            if ((str(strip_b).upper()) in (bot.commandnames)):
                # command exists, Its a cmd
                print(Fore.MAGENTA + "[LAUNCHER][ONMESSAGE][COMMAND RAN] " + str(message.author.name) + " (" + str(message.author.id) + ")  ->  " + (str((message.content).lower()).replace(bot.config["prefix"], "")) + Style.RESET_ALL)

                chars = (bot.config["prefix"] + (strip_b.lower()))
                charx = len(chars)
                fixedList = []
                for letter in list(chars):
                    fixedList.append(letter)

                i = 0
                for letter in (message.content):
                    if i >= charx: fixedList.append(letter)
                    i += 1

                fixedString = ("".join(fixedList))
                oldmessage = message
                message.content = fixedString # Replace content with Fixed string
                await bot.hook.commandSent(bot, oldmessage, message)
                await bot.process_commands(message)
                return

            await bot.safe_delete(message)

            cmd = (((message.content).replace(bot.config["token"], "")).replace(" ", "")).upper()
            if (len(cmd) == 0): cmd = "Nothing..."
            closestMatches = (difflib.get_close_matches(cmd, bot.commandnames))
            closestMatchString = ""
            if (len(closestMatches) == 0):
                closestMatchString = "There are no predictive closest matches found"
            else:
                closestMatchString = "The closest match to what you entered is ``" + str(closestMatches[0]).lower() + "``. Did you mean that?"
            await bot.hook.commandDoesntExist(bot, message, closestMatches)
            embed=discord.Embed(title="Couldn't find that command")
            embed.set_footer(text="Will Self-Destruct in 20 seconds")
            embed.add_field(name="You Entered", value=("``"+str(cmd.lower())+"``"), inline=True)
            embed.add_field(name="Closest Match", value=str(closestMatchString), inline=False)
            await message.channel.send(embed=embed, delete_after=20)
            return
        
        else:
            # Not a command, Normal chat message.
            # Check if user is muted or not
            await bot.hook.standardMessage(bot, message)
            if (await bot.permissions_userchatmuted(bot, message.author, takeBot=True)):
                await bot.hook.messageDeletedUserChatBanned(bot, message)
                await bot.safe_delete(message)
                return

        return

async def presence_changer():
    print("[LAUNCHER][PRESENCECHECKER] Loading...")
    await bot.wait_until_ready()
    await asyncio.sleep(5)
    if (await bot.permissions_restrictedtime(bot)):
        await bot.speak(bot, "Ready", isbot=True)
    else:
        print("[LAUNCHER][PRESENCECHECKER][SPEAK] Couldn't speak as its a restricted time")
    
    usedIDs = []

    import presences
    listOfpresences = presences.listOfPrecences
    lengthOfpresences = 0
    for item in listOfpresences.values():
        lengthOfpresences += 1

    while True:

        if not (bot.videoPlaying):
            
            foundItem = False
            while (not foundItem):

                # Select an item
                if (len(usedIDs) == lengthOfpresences):
                    usedIDs = []

                i = random.randint(0, lengthOfpresences - 1)

                if (not (str(i) in usedIDs)):
                    usedIDs.append(str(i))
                    foundItem = True
                    string = list(listOfpresences)[i]; mode = listOfpresences[list(listOfpresences)[i]]
                    break
            
            if mode.upper() == "PLAYING":
                print("[LAUNCHER][PRESENCECHECKER] Setting presence to 'PLAYING' '" + string + "'")
                await bot.change_presence(activity=discord.Game(name=string))
            elif mode.upper() == "WATCHING":
                print("[LAUNCHER][PRESENCECHECKER] Setting presence to 'WATCHING' '" + string + "'")
                activity = discord.Activity(name=string, type=discord.ActivityType.watching)
                await bot.change_presence(activity=activity)
            else:
                print(Fore.RED + "[LAUNCHER][PRESENCECHECKER][ERROR] Couldn't find valid dict item to change presence. Staying the same for now." + Style.RESET_ALL)

            await bot.hook.presenceChangerUpdate(bot, (mode.upper()), string)

            await asyncio.sleep(30)

        else:
            # Playing something, Wait
            await bot.hook.presenceChangerBlocked(bot)
            await asyncio.sleep(1)

@bot.event
async def on_disconnect():
    await bot.hook.disconnectEvent(bot)
    print(Fore.RED + "[LAUNCHER][ONDISCONNECT] Bot application is quitting" + Style.RESET_ALL)
    if bot.videoPlaying:
        # Video is playing
        os.system("killall vlc")
        bot.videoPlaying = False

    channel = bot.get_channel(bot.config["debugChannel"])
    print(Fore.GREEN + "[LAUNCHER][ONDISCONNECT][RELAUNCH] Attempting to begin relaunch..." + Style.RESET_ALL)
    os.system("python3 bot.py")

# Check needed for Vote Command in Fun
@bot.event
async def on_voice_state_update(member, before, after):
    if str(member.id) in bot.bannedFromChannels:
        # User is banned from channels still
        channelTheirBannedFrom = bot.bannedFromChannelID[str(member.id)]
        if (channelTheirBannedFrom == str(after.channel.id)):
            # User is not allowed there
            try:
                await member.send("You're still banned from going in there since people voted to have you removed. Try in ``5`` minutes time.")
            except Exception:
                pass

            channel = bot.get_channel(bot.config["afkvoice_channel"])
            try:
                await member.move_to(channel, reason=f"Tried to rejoin despite being votebanned")
            except Exception:
                pass
    return

if __name__ == "__main__":
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            do = True
            if (str(filename[:-3]).upper() == "NSFW"):
                # Check NSFW config
                if not ((bot.config["allowNSFWcommands"]) == "TRUE"):
                    print("[LAUNCHER][MAIN] NSFW Commands have been disabled. Not loading cog.")
                    do = False
            if do:
                bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"[LAUNCHER][MAIN][INFO] Loaded Cog : {filename[:-3]}")


presence_changer_task = bot.loop.create_task(presence_changer())
try:
    bot.run(bot.config["token"])
except Exception as e:
    err = str((e.args[0]).upper())
    knownErrorDefintions = {
        "EVENT LOOP STOPPED BEFORE FUTURE COMPLETED." : "You pressed CTRL+C to shutdown the bot.",
        "IMPROPER TOKEN HAS BEEN PASSED." : "Invalid token given, Please check your config.json"
    }
    if str(err) in knownErrorDefintions:
        errorMessage = knownErrorDefintions[err]
    else:
        errorMessage = ("Unknown error message: " + err)

    print(Fore.RED + "\n[LAUNCHER][END][FATAL] " + errorMessage + Style.RESET_ALL)
    os.system("sudo killall vlc") # VLC Player for music
    if bot.webSystem["enabled"]: os.system("sudo killall php") # Stop any running webserver
    print(Fore.GREEN + "[LAUNCHER][END] Successfully stopped all running processes (VLC, PHP)" + Style.RESET_ALL)
    sys.exit(0)
