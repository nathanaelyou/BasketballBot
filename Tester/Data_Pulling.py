# import pyodbc
# import requests
# from bs4 import BeautifulSoup
# sql_connection = 'DRIVER={SQL Server Native Client 11.0};SERVER=localhost;DATABASE=BotTester;UID=sa;PWD=wa11paper'
#
# def getfromtotal(table, playoffs, player_id):
#     def getstat(row, tag):
#         data = row.find(attrs={"data-stat": tag})
#         if data is not None:
#             return data.get_text()
#         else:
#             return None
#
#     if table is None:
#         return
#     rows = table.find_all("tr")
#     for row in rows:
#         if (row.th != None and row.th['data-stat'] == 'season' and row.th['scope'] == 'row' and row.th.get_text()!= ""):
#             # print(row)
#
#             season = row.th.get_text()
#             age = getstat(row, "age")
#             team_id = getstat(row, "team_id")
#             pos = getstat(row, "pos")
#             games_played = getstat(row, "g")
#             games_started = getstat(row, "gs")
#             min_played = getstat(row, "mp")
#             fg = getstat(row, "fg")
#             fga = getstat(row, "fga")
#             fg3 = getstat(row, "fg3")
#             fg3a = getstat(row, "fg3a")
#             fg2 = getstat(row, "fg2")
#             fg2a = getstat(row, "fg2a")
#             ft = getstat(row, "ft")
#             fta = getstat(row, "fta")
#             off_reb = getstat(row, "orb")
#             def_reb = getstat(row, "drb")
#             rebounds = getstat(row, "trb")
#             assists = getstat(row, "ast")
#             steals = getstat(row, "stl")
#             blocks = getstat(row, "blk")
#             turnovers = getstat(row, "tov")
#             fouls = getstat(row, "pf")
#             points = getstat(row, "pts")
#
#             # print(season, age, team_id, pos, games_played, games_started, min_played, fg, fga, fg3,
#             #       fg3a, fg2, fg2a, ft, fta, off_reb, def_reb, rebounds, assists, steals,
#             #       blocks, turnovers, fouls, points)
#             cursor.execute("insert into TotalStats (PlayerId, Playoffs, Season, Age, Team, Position, GamesPlayed, "
#                             "GamesStarted, MinutesPlayed, FgMade, FgAttempts, Fg3Made, Fg3Attempts, Fg2Made, "
#                            "Fg2Attempts, FtMade, FtAttempts, OffRebound, DefRebound, Rebounds, Assists, Steals, "
#                            "Blocks, Turnovers, Fouls, Points) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,"
#                            " ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", player_id, playoffs, season, age, team_id, pos,
#                            games_played, games_started, min_played, fg, fga, fg3, fg3a, fg2, fg2a, ft, fta, off_reb,
#                            def_reb, rebounds, assists, steals, blocks, turnovers, fouls, points)
#
#     cursor.commit()
#
# def scrape_total(player_id, link):
#
#     url = 'https://www.basketball-reference.com' + link
#     print(url)
#     page = requests.get(url)
#     soup = BeautifulSoup(page.content, 'html.parser')
#     table = soup.find(id="totals")
#     getfromtotal(table, 0, player_id)
#
#     playoffs = soup.find(id="playoffs_totals")
#
#     if table == None:
#         return
#
#     getfromtotal(playoffs, 1, player_id)
#
# cnxn = pyodbc.connect(sql_connection)
#
# cursor = cnxn.cursor()
#
# # cursor.execute("select top 2 PlayerId, Link from Players where playerid = 'architi01'")
# cursor.execute("select PlayerId, Link from Players")
# rows = cursor.fetchall()
# for row in rows:
#     print(row.PlayerId)
#     scrape_total(row.PlayerId, row.Link)
#
