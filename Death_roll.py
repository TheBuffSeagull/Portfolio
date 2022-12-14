# bot.py
import os
import time
import random
import asyncio

import class_object_storage as COS
from datetime import datetime


#env package stuff
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)


class Player:        
    def __init__(self, ID, name):
        self.ID = str(ID)
        self.name = str(name)

        try:
            DATA = COS.OBJECT.load_file('DATA.json')
        except:
            DATA = {}
    
        
        if str(ID) in list(DATA.keys()):
            print(f"Found {name}'s data.")
            LOAD = COS.OBJECT.load(str(ID), 'DATA.json')
            self.Points = LOAD.Points
            self.Wins = LOAD.Wins
            self.Losses = LOAD.Losses
            self.last_used = LOAD.last_used
        else:
            print(f"{name} has joined Death Roll.")
            self.Points = 100
            self.Wins = 0
            self.Losses = 0
            self.last_used = str(datetime.today().date())

    def save(PLAYER):
        COS.OBJECT.save(PLAYER.ID, PLAYER, 'DATA.json')


class Death_Roll:
    def __init__(self, PLAYER1, PLAYER2, bet):
        self.ID  = f"{PLAYER1.ID}-{PLAYER2.ID}"
        self.Player1 = PLAYER1
        self.Player2 = PLAYER2
        self.roll = 100
        self.bet = bet
        self.started = False

        MATCH = COS.OBJECT.load_file("MATCH.json")
        if f"{PLAYER1.ID}-{PLAYER2.ID}" in MATCH.keys():
            print("Match already exists.")
            self.exist = True
        else:
            print(f"New match between {PLAYER1.name} and {PLAYER2.name}.")
            COS.OBJECT.save(self.ID, self, "MATCH.json")
            self.exist = False

    def Death_roll(max_roll):
        result = random.randint(1, max_roll-1)
        return result

###### 1v1 MATCH STUFF #############################
async def pose_question(ctx, TARGET_obj, message):

        msg = await ctx.send(message)

        await msg.add_reaction('✅')    
        await msg.add_reaction('❌')
        #r = reaction, U = User
        def check(r, U, TARGET = TARGET_obj.id):  # r = discord.Reaction, u = discord.Member or discord.User.
            return str(U.id) == str(TARGET) and str(r) in ["✅", "❌"]
        
        try:
            print('Waiting...')
            reaction, _user = await bot.wait_for('reaction_add', timeout=300, check=check)
            print("Got response...")
            print(reaction, _user)
        
        except asyncio.TimeoutError:
            print("No response...")
            # at this point, the check didn't become True.
            await ctx.send(f"**{TARGET_obj.name}**, didnt react with a ✅ or ❌ in 5 minutes.")
            return False
        
        else:
            if str(reaction) == "✅":
                #r = reaction, U = User
                return True
            
            elif str(reaction) == "❌":
                return False  


@bot.command(aliases=['dr', 'DR', 'Dr','dR'], help=" Type !dr @SOMEONE Amount_to_Bet to Death Roll.")
async def death_roll(ctx, Target, bet= 0):
    ID = str(ctx.message.author.id)
    NAME = str(ctx.message.author)
    bet = int(bet)
    if Target != None:
        #TARGET STUFF for @
        TARGET = str(Target)
        if TARGET.startswith('<@'):
            TARGET = ctx.message.mentions
            TARGET = TARGET[0].id
        
        #TARGET OBJECT LEAVE IT
        TARGET_obj = await bot.fetch_user(int(TARGET))
        #USER OBJECT LEAVE IT
        user = ctx.message.author


    TARGET_NAME = str(await bot.fetch_user(TARGET))
    

    PLAYER1 = Player(ID, NAME)
    PLAYER2 = Player(TARGET, TARGET_NAME)
    
    #adding 100 daily points
    PLAYER_LIST = [PLAYER1, PLAYER2]
    for p in PLAYER_LIST:
        if p.last_used != str(datetime.today().date()):
            p.last_used = str(datetime.today().date())
            p.Points +=100
            await ctx.send(f"Gave {p.name[:-5]} 100 points for {str(datetime.today().date())}")
    
    Player.save(PLAYER1)
    Player.save(PLAYER2)
            


    
    CAN_BET = False
    print(PLAYER1.Points, PLAYER2.Points, int(bet))
    if PLAYER1.Points >= int(bet):
        if PLAYER2.Points >= int(bet):
            CAN_BET = True

    if int(bet) >= 0:
        if CAN_BET == False:
            await ctx.send(f"__{PLAYER1.name[:-5]}__ or __{PLAYER2.name[:-5]}__ is to fucking broke to do that.")
        else:    
            MATCH = Death_Roll(PLAYER1, PLAYER2, bet)
            if MATCH.exist == False:
                        await ctx.send(
                        f"----------------------------------------\n"+
                        f"__**{PLAYER1.name[:-5]}:**__\n"+
                        f"\tPoints: {PLAYER1.Points}\n"+
                        f"\t\tW: {PLAYER1.Wins}\t"+
                        f"\t\tL: {PLAYER1.Losses}\n\n"
                        f"\t\t\t__VS__ for __**{bet} points**__\n\n"
                        f"__**{PLAYER2.name[:-5]}:**__\n"+
                        f"\tPoints: {PLAYER2.Points}\n"+
                       f"\t\tW: {PLAYER2.Wins}\t"+
                        f"\t\tL: {PLAYER2.Losses}\n\n"
                        f"----------------------------------------\n"
                        )

                        if str(TARGET) == "1009710064308850799":
                            await accept(ctx, BOT= True)
                            
                        if str(TARGET) != "1009710064308850799":
                            if await pose_question(ctx, TARGET_obj, f"**{TARGET_obj.name}**, do you accept the Death Roll for **{bet}** points?"):
                                await accept(ctx, question = True)
                            else:
                                await decline(ctx)

            else:
                await ctx.send(f'**{PLAYER1.name[:-5]} or {PLAYER2.name[:-5]} are already in a match.**\n\nType !decline/!d to cancel any active matches.')




@bot.command(aliases=['d', 'D', 'Decline', 'DECLINE','DEcline'], help="Cancel any existing match you are in.")
async def decline(ctx):
    ID = str(ctx.message.author.id)
    MATCH = COS.OBJECT.load(ID, 'MATCH.json')

    if MATCH.roll >= 100:
        await ctx.send(f'Declined match between **{MATCH.Player1.name[:-5]}** and **{MATCH.Player2.name[:-5]}**')
        COS.OBJECT.delete(ID, 'MATCH.json')  
    else:
        await ctx.send(f'Game between **{MATCH.Player1.name[:-5]}** and **{MATCH.Player2.name[:-5]}** is already in progress.')

#accept command
@bot.command(aliases=['a', 'A', 'Accept', 'ACcept','ACCEPT'], help="Accepts a challenge and starts Death Roll.")
async def accept(ctx, BOT = False, question = False):
    ID = str(ctx.message.author.id)

    if BOT == False:
        MATCH = COS.OBJECT.load(ID, 'MATCH.json')
    else:
        MATCH = COS.OBJECT.load(f"{ID}-1009710064308850799", 'MATCH.json')
    
    if MATCH.started == False:
        
        MATCH.started = True
        COS.OBJECT.save(MATCH.ID, MATCH, 'MATCH.json')
        print("Match Accepted")

        ROLL = MATCH.roll
        BET = MATCH.bet

        PLAYER1 = Player(MATCH.Player1.ID, MATCH.Player1.name)
        PLAYER2 = Player(MATCH.Player2.ID, MATCH.Player2.name)
        
        TURN = PLAYER2.name

        if ID == PLAYER2.ID or BOT or question == True:
            if BOT == False:
                await ctx.send(f"__{PLAYER2.name[:-5]}__ started the match.")
            elif BOT == True:
                await ctx.send(f"__{PLAYER2.name[:-5]}__ automatically started the match.")
            while ROLL != 1:
                ROLL = MATCH.roll
                
                ROLL = Death_Roll.Death_roll(ROLL)
                
                if ROLL == 1:
                    print(f"Turn: {TURN} | Roll: {MATCH.roll-1}")
                    await ctx.send(f"__**{TURN[:-5]}**__: :game_die: **1**\t:skull:")
                    if TURN != PLAYER2.name:
                        PLAYER2.Points += BET
                        PLAYER1.Points -= BET
                        PLAYER2.Wins += 1
                        PLAYER1.Losses += 1

                        if BET != 0:
                            await ctx.send(
                                f"----------------------------------------\n"+
                                f":crown:  **__{PLAYER2.name[:-5]}__** wins **__{BET}__** points.\n"
                                f"\t\tPoints: {PLAYER2.Points}\n"+
                                f"\t\tW: {PLAYER2.Wins}\t"+
                                f"\t\tL: {PLAYER2.Losses}\n"+
                                f"----------------------------------------\n"
                                )

                    elif TURN != PLAYER1.name:
                        PLAYER1.Points += BET
                        PLAYER2.Points -= BET
                        PLAYER1.Wins += 1
                        PLAYER2.Losses += 1

                        if BET != 0:
                            await ctx.send(
                                f"----------------------------------------\n"+
                                f":crown:  **__{PLAYER1.name[:-5]}__** wins **__{BET}__** points.\n"
                                f"\t\tPoints: {PLAYER1.Points}\n"+
                                f"\t\tW: {PLAYER1.Wins}\t"+
                                f"\t\tL: {PLAYER1.Losses}\n"+
                                f"----------------------------------------\n"
                                )

                    Player.save(PLAYER1)
                    Player.save(PLAYER2)

                    COS.OBJECT.delete(MATCH.ID, "MATCH.json")
                
                else:
                    await ctx.send(f"__{TURN[:-5]}__: :game_die: **{ROLL}**")
                    MATCH.roll = ROLL
                    print(f"Turn: {TURN} | Roll: {MATCH.roll}")
                    #basic flip flop in while loop
                    if TURN == PLAYER2.name:
                        TURN = PLAYER1.name
                    elif TURN == PLAYER1.name:
                        TURN = PLAYER2.name
                    
                    if MATCH.roll <= 100:
                        time.sleep(1)
 
        else:
            await ctx.send(
                f"```{PLAYER1.name} started the match.\n\nThe other player must type !accept/!a in order to start.\n"+
                f"Type **!decline/!d** to decline or delete you own challenge.```\n"
                )
    else:
        await ctx.send("You have already started this match :eyes:")



@bot.command(aliases=['Info', 'INFO'], help="Get players stats.")
async def info(ctx):
    await ctx.send(
    f"__1.__ In this game __if you roll a 1 you lose.__\n"+
    f"__2.__ The game starts on a 100 sided dice.\n"+
    f"__3.__ Whenever someone rolls that result becomes the new highest possible roll.\n"+
    f"__4.__ Type **!dr @someone bet** to start.\n"
    f"\t\tEx:\n\t\t\t**!dr @TheBuffSeagull 50** <--- bet of 50 points\n\t\t\t**!dr @TheBuffSeagull** <--- no bet\n"
    f"__5.__ Type **!accept/!a** to accept a challenge and start a match.\n"
    f"__6.__ Type **!decline/!d** to decline or delete you own challenge.\n"
    f"__7.__ Type **!stats/!s** to see your player stats.\n"
    f"__8.__ The Dice will automatically roll until a loser is decided.\n"
    )

@bot.command(aliases=['Stats', 's', 'S', 'STats','STATS'], help="Get players stats by either @ing them or using their ID")
async def stats(ctx, TARGET = ''):
    ID = str(ctx.message.author.id)

    if TARGET.startswith('<@'):
        TARGET = ctx.message.mentions 
        
        TARGET = str(TARGET[0].id)
    
    if TARGET != '':
        PLAYER = COS.OBJECT.load(TARGET, 'DATA.json')
    else:
        PLAYER = COS.OBJECT.load(ID, 'DATA.json')

    if PLAYER.last_used != str(datetime.today().date()):
            PLAYER.last_used = str(datetime.today().date())
            PLAYER.Points +=100
            await ctx.send(f"Gave {PLAYER.name[:-5]} 100 points for {str(datetime.today().date())}")


    await ctx.send(
    f"\n\n__**{PLAYER.name[:-5]}:**__\n"+
    f"\tPoints: {PLAYER.Points}\n"+
    f"\tWins: {PLAYER.Wins}\n"+
    f"\tLosses: {PLAYER.Losses}\n\n"
    )
    Player.save(PLAYER)

@bot.command(aliases=['Gift', 'g', 'G', 'Give','give', 'GIFT', 'GIVE'], help="Give player points from your own stash.")
async def gift(ctx, TARGET, GIFT):
    ID = str(ctx.message.author.id)
    
    CAN_GIVE = False
    GIFT = int(GIFT)
    if TARGET.startswith('<@'):
        TARGET = ctx.message.mentions 
        
        TARGET = str(TARGET[0].id)
        print(TARGET)

    

    PLAYER1 = COS.OBJECT.load(ID, 'DATA.json')
    PLAYER2 = COS.OBJECT.load(TARGET, 'DATA.json')

    PLAYER_LIST = [PLAYER1, PLAYER2]
    for p in PLAYER_LIST:
        if p.last_used != str(datetime.today().date()):
            p.last_used = str(datetime.today().date())
            p.Points +=100
            await ctx.send(f"Gave {p.name[:-5]} 100 points for {str(datetime.today().date())}")
    
    if str(PLAYER1.name) != (str(PLAYER2.name)):
        if GIFT > 0:
            if GIFT <= int(PLAYER1.Points):
                CAN_GIVE = True
    else:
        await ctx.send(f"That is not possible.")
    
    if CAN_GIVE == True:
        PLAYER1.Points -= GIFT
        PLAYER2.Points += GIFT
        await ctx.send(f"Gave {GIFT} to {PLAYER2.name[:-5]}")
    elif GIFT == 0:
        await ctx.send(f":upside_down: :calling:")

    Player.save(PLAYER1)
    Player.save(PLAYER2)



@bot.command(aliases=['id', 'ID', 'lobby', 'LOBBY','Lobby', 'list', 'LIST'], help="Give player points for using other bot.")
async def usage_points(ctx, *, arg):
    ID = str(ctx.message.author.id)
    NAME = str(ctx.message.author)

    PLAYER = COS.OBJECT.load(ID, 'DATA.json')

    PLAYER_LIST = [PLAYER]
    for p in PLAYER_LIST:
        if p.last_used != str(datetime.today().date()):
            p.last_used = str(datetime.today().date())
            p.Points +=100
            await ctx.send(f"Gave {p.name[:-5]} 100 points for {str(datetime.today().date())}")
    
    PLAYER.Points += 5
    print("Added 5 points for bot usage")

    Player.save(PLAYER)

@bot.command(aliases=['q', 'Q', 'Quote', 'quote','QUOTE'], help="Give player points for using other bot.")
async def usage_points_quote(ctx, *args):
    ID = str(ctx.message.author.id)
    NAME = str(ctx.message.author)

    PLAYER = COS.OBJECT.load(ID, 'DATA.json')

    PLAYER_LIST = [PLAYER]
    for p in PLAYER_LIST:
        if p.last_used != str(datetime.today().date()):
            p.last_used = str(datetime.today().date())
            p.Points +=100
            await ctx.send(f"Gave {p.name[:-5]} 100 points for {str(datetime.today().date())}")
    
    args = ' '.join(args)
    
    #with open(r'C:\Users\Reach\Desktop\AOT_User_Dictionary_V4\Quotes.json', 'r') as f:
    #    quotes = f.read()
    #    print(quotes)
    #    print(type(quotes))
    if args.startswith("add"):
        PLAYER.Points += 5
        print("Added 5 points for quote")

    Player.save(PLAYER)


@bot.command(aliases=['Roll', 'r', 'R', 'ROLL'], help="Give player points from your own stash.")
async def roll(ctx, custom_roll):
    ID = str(ctx.message.author.id)
    MATCH = COS.OBJECT.load(ID, "MATCH.json")
    MATCH.roll = int(custom_roll)

    await ctx.send(f"Changed match 1st max roll to {custom_roll}")

    COS.OBJECT.save(MATCH.ID, MATCH, "MATCH.json")

@bot.command(aliases=['Servers'], help="gets current active server info (only usable by Seagull)")
async def servers(ctx):
    if ctx.message.author.id == 104454052884021248:
        await bot.wait_until_ready()
        await ctx.send(f'Current Servers:')
        i = 0
        activeservers= [f"{i}. **{g.name}**" for g in bot.guilds]

        await ctx.send('\n'.join(activeservers))

if __name__ == '__main__':
    bot.run(TOKEN)
