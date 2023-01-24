import requests
import configparser
import csv

# Queries blaseball's api for the list of games in the current season
def getCurrentGamesList():
    config = configparser.ConfigParser()
    config.read("config.ini")

    login_uri = "https://api2.blaseball.com//auth/sign-in"
    login_payload = {"email": config["login"]["email"], "password": config["login"]["password"]}
    bb_session = requests.Session()
    bb_session.post(login_uri, login_payload)
    sim_uri = "https://api2.blaseball.com/sim"
    sim_response = bb_session.get(sim_uri)
    season_num = sim_response.json()["simData"]["currentSeasonNumber"]
    season_id = sim_response.json()["simData"]["currentSeasonId"]

    seasonDict = dict()
    with open('seasons.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            seasonDict[int(row[0])] = row[1]
    if season_num not in seasonDict:
        with open('season.csv', 'a') as file:
            file.write(f"\n{season_num},{season_id}")
    games_uri = "https://api2.blaseball.com/seasons/" + season_id + "/games"
    return bb_session.get(games_uri).json()

# Very helpful mirror of games api when it happens to be down
def getCurrentGamesListMirror():
    games_uri = "https://api2.sibr.dev/mirror/games"
    return requests.get(games_uri).json()

# Queries chronicler's api for the list of games in the specified season
def getGamesList(seasonNumber):
    seasonDict = dict()
    with open('seasons.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            seasonDict[int(row[0])] = row[1]
    if seasonNumber - 1 in seasonDict:
        season_id = seasonDict[seasonNumber - 1]
        games_uri = "https://api2.sibr.dev/chronicler/v0/entities?kind=game"
        total_game_list = requests.get(games_uri).json()["items"]
        return [x["data"] for x in total_game_list if (x["data"]["seasonId"] == season_id)]
    else:
        raise ValueError('An invalid season number was entered.')

# Creates alphabetical list of team names from list of games
def createNameList(gamesList, nameField):
    nameList = []
    for x in gamesList:
        if x["complete"]:
            if x["awayTeam"][nameField] not in nameList:
                nameList.append(x["awayTeam"][nameField])
            if x["homeTeam"][nameField] not in nameList:
                nameList.append(x["homeTeam"][nameField])
    nameList.sort()
    return nameList

# Prints out a header for displaying when the games took place
def printDayHeader(gamesList, validGames):
    lastDay = -1
    for x in validGames:
        if x["day"] > lastDay:
            lastDay = x["day"]
    foundOngoingGame = False
    for x in gamesList:
        if x["day"] <= lastDay and x["started"] and not x["complete"]:
            lastDay = x["day"]
            foundOngoingGame = True
            break
    print("%s of day %d\n" % ("In the midst" if foundOngoingGame else "At the end", lastDay + 1))
