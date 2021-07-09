import discord
from discord.ext import commands
import pyodbc
from decimal import Decimal as D

sql_connection = 'DRIVER={SQL Server Native Client 11.0};SERVER=localhost;DATABASE=BotTester;UID=sa;PWD=wa11paper'

client = commands.Bot(command_prefix = "t!")

# ----------------------------------------------------------------------------------------------------------------------
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('.help'))
    print("We have logged in as {0.user}".format(client))

# ----------------------------------------------------------------------------------------------------------------------
@client.command(aliases = ['give', 'gift'])
@commands.cooldown(1,15,commands.BucketType.user)
async def donate(ctx, member:discord.Member, item_name, amount = 1):

    await open_account(member)

    res = await donate_this(ctx.author,member,item_name,amount)

    if not res[0]:
        if res[1]==1:
            em = discord.Embed(title="That isn't even a real item!", color=discord.Color.red())
            await ctx.send(embed=em)
            return
        if res[1]==2:
            em = discord.Embed(title=f"You don't have enough money in your wallet to buy {amount} {item_name}'s",
                               color=discord.Color.red())
            await ctx.send(embed=em)
            return

    em = discord.Embed(title=f"You just bought {amount} {item_name}'s!", color=discord.Color.red())
    await ctx.send(embed=em)

async def donate_this(author,member,item_name,amount):
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

# ----------------------------------------------------------------------------------------------------------------------
async def sell_this(user,item_name,amount):
    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select Price from ShopItems where ItemName = ?", item_name)
    row = cursor.fetchone()

    if not row:
        return [False,1]
    price = row.Price

    cost = int(D(price) * D(amount) * D(0.2))

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

async def buy_this(user,item_name,amount):
    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select Price from ShopItems where ItemName = ?", item_name)
    row = cursor.fetchone()

    if not row:
        return [False,1]
    price = row.Price

    cost = price*amount

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

    return [True,cost]

async def open_account(user):
    cnxn = pyodbc.connect(sql_connection)
    cursor = cnxn.cursor()
    cursor.execute("select balance from Balance where UserId = ?", user.id)
    row = cursor.fetchone()
    if not row:
        cursor.execute("insert into balance(UserId, Balance) values (?, ?)", user.id, 0)
        cnxn.commit()

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

# ----------------------------------------------------------------------------------------------------------------------
@client.command()
async def ping(ctx):
    await ctx.send(f"**Swish!**" + '\n'
        + f"You got the shot off with just **{round(client.latency * 1000)}ms** left on the clock!")

client.run('ODU5MTc4MTkwMjY1OTA5MjU5.YNo6Cw.gAIJFhxx9vWo-NLa-eksa5r_mAY')