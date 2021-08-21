import pyodbc
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
sql_connection = 'DRIVER={SQL Server Native Client 11.0};SERVER=localhost;DATABASE=BotTester;UID=sa;PWD=wa11paper'

# ----------------------------------------------------------------------------------------------------------------------
# def east_odds():
#     def get_east_odds(row, attributeValue):
#         data = row.find("td", attrs={"data-stat": attributeValue})
#         if data.get_text() != '':
#             return data.get_text()
#         else:
#             return None
#
#     url = 'https://www.basketball-reference.com/friv/playoff_prob.html'
#     page = requests.get(url)
#     soup = BeautifulSoup(page.content, 'html.parser')
#     # print(soup)
#     table = soup.find(id="projected_standings_e")
#     # print(table)
#
#     # print(table)
#
#     cnxn = pyodbc.connect(sql_connection)
#
#     cursor = cnxn.cursor()
#
#     rows = table.find_all("tr")
#     for row in rows:
#         if row.th is not None and row.th["data-stat"] == "ranker" and row.th["scope"] == "row":
#             team_name = row.td.a.get_text()
#             seed = row.th.get_text()
#             playoff = get_east_odds(row, "prob_playoffs")
#             final = get_east_odds(row, "prob_win_finals")
#             wins = get_east_odds(row, "wins_avg")
#             losses = get_east_odds(row, "losses_avg")
#             print(seed, team_name, playoff, final, wins, losses)
#
#
#             cursor.execute("insert into PlayoffOdds (Team, PlayoffPercent, WinFinal,"
#                            " ProjWin, ProjLoss, Conference, Seed) values(?, ?, ?, ?, ?, ?, ?)",
#                            team_name, playoff, final, wins, losses, 0, seed)
#
#     cursor.commit()
#
# east_odds()
#
# def west_odds():
#     def get_west_odds(row, attributeValue):
#         data = row.find("td", attrs={"data-stat": attributeValue})
#         if data.get_text() != '':
#             return data.get_text()
#         else:
#             return None
#
#     url = 'https://www.basketball-reference.com/friv/playoff_prob.html'
#     page = requests.get(url)
#     soup = BeautifulSoup(page.content, 'html.parser')
#     # print(soup)
#     table = soup.find(id="projected_standings_w")
#     # print(table)
#
#
#     cnxn = pyodbc.connect(sql_connection)
#
#     cursor = cnxn.cursor()
#
#     rows = table.find_all("tr")
#     for row in rows:
#         if row.th is not None and row.th["data-stat"] == "ranker" and row.th["scope"] == "row":
#             team_name = row.td.a.get_text()
#             seed = row.th.get_text()
#             playoff = get_west_odds(row, "prob_playoffs")
#             final = get_west_odds(row, "prob_win_finals")
#             wins = get_west_odds(row, "wins_avg")
#             losses = get_west_odds(row, "losses_avg")
#             print(seed, team_name, playoff, final, wins, losses)
#
#
#             cursor.execute("insert into PlayoffOdds (Team, PlayoffPercent, WinFinal,"
#                            " ProjWin, ProjLoss, Conference, Seed) values(?, ?, ?, ?, ?, ?, ?,)",
#                            team_name, playoff, final, wins, losses, 1, seed)
#
#     cursor.commit()
#
# west_odds()

