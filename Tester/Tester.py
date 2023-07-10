import discord
from discord.ext import commands
import pyodbc
from datetime import *
from discord_components import *

sql_connection = 'DRIVER={SQL Server Native Client 11.0};SERVER=localhost;DATABASE=BotTester;UID=sa;PWD=wa11paper'

client = commands.Bot(command_prefix = "t!")

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('t!help'))
    print("We have logged in as {0.user}".format(client))
    DiscordComponents(client)

# t!search -------------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def search(ctx, *, player = ""):

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute(f"select top 10 Name from Players where FinalYear = 2021 and name like '%{player}%' "
                   f"order by name")
    rows = cursor.fetchall()

    info = ""

    if cursor.rowcount == 0:
        info = "There are no active players with `" + player + "` in their name"
    else:
        for row in rows:
            info += '\n' + row.Name

    cursor = cnxn.cursor()
    cursor.execute(f"select players = count(*) from players where FinalYear = 2021 and name like '%{player}%'")
    rowp = cursor.fetchone()

    if cursor.rowcount == 0:
        pass
    else:
        players = rowp.players


    em = discord.Embed(color=discord.Color.red())
    em.add_field(name="All active NBA players with `" + player.title() + "` in their name:", value = info, inline=False)
    em.set_footer(text=f"{players} total players")
    await ctx.send(embed = em)

# t!salary -------------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def salary(ctx, *, player = ""):

    def format_salary(salary):
        if salary is None:
            return "None"
        else:
            return "$" + str("{:,}".format(salary))

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select Salary1, Salary2, Salary3, Salary4, Salary5, Salary6, Image from Players "
                   "where FinalYear = 2021 and Name = ?", player)
    row = cursor.fetchone()


    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=player.capitalize() + " Salary",
                     value="There are no active players with the name: `" + player.capitalize() + "`",
                     inline=False)
        await ctx.send(embed=em)
    else:
        salary1 = row.Salary1
        salary2 = row.Salary2
        salary3 = row.Salary3
        salary4 = row.Salary4
        salary5 = row.Salary5
        salary6 = row.Salary6
        image = row.Image
        em = discord.Embed(title="", color=discord.Color.red())
        if image is None:
            pass
        else:
            em.set_thumbnail(url=image)
        em.add_field(name=player.capitalize() + "'s Salary",
                     value = "**2021:** " + format_salary(salary1) + '\n'
                        + "**2022:** " + format_salary(salary2) + '\n'
                        + "**2023:** " + format_salary(salary3) + '\n'
                        + "**2024:** " + format_salary(salary4) + '\n'
                        + "**2025:** " + format_salary(salary5) + '\n'
                        + "**2026:** " + format_salary(salary6))
        em.set_footer(text="Data From Basketball Reference")
        await ctx.send(embed = em)

# t!player ---------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def player(ctx, *, player = ""):

    def format_class(draft):
        if draft is None:
            return row.FirstYear
        else:
            return draft

    def format_draft(draft):
        if draft is None:
            return "Undrafted"
        else:
            return draft

    def active(active):
        if active == 2021:
            return"Active"
        else:
            return"Inactive"

    def format_field(field):
        if field is None or field == "":
            return "n/a"
        else:
            return field

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select FirstYear, FinalYear, Image, Country, College, Height, Weight, JerseyNumber, Birthday, "
                   "DraftTeam, DraftPick, DraftYear from Players "
                   "where Name = ? order by FinalYear desc", player)
    rows = cursor.fetchall()



    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=player.title() + "'s Info",
                     value="There are no players with the name: `" + player.title() + "`",
                     inline=False)
        await ctx.send(embed=em)
    else:
        for row in rows:
            em = discord.Embed(title=player.capitalize() + " Info", color=discord.Color.red())
            if row.Image is None or "":
                pass
            else:
                em.set_thumbnail(url=row.Image)

            em.add_field(name="Birthday", value=format_field(row.Birthday))
            em.add_field(name="Seasons Played", value= str(format_field(row.FinalYear - row.FirstYear)) + " seasons; "
                                                       + format_field(active(row.FinalYear)))
            em.add_field(name="College", value=format_field(row.College))
            em.add_field(name="Draft", value="**Draft Class:** " + str(format_class(row.DraftYear)) + '\n'
                                            + "**Pick:** " + str(format_draft(row.DraftPick)) + '\n'
                                            + "**Team:** " + str(format_draft(row.DraftTeam)))
            em.add_field(name="Birth Place", value=format_field(row.Country))
            em.add_field(name="** **", value="** **")
            em.add_field(name="Height", value=format_field(row.Height))
            em.add_field(name="Weight", value=str(format_field(row.Weight)) + " lb")
            em.add_field(name="Jersey Number", value=format_field(row.JerseyNumber))
            em.set_footer(text="Data From Basketball Reference")
            await ctx.send(embed = em)

# t!stats --------------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def stats(ctx, *, args):
    ss = args.split(' ')
    player = ""
    season = datetime.today().year - 1
    for i in range(0, len(ss)):
        if i == len(ss) - 1 and ss[i].isnumeric():
            season = ss[i]
        else:
            player += ss[i] + " "

    def format_field(field):
        if field is None or field == "":
            return 0
        else:
            return field

    def format_percent(field):
        if field is None or field == "":
            return 0
        else:
            return '{:.1f}'.format(field * 100)

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, MinPerGame, FgPerGame, " \
          f"FgaPerGame, FgPercent, Fg3PerGame, Fg3aPerGame, Fg3Percent, Fg2PerGame, Fg2aPerGame, Fg2Percent, " \
          f"EfgPercent, FtPerGame, FtaPerGame, FtPercent, OffRebound, DefRebound, Rebounds, Assists, Steals, Blocks," \
          f" Turnovers, Fouls, Points from PlayerStats ps join Players p on ps.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season = 'Career' and Playoffs = 0"
    cursor.execute(sql)
    rowc = cursor.fetchone()

    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, MinPerGame, FgPerGame, " \
          f"FgaPerGame, FgPercent, Fg3PerGame, Fg3aPerGame, Fg3Percent, Fg2PerGame, Fg2aPerGame, Fg2Percent, " \
          f"EfgPercent, FtPerGame, FtaPerGame, FtPercent, OffRebound, DefRebound, Rebounds, Assists, Steals, Blocks," \
          f" Turnovers, Fouls, Points from PlayerStats ps join Players p on ps.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season like '{season}%' and Playoffs = 0"

    cursor.execute(sql)
    row = cursor.fetchone()
    if cursor.rowcount == 0:
        sql = f"select top 1 p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, MinPerGame, " \
              f"FgPerGame, FgaPerGame, FgPercent, Fg3PerGame, Fg3aPerGame, Fg3Percent, Fg2PerGame, Fg2aPerGame, " \
              f"Fg2Percent, EfgPercent, FtPerGame, FtaPerGame, FtPercent, OffRebound, DefRebound, Rebounds, Assists," \
              f" Steals, Blocks, Turnovers, Fouls, Points from PlayerStats ps join " \
              f"Players p on ps.PlayerId = p.PlayerId where p.Name = '{player}' and " \
              f"(season like '19%' or season like '20%') and Playoffs = 0 order by Season desc"
        cursor.execute(sql)
        row = cursor.fetchone()

    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=player.title() + "Stats",
                     value="There are no players with the name: `" + player.title() + "`",
                     inline=False)
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.title() + "Stats (" + row.Team + ") " + str(row.Age) + " y/o "
                                 + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Games Started/Played", value=str(format_field(row.GamesStarted)) + " of " +
                                                        str(format_field(row.GamesPlayed)) + " | " +
                                                        str(format_field(rowc.GamesStarted)) + " of " +
                                                        str(format_field(rowc.GamesPlayed)))
        em.add_field(name="Minutes Per Game", value=str(format_field(row.MinPerGame)) + " | " +
                                                    str(format_field(rowc.MinPerGame)))
        em.add_field(name="Fg%/2Pt%/3Pt%/Ft%", value="__" + str(format_percent(row.FgPercent)) +
                                            "/" + str(format_percent(row.Fg2Percent)) + "/" +
                                            str(format_percent(row.Fg3Percent)) + "/" +
                                            str(format_percent(row.FtPercent)) + "__" + '\n' +
                                            str(format_percent(rowc.FgPercent)) + "/" +
                                            str(format_percent(rowc.Fg2Percent)) + "/" +
                                            str(format_percent(rowc.Fg3Percent)) + "/" +
                                            str(format_percent(rowc.FtPercent)))
        em.add_field(name="Fg/2Pt/3Pt/Ft Shooting", value=str(format_field(row.FgPerGame)) + "/" +
                                            str(format_field(row.Fg2PerGame)) + "/" + str(format_field(row.Fg3PerGame))
                                            + "/" + str(format_field(row.FtPerGame)) + " Makes On" + '\n' +
                                            "__" + str(format_field(row.FgaPerGame)) + "/" +
                                            str(format_field(row.Fg2aPerGame)) + "/" +
                                            str(format_field(row.Fg3aPerGame)) + "/" + str(format_field(row.FtaPerGame))
                                            + " Attempts__" + '\n' + str(format_field(rowc.FgPerGame)) + "/" +
                                            str(format_field(rowc.Fg2PerGame)) + "/" +
                                            str(format_field(rowc.Fg3PerGame)) + "/" + str(format_field(rowc.FtPerGame))
                                            + " Makes On" + '\n' + str(format_field(rowc.FgaPerGame)) + "/" +
                                            str(format_field(rowc.Fg2aPerGame)) + "/" +
                                            str(format_field(rowc.Fg3aPerGame)) + "/" +
                                            str(format_field(rowc.FtaPerGame)) + " Attempts")
        em.add_field(name="Rebounds Per Game", value="__" + str(row.Rebounds) + " (Offensive: " +
                                                     str(format_field(row.OffRebound)) +
                                                     ", Defensive: " + str(format_field(row.DefRebound)) + ")__" + '\n'
                                                     + str(format_field(rowc.Rebounds)) + " (Offensive: "
                                                     + str(format_field(rowc.OffRebound)) +
                                                     ", Defensive: " + str(format_field(rowc.DefRebound)) + ")",
                                                     inline = False)
        em.add_field(name="Assists Per Game", value=str(format_field(row.Assists)) + " | " +
                                                    str(format_field(rowc.Assists)))
        em.add_field(name="Steals Per Game", value=str(format_field(row.Steals)) + " | " +
                                                   str(format_field(rowc.Steals)))
        em.add_field(name="Blocks Per Game", value=str(format_field(row.Blocks)) + " | " +
                                                   str(format_field(rowc.Blocks)))
        em.add_field(name="Turnovers Per Game", value=str(format_field(row.Turnovers)) + " | " +
                                                      str(format_field(rowc.Turnovers)))
        em.add_field(name="Fouls Per Game", value=str(format_field(row.Fouls)) + " | " + str(format_field(rowc.Fouls)))
        em.add_field(name="Points Per Game", value=(str(format_field(row.Points)) + " | " +
                                                    str(format_field(rowc.Points))))
        em.set_footer(text="Data From Basketball Reference")
        await ctx.send(embed = em)

# t!playoffstats -------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def playoffstats(ctx, *, args):
    ss = args.split(' ')
    player = ""
    season = datetime.today().year - 1
    for i in range(0, len(ss)):
        if i == len(ss) - 1 and ss[i].isnumeric():
            season = ss[i]
        else:
            player += ss[i] + " "

    def format_field(field):
        if field is None or field == "":
            return 0
        else:
            return field

    def format_percent(field):
        if field is None or field == "":
            return 0
        else:
            return '{:.1f}'.format(field * 100)

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, MinPerGame, FgPerGame, " \
          f"FgaPerGame, FgPercent, Fg3PerGame, Fg3aPerGame, Fg3Percent, Fg2PerGame, Fg2aPerGame, Fg2Percent, " \
          f"EfgPercent, FtPerGame, FtaPerGame, FtPercent, OffRebound, DefRebound, Rebounds, Assists, Steals, Blocks," \
          f" Turnovers, Fouls, Points from PlayerStats ps join Players p on ps.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season = 'Career' and Playoffs = 1"
    cursor.execute(sql)
    rowc = cursor.fetchone()

    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, MinPerGame, FgPerGame, " \
          f"FgaPerGame, FgPercent, Fg3PerGame, Fg3aPerGame, Fg3Percent, Fg2PerGame, Fg2aPerGame, Fg2Percent, " \
          f"EfgPercent, FtPerGame, FtaPerGame, FtPercent, OffRebound, DefRebound, Rebounds, Assists, Steals, Blocks," \
          f" Turnovers, Fouls, Points from PlayerStats ps join Players p on ps.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season like '{season}%' and Playoffs = 1"

    cursor.execute(sql)
    row = cursor.fetchone()
    if cursor.rowcount == 0:
        sql = f"select top 1 p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, MinPerGame, " \
              f"FgPerGame, FgaPerGame, FgPercent, Fg3PerGame, Fg3aPerGame, Fg3Percent, Fg2PerGame, Fg2aPerGame, " \
              f"Fg2Percent, EfgPercent, FtPerGame, FtaPerGame, FtPercent, OffRebound, DefRebound, Rebounds, Assists," \
              f" Steals, Blocks, Turnovers, Fouls, Points from PlayerStats ps join " \
              f"Players p on ps.PlayerId = p.PlayerId where p.Name = '{player}' and " \
              f"(season like '19%' or season like '20%') and Playoffs = 1 order by Season desc"
        cursor.execute(sql)
        row = cursor.fetchone()

    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=player.title() + "Playoff Stats",
                     value="There are no players with the name: `" + player.title() + "`",
                     inline=False)
        em.set_footer(text="Or they've never been to the playoffs")
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.title() + "Playoff Stats (" + row.Team + ") " + str(row.Age) + " y/o "
                                 + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Games Started/Played", value=str(format_field(row.GamesStarted)) + " of " +
                                                        str(format_field(row.GamesPlayed)) + " | " +
                                                        str(format_field(rowc.GamesStarted)) + " of " +
                                                        str(format_field(rowc.GamesPlayed)))
        em.add_field(name="Minutes Per Game", value=str(format_field(row.MinPerGame)) + " | " +
                                                    str(format_field(rowc.MinPerGame)))
        em.add_field(name="Fg%/2Pt%/3Pt%/Ft%", value="__" + str(format_percent(row.FgPercent)) +
                                            "/" + str(format_percent(row.Fg2Percent)) + "/" +
                                            str(format_percent(row.Fg3Percent)) + "/" +
                                            str(format_percent(row.FtPercent)) + "__" + '\n' +
                                            str(format_percent(rowc.FgPercent)) + "/" +
                                            str(format_percent(rowc.Fg2Percent)) + "/" +
                                            str(format_percent(rowc.Fg3Percent)) + "/" +
                                            str(format_percent(rowc.FtPercent)))
        em.add_field(name="Fg/2Pt/3Pt/Ft Shooting", value=str(format_field(row.FgPerGame)) + "/" +
                                            str(format_field(row.Fg2PerGame)) + "/" + str(format_field(row.Fg3PerGame))
                                            + "/" + str(format_field(row.FtPerGame)) + " Makes On" + '\n' +
                                            "__" + str(format_field(row.FgaPerGame)) + "/" +
                                            str(format_field(row.Fg2aPerGame)) + "/" +
                                            str(format_field(row.Fg3aPerGame)) + "/" + str(format_field(row.FtaPerGame))
                                            + " Attempts__" + '\n' + str(format_field(rowc.FgPerGame)) + "/" +
                                            str(format_field(rowc.Fg2PerGame)) + "/" +
                                            str(format_field(rowc.Fg3PerGame)) + "/" + str(format_field(rowc.FtPerGame))
                                            + " Makes On" + '\n' + str(format_field(rowc.FgaPerGame)) + "/" +
                                            str(format_field(rowc.Fg2aPerGame)) + "/" +
                                            str(format_field(rowc.Fg3aPerGame)) + "/" +
                                            str(format_field(rowc.FtaPerGame)) + " Attempts")
        em.add_field(name="Rebounds Per Game", value="__" + str(row.Rebounds) + " (Offensive: " +
                                                     str(format_field(row.OffRebound)) +
                                                     ", Defensive: " + str(format_field(row.DefRebound)) + ")__" + '\n'
                                                     + str(format_field(rowc.Rebounds)) + " (Offensive: "
                                                     + str(format_field(rowc.OffRebound)) +
                                                     ", Defensive: " + str(format_field(rowc.DefRebound)) + ")",
                                                     inline = False)
        em.add_field(name="Assists Per Game", value=str(format_field(row.Assists)) + " | " +
                                                    str(format_field(rowc.Assists)))
        em.add_field(name="Steals Per Game", value=str(format_field(row.Steals)) + " | " +
                                                   str(format_field(rowc.Steals)))
        em.add_field(name="Blocks Per Game", value=str(format_field(row.Blocks)) + " | " +
                                                   str(format_field(rowc.Blocks)))
        em.add_field(name="Turnovers Per Game", value=str(format_field(row.Turnovers)) + " | " +
                                                      str(format_field(rowc.Turnovers)))
        em.add_field(name="Fouls Per Game", value=str(format_field(row.Fouls)) + " | " + str(format_field(rowc.Fouls)))
        em.add_field(name="Points Per Game", value=(str(format_field(row.Points)) + " | " +
                                                    str(format_field(rowc.Points))))
        em.set_footer(text="Data From Basketball Reference")
        await ctx.send(embed = em)

# t!teamsalary ---------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def teamsalary(ctx):

    def format_salary(salary):
        if salary is None:
            return "$0"
        else:
            return "$" + str("{:,}".format(salary))

    def format_salary2(salary):
        if salary is None:
            return ""
        else:
            return " | $" + str("{:,}".format(salary))

    def format_total(salary):
        if salary is None:
            return 0
        else:
            return salary

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select p.Name, TeamId, ts.PlayerId, ts.Salary1, ts.Salary2, ts.Salary3, ts.Salary4, "
                   "ts.Salary5, ts.Salary6 from TeamSalary ts join Players p on ts.PlayerId = p.PlayerId where "
                   "TeamId = ? order by ts.Salary1 desc", "atl")
    rows = cursor.fetchall()

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select TeamName from Teams where AltTeamId = ?", "atl")
    rowc = cursor.fetchone()

    salaries = ""
    team_1 = 0
    team_2 = 0
    team_3 = 0
    team_4 = 0
    team_5 = 0
    team_6 = 0


    for row in rows:
        salaries += "**" + row.Name + "**: " + str(format_salary(row.Salary1)) + str(format_salary2(row.Salary2)) \
                        + str(format_salary2(row.Salary3)) + str(format_salary2(row.Salary4)) + \
                        str(format_salary2(row.Salary5)) + str(format_salary2(row.Salary6)) + '\n'

        team_1 += format_total(row.Salary1)
        team_2 += format_total(row.Salary2)
        team_3 += format_total(row.Salary3)
        team_4 += format_total(row.Salary4)
        team_5 += format_total(row.Salary5)
        team_6 += format_total(row.Salary6)

    team_tot = "6 Year Total: **$" + str("{:,}".format(team_1 + team_2 + team_3 + team_4 + team_5 + team_6)) + "**"

    em = discord.Embed(title=f"{rowc.TeamName} Payroll",color=discord.Color.red())
    em.add_field(name="Name: 2021 | 2022 | 2023 | 2024 | 2025 | 2026", value= salaries, inline = False)
    em.add_field(name="Total: $" + str("{:,}".format(team_1)) + " | $" + str("{:,}".format(team_2)) + " | $" +
                      str("{:,}".format(team_3)) + " | $" + str("{:,}".format(team_4)) +
                      " | $" + str("{:,}".format(team_5)) + " | $" + str("{:,}".format(team_6)), value= team_tot)
    em.set_footer(text="Data From Basketball Reference")

    atl = "Atl_Sal_" + str(ctx.author.id)
    bos = "Bos_Sal_" + str(ctx.author.id)
    brk = "Brk_Sal_" + str(ctx.author.id)
    cho = "Cho_Sal_" + str(ctx.author.id)
    chi = "Chi_Sal_" + str(ctx.author.id)
    cle = "Cle_Sal_" + str(ctx.author.id)
    dal = "Dal_Sal_" + str(ctx.author.id)
    den = "Den_Sal_" + str(ctx.author.id)
    det = "Det_Sal_" + str(ctx.author.id)
    gsw = "Gsw_Sal_" + str(ctx.author.id)
    hou = "Hou_Sal_" + str(ctx.author.id)
    ind = "Ind_Sal_" + str(ctx.author.id)
    lac = "Lac_Sal_" + str(ctx.author.id)
    lal = "Lal_Sal_" + str(ctx.author.id)
    mem = "Mem_Sal_" + str(ctx.author.id)
    mia = "Mia_Sal_" + str(ctx.author.id)
    mil = "Mil_Sal_" + str(ctx.author.id)
    min = "Min_Sal_" + str(ctx.author.id)
    nop = "Nop_Sal_" + str(ctx.author.id)
    nyk = "Nyk_Sal_" + str(ctx.author.id)
    okc = "Okc_Sal_" + str(ctx.author.id)
    orl = "Orl_Sal_" + str(ctx.author.id)
    phi = "Phi_Sal_" + str(ctx.author.id)
    pho = "Pho_Sal_" + str(ctx.author.id)
    por = "Por_Sal_" + str(ctx.author.id)
    sac = "Sac_Sal_" + str(ctx.author.id)
    sas = "Sas_Sal_" + str(ctx.author.id)
    tor = "Tor_Sal_" + str(ctx.author.id)
    uta = "Uta_Sal_" + str(ctx.author.id)
    was = "Was_Sal_" + str(ctx.author.id)

    await ctx.send(
                embed=em,
                components = [[
                    Select(
                        placeholder = "Select A Team",
                        options = [
                            SelectOption(label="Atlanta Hawks", value= atl),
                            SelectOption(label="Boston Celtics", value= bos),
                            SelectOption(label="Brooklyn Nets", value= brk),
                            SelectOption(label="Charlotte Hornets", value= cho),
                            SelectOption(label="Chicago Bulls", value= chi),
                            SelectOption(label="Cleveland Cavaliers", value= cle),
                            SelectOption(label="Dallas Mavericks", value= dal),
                            SelectOption(label="Denver Nuggets", value= den),
                            SelectOption(label="Detroit Pistons", value= det),
                            SelectOption(label="Golden State Warriors", value= gsw),
                            SelectOption(label="Houston Rockets", value= hou),
                            SelectOption(label="Indiana Pacers", value= ind),
                            SelectOption(label="Los Angeles Clippers", value= lac),
                            SelectOption(label="Los Angeles Lakers", value= lal),
                            SelectOption(label="Memphis Grizzlies", value= mem)
                        ]
                    )
                ],
                [
                    Select(
                        placeholder="Select A Team",
                        options=[
                            SelectOption(label="Miami Heat", value= mia),
                            SelectOption(label="Milwaukee Bucks", value= mil),
                            SelectOption(label="Minnesota Timberwolves", value= min),
                            SelectOption(label="New Orleans Pelicans", value= nop),
                            SelectOption(label="New York Knicks", value= nyk),
                            SelectOption(label="Oklahoma City Thunder", value= okc),
                            SelectOption(label="Orlando Magic", value= orl),
                            SelectOption(label="Philadelphia 76ers", value= phi),
                            SelectOption(label="Phoenix Suns", value= pho),
                            SelectOption(label="Portland Trail Blazers", value= por),
                            SelectOption(label="Sacramento Kings", value= sac),
                            SelectOption(label="San Antonio Spurs", value= sas),
                            SelectOption(label="Toronto Raptors", value= tor),
                            SelectOption(label="Utah Jazz", value= uta),
                            SelectOption(label="Washington Wizards", value= was)
                        ]
                    )
                ]
                ],
            )

    while True:
        interaction = await client.wait_for("select_option", check=lambda i: i.values[0].find("Sal") >= 0)
        author_id = interaction.values[0].split('_')[2]

        if author_id == str(interaction.author.id):
            cnxn = pyodbc.connect(sql_connection)

            cursor = cnxn.cursor()
            cursor.execute("select p.Name, TeamId, ts.PlayerId, ts.Salary1, ts.Salary2, ts.Salary3, ts.Salary4, "
                           "ts.Salary5, ts.Salary6 from TeamSalary ts join Players p on ts.PlayerId = p.PlayerId where "
                           "TeamId = ? order by ts.Salary1 desc", interaction.values[0].split('_')[0])
            rows = cursor.fetchall()

            cnxn = pyodbc.connect(sql_connection)

            cursor = cnxn.cursor()
            cursor.execute("select TeamName from Teams where AltTeamId = ?", interaction.values[0].split('_')[0])
            rowc = cursor.fetchone()

            salaries = ""
            team_1 = 0
            team_2 = 0
            team_3 = 0
            team_4 = 0
            team_5 = 0
            team_6 = 0

            for row in rows:
                salaries += "**" + row.Name + "**: " + str(format_salary(row.Salary1)) + \
                            str(format_salary2(row.Salary2)) \
                            + str(format_salary2(row.Salary3)) + str(format_salary2(row.Salary4)) + \
                            str(format_salary2(row.Salary5)) + str(format_salary2(row.Salary6)) + '\n'

                team_1 += format_total(row.Salary1)
                team_2 += format_total(row.Salary2)
                team_3 += format_total(row.Salary3)
                team_4 += format_total(row.Salary4)
                team_5 += format_total(row.Salary5)
                team_6 += format_total(row.Salary6)

            team_tot = "6 Year Total: **$" + str("{:,}".format(team_1 + team_2 + team_3 + team_4 + team_5 + team_6)) \
                       + "**"

            em = discord.Embed(title=f"{rowc.TeamName} Payroll", color=discord.Color.red())
            em.add_field(name="Name: 2021 | 2022 | 2023 | 2024 | 2025 | 2026", value=salaries, inline=False)
            em.add_field(name="Total: $" + str("{:,}".format(team_1)) + " | $" + str("{:,}".format(team_2)) + " | $" +
                              str("{:,}".format(team_3)) + " | $" + str("{:,}".format(team_4)) +
                              " | $" + str("{:,}".format(team_5)) + " | $" + str("{:,}".format(team_6)), value=team_tot)
            em.set_footer(text="Data From Basketball Reference")
            await interaction.respond(embed=em, type=7)
        else:
            await interaction.respond(content="This isn't yor button!", type=4)

# t!totals -------------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def totals(ctx, *, args):
    ss = args.split(' ')
    player = ""
    season = datetime.today().year - 1
    for i in range(0, len(ss)):
        if i == len(ss) - 1 and ss[i].isnumeric():
            season = ss[i]
        else:
            player += ss[i] + " "

    def format_field(field):
        if field is None or field == "":
            return 0
        else:
            return field

    def format_num(field):
        if field is None or field == "":
            return 0
        else:
            return '{:,}'.format(field)

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, " \
          f"MinutesPlayed, FgMade, FgAttempts, Fg3Made, Fg3Attempts, Fg2Made, Fg2Attempts, FtMade, FtAttempts, " \
          f"OffRebound, DefRebound, Rebounds, Assists, Steals, Blocks, Turnovers, Fouls, Points from TotalStats" \
          f" ts join Players p on ts.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season = 'Career' and Playoffs = 0"
    cursor.execute(sql)
    rowc = cursor.fetchone()

    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, " \
          f"MinutesPlayed, FgMade, FgAttempts, Fg3Made, Fg3Attempts, Fg2Made, Fg2Attempts, FtMade, FtAttempts, " \
          f"OffRebound, DefRebound, Rebounds, Assists, Steals, Blocks, Turnovers, Fouls, Points from TotalStats" \
          f" ts join Players p on ts.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season like '{season}%' and Playoffs = 0"

    cursor.execute(sql)
    row = cursor.fetchone()
    if cursor.rowcount == 0:
        sql = f"select top 1 p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, " \
              f"MinutesPlayed, FgMade, FgAttempts, Fg3Made, Fg3Attempts, Fg2Made, Fg2Attempts, FtMade, FtAttempts, " \
              f"OffRebound, DefRebound, Rebounds, Assists, Steals, Blocks, Turnovers, Fouls, Points from TotalStats" \
              f" ts join Players p on ts.PlayerId = p.PlayerId where p.Name = '{player}' and " \
              f"(season like '19%' or season like '20%') and Playoffs = 0 order by Season desc"
        cursor.execute(sql)
        row = cursor.fetchone()

    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=player.title() + "Totals",
                     value="There are no players with the name: `" + player.title() + "`",
                     inline=False)
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.title() + "Totals (" + row.Team + ") " + str(row.Age) + " y/o "
                                 + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Games Started/Played", value=str(format_field(row.GamesStarted)) + " of " +
                                                        str(format_field(row.GamesPlayed)) + " | " +
                                                        str(format_num(rowc.GamesStarted)) + " of " +
                                                        str(format_num(rowc.GamesPlayed)))
        em.add_field(name="Minutes Played", value=str(format_num(row.MinutesPlayed)) + " | " +
                                                  str(format_num(rowc.MinutesPlayed)))
        em.add_field(name="Fg/2Pt/3Pt/Ft Shooting", value=str(format_num(row.FgMade)) + "/" +
                                            str(format_num(row.Fg2Made)) + "/" +
                                            str(format_num(row.Fg3Made)) +
                                            "/" + str(format_num(row.FtMade)) + " Makes On" + '\n' +
                                            "__" + str(format_num(row.FgAttempts)) + "/" +
                                            str(format_num(row.Fg2Attempts)) + "/" +
                                            str(format_num(row.Fg3Attempts)) + "/" +
                                            str(format_num(row.FtAttempts))
                                            + " Attempts__" + '\n' + str(format_num(rowc.FgMade)) +
                                            "/" + str(format_num(rowc.Fg2Made)) + "/" +
                                            str(format_num(rowc.Fg3Made)) + "/" +
                                            str(format_num(rowc.FtMade)) +
                                            " Makes On" + '\n' + str(format_num(rowc.FgAttempts)) +
                                            "/" + str(format_num(rowc.Fg2Attempts)) + "/" +
                                            str(format_num(rowc.Fg3Attempts)) + "/" +
                                            str(format_num(rowc.FtAttempts)) + " Attempts", inline=False)
        em.add_field(name="Rebounds", value="__" + str(format_num(row.Rebounds)) + " (Offensive: " +
                                            str(format_num(row.OffRebound)) +
                                            ", Defensive: " + str(format_num(row.DefRebound)) + ")__" +
                                            '\n' + str(format_num(rowc.Rebounds)) + " (Offensive: "
                                            + str(format_num(rowc.OffRebound)) +
                                            ", Defensive: " + str(format_num(rowc.DefRebound)) + ")", inline = False)
        em.add_field(name="Assists", value=str(format_num(row.Assists)) + " | " +
                                                    str(format_num(rowc.Assists)))
        em.add_field(name="Steals", value=str(format_num(row.Steals)) + " | " +
                                                   str(format_num(rowc.Steals)))
        em.add_field(name="Blocks", value=str(format_num(row.Blocks)) + " | " +
                                          str(format_num(rowc.Blocks)))
        em.add_field(name="Turnovers", value=str(format_num(row.Turnovers)) + " | " +
                                             str(format_num(rowc.Turnovers)))
        em.add_field(name="Fouls", value=str(format_num(row.Fouls)) + " | " +
                                         str(format_num(rowc.Fouls)))
        em.add_field(name="Points", value=(str(format_num(row.Points)) + " | " +
                                                    str(format_num(rowc.Points))))
        em.set_footer(text="Data From Basketball Reference")
        await ctx.send(embed = em)

# t!playofftotals ------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def playofftotals(ctx, *, args):
    ss = args.split(' ')
    player = ""
    season = datetime.today().year - 1
    for i in range(0, len(ss)):
        if i == len(ss) - 1 and ss[i].isnumeric():
            season = ss[i]
        else:
            player += ss[i] + " "

    def format_field(field):
        if field is None or field == "":
            return 0
        else:
            return field

    def format_num(field):
        if field is None or field == "":
            return 0
        else:
            return '{:,}'.format(field)

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, " \
          f"MinutesPlayed, FgMade, FgAttempts, Fg3Made, Fg3Attempts, Fg2Made, Fg2Attempts, FtMade, FtAttempts, " \
          f"OffRebound, DefRebound, Rebounds, Assists, Steals, Blocks, Turnovers, Fouls, Points from TotalStats" \
          f" ts join Players p on ts.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season = 'Career' and Playoffs = 1"
    cursor.execute(sql)
    rowc = cursor.fetchone()

    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, " \
          f"MinutesPlayed, FgMade, FgAttempts, Fg3Made, Fg3Attempts, Fg2Made, Fg2Attempts, FtMade, FtAttempts, " \
          f"OffRebound, DefRebound, Rebounds, Assists, Steals, Blocks, Turnovers, Fouls, Points from TotalStats" \
          f" ts join Players p on ts.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season like '{season}%' and Playoffs = 1"

    cursor.execute(sql)
    row = cursor.fetchone()
    if cursor.rowcount == 0:
        sql = f"select top 1 p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, " \
              f"MinutesPlayed, FgMade, FgAttempts, Fg3Made, Fg3Attempts, Fg2Made, Fg2Attempts, FtMade, FtAttempts, " \
              f"OffRebound, DefRebound, Rebounds, Assists, Steals, Blocks, Turnovers, Fouls, Points from TotalStats" \
              f" ts join Players p on ts.PlayerId = p.PlayerId where p.Name = '{player}' and " \
              f"(season like '19%' or season like '20%') and Playoffs = 1 order by Season desc"
        cursor.execute(sql)
        row = cursor.fetchone()

    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=player.title() + "Playoff Totals",
                     value="There are no players with the name: `" + player.title() + "`",
                     inline=False)
        em.set_footer(text="Or they've never been to the playoffs")
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.title() + "Playoff Totals (" + row.Team + ") " + str(row.Age) + " y/o "
                                 + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Games Started/Played", value=str(format_field(row.GamesStarted)) + " of " +
                                                        str(format_field(row.GamesPlayed)) + " | " +
                                                        str(format_num(rowc.GamesStarted)) + " of " +
                                                        str(format_num(rowc.GamesPlayed)))
        em.add_field(name="Minutes Played", value=str(format_num(row.MinutesPlayed)) + " | " +
                                                  str(format_num(rowc.MinutesPlayed)))
        em.add_field(name="Fg/2Pt/3Pt/Ft Shooting", value=str(format_num(row.FgMade)) + "/" +
                                            str(format_num(row.Fg2Made)) + "/" +
                                            str(format_num(row.Fg3Made)) +
                                            "/" + str(format_num(row.FtMade)) + " Makes On" + '\n' +
                                            "__" + str(format_num(row.FgAttempts)) + "/" +
                                            str(format_num(row.Fg2Attempts)) + "/" +
                                            str(format_num(row.Fg3Attempts)) + "/" +
                                            str(format_num(row.FtAttempts))
                                            + " Attempts__" + '\n' + str(format_num(rowc.FgMade)) +
                                            "/" + str(format_num(rowc.Fg2Made)) + "/" +
                                            str(format_num(rowc.Fg3Made)) + "/" +
                                            str(format_num(rowc.FtMade)) +
                                            " Makes On" + '\n' + str(format_num(rowc.FgAttempts)) +
                                            "/" + str(format_num(rowc.Fg2Attempts)) + "/" +
                                            str(format_num(rowc.Fg3Attempts)) + "/" +
                                            str(format_num(rowc.FtAttempts)) + " Attempts", inline=False)
        em.add_field(name="Rebounds", value="__" + str(format_num(row.Rebounds)) + " (Offensive: " +
                                            str(format_num(row.OffRebound)) +
                                            ", Defensive: " + str(format_num(row.DefRebound)) + ")__" +
                                            '\n' + str(format_num(rowc.Rebounds)) + " (Offensive: "
                                            + str(format_num(rowc.OffRebound)) +
                                            ", Defensive: " + str(format_num(rowc.DefRebound)) + ")", inline = False)
        em.add_field(name="Assists", value=str(format_num(row.Assists)) + " | " +
                                                    str(format_num(rowc.Assists)))
        em.add_field(name="Steals", value=str(format_num(row.Steals)) + " | " +
                                                   str(format_num(rowc.Steals)))
        em.add_field(name="Blocks", value=str(format_num(row.Blocks)) + " | " +
                                          str(format_num(rowc.Blocks)))
        em.add_field(name="Turnovers", value=str(format_num(row.Turnovers)) + " | " +
                                             str(format_num(rowc.Turnovers)))
        em.add_field(name="Fouls", value=str(format_num(row.Fouls)) + " | " +
                                         str(format_num(rowc.Fouls)))
        em.add_field(name="Points", value=(str(format_num(row.Points)) + " | " +
                                                    str(format_num(rowc.Points))))
        em.set_footer(text="Data From Basketball Reference")
        await ctx.send(embed = em)

# t!adv ----------------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def adv(ctx, *, args):
    ss = args.split(' ')
    player = ""
    season = datetime.today().year - 1
    for i in range(0, len(ss)):
        if i == len(ss) - 1 and ss[i].isnumeric():
            season = ss[i]
        else:
            player += ss[i] + " "

    def format_field(field):
        if field is None or field == "":
            return 0
        else:
            return field

    def format_percent(field):
        if field is None or field == "":
            return 0
        else:
            return '{:.1f}'.format(field * 100)

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, PlayerEfficiency, TrueShooting, Fg3Rate, FtRate," \
          f" OffRebRate, DefRebRate, ReboundRate, AssistRate, StealRate, BlockRate, TurnoverRate, UsageRate," \
          f" WinShares, PlusMinus, OffPlusMinus, DefPlusMinus from AdvancedStats s join Players p on " \
          f"s.PlayerId = p.PlayerId where p.Name = '{player}' and season = 'Career' and Playoffs = 0"
    cursor.execute(sql)
    rowc = cursor.fetchone()

    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, PlayerEfficiency, TrueShooting, Fg3Rate, FtRate," \
          f" OffRebRate, DefRebRate, ReboundRate, AssistRate, StealRate, BlockRate, TurnoverRate, UsageRate," \
          f" WinShares, PlusMinus, OffPlusMinus, DefPlusMinus from AdvancedStats s join Players p on " \
          f"s.PlayerId = p.PlayerId where p.Name = '{player}' and season like '{season}%' and Playoffs = 0"

    cursor.execute(sql)
    row = cursor.fetchone()
    if cursor.rowcount == 0:
        sql = f"select p.Image, Playoffs, Season, Age, Team, Position, PlayerEfficiency, TrueShooting, Fg3Rate, " \
              f"FtRate, OffRebRate, DefRebRate, ReboundRate, AssistRate, StealRate, BlockRate, TurnoverRate, " \
              f"UsageRate, WinShares, PlusMinus, OffPlusMinus, DefPlusMinus from AdvancedStats" \
              f" s join Players p on s.PlayerId = p.PlayerId where p.Name = '{player}' and " \
              f"(season like '19%' or season like '20%') and Playoffs = 0 order by Season desc"
        cursor.execute(sql)
        row = cursor.fetchone()

    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=player.title() + "Advanced Stats",
                     value="There are no players with the name: `" + player.title() + "`",
                     inline=False)
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.title() + "Advanced Stats (" + row.Team + ") " + str(row.Age) + " y/o "
                                 + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Player Efficiency", value=str(format_field(row.PlayerEfficiency)) + " | " +
                                                        str(format_field(rowc.PlayerEfficiency)))
        em.add_field(name="Win Shares", value=(str(format_field(row.WinShares)) + " | " +
                                                    str(format_field(rowc.WinShares))))
        em.add_field(name="True Shooting %", value=str(format_percent(row.TrueShooting)) + " | " +
                                                  str(format_percent(rowc.TrueShooting)))
        em.add_field(name="3Pt Attempt Rate", value= str(format_percent(row.Fg3Rate)) +
                                                  " | "  + str(format_percent(rowc.Fg3Rate)))
        em.add_field(name="Ft Attempt Rate", value= str(format_percent(row.FtRate)) +
                                                 " | " + str(format_percent(rowc.FtRate)))
        em.add_field(name="Rebound Rate", value="__" + str(format_field(row.ReboundRate)) + " (Offensive: " +
                                            str(format_field(row.OffRebRate)) +
                                            ", Defensive: " + str(format_field(row.DefRebRate)) + ")__" +
                                            '\n' + str(format_field(rowc.ReboundRate)) + " (Offensive: "
                                            + str(format_field(rowc.OffRebRate)) +
                                            ", Defensive: " + str(format_field(rowc.DefRebRate))
                                            + ")", inline=False)
        em.add_field(name="Assist Rate", value=str(format_field(row.AssistRate)) + " | " +
                                                    str(format_field(rowc.AssistRate)))
        em.add_field(name="Steal Rate", value=str(format_field(row.StealRate)) + " | " +
                                                   str(format_field(rowc.StealRate)))
        em.add_field(name="Block Rate", value=str(format_field(row.BlockRate)) + " | " +
                                                   str(format_field(rowc.BlockRate)))
        em.add_field(name="Turnover Rate", value=str(format_field(row.TurnoverRate)) + " | " +
                                                      str(format_field(rowc.TurnoverRate)))
        em.add_field(name="Usage Rate", value=str(format_field(row.UsageRate)) + " | " +
                                                  str(format_field(rowc.UsageRate)))
        em.add_field(name="Plus Minus", value="__" + str(format_field(row.PlusMinus)) + "(Offensive: " +
                                              str(format_field(row.OffPlusMinus))  + ", Defensive: " +
                                              str(format_field(row.DefPlusMinus)) + "__" + '\n' +
                                                     str(format_field(rowc.PlusMinus)) + "(Offensive: " +
                                              str(format_field(rowc.OffPlusMinus))  + ", Defensive: " +
                                              str(format_field(rowc.DefPlusMinus)))
        em.set_footer(text="Data From Basketball Reference")
        await ctx.send(embed = em)



# t!playoffadv ---------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def playoffadv(ctx, *, args):
    ss = args.split(' ')
    player = ""
    season = datetime.today().year - 1
    for i in range(0, len(ss)):
        if i == len(ss) - 1 and ss[i].isnumeric():
            season = ss[i]
        else:
            player += ss[i] + " "

    def format_field(field):
        if field is None or field == "":
            return 0
        else:
            return field

    def format_percent(field):
        if field is None or field == "":
            return 0
        else:
            return '{:.1f}'.format(field * 100)

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, PlayerEfficiency, TrueShooting, Fg3Rate, FtRate," \
          f" OffRebRate, DefRebRate, ReboundRate, AssistRate, StealRate, BlockRate, TurnoverRate, UsageRate," \
          f" WinShares, PlusMinus, OffPlusMinus, DefPlusMinus from AdvancedStats s join Players p on " \
          f"s.PlayerId = p.PlayerId where p.Name = '{player}' and season = 'Career' and Playoffs = 1"
    cursor.execute(sql)
    rowc = cursor.fetchone()

    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, PlayerEfficiency, TrueShooting, Fg3Rate, FtRate," \
          f" OffRebRate, DefRebRate, ReboundRate, AssistRate, StealRate, BlockRate, TurnoverRate, UsageRate," \
          f" WinShares, PlusMinus, OffPlusMinus, DefPlusMinus from AdvancedStats s join Players p on " \
          f"s.PlayerId = p.PlayerId where p.Name = '{player}' and season like '{season}%' and Playoffs = 1"

    cursor.execute(sql)
    row = cursor.fetchone()
    if cursor.rowcount == 0:
        sql = f"select p.Image, Playoffs, Season, Age, Team, Position, PlayerEfficiency, TrueShooting, Fg3Rate, " \
              f"FtRate, OffRebRate, DefRebRate, ReboundRate, AssistRate, StealRate, BlockRate, TurnoverRate, " \
              f"UsageRate, WinShares, PlusMinus, OffPlusMinus, DefPlusMinus from AdvancedStats" \
              f" s join Players p on s.PlayerId = p.PlayerId where p.Name = '{player}' and " \
              f"(season like '19%' or season like '20%') and Playoffs = 1 order by Season desc"
        cursor.execute(sql)
        row = cursor.fetchone()

    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=player.title() + "Playoff Advanced Stats",
                     value="There are no players with the name: `" + player.title() + "`",
                     inline=False)
        em.set_footer(text="Or they've never been to the playoffs")
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.title() + "Playoff Advanced Stats (" + row.Team + ") " + str(row.Age) + " y/o "
                                 + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Player Efficiency", value=str(format_field(row.PlayerEfficiency)) + " | " +
                                                        str(format_field(rowc.PlayerEfficiency)))
        em.add_field(name="Win Shares", value=(str(format_field(row.WinShares)) + " | " +
                                                    str(format_field(rowc.WinShares))))
        em.add_field(name="True Shooting %", value=str(format_percent(row.TrueShooting)) + " | " +
                                                  str(format_percent(rowc.TrueShooting)))
        em.add_field(name="3Pt Attempt Rate", value= str(format_percent(row.Fg3Rate)) +
                                                  " | "  + str(format_percent(rowc.Fg3Rate)))
        em.add_field(name="Ft Attempt Rate", value= str(format_percent(row.FtRate)) +
                                                 " | " + str(format_percent(rowc.FtRate)))
        em.add_field(name="Rebound Rate", value="__" + str(format_field(row.ReboundRate)) + " (Offensive: " +
                                            str(format_field(row.OffRebRate)) +
                                            ", Defensive: " + str(format_field(row.DefRebRate)) + ")__" +
                                            '\n' + str(format_field(rowc.ReboundRate)) + " (Offensive: "
                                            + str(format_field(rowc.OffRebRate)) +
                                            ", Defensive: " + str(format_field(rowc.DefRebRate))
                                            + ")", inline=False)
        em.add_field(name="Assist Rate", value=str(format_field(row.AssistRate)) + " | " +
                                                    str(format_field(rowc.AssistRate)))
        em.add_field(name="Steal Rate", value=str(format_field(row.StealRate)) + " | " +
                                                   str(format_field(rowc.StealRate)))
        em.add_field(name="Block Rate", value=str(format_field(row.BlockRate)) + " | " +
                                                   str(format_field(rowc.BlockRate)))
        em.add_field(name="Turnover Rate", value=str(format_field(row.TurnoverRate)) + " | " +
                                                      str(format_field(rowc.TurnoverRate)))
        em.add_field(name="Usage Rate", value=str(format_field(row.UsageRate)) + " | " +
                                                  str(format_field(rowc.UsageRate)))
        em.add_field(name="Plus Minus", value="__" + str(format_field(row.PlusMinus)) + "(Offensive: " +
                                              str(format_field(row.OffPlusMinus))  + ", Defensive: " +
                                              str(format_field(row.DefPlusMinus)) + "__" + '\n' +
                                                     str(format_field(rowc.PlusMinus)) + "(Offensive: " +
                                              str(format_field(rowc.OffPlusMinus))  + ", Defensive: " +
                                              str(format_field(rowc.DefPlusMinus)))
        em.set_footer(text="Data From Basketball Reference")
        await ctx.send(embed = em)

# t!per100 -------------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def per100(ctx, *, args):
    ss = args.split(' ')
    player = ""
    season = datetime.today().year - 1
    for i in range(0, len(ss)):
        if i == len(ss) - 1 and ss[i].isnumeric():
            season = ss[i]
        else:
            player += ss[i] + " "

    def format_field(field):
        if field is None or field == "":
            return 0
        else:
            return field

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, FgMade, FgAttempts, " \
          f"Fg3Made, Fg3Attempts, Fg2Made, Fg2Attempts, FtMade, FtAttempts, OffRebound, DefRebound, Rebounds," \
          f" Assists, Steals, Blocks, Turnovers, Fouls, Points, OffRating, DefRating " \
          f"from Per100Stats s join Players p on s.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season = 'Career' and Playoffs = 0"
    cursor.execute(sql)
    rowc = cursor.fetchone()

    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, FgMade, FgAttempts, " \
          f"Fg3Made, Fg3Attempts, Fg2Made, Fg2Attempts, FtMade, FtAttempts, OffRebound, DefRebound, Rebounds," \
          f" Assists, Steals, Blocks, Turnovers, Fouls, Points, OffRating, DefRating " \
          f"from Per100Stats s join Players p on s.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season like '{season}%' and Playoffs = 0"

    cursor.execute(sql)
    row = cursor.fetchone()
    if cursor.rowcount == 0:
        sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, FgMade, FgAttempts," \
              f" Fg3Made, Fg3Attempts, Fg2Made, Fg2Attempts, FtMade, FtAttempts, OffRebound, DefRebound, Rebounds," \
              f" Assists, Steals, Blocks, Turnovers, Fouls, Points, OffRating, DefRating from Per100Stats" \
              f" s join Players p on s.PlayerId = p.PlayerId where p.Name = '{player}' and " \
              f"(season like '19%' or season like '20%') and Playoffs = 0 order by Season desc"
        cursor.execute(sql)
        row = cursor.fetchone()

    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=player.title() + "Per 100 Poss Stats",
                     value="There are no players with the name: `" + player.title() + "`",
                     inline=False)
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.title() + "Per 100 Poss Stats (" + row.Team + ") " + str(row.Age) +
                                 " y/o " + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Games Started/Played", value=str(format_field(row.GamesPlayed)) + " of " +
                                                        str(format_field(row.GamesStarted)) + " | " +
                                                        str(format_field(rowc.GamesPlayed)) + " of " +
                                                        str(format_field(rowc.GamesStarted)))
        em.add_field(name="Points", value=str(format_field(row.Points)) + " | " + str(format_field(rowc.Points)))
        em.add_field(name="Fg/2Pt/3Pt/Ft Shooting", value=str(format_field(row.FgMade)) + "/" +
                                                          str(format_field(row.Fg2Made)) + "/" +
                                                          str(format_field(row.Fg3Made)) +
                                                          "/" + str(format_field(row.FtMade)) + " Makes On" + '\n' +
                                                          "__" + str(format_field(row.FgAttempts)) + "/" +
                                                          str(format_field(row.Fg2Attempts)) + "/" +
                                                          str(format_field(row.Fg3Attempts)) + "/" +
                                                          str(format_field(row.FtAttempts))
                                                          + " Attempts__" + '\n' + str(format_field(rowc.FgMade)) +
                                                          "/" + str(format_field(rowc.Fg2Made)) + "/" +
                                                          str(format_field(rowc.Fg3Made)) + "/" +
                                                          str(format_field(rowc.FtMade)) +
                                                          " Makes On" + '\n' + str(format_field(rowc.FgAttempts)) +
                                                          "/" + str(format_field(rowc.Fg2Attempts)) + "/" +
                                                          str(format_field(rowc.Fg3Attempts)) + "/" +
                                                          str(format_field(rowc.FtAttempts)) + " Attempts")
        em.add_field(name="Offensive/Defensive Rating", value=str(format_field(row.OffRating)) + "/" +
                                                  str(format_field(row.DefRating)) + " | " +
                                                  str(format_field(rowc.OffRating)) + "/" +
                                                  str(format_field(rowc.DefRating)))
        em.add_field(name="** **", value="** **")
        em.add_field(name="Rebounds", value="__" + str(format_field(row.Rebounds)) + " (Off: " +
                                            str(format_field(row.OffRebound)) +
                                            ", Def: " + str(format_field(row.DefRebound)) + ")__" +
                                            '\n' + str(format_field(rowc.Rebounds)) + " (Off: "
                                            + str(format_field(rowc.OffRebound)) +
                                            ", Def: " + str(format_field(rowc.DefRebound)) + ")")
        em.add_field(name="Assists", value=str(format_field(row.Assists)) + " | " +
                                                    str(format_field(rowc.Assists)))
        em.add_field(name="Steals", value=str(format_field(row.Steals)) + " | " +
                                                   str(format_field(rowc.Steals)))
        em.add_field(name="Blocks", value=str(format_field(row.Blocks)) + " | " +
                                                   str(format_field(rowc.Blocks)))
        em.add_field(name="Turnovers", value=str(format_field(row.Turnovers)) + " | " +
                                                      str(format_field(rowc.Turnovers)))
        em.add_field(name="Fouls", value=str(format_field(row.Fouls)) + " | " + str(format_field(rowc.Fouls)))
        em.set_footer(text="Data From Basketball Reference")
        await ctx.send(embed = em)

# t!playoffsper100 -----------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def playoffper100(ctx, *, args):
    ss = args.split(' ')
    player = ""
    season = datetime.today().year - 1
    for i in range(0, len(ss)):
        if i == len(ss) - 1 and ss[i].isnumeric():
            season = ss[i]
        else:
            player += ss[i] + " "

    def format_field(field):
        if field is None or field == "":
            return 0
        else:
            return field

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, FgMade, FgAttempts, " \
          f"Fg3Made, Fg3Attempts, Fg2Made, Fg2Attempts, FtMade, FtAttempts, OffRebound, DefRebound, Rebounds," \
          f" Assists, Steals, Blocks, Turnovers, Fouls, Points, OffRating, DefRating " \
          f"from Per100Stats s join Players p on s.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season = 'Career' and Playoffs = 1"
    cursor.execute(sql)
    rowc = cursor.fetchone()

    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, FgMade, FgAttempts, " \
          f"Fg3Made, Fg3Attempts, Fg2Made, Fg2Attempts, FtMade, FtAttempts, OffRebound, DefRebound, Rebounds," \
          f" Assists, Steals, Blocks, Turnovers, Fouls, Points, OffRating, DefRating " \
          f"from Per100Stats s join Players p on s.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season like '{season}%' and Playoffs = 1"

    cursor.execute(sql)
    row = cursor.fetchone()
    if cursor.rowcount == 0:
        sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, FgMade, FgAttempts," \
              f" Fg3Made, Fg3Attempts, Fg2Made, Fg2Attempts, FtMade, FtAttempts, OffRebound, DefRebound, Rebounds," \
              f" Assists, Steals, Blocks, Turnovers, Fouls, Points, OffRating, DefRating from Per100Stats" \
              f" s join Players p on s.PlayerId = p.PlayerId where p.Name = '{player}' and " \
              f"(season like '19%' or season like '20%') and Playoffs = 1 order by Season desc"
        cursor.execute(sql)
        row = cursor.fetchone()

    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=player.title() + "Playoff Per 100 Poss Stats",
                     value="There are no players with the name: `" + player.title() + "`",
                     inline=False)
        em.set_footer(text="Or they've never been to the playoffs")
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.title() + "Playoff Per 100 Poss Stats (" + row.Team + ") " +
                                 str(row.Age) + " y/o " + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Games Started/Played", value=str(format_field(row.GamesPlayed)) + " of " +
                                                        str(format_field(row.GamesStarted)) + " | " +
                                                        str(format_field(rowc.GamesPlayed)) + " of " +
                                                        str(format_field(rowc.GamesStarted)))
        em.add_field(name="Points", value=str(format_field(row.Points)) + " | " + str(format_field(rowc.Points)))
        em.add_field(name="Fg/2Pt/3Pt/Ft Shooting", value=str(format_field(row.FgMade)) + "/" +
                                                          str(format_field(row.Fg2Made)) + "/" +
                                                          str(format_field(row.Fg3Made)) +
                                                          "/" + str(format_field(row.FtMade)) + " Makes On" + '\n' +
                                                          "__" + str(format_field(row.FgAttempts)) + "/" +
                                                          str(format_field(row.Fg2Attempts)) + "/" +
                                                          str(format_field(row.Fg3Attempts)) + "/" +
                                                          str(format_field(row.FtAttempts))
                                                          + " Attempts__" + '\n' + str(format_field(rowc.FgMade)) +
                                                          "/" + str(format_field(rowc.Fg2Made)) + "/" +
                                                          str(format_field(rowc.Fg3Made)) + "/" +
                                                          str(format_field(rowc.FtMade)) +
                                                          " Makes On" + '\n' + str(format_field(rowc.FgAttempts)) +
                                                          "/" + str(format_field(rowc.Fg2Attempts)) + "/" +
                                                          str(format_field(rowc.Fg3Attempts)) + "/" +
                                                          str(format_field(rowc.FtAttempts)) + " Attempts")
        em.add_field(name="Offensive/Defensive Rating", value=str(format_field(row.OffRating)) + "/" +
                                                  str(format_field(row.DefRating)) + " | " +
                                                  str(format_field(rowc.OffRating)) + "/" +
                                                  str(format_field(rowc.DefRating)))
        em.add_field(name="** **", value="** **")
        em.add_field(name="Rebounds", value="__" + str(format_field(row.Rebounds)) + " (Off: " +
                                            str(format_field(row.OffRebound)) +
                                            ", Def: " + str(format_field(row.DefRebound)) + ")__" +
                                            '\n' + str(format_field(rowc.Rebounds)) + " (Off: "
                                            + str(format_field(rowc.OffRebound)) +
                                            ", Def: " + str(format_field(rowc.DefRebound)) + ")")
        em.add_field(name="Assists", value=str(format_field(row.Assists)) + " | " +
                                                    str(format_field(rowc.Assists)))
        em.add_field(name="Steals", value=str(format_field(row.Steals)) + " | " +
                                                   str(format_field(rowc.Steals)))
        em.add_field(name="Blocks", value=str(format_field(row.Blocks)) + " | " +
                                                   str(format_field(rowc.Blocks)))
        em.add_field(name="Turnovers", value=str(format_field(row.Turnovers)) + " | " +
                                                      str(format_field(rowc.Turnovers)))
        em.add_field(name="Fouls", value=str(format_field(row.Fouls)) + " | " + str(format_field(rowc.Fouls)))
        em.set_footer(text="Data From Basketball Reference")
        await ctx.send(embed = em)

# t!per36 -------------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def per36(ctx, *, args):
    ss = args.split(' ')
    player = ""
    season = datetime.today().year - 1
    for i in range(0, len(ss)):
        if i == len(ss) - 1 and ss[i].isnumeric():
            season = ss[i]
        else:
            player += ss[i] + " "

    def format_field(field):
        if field is None or field == "":
            return 0
        else:
            return field

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, Fg, Fga, " \
          f"Fg3, Fg3a, Fg2, Fg2a, Ft, Fta, OffRebound, DefRebound, Rebounds," \
          f" Assists, Steals, Blocks, Turnovers, Fouls, Points " \
          f"from Per36Stats s join Players p on s.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season = 'Career' and Playoffs = 0"
    cursor.execute(sql)
    rowc = cursor.fetchone()

    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, Fg, Fga, " \
          f"Fg3, Fg3a, Fg2, Fg2a, Ft, Fta, OffRebound, DefRebound, Rebounds," \
          f" Assists, Steals, Blocks, Turnovers, Fouls, Points " \
          f"from Per36Stats s join Players p on s.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season like '{season}%' and Playoffs = 0"

    cursor.execute(sql)
    row = cursor.fetchone()
    if cursor.rowcount == 0:
        sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, Fg, Fga," \
              f" Fg3, Fg3a, Fg2, Fg2a, Ft, Fta, OffRebound, DefRebound, Rebounds," \
              f" Assists, Steals, Blocks, Turnovers, Fouls, Points from Per36Stats" \
              f" s join Players p on s.PlayerId = p.PlayerId where p.Name = '{player}' and " \
              f"(season like '19%' or season like '20%') and Playoffs = 0 order by Season desc"
        cursor.execute(sql)
        row = cursor.fetchone()

    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=player.title() + "Per 36 Min Stats",
                     value="There are no players with the name: `" + player.title() + "`",
                     inline=False)
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.title() + "Per 36 Min Stats (" + row.Team + ") " + str(row.Age) +
                                 " y/o " + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Games Started/Played", value=str(format_field(row.GamesPlayed)) + " of " +
                                                        str(format_field(row.GamesStarted)) + " | " +
                                                        str(format_field(rowc.GamesPlayed)) + " of " +
                                                        str(format_field(rowc.GamesStarted)))
        em.add_field(name="** **", value="** **")
        em.add_field(name="Fg/2Pt/3Pt/Ft Shooting", value=str(format_field(row.Fg)) + "/" +
                                                          str(format_field(row.Fg2)) + "/" +
                                                          str(format_field(row.Fg3)) +
                                                          "/" + str(format_field(row.Ft)) + " Makes On" + '\n' +
                                                          "__" + str(format_field(row.Fga)) + "/" +
                                                          str(format_field(row.Fg2a)) + "/" +
                                                          str(format_field(row.Fg3a)) + "/" +
                                                          str(format_field(row.Fta))
                                                          + " Attempts__" + '\n' + str(format_field(rowc.Fg)) +
                                                          "/" + str(format_field(rowc.Fg2)) + "/" +
                                                          str(format_field(rowc.Fg3)) + "/" +
                                                          str(format_field(rowc.Ft)) +
                                                          " Makes On" + '\n' + str(format_field(rowc.Fga)) +
                                                          "/" + str(format_field(rowc.Fg2a)) + "/" +
                                                          str(format_field(rowc.Fg3a)) + "/" +
                                                          str(format_field(rowc.Fta)) + " Attempts")
        em.add_field(name="Rebounds", value="__" + str(format_field(row.Rebounds)) + " (Off: " +
                                            str(format_field(row.OffRebound)) +
                                            ", Def: " + str(format_field(row.DefRebound)) + ")__" +
                                            '\n' + str(format_field(rowc.Rebounds)) + " (Off: "
                                            + str(format_field(rowc.OffRebound)) +
                                            ", Def: " + str(format_field(rowc.DefRebound)) + ")")
        em.add_field(name="** **", value="** **")
        em.add_field(name="Assists", value=str(format_field(row.Assists)) + " | " +
                                                    str(format_field(rowc.Assists)))
        em.add_field(name="Steals", value=str(format_field(row.Steals)) + " | " +
                                                   str(format_field(rowc.Steals)))
        em.add_field(name="Blocks", value=str(format_field(row.Blocks)) + " | " +
                                                   str(format_field(rowc.Blocks)))
        em.add_field(name="Turnovers", value=str(format_field(row.Turnovers)) + " | " +
                                                      str(format_field(rowc.Turnovers)))
        em.add_field(name="Fouls", value=str(format_field(row.Fouls)) + " | " + str(format_field(rowc.Fouls)))
        em.add_field(name="Points", value=str(format_field(row.Points)) + " | " + str(format_field(rowc.Points)))
        em.set_footer(text="Data From Basketball Reference")
        await ctx.send(embed = em)

# t!playoffper36 -------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def playoffper36(ctx, *, args):
    ss = args.split(' ')
    player = ""
    season = datetime.today().year - 1
    for i in range(0, len(ss)):
        if i == len(ss) - 1 and ss[i].isnumeric():
            season = ss[i]
        else:
            player += ss[i] + " "

    def format_field(field):
        if field is None or field == "":
            return 0
        else:
            return field

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, Fg, Fga, " \
          f"Fg3, Fg3a, Fg2, Fg2a, Ft, Fta, OffRebound, DefRebound, Rebounds," \
          f" Assists, Steals, Blocks, Turnovers, Fouls, Points " \
          f"from Per36Stats s join Players p on s.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season = 'Career' and Playoffs = 1"
    cursor.execute(sql)
    rowc = cursor.fetchone()

    sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, Fg, Fga, " \
          f"Fg3, Fg3a, Fg2, Fg2a, Ft, Fta, OffRebound, DefRebound, Rebounds," \
          f" Assists, Steals, Blocks, Turnovers, Fouls, Points " \
          f"from Per36Stats s join Players p on s.PlayerId = p.PlayerId " \
          f"where p.Name = '{player}' and season like '{season}%' and Playoffs = 1"

    cursor.execute(sql)
    row = cursor.fetchone()
    if cursor.rowcount == 0:
        sql = f"select p.Image, Playoffs, Season, Age, Team, Position, GamesPlayed, GamesStarted, Fg, Fga," \
              f" Fg3, Fg3a, Fg2, Fg2a, Ft, Fta, OffRebound, DefRebound, Rebounds," \
              f" Assists, Steals, Blocks, Turnovers, Fouls, Points from Per36Stats" \
              f" s join Players p on s.PlayerId = p.PlayerId where p.Name = '{player}' and " \
              f"(season like '19%' or season like '20%') and Playoffs = 1 order by Season desc"
        cursor.execute(sql)
        row = cursor.fetchone()

    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=player.title() + "Playoff Per 36 Min Stats",
                     value="There are no players with the name: `" + player.title() + "`",
                     inline=False)
        em.set_footer(text="Or they've never been to the playoffs")
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.title() + "Playoff Per 36 Min Stats (" + row.Team + ") " + str(row.Age) +
                                 " y/o " + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Games Started/Played", value=str(format_field(row.GamesPlayed)) + " of " +
                                                        str(format_field(row.GamesStarted)) + " | " +
                                                        str(format_field(rowc.GamesPlayed)) + " of " +
                                                        str(format_field(rowc.GamesStarted)))
        em.add_field(name="** **", value="** **")
        em.add_field(name="Fg/2Pt/3Pt/Ft Shooting", value=str(format_field(row.Fg)) + "/" +
                                                          str(format_field(row.Fg2)) + "/" +
                                                          str(format_field(row.Fg3)) +
                                                          "/" + str(format_field(row.Ft)) + " Makes On" + '\n' +
                                                          "__" + str(format_field(row.Fga)) + "/" +
                                                          str(format_field(row.Fg2a)) + "/" +
                                                          str(format_field(row.Fg3a)) + "/" +
                                                          str(format_field(row.Fta))
                                                          + " Attempts__" + '\n' + str(format_field(rowc.Fg)) +
                                                          "/" + str(format_field(rowc.Fg2)) + "/" +
                                                          str(format_field(rowc.Fg3)) + "/" +
                                                          str(format_field(rowc.Ft)) +
                                                          " Makes On" + '\n' + str(format_field(rowc.Fga)) +
                                                          "/" + str(format_field(rowc.Fg2a)) + "/" +
                                                          str(format_field(rowc.Fg3a)) + "/" +
                                                          str(format_field(rowc.Fta)) + " Attempts")
        em.add_field(name="Rebounds", value="__" + str(format_field(row.Rebounds)) + " (Off: " +
                                            str(format_field(row.OffRebound)) +
                                            ", Def: " + str(format_field(row.DefRebound)) + ")__" +
                                            '\n' + str(format_field(rowc.Rebounds)) + " (Off: "
                                            + str(format_field(rowc.OffRebound)) +
                                            ", Def: " + str(format_field(rowc.DefRebound)) + ")")
        em.add_field(name="** **", value="** **")
        em.add_field(name="Assists", value=str(format_field(row.Assists)) + " | " +
                                                    str(format_field(rowc.Assists)))
        em.add_field(name="Steals", value=str(format_field(row.Steals)) + " | " +
                                                   str(format_field(rowc.Steals)))
        em.add_field(name="Blocks", value=str(format_field(row.Blocks)) + " | " +
                                                   str(format_field(rowc.Blocks)))
        em.add_field(name="Turnovers", value=str(format_field(row.Turnovers)) + " | " +
                                                      str(format_field(rowc.Turnovers)))
        em.add_field(name="Fouls", value=str(format_field(row.Fouls)) + " | " + str(format_field(rowc.Fouls)))
        em.add_field(name="Points", value=str(format_field(row.Points)) + " | " + str(format_field(rowc.Points)))
        em.set_footer(text="Data From Basketball Reference")
        await ctx.send(embed = em)

# t!odds ---------------------------------------------------------------------------------------------------------------
@client.command()
async def odds(ctx):

    def format_field(field):
        if field is None or field == "":
            return "0.0%"
        else:
            return field

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()

    sql = "select Team, PlayoffPercent, WinFinal, ProjWIn, ProjLoss, Conference, Seed " \
          "from PlayoffOdds where Conference = 0 order by ProjWin desc"
    cursor.execute(sql)
    rowe = cursor.fetchall()

    sql = "select Team, PlayoffPercent, WinFinal, ProjWIn, ProjLoss, Conference, Seed " \
          "from PlayoffOdds where Conference = 1 order by ProjWin desc"
    cursor.execute(sql)
    roww = cursor.fetchall()

    west = ""
    east = ""
    
    for rows in roww:
        west += "**" + rows.Team + "** | " + str(rows.ProjWIn) + " **/** " + str(rows.ProjLoss) + " **|** " + \
                str(format_field(rows.PlayoffPercent)) + " **|** " + str(format_field(rows.WinFinal)) + '\n'

    for rows in rowe:
        east += "**" + rows.Team + "** | " + str(rows.ProjWIn) + " **/** " + str(rows.ProjLoss) + " **|** " + \
                str(format_field(rows.PlayoffPercent)) + " **|** " + str(format_field(rows.WinFinal)) + '\n'



    em = discord.Embed(title="West Odds", color=discord.Color.red())
    em.add_field(name="Team | Projected Wins/Losses | Playoff Odds | Title Odds",
                 value=west,
                 inline=False)
    em.set_footer(text="Data From Basketball Reference")

    west_id = "West_Odds_" + str(ctx.author.id)
    east_id = "East_Odds_" + str(ctx.author.id)
    await ctx.send(embed=em,
                   components=[[
         Button(style=ButtonStyle.blue, label="West", custom_id=west_id),
         Button(style=ButtonStyle.blue, label="East", custom_id=east_id)
         ]]
                   )
    while True:
        interaction = await client.wait_for("button_click", check=lambda i: i.component.custom_id.find("Odds") >= 0)
        author_id = interaction.component.id.split('_')[2]
        if author_id == str(interaction.author.id):
            if interaction.component.label.startswith("West"):
                    em = discord.Embed(title="West Odds", color=discord.Color.red())
                    em.add_field(name="Team | Projected Wins/Losses | Playoff Odds | Title Odds",
                                 value=west,
                                 inline=False)
                    em.set_footer(text="Data From Basketball Reference")
                    await interaction.respond(embed=em, type=7)
            else:
                em = discord.Embed(title="East Odds", color=discord.Color.red())
                em.add_field(name="Team | Projected Wins/Losses | Playoff Odds | Title Odds",
                             value=east,
                             inline=False)
                em.set_footer(text="Data From Basketball Reference")
                await interaction.respond(embed=em, type=7)
        else:
            await interaction.respond(content="This isn't yor button!", type=4)

# t!standings ----------------------------------------------------------------------------------------------------------
@client.command()
async def standings(ctx):

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()

    sql = "select TeamName, Wins, Losses, GamesBehind, WinLoss, Conference, Seed " \
          "from Standings where Conference = 0 order by Seed asc"
    cursor.execute(sql)
    rowe = cursor.fetchall()

    sql = "select TeamName, Wins, Losses, GamesBehind, WinLoss, Conference, Seed " \
          "from Standings where Conference = 1 order by Seed asc"
    cursor.execute(sql)
    roww = cursor.fetchall()

    west = ""
    east = ""

    for rows in roww:
        west += "**" + str(rows.Seed) + ". " + str(rows.TeamName) + " | **" + str(rows.Wins) + " **/** " + \
                str(rows.Losses) + " **|** " + str(rows.WinLoss) + " **|** " + \
                str(rows.GamesBehind) + '\n'

    for rows in rowe:
        east += "**" + str(rows.Seed) + ". " + str(rows.TeamName) + "** | " + str(rows.Wins) + " **/** " + \
                str(rows.Losses) + " **|** " + str(rows.WinLoss) + " **|** " + \
                str(rows.GamesBehind) + '\n'

    em = discord.Embed(title="West Standings", color=discord.Color.red())
    em.add_field(name="Team | Wins/Losses | Win % | Games Behind",
                 value=west,
                 inline=False)
    em.set_footer(text="Data From Basketball Reference")

    west_id = "West_Standing_" + str(ctx.author.id)
    east_id = "East_Standing_" + str(ctx.author.id)
    await ctx.send(embed=em,
                   components=[[
         Button(style=ButtonStyle.blue, label="West", custom_id=west_id),
         Button(style=ButtonStyle.blue, label="East", custom_id=east_id)
         ]]
                   )
    while True:
        interaction = await client.wait_for("button_click", check=lambda i: i.component.custom_id.find("Standing") >= 0)
        author_id = interaction.component.id.split('_')[2]
        if author_id == str(interaction.author.id):
            if interaction.component.label.startswith("West"):
                    em = discord.Embed(title="West Standings", color=discord.Color.red())
                    em.add_field(name="Team | Wins/Losses | Win % | Games Behind",
                                 value=west,
                                 inline=False)
                    em.set_footer(text="Data From Basketball Reference")
                    await interaction.respond(embed=em, type=7)
            else:
                em = discord.Embed(title="East Standings", color=discord.Color.red())
                em.add_field(name="Team | Wins/Losses | Win % | Games Behind",
                             value=east,
                             inline=False)
                em.set_footer(text="Data From Basketball Reference")
                await interaction.respond(embed=em, type=7)
        else:
            await interaction.respond(content="This isn't yor button!", type=4)

# t!teamstats ----------------------------------------------------------------------------------------------------------
@client.command()
async def teamstats(ctx):

    def format_field(field):
        if field is None or field == "":
            return 0
        else:
            return field

    def format_percent(field):
        if field is None or field == "":
            return 0
        else:
            return '{:.1f}'.format(field * 100)

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()

    cursor.execute("select TeamName, GamesPlayed, FgPercent, Fg, Fga, Fg3Percent, Fg3, Fg3a, Fg2Percent, Fg2, Fg2a, "
                   "FtPercent, Ft, Fta, OffRebound, DefRebound, Rebounds, Steals, Blocks, Assists, Turnovers, Fouls, "
                   "Points, OppPoints from TeamStats where TeamName = ?", "Atlanta Hawks")
    row = cursor.fetchone()

    cursor = cnxn.cursor()
    cursor.execute("select TeamName, Wins, Losses, Seed from Standings where TeamName = ?", "Atlanta Hawks")
    rowe = cursor.fetchone()

    cursor = cnxn.cursor()
    cursor.execute("select TeamName, TeamLogo from Teams where TeamName = ?", "Atlanta Hawks")
    rowi = cursor.fetchone()

    em = discord.Embed(title=row.TeamName + " Stats", color=discord.Color.red())
    em.set_thumbnail(url=rowi.TeamLogo)
    em.add_field(name="Seed", value=str(rowe.Seed))
    em.add_field(name="Games Played", value=str(format_field(row.GamesPlayed)))
    em.add_field(name="Wins/Losses", value=str(format_field(rowe.Wins)) + " / " + str(format_field(rowe.Losses)))
    em.add_field(name="Fg%/2Pt%/3Pt%/Ft%", value=str(format_percent(row.FgPercent)) +
                                                 "/" + str(format_percent(row.Fg2Percent)) + "/" +
                                                 str(format_percent(row.Fg3Percent)) + "/" +
                                                 str(format_percent(row.FtPercent)))
    em.add_field(name="Fg/2Pt/3Pt/Ft Shooting", value=str(format_field(row.Fg)) + "/" +
                                                      str(format_field(row.Fg2)) + "/" +
                                                      str(format_field(row.Fg3)) +
                                                      "/" + str(format_field(row.Ft)) + " Makes On" + '\n' +
                                                      str(format_field(row.Fga)) + "/" +
                                                      str(format_field(row.Fg2a)) + "/" +
                                                      str(format_field(row.Fg3a)) + "/" +
                                                      str(format_field(row.Fta))
                                                      + " Attempts")
    em.add_field(name="Rebounds", value=str(format_field(row.Rebounds)) + " (Offensive: " +
                                        str(format_field(row.OffRebound)) +
                                        ", Defensive: " + str(format_field(row.DefRebound)) + ")",
                                        inline=False)
    em.add_field(name="Assists", value=str(format_field(row.Assists)))
    em.add_field(name="Steals", value=str(format_field(row.Steals)))
    em.add_field(name="Blocks", value=str(format_field(row.Blocks)))
    em.add_field(name="Turnovers", value=str(format_field(row.Turnovers)))
    em.add_field(name="Fouls", value=str(format_field(row.Fouls)))
    em.add_field(name="Points/Opp Points", value=str(format_field(row.Points)) + " / " +
                                                 str(format_field(row.OppPoints)))
    em.set_footer(text="Data From Basketball Reference")

    atl = "Atlanta Hawks_TeamStats_" + str(ctx.author.id)
    bos = "Boston Celitcs_TeamStats_" + str(ctx.author.id)
    brk = "Brooklyn Nets_TeamStats_" + str(ctx.author.id)
    cho = "Charlotte Hornets_TeamStats_" + str(ctx.author.id)
    chi = "Chicago Bulls_TeamStats_" + str(ctx.author.id)
    cle = "Clevland Cavaliers_TeamStats_" + str(ctx.author.id)
    dal = "Dallas Mavericks_TeamStats_" + str(ctx.author.id)
    den = "Denver Nuggets_TeamStats_" + str(ctx.author.id)
    det = "Detroit Pistons_TeamStats_" + str(ctx.author.id)
    gsw = "Golden Stats Warriors_TeamStats_" + str(ctx.author.id)
    hou = "Houston Rockets_TeamStats_" + str(ctx.author.id)
    ind = "Indiana Pacers_TeamStats_" + str(ctx.author.id)
    lac = "Los Angeles Clippers_TeamStats_" + str(ctx.author.id)
    lal = "Los Angeles Lakers_TeamStats_" + str(ctx.author.id)
    mem = "Memphis Grizzlies_TeamStats_" + str(ctx.author.id)
    mia = "Miami Heat_TeamStats_" + str(ctx.author.id)
    mil = "Milwaukee Bucks_TeamStats_" + str(ctx.author.id)
    min = "Minnesota Timberwolves_TeamStats_" + str(ctx.author.id)
    nop = "New Orleans Pelicans_TeamStats_" + str(ctx.author.id)
    nyk = "New York Knicks_TeamStats_" + str(ctx.author.id)
    okc = "Oklahoma City Thunder_TeamStats_" + str(ctx.author.id)
    orl = "Orlando Magic_TeamStats_" + str(ctx.author.id)
    phi = "Philadelphia 76ers_TeamStats_" + str(ctx.author.id)
    pho = "Phoenix Suns_TeamStats_" + str(ctx.author.id)
    por = "Portland Trail Blazers_TeamStats_" + str(ctx.author.id)
    sac = "Sacramento Kings_TeamStats_" + str(ctx.author.id)
    sas = "San Antonio Spurs_TeamStats_" + str(ctx.author.id)
    tor = "Toronto Raptors_TeamStats_" + str(ctx.author.id)
    uta = "Utah Jass_TeamStats_" + str(ctx.author.id)
    was = "Washington Wizards_TeamStats_" + str(ctx.author.id)

    await ctx.send(
        embed=em,
        components=[[
            Select(
                placeholder="Select A Team",
                options=[
                    SelectOption(label="Atlanta Hawks", value=atl),
                    SelectOption(label="Boston Celtics", value=bos),
                    SelectOption(label="Brooklyn Nets", value=brk),
                    SelectOption(label="Charlotte Hornets", value=cho),
                    SelectOption(label="Chicago Bulls", value=chi),
                    SelectOption(label="Cleveland Cavaliers", value=cle),
                    SelectOption(label="Dallas Mavericks", value=dal),
                    SelectOption(label="Denver Nuggets", value=den),
                    SelectOption(label="Detroit Pistons", value=det),
                    SelectOption(label="Golden State Warriors", value=gsw),
                    SelectOption(label="Houston Rockets", value=hou),
                    SelectOption(label="Indiana Pacers", value=ind),
                    SelectOption(label="Los Angeles Clippers", value=lac),
                    SelectOption(label="Los Angeles Lakers", value=lal),
                    SelectOption(label="Memphis Grizzlies", value=mem)
                ]
            )
        ],
            [
                Select(
                    placeholder="Select A Team",
                    options=[
                        SelectOption(label="Miami Heat", value=mia),
                        SelectOption(label="Milwaukee Bucks", value=mil),
                        SelectOption(label="Minnesota Timberwolves", value=min),
                        SelectOption(label="New Orleans Pelicans", value=nop),
                        SelectOption(label="New York Knicks", value=nyk),
                        SelectOption(label="Oklahoma City Thunder", value=okc),
                        SelectOption(label="Orlando Magic", value=orl),
                        SelectOption(label="Philadelphia 76ers", value=phi),
                        SelectOption(label="Phoenix Suns", value=pho),
                        SelectOption(label="Portland Trail Blazers", value=por),
                        SelectOption(label="Sacramento Kings", value=sac),
                        SelectOption(label="San Antonio Spurs", value=sas),
                        SelectOption(label="Toronto Raptors", value=tor),
                        SelectOption(label="Utah Jazz", value=uta),
                        SelectOption(label="Washington Wizards", value=was)
                    ]
                )
            ]
        ],
    )

    while True:
        interaction = await client.wait_for("select_option", check=lambda i: i.values[0].find("TeamStats") >= 0)
        author_id = interaction.values[0].split('_')[2]

        if author_id == str(interaction.author.id):
            cnxn = pyodbc.connect(sql_connection)

            cursor = cnxn.cursor()

            cursor.execute(
                "select TeamName, GamesPlayed, FgPercent, Fg, Fga, Fg3Percent, Fg3, Fg3a, Fg2Percent, Fg2, Fg2a, "
                "FtPercent, Ft, Fta, OffRebound, DefRebound, Rebounds, Steals, Blocks, Assists, Turnovers, Fouls, "
                "Points, OppPoints from TeamStats where TeamName = ?", interaction.values[0].split('_')[0])
            row = cursor.fetchone()

            cursor = cnxn.cursor()
            cursor.execute("select TeamName, Wins, Losses, Seed from Standings where TeamName = ?",
                           interaction.values[0].split('_')[0])
            rowe = cursor.fetchone()

            cursor = cnxn.cursor()
            cursor.execute("select TeamName, TeamLogo from Teams where TeamName = ?",
                           interaction.values[0].split('_')[0])
            rowi = cursor.fetchone()

            em = discord.Embed(title=row.TeamName + " Stats", color=discord.Color.red())
            em.set_thumbnail(url=rowi.TeamLogo)
            em.add_field(name="Seed", value=str(rowe.Seed))
            em.add_field(name="Games Played", value=str(format_field(row.GamesPlayed)))
            em.add_field(name="Wins/Losses", value=str(format_field("{:.0f}".format(rowe.Wins))) + " / " +
                                                   str(format_field("{:.0f}".format(rowe.Losses))))
            em.add_field(name="Fg%/2Pt%/3Pt%/Ft%", value=str(format_percent(row.FgPercent)) +
                                                         "/" + str(format_percent(row.Fg2Percent)) + "/" +
                                                         str(format_percent(row.Fg3Percent)) + "/" +
                                                         str(format_percent(row.FtPercent)))
            em.add_field(name="Fg/2Pt/3Pt/Ft Shooting", value=str(format_field(row.Fg)) + "/" +
                                                              str(format_field(row.Fg2)) + "/" +
                                                              str(format_field(row.Fg3)) +
                                                              "/" + str(format_field(row.Ft)) + " Makes On" + '\n' +
                                                              str(format_field(row.Fga)) + "/" +
                                                              str(format_field(row.Fg2a)) + "/" +
                                                              str(format_field(row.Fg3a)) + "/" +
                                                              str(format_field(row.Fta))
                                                              + " Attempts")
            em.add_field(name="Rebounds", value=str(format_field(row.Rebounds)) + " (Offensive: " +
                                                str(format_field(row.OffRebound)) +
                                                ", Defensive: " + str(format_field(row.DefRebound)) + ")",
                                                inline=False)
            em.add_field(name="Assists", value=str(format_field(row.Assists)))
            em.add_field(name="Steals", value=str(format_field(row.Steals)))
            em.add_field(name="Blocks", value=str(format_field(row.Blocks)))
            em.add_field(name="Turnovers", value=str(format_field(row.Turnovers)))
            em.add_field(name="Fouls", value=str(format_field(row.Fouls)))
            em.add_field(name="Points/Opp Points", value=str(format_field(row.Points)) + " / " +
                                                         str(format_field(row.OppPoints)))
            em.set_footer(text="Data From Basketball Reference")
            await interaction.respond(embed=em, type=7)
        else:
            await interaction.respond(content="This isn't yor button!", type=4)

# t!roster ---------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def roster(ctx):

    def format_exp(exp):
        if exp.isnumeric():
            return str(exp) + " Years"
        else:
            return exp

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("Select TeamId, Player, JerseyNumber, Experience, Position from Roster where TeamId = ?", "atl")
    rows = cursor.fetchall()

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select TeamName, TeamLogo from Teams where AltTeamId = ?", "atl")
    rowc = cursor.fetchone()

    roster = ""

    for row in rows:
        roster += "**" + row.JerseyNumber + " | " + row.Player + "** | " + row.Position + " | " + \
                  format_exp(row.Experience) + '\n'

    em = discord.Embed(title=f"{rowc.TeamName} Roster",color=discord.Color.red())
    em.set_thumbnail(url=rowc.TeamLogo)
    em.add_field(name="Jersey Number | Player | Position | Experience", value= roster)
    em.set_footer(text="Data From Basketball Reference")

    atl = "Atl_Ros_" + str(ctx.author.id)
    bos = "Bos_Ros_" + str(ctx.author.id)
    brk = "Brk_Ros_" + str(ctx.author.id)
    cho = "Cho_Ros_" + str(ctx.author.id)
    chi = "Chi_Ros_" + str(ctx.author.id)
    cle = "Cle_Ros_" + str(ctx.author.id)
    dal = "Dal_Ros_" + str(ctx.author.id)
    den = "Den_Ros_" + str(ctx.author.id)
    det = "Det_Ros_" + str(ctx.author.id)
    gsw = "Gsw_Ros_" + str(ctx.author.id)
    hou = "Hou_Ros_" + str(ctx.author.id)
    ind = "Ind_Ros_" + str(ctx.author.id)
    lac = "Lac_Ros_" + str(ctx.author.id)
    lal = "Lal_Ros_" + str(ctx.author.id)
    mem = "Mem_Ros_" + str(ctx.author.id)
    mia = "Mia_Ros_" + str(ctx.author.id)
    mil = "Mil_Ros_" + str(ctx.author.id)
    min = "Min_Ros_" + str(ctx.author.id)
    nop = "Nop_Ros_" + str(ctx.author.id)
    nyk = "Nyk_Ros_" + str(ctx.author.id)
    okc = "Okc_Ros_" + str(ctx.author.id)
    orl = "Orl_Ros_" + str(ctx.author.id)
    phi = "Phi_Ros_" + str(ctx.author.id)
    pho = "Pho_Ros_" + str(ctx.author.id)
    por = "Por_Ros_" + str(ctx.author.id)
    sac = "Sac_Ros_" + str(ctx.author.id)
    sas = "Sas_Ros_" + str(ctx.author.id)
    tor = "Tor_Ros_" + str(ctx.author.id)
    uta = "Uta_Ros_" + str(ctx.author.id)
    was = "Was_Ros_" + str(ctx.author.id)

    await ctx.send(
                embed=em,
                components = [[
                    Select(
                        placeholder = "Select A Team",
                        options = [
                            SelectOption(label="Atlanta Hawks", value= atl),
                            SelectOption(label="Boston Celtics", value= bos),
                            SelectOption(label="Brooklyn Nets", value= brk),
                            SelectOption(label="Charlotte Hornets", value= cho),
                            SelectOption(label="Chicago Bulls", value= chi),
                            SelectOption(label="Cleveland Cavaliers", value= cle),
                            SelectOption(label="Dallas Mavericks", value= dal),
                            SelectOption(label="Denver Nuggets", value= den),
                            SelectOption(label="Detroit Pistons", value= det),
                            SelectOption(label="Golden State Warriors", value= gsw),
                            SelectOption(label="Houston Rockets", value= hou),
                            SelectOption(label="Indiana Pacers", value= ind),
                            SelectOption(label="Los Angeles Clippers", value= lac),
                            SelectOption(label="Los Angeles Lakers", value= lal),
                            SelectOption(label="Memphis Grizzlies", value= mem)
                        ]
                    )
                ],
                [
                    Select(
                        placeholder="Select A Team",
                        options=[
                            SelectOption(label="Miami Heat", value= mia),
                            SelectOption(label="Milwaukee Bucks", value= mil),
                            SelectOption(label="Minnesota Timberwolves", value= min),
                            SelectOption(label="New Orleans Pelicans", value= nop),
                            SelectOption(label="New York Knicks", value= nyk),
                            SelectOption(label="Oklahoma City Thunder", value= okc),
                            SelectOption(label="Orlando Magic", value= orl),
                            SelectOption(label="Philadelphia 76ers", value= phi),
                            SelectOption(label="Phoenix Suns", value= pho),
                            SelectOption(label="Portland Trail Blazers", value= por),
                            SelectOption(label="Sacramento Kings", value= sac),
                            SelectOption(label="San Antonio Spurs", value= sas),
                            SelectOption(label="Toronto Raptors", value= tor),
                            SelectOption(label="Utah Jazz", value= uta),
                            SelectOption(label="Washington Wizards", value= was)
                        ]
                    )
                ]
                ],
            )

    while True:
        interaction = await client.wait_for("select_option", check=lambda i: i.values[0].find("Ros") >= 0)
        author_id = interaction.values[0].split('_')[2]

        if author_id == str(interaction.author.id):
            cnxn = pyodbc.connect(sql_connection)

            cursor = cnxn.cursor()
            cursor.execute("Select TeamId, Player, JerseyNumber, Experience, Position from Roster where TeamId = ?",
                           interaction.values[0].split('_')[0])
            rows = cursor.fetchall()

            cnxn = pyodbc.connect(sql_connection)

            cursor = cnxn.cursor()
            cursor.execute("select TeamName, TeamLogo from Teams where AltTeamId = ?",
                           interaction.values[0].split('_')[0])
            rowc = cursor.fetchone()

            roster = ""

            for row in rows:
                roster += "**" + row.JerseyNumber + " | " + row.Player + "** | " + row.Position + " | " + \
                          format_exp(row.Experience) + '\n'

            em = discord.Embed(title=f"{rowc.TeamName} Roster", color=discord.Color.red())
            em.set_thumbnail(url=rowc.TeamLogo)
            em.add_field(name="Jersey Number | Player | Position | Experience", value=roster)
            em.set_footer(text="Data From Basketball Reference")
            await interaction.respond(embed=em, type=7)
        else:
            await interaction.respond(content="This isn't yor button!", type=4)

# t!injuries ---------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def injuries(ctx):

    def format_inj(inj):
        if inj is None:
            return "There are no injuries for this team"
        else:
            return inj

    def format_date(inj):
        if inj is None:
            return "** **"
        else:
            return "**Date: **" + inj

    def format_desc(inj):
        if inj is None:
            return "** **"
        else:
            return inj

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("Select Player, Team, Description, Date, TeamId from Injuries where TeamId = ?", "atl")
    rows = cursor.fetchall()

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select TeamName, TeamLogo from Teams where AltTeamId = ?", "atl")
    rowc = cursor.fetchone()

    em = discord.Embed(title=f"{rowc.TeamName} I    njuries", color=discord.Color.red())
    em.set_thumbnail(url=rowc.TeamLogo)

    for row in rows:
        em.add_field(name=format_inj(row.Player),
                     value=format_date(row.Date) + '\n' + format_desc(row.Description), inline=False)

    em.set_footer(text="Data From Basketball Reference")

    atl = "Atl_Inj_" + str(ctx.author.id)
    bos = "Bos_Inj_" + str(ctx.author.id)
    brk = "Brk_Inj_" + str(ctx.author.id)
    cho = "Cho_Inj_" + str(ctx.author.id)
    chi = "Chi_Inj_" + str(ctx.author.id)
    cle = "Cle_Inj_" + str(ctx.author.id)
    dal = "Dal_Inj_" + str(ctx.author.id)
    den = "Den_Inj_" + str(ctx.author.id)
    det = "Det_Inj_" + str(ctx.author.id)
    gsw = "Gsw_Inj_" + str(ctx.author.id)
    hou = "Hou_Inj_" + str(ctx.author.id)
    ind = "Ind_Inj_" + str(ctx.author.id)
    lac = "Lac_Inj_" + str(ctx.author.id)
    lal = "Lal_Inj_" + str(ctx.author.id)
    mem = "Mem_Inj_" + str(ctx.author.id)
    mia = "Mia_Inj_" + str(ctx.author.id)
    mil = "Mil_Inj_" + str(ctx.author.id)
    min = "Min_Inj_" + str(ctx.author.id)
    nop = "Nop_Inj_" + str(ctx.author.id)
    nyk = "Nyk_Inj_" + str(ctx.author.id)
    okc = "Okc_Inj_" + str(ctx.author.id)
    orl = "Orl_Inj_" + str(ctx.author.id)
    phi = "Phi_Inj_" + str(ctx.author.id)
    pho = "Pho_Inj_" + str(ctx.author.id)
    por = "Por_Inj_" + str(ctx.author.id)
    sac = "Sac_Inj_" + str(ctx.author.id)
    sas = "Sas_Inj_" + str(ctx.author.id)
    tor = "Tor_Inj_" + str(ctx.author.id)
    uta = "Uta_Inj_" + str(ctx.author.id)
    was = "Was_Inj_" + str(ctx.author.id)

    await ctx.send(
                embed=em,
                components = [[
                    Select(
                        placeholder = "Select A Team",
                        options = [
                            SelectOption(label="Atlanta Hawks", value= atl),
                            SelectOption(label="Boston Celtics", value= bos),
                            SelectOption(label="Brooklyn Nets", value= brk),
                            SelectOption(label="Charlotte Hornets", value= cho),
                            SelectOption(label="Chicago Bulls", value= chi),
                            SelectOption(label="Cleveland Cavaliers", value= cle),
                            SelectOption(label="Dallas Mavericks", value= dal),
                            SelectOption(label="Denver Nuggets", value= den),
                            SelectOption(label="Detroit Pistons", value= det),
                            SelectOption(label="Golden State Warriors", value= gsw),
                            SelectOption(label="Houston Rockets", value= hou),
                            SelectOption(label="Indiana Pacers", value= ind),
                            SelectOption(label="Los Angeles Clippers", value= lac),
                            SelectOption(label="Los Angeles Lakers", value= lal),
                            SelectOption(label="Memphis Grizzlies", value= mem)
                        ]
                    )
                ],
                [
                    Select(
                        placeholder="Select A Team",
                        options=[
                            SelectOption(label="Miami Heat", value= mia),
                            SelectOption(label="Milwaukee Bucks", value= mil),
                            SelectOption(label="Minnesota Timberwolves", value= min),
                            SelectOption(label="New Orleans Pelicans", value= nop),
                            SelectOption(label="New York Knicks", value= nyk),
                            SelectOption(label="Oklahoma City Thunder", value= okc),
                            SelectOption(label="Orlando Magic", value= orl),
                            SelectOption(label="Philadelphia 76ers", value= phi),
                            SelectOption(label="Phoenix Suns", value= pho),
                            SelectOption(label="Portland Trail Blazers", value= por),
                            SelectOption(label="Sacramento Kings", value= sac),
                            SelectOption(label="San Antonio Spurs", value= sas),
                            SelectOption(label="Toronto Raptors", value= tor),
                            SelectOption(label="Utah Jazz", value= uta),
                            SelectOption(label="Washington Wizards", value= was)
                        ]
                    )
                ]
                ],
            )

    while True:
        interaction = await client.wait_for("select_option", check=lambda i: i.values[0].find("Inj") >= 0)
        author_id = interaction.values[0].split('_')[2]

        if author_id == str(interaction.author.id):
            cnxn = pyodbc.connect(sql_connection)

            cursor = cnxn.cursor()
            cursor.execute("Select Player, Team, Description, Date, TeamId from Injuries where TeamId = ?",
                           interaction.values[0].split('_')[0])
            rows = cursor.fetchall()

            cnxn = pyodbc.connect(sql_connection)

            cursor = cnxn.cursor()
            cursor.execute("select TeamName, TeamLogo from Teams where AltTeamId = ?",
                           interaction.values[0].split('_')[0])
            rowc = cursor.fetchone()

            em = discord.Embed(title=f"{rowc.TeamName} Injuries", color=discord.Color.red())
            em.set_thumbnail(url=rowc.TeamLogo)

            for row in rows:
                em.add_field(name=format_inj(row.Player),
                             value=format_date(row.Date) + '\n' + format_desc(row.Description), inline=False)

            em.set_footer(text="Data From Basketball Reference")
            await interaction.respond(embed=em, type=7)
        else:
            await interaction.respond(content="This isn't yor button!", type=4)

# ----------------------------------------------------------------------------------------------------------------------
@client.command()
async def ping(ctx):
    await ctx.send(f"**Swish!**" + '\n'
        + f"You got the shot off with just **{round(client.latency * 1000)}ms** left on the clock!")

client.run(hidden)
