import discord
from discord.ext import commands
import pyodbc
from datetime import datetime

sql_connection = 'DRIVER={SQL Server Native Client 11.0};SERVER=localhost;DATABASE=BotTester;UID=sa;PWD=wa11paper'

client = commands.Bot(command_prefix = "t!")

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('t!help'))
    print("We have logged in as {0.user}".format(client))

# t!search -------------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def search(ctx, *, player = ""):

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    sql = "select Name from Players where FinalYear = 2021 and " \
          "(Name like '" + player + "%' or Name like '% " + player + "' or Name like '% " + player +\
          " %') order by Name"
    cursor.execute(sql)
    rows = cursor.fetchall()

    info = ""

    if cursor.rowcount == 0:
        info = "There are no active players with the name " + player
    else:
        for row in rows:
             info += '\n' + row.Name

    em = discord.Embed(color=discord.Color.red())
    em.add_field(name="All active NBA players with the name `" + player.capitalize() + "`:", value = info, inline=False)
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
        await ctx.send(embed = em)

# t!playerinfo ---------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def playerinfo(ctx, *, player = ""):

    def format_class(draft):
        if draft is None:
            return first_year
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
                   "Age = DATEDIFF(year, birthday, getdate()), DraftTeam, DraftPick, DraftYear from Players "
                   "where Name = ? order by FinalYear desc", player)
    rows = cursor.fetchall()


    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=player.capitalize() + "'s Info",
                     value="There are no players with the name: `" + player.capitalize() + "`",
                     inline=False)
        await ctx.send(embed=em)
    else:
        for row in rows:
            first_year = row.FirstYear
            final_year = row.FinalYear
            country = row.Country
            college = row.College
            height = row.Height
            weight = row.Weight
            jersey_number = row.JerseyNumber
            birthday = row.Birthday
            age = row.Age
            draft_team = row.DraftTeam
            draft_pick = row.DraftPick
            draft_year = row.DraftYear
            image = row.Image
            em = discord.Embed(title=player.capitalize() + " Info", color=discord.Color.red())
            if image is None:
                pass
            else:
                em.set_thumbnail(url=image)
            em.add_field(name="Birthday", value=format_field(birthday))
            em.add_field(name="Age", value=format_field(age))
            em.add_field(name="Seasons Played", value= str(format_field(final_year - first_year)) + " seasons; "
                                                       + format_field(active(final_year)))
            em.add_field(name="Draft", value="**Draft Class:** " + str(format_class(draft_year)) + '\n'
                                            + "**Pick:** " + str(format_draft(draft_pick)) + '\n'
                                            + "**Team:** " + str(format_draft(draft_team)))
            em.add_field(name="College", value=format_field(college))
            em.add_field(name="Birth Place", value=format_field(country))
            em.add_field(name="Height", value=format_field(height))
            em.add_field(name="Weight", value=str(format_field(weight)) + " lb")
            em.add_field(name="Jersey Number", value=format_field(jersey_number))
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
            return "0"
        else:
            return field

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
        em.add_field(name=player.capitalize() + "Stats",
                     value="There are no players with the name: `" + player.capitalize() + ":(`",
                     inline=False)
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.capitalize() + "Stats (" + row.Team + ") " + str(row.Age) + " y/o "
                                 + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Games Started/Played", value=str(row.GamesStarted) + " of " + str(row.GamesPlayed) + " | "
                                                + str(rowc.GamesStarted) + " of " + str(rowc.GamesPlayed))
        em.add_field(name="Minutes Per Game", value=str(row.MinPerGame) + " | " + str(rowc.MinPerGame))
        em.add_field(name="Fg%/2Pt%/3Pt%/Ft%", value="__" + str(format_field('{:.1f}'.format(row.FgPercent * 100))) +
                                            "/" + str(format_field('{:.1f}'.format(row.Fg2Percent * 100))) + "/" +
                                            str(format_field('{:.1f}'.format(row.Fg3Percent * 100))) + "/" +
                                            str(format_field('{:.1f}'.format(row.FtPercent * 100))) + "__" + '\n' +
                                            str(format_field('{:.1f}'.format(rowc.FgPercent * 100))) + "/" +
                                            str(format_field('{:.1f}'.format(rowc.Fg2Percent * 100))) + "/" +
                                            str(format_field('{:.1f}'.format(rowc.Fg3Percent * 100))) + "/" +
                                            str(format_field('{:.1f}'.format(rowc.FtPercent * 100))))
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
        em.add_field(name="Points Per Game", value=(str(row.Points) + " | " + str(rowc.Points)))
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
            return "0"
        else:
            return field

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
        em.add_field(name=player.capitalize() + "Stats",
                     value="There are no players with the name: `" + player.capitalize() + "`",
                     inline=False)
        em.set_footer(text="Or they've never been to the playoffs")
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.capitalize() + "Stats (" + row.Team + ") " + str(row.Age) + " y/o "
                                 + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Games Started/Played", value=str(row.GamesStarted) + " of " + str(row.GamesPlayed) + " | "
                                                + str(rowc.GamesStarted) + " of " + str(rowc.GamesPlayed))
        em.add_field(name="Minutes Per Game", value=str(row.MinPerGame) + " | " + str(rowc.MinPerGame))
        em.add_field(name="Fg%/2Pt%/3Pt%/Ft%", value="__" + str(format_field('{:.1f}'.format(row.FgPercent * 100))) +
                                            "/" + str(format_field('{:.1f}'.format(row.Fg2Percent * 100))) + "/" +
                                            str(format_field('{:.1f}'.format(row.Fg3Percent * 100))) + "/" +
                                            str(format_field('{:.1f}'.format(row.FtPercent * 100))) + "__" + '\n' +
                                            str(format_field('{:.1f}'.format(rowc.FgPercent * 100))) + "/" +
                                            str(format_field('{:.1f}'.format(rowc.Fg2Percent * 100))) + "/" +
                                            str(format_field('{:.1f}'.format(rowc.Fg3Percent * 100))) + "/" +
                                            str(format_field('{:.1f}'.format(rowc.FtPercent * 100))))
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
        em.add_field(name="Points Per Game", value=(str(row.Points) + " | " + str(rowc.Points)))
        await ctx.send(embed = em)

# t!teams --------------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def teams(ctx):
    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    sql = "select TeamName, Division, Conference, AltTeamId from Teams order by AltTeamId"
    cursor.execute(sql)
    rows = cursor.fetchall()

    teams = ""

    for row in rows:
        teams += "**" + row.AltTeamId + "** | " + row.TeamName + '\n'

    em = discord.Embed(title= "All Nba Teams",color=discord.Color.red())
    em.add_field(name="Team Id | Team", value=teams)
    await ctx.send(embed=em)

# t!teamsalary ---------------------------------------------------------------------------------------------------------
@client.command()
@commands.cooldown(1,3,commands.BucketType.user)
async def teamsalary(ctx, team):

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
                   "TeamId = ? order by ts.Salary1 desc", team)
    rows = cursor.fetchall()

    cnxn = pyodbc.connect(sql_connection)

    cursor = cnxn.cursor()
    cursor.execute("select TeamName from Teams where AltTeamId = ?", team)
    rowc = cursor.fetchone()

    salaries = ""
    team_1 = 0
    team_2 = 0
    team_3 = 0
    team_4 = 0
    team_5 = 0
    team_6 = 0

    if cursor.rowcount == 0:
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name="You may have put in the wrong team id", value=f"`{team}` is not a valid team id")
        await ctx.send(embed=em)
    else:
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
        await ctx.send(embed=em)

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
            return "0"
        else:
            return field

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
        em.add_field(name=player.capitalize() + "Totals",
                     value="There are no players with the name: `" + player.capitalize() + ":(`",
                     inline=False)
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.capitalize() + "Totals (" + row.Team + ") " + str(row.Age) + " y/o "
                                 + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Games Started/Played", value=str(row.GamesStarted) + " of " + str(row.GamesPlayed) + " | " +
                                                        str('{:,}'.format(rowc.GamesStarted)) + " of " +
                                                        str('{:,}'.format(rowc.GamesPlayed)))
        em.add_field(name="Minutes Played", value=str('{:,}'.format(row.MinutesPlayed)) + " | " +
                                                  str('{:,}'.format(rowc.MinutesPlayed)))
        em.add_field(name="Fg/2Pt/3Pt/Ft Shooting", value=str('{:,}'.format(format_field(row.FgMade))) + "/" +
                                            str('{:,}'.format(format_field(row.Fg2Made))) + "/" +
                                            str('{:,}'.format(format_field(row.Fg3Made))) +
                                            "/" + str('{:,}'.format(format_field(row.FtMade))) + " Makes On" + '\n' +
                                            "__" + str('{:,}'.format(format_field(row.FgAttempts))) + "/" +
                                            str('{:,}'.format(format_field(row.Fg2Attempts))) + "/" +
                                            str('{:,}'.format(format_field(row.Fg3Attempts))) + "/" +
                                            str('{:,}'.format(format_field(row.FtAttempts)))
                                            + " Attempts__" + '\n' + str('{:,}'.format(format_field(rowc.FgMade))) +
                                            "/" + str('{:,}'.format(format_field(rowc.Fg2Made))) + "/" +
                                            str('{:,}'.format(format_field(rowc.Fg3Made))) + "/" +
                                            str('{:,}'.format(format_field(rowc.FtMade))) +
                                            " Makes On" + '\n' + str('{:,}'.format(format_field(rowc.FgAttempts))) +
                                            "/" + str('{:,}'.format(format_field(rowc.Fg2Attempts))) + "/" +
                                            str('{:,}'.format(format_field(rowc.Fg3Attempts))) + "/" +
                                            str('{:,}'.format(format_field(rowc.FtAttempts))) + " Attempts",
                                            inline=False)
        em.add_field(name="Rebounds", value="__" + str('{:,}'.format(row.Rebounds)) + " (Offensive: " +
                                            str('{:,}'.format(format_field(row.OffRebound))) +
                                            ", Defensive: " + str('{:,}'.format(format_field(row.DefRebound))) + ")__" +
                                            '\n' + str('{:,}'.format(format_field(rowc.Rebounds))) + " (Offensive: "
                                            + str('{:,}'.format(format_field(rowc.OffRebound))) +
                                            ", Defensive: " + str('{:,}'.format(format_field(rowc.DefRebound)))
                                            + ")", inline = False)
        em.add_field(name="Assists", value=str('{:,}'.format(format_field(row.Assists))) + " | " +
                                                    str('{:,}'.format(format_field(rowc.Assists))))
        em.add_field(name="Steals", value=str('{:,}'.format(format_field(row.Steals))) + " | " +
                                                   str('{:,}'.format(format_field(rowc.Steals))))
        em.add_field(name="Blocks", value=str('{:,}'.format(format_field(row.Blocks))) + " | " +
                                                   str('{:,}'.format(format_field(rowc.Blocks))))
        em.add_field(name="Turnovers", value=str('{:,}'.format(format_field(row.Turnovers))) + " | " +
                                                      str('{:,}'.format(format_field(rowc.Turnovers))))
        em.add_field(name="Fouls Per Game", value=str('{:,}'.format(format_field(row.Fouls))) + " | " +
                                                  str('{:,}'.format(format_field(rowc.Fouls))))
        em.add_field(name="Points", value=(str('{:,}'.format(row.Points)) + " | " +
                                                    str('{:,}'.format(rowc.Points))))
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
            return "0"
        else:
            return field

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
        em.add_field(name=player.capitalize() + "Totals",
                     value="There are no players with the name: `" + player.capitalize() + "`",
                     inline=False)
        em.set_footer(text="Or they've never been to the playoffs")
        await ctx.send(embed=em)
    else:
        em = discord.Embed(title=player.capitalize() + "Totals (" + row.Team + ") " + str(row.Age) + " y/o "
                                 + row.Position, color=discord.Color.red())
        if row.Image is None:
            pass
        else:
            em.set_thumbnail(url=row.Image)
        em.add_field(name="Year | Career", value=str(row.Season) + " | Career")
        em.add_field(name="Games Started/Played", value=str(row.GamesStarted) + " of " + str(row.GamesPlayed) + " | " +
                                                        str('{:,}'.format(rowc.GamesStarted)) + " of " +
                                                        str('{:,}'.format(rowc.GamesPlayed)))
        em.add_field(name="Minutes Played", value=str('{:,}'.format(row.MinutesPlayed)) + " | " +
                                                  str('{:,}'.format(rowc.MinutesPlayed)))
        em.add_field(name="Fg/2Pt/3Pt/Ft Shooting", value=str('{:,}'.format(format_field(row.FgMade))) + "/" +
                                            str('{:,}'.format(format_field(row.Fg2Made))) + "/" +
                                            str('{:,}'.format(format_field(row.Fg3Made))) +
                                            "/" + str('{:,}'.format(format_field(row.FtMade))) + " Makes On" + '\n' +
                                            "__" + str('{:,}'.format(format_field(row.FgAttempts))) + "/" +
                                            str('{:,}'.format(format_field(row.Fg2Attempts))) + "/" +
                                            str('{:,}'.format(format_field(row.Fg3Attempts))) + "/" +
                                            str('{:,}'.format(format_field(row.FtAttempts)))
                                            + " Attempts__" + '\n' + str('{:,}'.format(format_field(rowc.FgMade))) +
                                            "/" + str('{:,}'.format(format_field(rowc.Fg2Made))) + "/" +
                                            str('{:,}'.format(format_field(rowc.Fg3Made))) + "/" +
                                            str('{:,}'.format(format_field(rowc.FtMade))) +
                                            " Makes On" + '\n' + str('{:,}'.format(format_field(rowc.FgAttempts))) +
                                            "/" + str('{:,}'.format(format_field(rowc.Fg2Attempts))) + "/" +
                                            str('{:,}'.format(format_field(rowc.Fg3Attempts))) + "/" +
                                            str('{:,}'.format(format_field(rowc.FtAttempts))) + " Attempts",
                                            inline=False)
        em.add_field(name="Rebounds", value="__" + str('{:,}'.format(row.Rebounds)) + " (Offensive: " +
                                            str('{:,}'.format(format_field(row.OffRebound))) +
                                            ", Defensive: " + str('{:,}'.format(format_field(row.DefRebound))) + ")__" +
                                            '\n' + str('{:,}'.format(format_field(rowc.Rebounds))) + " (Offensive: "
                                            + str('{:,}'.format(format_field(rowc.OffRebound))) +
                                            ", Defensive: " + str('{:,}'.format(format_field(rowc.DefRebound)))
                                            + ")", inline = False)
        em.add_field(name="Assists", value=str('{:,}'.format(format_field(row.Assists))) + " | " +
                                                    str('{:,}'.format(format_field(rowc.Assists))))
        em.add_field(name="Steals", value=str('{:,}'.format(format_field(row.Steals))) + " | " +
                                                   str('{:,}'.format(format_field(rowc.Steals))))
        em.add_field(name="Blocks", value=str('{:,}'.format(format_field(row.Blocks))) + " | " +
                                                   str('{:,}'.format(format_field(rowc.Blocks))))
        em.add_field(name="Turnovers", value=str('{:,}'.format(format_field(row.Turnovers))) + " | " +
                                                      str('{:,}'.format(format_field(rowc.Turnovers))))
        em.add_field(name="Fouls Per Game", value=str('{:,}'.format(format_field(row.Fouls))) + " | " +
                                                  str('{:,}'.format(format_field(rowc.Fouls))))
        em.add_field(name="Points", value=(str('{:,}'.format(row.Points)) + " | " +
                                                    str('{:,}'.format(rowc.Points))))
        await ctx.send(embed = em)

# ----------------------------------------------------------------------------------------------------------------------
@client.command()
async def ping(ctx):
    await ctx.send(f"**Swish!**" + '\n'
        + f"You got the shot off with just **{round(client.latency * 1000)}ms** left on the clock!")

client.run('ODU5MTc4MTkwMjY1OTA5MjU5.YNo6Cw.gAIJFhxx9vWo-NLa-eksa5r_mAY')
