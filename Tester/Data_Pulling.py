import pyodbc
import requests
from bs4 import BeautifulSoup
sql_connection = 'DRIVER={SQL Server Native Client 11.0};SERVER=localhost;DATABASE=BotTester;UID=sa;PWD=wa11paper'

def getfromtable(table, playoffs, player_id):
    def getstat(row, tag):
        data = row.find(attrs={"data-stat": tag})
        if data is not None:
            return data.get_text()
        else:
            return None

    rows = table.find_all("tr")
    for row in rows:
        if (row.th != None and row.th['data-stat'] == 'season' and row.th['scope'] == 'row' and row.th.get_text()!= ""):
            # print(row)
            season = row.th.get_text()
            age = getstat(row, "age")
            team_id = getstat(row, "team_id")
            pos = getstat(row, "pos")
            g = getstat(row, "g")
            gs = getstat(row, "gs")
            mp_per_g = getstat(row, "mp_per_g")
            fg_per_g = getstat(row, "fg_per_g")
            fga_per_g = getstat(row, "fga_per_g")
            fg_pct = getstat(row, "fg_pct")
            fg3_per_g = getstat(row, "fg3_per_g")
            fg3a_per_g = getstat(row, "fg3a_per_g")
            fg3_pct = getstat(row, "fg3_pct")
            fg2_per_g = getstat(row, "fg2_per_g")
            fg2a_per_g = getstat(row, "fg2a_per_g")
            fg2_pct = getstat(row, "fg2_pct")
            efg_pct = getstat(row, "efg_pct")
            ft_per_g = getstat(row, "ft_per_g")
            fta_per_g = getstat(row, "fta_per_g")
            ft_pct = getstat(row, "ft_pct")
            orb_per_g = getstat(row, "orb_per_g")
            drb_per_g = getstat(row, "drb_per_g")
            trb_per_g = getstat(row, "trb_per_g")
            ast_per_g = getstat(row, "ast_per_g")
            stl_per_g = getstat(row, "stl_per_g")
            blk_per_g = getstat(row, "blk_per_g")
            tov_per_g = getstat(row, "tov_per_g")
            pf_per_g = getstat(row, "pf_per_g")
            pts_per_g = getstat(row, "pts_per_g")

            # print(season, age, team_id, pos, g, gs, mp_per_g, fg_per_g, fga_per_g, fg_pct, fg3_per_g, fg3a_per_g,
            #       fg3_pct, fg2_per_g, fg2a_per_g, fg2_pct, efg_pct, ft_per_g, fta_per_g, ft_pct, orb_per_g, drb_per_g,
            #       trb_per_g, ast_per_g, stl_per_g, blk_per_g, tov_per_g, pf_per_g, pts_per_g)

            cursor.execute("insert into PlayerStats (PlayerId, Playoffs, Season, Age, Team, Position, GamesPlayed,"
                           " GamesStarted, MinPerGame, FgPerGame, FgaPerGame, FgPercent, Fg3PerGame, Fg3aPerGame, "
                           "Fg3Percent, Fg2PerGame, Fg2aPerGame, Fg2Percent, EfgPercent, FtPerGame, FtaPerGame, "
                           "FtPercent, OffRebound, DefRebound, Rebounds, Assists, Steals, Blocks, Turnovers, Fouls, "
                           "Points) "
                           "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,"
                           " ?, ?, ?)",
                           player_id, playoffs, season, age, team_id, pos, g, gs, mp_per_g, fg_per_g,
                           fga_per_g, fg_pct, fg3_per_g, fg3a_per_g, fg3_pct, fg2_per_g, fg2a_per_g, fg2_pct, efg_pct,
                           ft_per_g, fta_per_g, ft_pct, orb_per_g, drb_per_g, trb_per_g, ast_per_g, stl_per_g,
                           blk_per_g, tov_per_g, pf_per_g, pts_per_g)

    cursor.commit()

def scrape_data(player_id, link):

    url = 'https://www.basketball-reference.com' + link
    print(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find(id="per_game")
    getfromtable(table, 0, player_id)

    table = soup.find(id="playoffs_per_game")

    if table == None:
        return

    getfromtable(table, 1, player_id)

cnxn = pyodbc.connect(sql_connection)

cursor = cnxn.cursor()

# cursor.execute("select top 2 PlayerId, Link from Players where playerid = 'architi01'")
cursor.execute("select PlayerId, Link from Players")
rows = cursor.fetchall()
for row in rows:
    print(row.PlayerId)
    scrape_data(row.PlayerId, row.Link)