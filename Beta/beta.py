import discord
from discord.ext import commands
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo
import random
import pyodbc
from decimal import Decimal as D

sql_connection = 'DRIVER={SQL Server Native Client 11.0};SERVER=localhost;DATABASE=BotBeta;UID=sa;PWD=wa11paper'

# get_prefix Definition ------------------------------------------------------------------------------------------------
def get_prefix(client, message):
    cnxn = pyodbc.connect(sql_connection)
    cursor = cnxn.cursor()
    cursor.execute("select prefix from Prefixes where ServerId = ?", message.guild.id)
    row = cursor.fetchone()
    if not row:
        return "."
    else:
        return row.prefix

client = commands.Bot(command_prefix = get_prefix)

# update_prefix Definition ---------------------------------------------------------------------------------------------
async def update_prefix(serverid, prefix):

    cnxn = pyodbc.connect(sql_connection)
    cursor = cnxn.cursor()
    cursor.execute("select prefix from Prefixes where ServerId = ?", serverid)
    row = cursor.fetchone()
    if not row:
        cursor.execute("insert into Prefixes (ServerId, Prefix) values (?, ?)", serverid, prefix)
    else:
        cursor.execute("Update Prefixes set prefix = ? where serverid = ?", prefix, serverid)

    cnxn.commit()
    return

# Only Allow Admins To Change Prefix -----------------------------------------------------------------------------------
@client.command()
@commands.has_permissions(administrator = True)
async def setprefix(ctx, prefix):

    await update_prefix(ctx.guild.id, prefix)

    em = discord.Embed(title=f"My server prefix was changed to `{prefix}`", color=discord.Color.red())
    await ctx.send(embed=em)

# Reveals Prefix On Ping -----------------------------------------------------------------------------------------------
@client.event
async def on_message(message):
    if client.user.mentioned_in(message):

        pre = get_prefix(client, message)

        em = discord.Embed(title=f"My current server prefix is `{pre}`", color=discord.Color.red())
        await message.channel.send(embed = em)
    else:
        pass
    await client.process_commands(message)

# Bot Setup ------------------------------------------------------------------------------------------------------------
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('.help'))
    print("We have logged in as {0.user}".format(client))

# Removes Default help Command -----------------------------------------------------------------------------------------
client.remove_command('help')

# Command Responses ----------------------------------------------------------------------------------------------------
# Inompleted Command Response ------------------------------------------------------------------------------------------
# Command Responses ----------------------------------------------------------------------------------------------------
# Inompleted Command Response ------------------------------------------------------------------------------------------
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        msg = "Rerun the command and put in all the required arguments next time"
        em = discord.Embed(title = "", color=discord.Color.red())
        em.add_field(name="Woah There!", value=msg, inline=False)
        await ctx.send(embed=em)

# Fake Player Name Response --------------------------------------------------------------------------------------------
    elif isinstance(error, commands.CommandInvokeError):
        msg = "Try putting in the correct arguments next time"
        em = discord.Embed(title ="", color=discord.Color.red())
        em.add_field(name="Don't Break Me!", value=msg, inline=False)
        await ctx.send(embed=em)

# Command Cooldown Response---------------------------------------------------------------------------------------------
    elif isinstance(error, commands.CommandOnCooldown):
        msg = "You can't use this command for another **{:.2f} seconds**".format(error.retry_after)
        em = discord.Embed(title = "", color=discord.Color.red())
        em.add_field(name="Woah Chill!", value=msg)
        await ctx.send(embed=em)

# Utility Commands -----------------------------------------------------------------------------------------------------
# .ping to get bot ping ------------------------------------------------------------------------------------------------
@client.command()
async def ping(ctx):
    await ctx.send(f"**Swish!**" + '\n'
        + f"You got the shot off with just **{round(client.latency * 1000)}ms** left on the clock!")

# .invite To Invite The Bot & Join The Official Server -----------------------------------------------------------------
@client.command()
async def invite(ctx):
    em = discord.Embed(title = "Basketball Beta", color=discord.Color.red())
    em.description = ("[**Click here to add me to your server**]"
                      "(https://discord.com/api/oauth2/authorize?client_"
                      "id=859058240439844905&permissions=2147875904&scope=bot)." + '\n' +
                      "[**Click here to join my official server for giveaways and support**]"
                      "(https://discord.gg/eshTCtcaA3).")
    await ctx.send(embed=em)

# Economy Commands -----------------------------------------------------------------------------------------------------
# .balance To Get Balance ----------------------------------------------------------------------------------------------
@client.command(aliases = ['bal', 'wallet'])
@commands.cooldown(1,3,commands.BucketType.user)
async def balance(ctx):
    wallet_amt = await get_balance(ctx.author)

    # Balance Embed
    em = discord.Embed(title = f"{ctx.author.name}'s Net Worth", color = discord.Color.red())
    em.add_field(name = "Bank balance", value = "{:,}".format(wallet_amt))
    em.add_field(name="Player Values", value=0)
    await ctx.send(embed = em)

# .payday To Receive Money ---------------------------------------------------------------------------------------------
@client.command(aliases = ['pd'])
@commands.cooldown(1,150,commands.BucketType.user)
async def payday(ctx):

    earnings = random.randrange(3001)

    em = discord.Embed(title="", color=discord.Color.red())
    em.add_field(name = f"You received ${earnings} for your payday!", value = f"Paid to {ctx.author.name}")
    await ctx.send(embed =em)

    await update_bank(ctx.author, earnings)

# .workout To Receive Money --------------------------------------------------------------------------------------------
@client.command(aliases = ['wo', 'gym'])
@commands.cooldown(1,15,commands.BucketType.user)
async def workout(ctx):

    earnings = random.randrange(601)

    em = discord.Embed(title="", color=discord.Color.red())
    em.add_field(name = f"You went to workout, a fan gave you ${earnings}!", value = f"Paid to {ctx.author.name}")
    await ctx.send(embed =em)

    await update_bank(ctx.author, earnings)

# .autograph To Receive Money ------------------------------------------------------------------------------------------
@client.command(aliases = ['ag', 'signature'])
@commands.cooldown(1,30,commands.BucketType.user)
async def autograph(ctx):

    earnings = random.randrange(1501)

    em = discord.Embed(title="", color=discord.Color.red())
    em.add_field(name = f"You went out to meet some fans and sign some autographs. You received ${earnings}!",
                 value = f"Paid to {ctx.author.name}")
    await ctx.send(embed =em)

    await update_bank(ctx.author, earnings)


# .sponsor To Receive Money --------------------------------------------------------------------------------------------
@client.command(aliases = ['spons'])
@commands.cooldown(1,60,commands.BucketType.user)
async def sponsor(ctx):

    earnings = random.randrange(2251)

    em = discord.Embed(title="", color=discord.Color.red())
    em.add_field(name = f"You drank some Gatorade! As part of the sponsorship deal, you received ${earnings}!",
                 value = f"Paid to {ctx.author.name}")
    await ctx.send(embed =em)

    await update_bank(ctx.author, earnings)

# .golf To Receive Money -----------------------------------------------------------------------------------------------
@client.command(aliases = ['holeinone', 'wio'])
@commands.cooldown(1,45,commands.BucketType.user)
async def golf(ctx):

    earnings = random.randrange(1801)

    em = discord.Embed(title="", color=discord.Color.red())
    em.add_field(name = f"You went golfing and made a hole in one. A fan saw and gave you ${earnings}!",
                 value = f"Paid to {ctx.author.name}")
    await ctx.send(embed =em)

    await update_bank(ctx.author, earnings)

# .daily To Receive Money ----------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,86400,commands.BucketType.user)
async def daily(ctx):

    em = discord.Embed(title="", color=discord.Color.red())
    em.add_field(name = f"You received $10,030 as your daily reward!",
                 value = f"Paid to {ctx.author.name}")
    await ctx.send(embed =em)

    await update_bank(ctx.author, 10030)

# .transfer To Give User Money -----------------------------------------------------------------------------------------
@client.command(aliases = ['share', 'send'])
@commands.cooldown(1,15,commands.BucketType.user)
async def transfer(ctx, member:discord.Member, amount = None):

    if amount == None:
        em = discord.Embed(title=f"Please put in a real number next time", color=discord.Color.red())
        em.set_footer(text=f"Basketball Beta")
        await ctx.send(embed=em)
        return

    bal = await get_balance(ctx.author)

    amount = int(amount)
    if amount > bal:
        em = discord.Embed(title="You don't even have that much money", color=discord.Color.red())
        em.set_footer(text=f"Basketball Beta")
        await ctx.send(embed=em)
        return
    if amount < 0:
        em = discord.Embed(title="Don't try to break me, Put in a positive number", color=discord.Color.red())
        em.set_footer(text=f"Basketball Beta")
        await ctx.send(embed=em)
        return

    await update_bank(ctx.author, -1*amount)
    await update_bank(member, amount)

    em = discord.Embed(title=f"From: {ctx.author.name}", color=discord.Color.red())
    em.add_field(name= f"To the {member.name} foundation", value=f"They have been given ${amount}!", inline=False)
    em.set_footer(text="Basketball Beta")
    await ctx.send(embed=em)

# .donate To Give The User Items ---------------------------------------------------------------------------------------
@client.command(aliases = ['give', 'gift'])
@commands.cooldown(1,15,commands.BucketType.user)
async def donate(ctx, member:discord.Member,amount, item_name):

    await open_account(member)

    res = await donate_this(ctx.author,member, amount, item_name)

    if not res[0]:
        if res[1]==1:
            em = discord.Embed(title="You don't even have that item!", color=discord.Color.red())
            await ctx.send(embed=em)
            return
        if res[1]==2:
            em = discord.Embed(title=f"You don't have enough items to give them {amount} {item_name}'s",
                               color=discord.Color.red())
            await ctx.send(embed=em)
            return

    em = discord.Embed(title=f"From: {ctx.author.name}", color=discord.Color.red())
    em.add_field(name= f"To the {member.name} foundation",
                 value=f"They have been given {amount} {item_name}'s!", inline=False)
    em.set_footer(text="Basketball Beta")
    await ctx.send(embed=em)

# .invest To Bet Your Money --------------------------------------------------------------------------------------------
@client.command(aliases = ['slots', 'gamble'])
@commands.cooldown(1,30,commands.BucketType.user)
async def invest(ctx, amount = None):

    if amount == None:
        em = discord.Embed(title=f"Please put in a real number next time", color=discord.Color.red())
        em.set_footer(text=f"Basketball Beta")
        await ctx.send(embed=em)
        return

    bal = await get_balance(ctx.author)

    amount = int(amount)
    if amount > bal:
        em = discord.Embed(title="You don't even have that much money", color=discord.Color.red())
        em.set_footer(text=f"Basketball Beta")
        await ctx.send(embed=em)
        return
    if amount < 0:
        em = discord.Embed(title="Don't try to break me, Put in a positive number", color=discord.Color.red())
        em.set_footer(text=f"Basketball Beta")
        await ctx.send(embed=em)
        return

    final = []
    for i in range (3):
        a = random.choice([":basketball:",
                           ":chart_with_upwards_trend:",
                           ":chart_with_downwards_trend:",
                           ":dollar:",
                           ":medal:"])

        final.append(a)

    # List to String
    def listToString(a):

        str1 = ""

        for ele in a:
            str1 += ele + " "

        return str1

    if final[0] == final[1] == final [2]:
        await update_bank(ctx.author, 3*amount)
        message = "**Super Stonks!**" + '\n' + "You won `x4` your investment"
    elif final[0] == final[1] or final[0] == final[2] or final[1] == final[2]:
        await update_bank(ctx.author, amount)
        message = "**Nice investment!**" + '\n' + "You won `x2` your investment"
    else:
        await update_bank(ctx.author, -1*amount)
        message = "**Maybe don't invest next time**" + '\n' + "You lost `all` your investment"


    em = discord.Embed(title=f"{ctx.author.name}'s Stocks", color=discord.Color.red())
    em.add_field(name=f"**------------------**" + '\n'
                      + f"**>** {listToString(final)} **<**"+ '\n'
                      + f"**------------------**", value = message, inline=False)
    em.set_footer(text="Basketball Beta")
    await ctx.send(embed=em)

# .leaderboard To Show The 10 Richest People In The Server -------------------------------------------------------------
@client.command(aliases = ["lb"])
@commands.cooldown(1,1,commands.BucketType.user)
async def leaderboard(ctx):

    em = discord.Embed(color=discord.Color.red())

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select Top 10 UserId, Balance from Balance order by Balance desc")
    rows = cursor.fetchall()

    index = 1
    top10 = ""
    for row in rows:
        # member = row.UserId
        amount = row.Balance
        member = await client.fetch_user(row.UserId)
        top10 = top10 + f"**{index}. {member}** - $" + "{:,}".format(int(amount)) + '\n'

        index = index + 1

    em.add_field(name= "Richest People In The Bot", value = top10)
    await ctx.send(embed=em)

# Shop Commands --------------------------------------------------------------------------------------------------------
# .market To Veiw The Market -------------------------------------------------------------------------------------------
@client.command(aliases = ['shop'])
@commands.cooldown(1,1,commands.BucketType.user)
async def market(ctx, page = 1):

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select ItemName, Description, Price, Icon from ShopItems order by Price, ItemName "
                   "offset ? rows fetch next 6 rows only", (page - 1) * 6)
    rows = cursor.fetchall()
    if cursor.rowcount == 0:
        em = discord.Embed(title="There aren't even that many shop pages", color = discord.Color.red())
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title="Basketball Beta Shop", color = discord.Color.red())
        for row in rows:
            em.add_field(name=row.Icon + " " + row.ItemName,
                         value = "**$" + "{:,}".format(int(row.Price)) + "**" + '\n' + row.Description, inline = False)
        em.set_footer(text="Run 'shop [1-8]` to view other shop pages" + '\n' + f"Page {page} of 8")
        await ctx.send(embed=em)

# .buy To Buy An Item In The Shop --------------------------------------------------------------------------------------
@client.command(aliases = ['purchase'])
@commands.cooldown(1,3,commands.BucketType.user)
async def buy(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            em = discord.Embed(title="That isn't even a real item!", color=discord.Color.red())
            await ctx.send(embed=em)
            return
        if res[1]==2:
            em = discord.Embed(title=f"You don't have enough money in your wallet to buy {amount} {item}'s",
                               color=discord.Color.red())
            await ctx.send(embed=em)
            return

    em = discord.Embed(title=f"You just bought {amount} {item}'s for $"+str(res[1] * -1)+"!", color=discord.Color.red())
    await ctx.send(embed=em)

# .sell To Sell An Item ------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def sell(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            em = discord.Embed(title="That isn't even a real item!", color=discord.Color.red())
            await ctx.send(embed=em)
            return
        if res[1]==2:
            em = discord.Embed(title=f"You don't have enough items to sell {amount} {item}'s",
                               color=discord.Color.red())
            await ctx.send(embed=em)
            return

    em = discord.Embed(title=f"You just sold {amount} {item}'s for ${res[1]}!", color=discord.Color.red())
    await ctx.send(embed=em)

# .locker To View The Users Locker Room --------------------------------------------------------------------------------
@client.command(aliases = ['inventory', 'inv', 'bag'])
@commands.cooldown(1,1,commands.BucketType.user)
async def locker(ctx, page = 1):
    await open_account(ctx.author)
    user = ctx.author

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()

    cursor.execute("select ItemCount = Count(*) from Inventory where UserId = ?", user.id)
    row = cursor.fetchone()
    itemCount = row.ItemCount
    totalPages = (itemCount + 5) // 6

    cursor.execute("select i.ItemName, i.ItemAmount, si.Icon from Inventory i, ShopItems si "
                   "where i.ItemName = si.ItemName and i.UserId = ? order by i.ItemName "
                   "offset ? rows fetch next 6 rows only", user.id, (page - 1) * 6)
    rows = cursor.fetchall()
    if cursor.rowcount == 0:
        em = discord.Embed(title=f"You don't even have enough items to have `{page}` pages", color=discord.Color.red())
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=f"{user.name}'s Locker Room", color=discord.Color.red())
        for row in rows:
            em.add_field(name=row.Icon + " " + row.ItemName.capitalize() + "'s",
                         value="**Amount: **" + "{:,}".format(int(row.ItemAmount)), inline=False)
        em.set_footer(text=f"Page {page} of {totalPages}")
        await ctx.send(embed=em)

# Function Definitions -------------------------------------------------------------------------------------------------
# Opens Account In SQL Server ------------------------------------------------------------------------------------------
async def open_account(user):
    cnxn = pyodbc.connect(sql_connection)
    cursor = cnxn.cursor()
    cursor.execute("select balance from Balance where UserId = ?", user.id)
    row = cursor.fetchone()
    if not row:
        cursor.execute("insert into balance(UserId, Balance) values (?, ?)", user.id, 0)
        cnxn.commit()

    return True

# Gets The Users Balance -----------------------------------------------------------------------------------------------
async def get_balance(user):
    await open_account(user);

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select balance from Balance where UserId = ?", user.id)
    row = cursor.fetchone()
    if row:
        return int(row.balance)
    else:
        return 0

# Updates The Users Money ----------------------------------------------------------------------------------------------
async def update_bank(user, change=0):
    await open_account(user)

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select balance from Balance where UserId = ?", user.id)
    row = cursor.fetchone()
    row.balance = row.balance + change;
    cursor.execute("Update Balance set balance = ? where UserId = ?", row.balance, user.id)

    cnxn.commit()
    return

# Defines buy_this To Buy Item -----------------------------------------------------------------------------------------
async def buy_this(user, item_name, amount):
    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select Price from ShopItems where ItemName = ?", item_name)
    row = cursor.fetchone()

    if not row:
        return [False,1]
    price = row.Price

    cost = int(price*amount)

    cursor.execute("select Balance from Balance where UserId = ?", user.id)
    row = cursor.fetchone()

    bal = row.Balance

    if bal < cost:
        return [False,2]

    cursor = cnxn.cursor()
    cursor.execute("select * from Inventory where UserId = ? and ItemName = ?", user.id, item_name)
    row = cursor.fetchone()

    if not row:
        cursor.execute("Insert into Inventory(UserId, ItemName, ItemAmount) values(?, ?, ?)",
                       user.id, item_name, amount)
    else:
        cursor.execute("Update Inventory set ItemAmount = ItemAmount + ? where UserId = ? and ItemName = ?",
                       amount, user.id, item_name)
    cursor.commit()

    await update_bank(user, cost*-1)

    return [True, cost*-1]

# Defines sell_this To Sell Item ---------------------------------------------------------------------------------------
async def sell_this(user,item_name,amount):
    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select Price from ShopItems where ItemName = ?", item_name)
    row = cursor.fetchone()

    if not row:
        return [False,1]
    price = row.Price

    cost = int(D(price) * D(amount) * D(0.3))

    cursor.execute("select ItemAmount from Inventory where UserId = ? and ItemName = ?", user.id, item_name)
    row = cursor.fetchone()

    item_amount = row.ItemAmount

    if item_amount < amount:
        return [False,2]

    if item_amount == amount:
        cursor.execute("Delete Inventory where UserId = ? and ItemName = ?",
                       user.id, item_name)
    else:
        cursor.execute("Update Inventory set ItemAmount = ItemAmount - ? where UserId = ? and ItemName = ?",
                       amount, user.id, item_name)
    cursor.commit()

    await update_bank(user, cost)

    return [True,cost]

# Defines donate_this To Give Items ------------------------------------------------------------------------------------
async def donate_this(author,member,amount, item_name):
    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select ItemAmount from Inventory where UserId = ? and ItemName = ?",author.id, item_name)
    row = cursor.fetchone()

    if not row:
        return [False,1]
    ItemAmount = row.ItemAmount

    if ItemAmount < amount:
        return [False,2]

    cursor = cnxn.cursor()

    cursor.execute("Update Inventory set ItemAmount = ItemAmount - ? where UserId = ? and ItemName = ?",
                   amount, author.id, item_name)

    cursor.execute("select ItemAmount from Inventory where UserId = ? and ItemName = ?", member.id, item_name)
    row = cursor.fetchone()

    if not row:
        cursor.execute("Insert into Inventory(UserId, ItemName, ItemAmount) values(?, ?, ?)",
                       member.id, item_name, amount)
    else:
        cursor.execute("Update Inventory set ItemAmount = ItemAmount + ? where UserId = ? and ItemName = ?",
                       amount, member.id, item_name)
    cursor.commit()

    return [True,ItemAmount]

# Basketball Commands --------------------------------------------------------------------------------------------------
# .search [player] to find all active players with the name ------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def search(ctx, *, name):
    all_play = players.find_players_by_full_name(name)
    has_active_players = False
    info = ""

    for p in all_play:
        if p["is_active"] and (p["first_name"].lower() == name.lower() or p["last_name"].lower() == name.lower()):
            if not has_active_players:
                info = ""
            has_active_players = True
            info += '\n' + p["full_name"]

    # If there are no active players with the name
    if not has_active_players:
        info = "There are no active players with the name " + name
    em = discord.Embed(title="Basketball Beta Search", color=discord.Color.red())
    em.add_field(name="All active NBA players with the name `" + name.capitalize() + "`:", value = info, inline=False)
    await ctx.send(embed = em)

# .stats [player] to get players stats ---------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,5,commands.BucketType.user)
async def stats(ctx, *, name):
    all_play = players.find_players_by_full_name(name)
    p = all_play[0]
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=p["id"])
    PlayerHeadlineStats = player_info.get_normalized_dict().get("PlayerHeadlineStats")
    stat = PlayerHeadlineStats[0]
    CommonPlayerInfo = player_info.get_normalized_dict().get("CommonPlayerInfo")
    info = CommonPlayerInfo[0]

    # Player Stats
    em = discord.Embed(title="Basketball Beta Stats", color=discord.Color.red())
    em.add_field(name = info["DISPLAY_FIRST_LAST"] + " stats:", value = "Team: " + str(info["TEAM_NAME"]) + '\n'
            + "Season: " + str(stat["TimeFrame"]) + '\n'
            + "Points Per Game: " + str(stat["PTS"]) + '\n'
            + "Assists Per Game: " + str(stat["AST"]) + '\n'
            + "Rebounds Per Game: " + str(stat["REB"]), inline=False)
    await ctx.send(embed = em)

# .info [player] to find the info of a player --------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,5,commands.BucketType.user)
async def info(ctx, *, name):
    all_play = players.find_players_by_full_name(name)
    p = all_play[0]
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=p["id"])
    CommonPlayerInfo = player_info.get_normalized_dict().get("CommonPlayerInfo")
    info = CommonPlayerInfo[0]

    # Player Info
    em = discord.Embed(title="Basketball Beta Info", color=discord.Color.red())
    em.add_field(name = info["DISPLAY_FIRST_LAST"] + " info: ", value = "Home Country: " + info["COUNTRY"] + '\n'
            + "Height: " + str(info["HEIGHT"]) + '\n'
            + "Weight: " + str(info["WEIGHT"]) + "Lb" + '\n'
            + "Draft year: " + str(info["DRAFT_YEAR"]) + '\n'
            + "Pick: " + str(info["DRAFT_NUMBER"]) + '\n'
            + "Jersey Number: " + str(info["JERSEY"]), inline=False)
    await ctx.send(embed = em)

# .help for help with the bot ------------------------------------------------------------------------------------------
@client.group(invoke_without_command = True)
async def help(ctx):

    # Help Embed
    em = discord.Embed(title = "Basketball Bot Commands & Help", color = discord.Color.red())
    em.add_field(name = ":tools: **Utility**", value = "`setprefix`,"
                                                       "`ping`,"
                                                       "`invite`", inline=False)
    em.add_field(name = ":moneybag: **Economy**", value = "`balance`,"
                                                          "`payday`,"
                                                          "`workout`,"
                                                          "`autograph`,"
                                                          "`sponsor`,"
                                                          "`golf`,"
                                                          "`daily`,"
                                                          "`transfer`,"
                                                          "`donate`," + '\n'
                                                          "`invest`,"
                                                          "`leaderboard`,"
                                                          "`market`,"
                                                          "`buy`,"
                                                          "`sell`,"
                                                          "`locker`", inline=False)
    em.add_field(name = ":basketball: **Basketball**", value = "`search`,"
                                                               "`stats`,`"
                                                               "info`", inline=False)
    em.set_footer(text = "Run 'help [command]' for more info on the command")
    await ctx.send(embed = em)

# Utility Help Embeds --------------------------------------------------------------------------------------------------
# Help with Set prefix -------------------------------------------------------------------------------------------------
@help.command()
async def setprefix(ctx):
        em = discord.Embed(title = "Setprefix Help", color = discord.Color.red())
        em.add_field(name = "Description:", value = "Changes the server prefix for everyone", inline=False)
        em.add_field(name = "Usage:", value = "`setprefix [new prefix]`", inline=False)
        em.add_field(name = "Permissions needed:", value = "`administrator`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed = em)

# Help with Ping -------------------------------------------------------------------------------------------------------
@help.command()
async def ping(ctx):
        em = discord.Embed(title = "Ping Help", color = discord.Color.red())
        em.add_field(name = "Description:", value = "Returns the ping in miliseconds", inline=False)
        em.add_field(name = "Usage:", value = "`ping`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed = em)

# Help with Invite ------------------------------------------------------------------------------------------------------
@help.command()
async def invite(ctx):
        em = discord.Embed(title = "Invite Help", color = discord.Color.red())
        em.add_field(name = "Description:", value = "Returns the bot and official server invite links", inline=False)
        em.add_field(name = "Usage:", value = "`invite`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed = em)

# Economy Help Embeds --------------------------------------------------------------------------------------------------
# Help with Balance ----------------------------------------------------------------------------------------------------
@help.command()
async def balance(ctx):
        em = discord.Embed(title = "Balance Help", color = discord.Color.red())
        em.add_field(name = "Description:", value = "Returns the amount of money the user currently has", inline=False)
        em.add_field(name = "Usage:", value = "`balance`", inline=False)
        em.add_field(name = "Aliases:", value = "`bal`, `wallet`", inline=False)
        em.add_field(name = "Cooldown:", value = "`3 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed = em)

# Help with Payday -----------------------------------------------------------------------------------------------------
@help.command()
async def payday(ctx):
        em = discord.Embed(title="Payday Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Gives the user money as a payday", inline=False)
        em.add_field(name="Usage:", value="`payday`", inline=False)
        em.add_field(name="Aliases:", value="`pd`", inline=False)
        em.add_field(name="Cooldown:", value="`1.5 minutes/90 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help with Workout ----------------------------------------------------------------------------------------------------
@help.command()
async def workout(ctx):
        em = discord.Embed(title="Workout Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Gives the user money after a workout", inline=False)
        em.add_field(name="Usage:", value="`workout`", inline=False)
        em.add_field(name="Aliases:", value="`wo`,`gym`", inline=False)
        em.add_field(name="Cooldown:", value="`15 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help with Autograph --------------------------------------------------------------------------------------------------
@help.command()
async def autograph(ctx):
        em = discord.Embed(title="Autograph Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Gives the user money after meeting some fans", inline=False)
        em.add_field(name="Usage:", value="`autograph`", inline=False)
        em.add_field(name="Aliases:", value="`ag`,`signature`", inline=False)
        em.add_field(name="Cooldown:", value="`30 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help with Sponsor ----------------------------------------------------------------------------------------------------
@help.command()
async def sponsor(ctx):
        em = discord.Embed(title="Sponsor Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Gives the user money after drinking some Gatorade", inline=False)
        em.add_field(name="Usage:", value="`sponsor`", inline=False)
        em.add_field(name="Aliases:", value="`spons`", inline=False)
        em.add_field(name="Cooldown:", value="`1 minute/60 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help with Golf -------------------------------------------------------------------------------------------------------
@help.command()
async def golf(ctx):
        em = discord.Embed(title="Golf Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Gives the user money after sinking a hole in one", inline=False)
        em.add_field(name="Usage:", value="`golf`", inline=False)
        em.add_field(name="Aliases:", value="`holeinone`,`hio`", inline=False)
        em.add_field(name="Cooldown:", value="`45 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help with Daily ------------------------------------------------------------------------------------------------------
@help.command()
async def daily(ctx):
        em = discord.Embed(title="Daily Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Gives the user $15,030 as a daily reward", inline=False)
        em.add_field(name="Usage:", value="`daily`", inline=False)
        em.add_field(name="Cooldown:", value="`1 day/86400 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help with Transfer ---------------------------------------------------------------------------------------------------
@help.command()
async def transfer(ctx):
        em = discord.Embed(title="Transfer Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Gives the mentioned user the specified amount of money", inline=False)
        em.add_field(name="Usage:", value="`transfer [@user] [amount]`", inline=False)
        em.add_field(name="Aliases:", value="`share`,`send`", inline=False)
        em.add_field(name="Cooldown:", value="`15 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help with Donate ---------------------------------------------------------------------------------------------------
@help.command()
async def donate(ctx):
        em = discord.Embed(title="Donate Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Gives the mentioned user the specified amount of items", inline=False)
        em.add_field(name="Usage:", value="`donate [@user] [item name] [amount]`", inline=False)
        em.add_field(name="Aliases:", value="`give`,`gift`", inline=False)
        em.add_field(name="Cooldown:", value="`15 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help with Invest -----------------------------------------------------------------------------------------------------
@help.command()
async def invest(ctx):
        em = discord.Embed(title="Invest Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Test your luck and see if you win or lose money", inline=False)
        em.add_field(name="Usage:", value="`invest [amount]`", inline=False)
        em.add_field(name="Aliases:", value="`slots`,`gamble`", inline=False)
        em.add_field(name="Cooldown:", value="`30 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help with Leaderboard ------------------------------------------------------------------------------------------------
@help.command()
async def leaderboard(ctx):
        em = discord.Embed(title="Leaderboard Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Shows the top 10 richest people in the server", inline=False)
        em.add_field(name="Usage:", value="`leaderboard`", inline=False)
        em.add_field(name="Aliases:", value="`lb`", inline=False)
        em.add_field(name="Cooldown:", value="`1 second`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Shop Help Embeds -----------------------------------------------------------------------------------------------------
# Help with Market -----------------------------------------------------------------------------------------------------
@help.command()
async def market(ctx):
        em = discord.Embed(title="Market Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Displays all the amazing items on the market", inline=False)
        em.add_field(name="Usage:", value="`market [page number]`", inline=False)
        em.add_field(name="Aliases:", value="`shop`", inline=False)
        em.add_field(name="Cooldown:", value="`1 second`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help with Buy --------------------------------------------------------------------------------------------------------
@help.command()
async def buy(ctx):
        em = discord.Embed(title="Buy Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Purchase some nice items from the shop", inline=False)
        em.add_field(name="Usage:", value="`buy [item name] [amount]`", inline=False)
        em.add_field(name="Aliases:", value="`purchase`", inline=False)
        em.add_field(name="Cooldown:", value="`3 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help with Sell -------------------------------------------------------------------------------------------------------
@help.command()
async def sell(ctx):
        em = discord.Embed(title="Sell Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Sell items you have bought with 20% shop value", inline=False)
        em.add_field(name="Usage:", value="`sell [item name] [amount]`", inline=False)
        em.add_field(name="Cooldown:", value="`3 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help with Locker -----------------------------------------------------------------------------------------------------
@help.command()
async def locker(ctx):
        em = discord.Embed(title="Buy Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Shows all the items you currently have", inline=False)
        em.add_field(name="Usage:", value="`buy [page number]`", inline=False)
        em.add_field(name="Aliases:", value="`inventory`,`inv`,`bag`", inline=False)
        em.add_field(name="Cooldown:", value="`1 second`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Basketball Help Embeds -----------------------------------------------------------------------------------------------
# Help with Search -----------------------------------------------------------------------------------------------------
@help.command()
async def search(ctx):
        em = discord.Embed(title="Search Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Searches up all active NBA players with the name", inline=False)
        em.add_field(name="Usage:", value="`search [player name]`", inline=False)
        em.add_field(name="Cooldown:", value="`3 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help wtih Stats ------------------------------------------------------------------------------------------------------
@help.command()
async def stats(ctx):
        em = discord.Embed(title="Stats Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Gives the stats of the NBA player", inline=False)
        em.add_field(name="Usage:", value="`stats [player name]`", inline=False)
        em.add_field(name="Cooldown:", value="`5 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Help with Info -------------------------------------------------------------------------------------------------------
@help.command()
async def info(ctx):
        em = discord.Embed(title="Info Help", color=discord.Color.red())
        em.add_field(name="Description:", value="Gives general information of the NBA player", inline=False)
        em.add_field(name="Usage:", value="`info [player name]`", inline=False)
        em.add_field(name="Cooldown:", value="`5 seconds`", inline=False)
        em.set_footer(text="Basketball Beta")
        await ctx.send(embed=em)

# Super Secret Token ---------------------------------------------------------------------------------------------------
client.run('ODU5MDU4MjQwNDM5ODQ0OTA1.YNnKVQ.bawFjJfTYljnsMn7p1mgWSlaEZY')
