import requests
import configparser

def getGamesList():
    config = configparser.ConfigParser()
    config.read("config.ini")

    login_uri = "https://api2.blaseball.com//auth/sign-in"
    login_payload = {"email": config["login"]["email"], "password": config["login"]["password"]}
    bb_session = requests.Session()
    bb_session.post(login_uri, login_payload)

    sim_uri = "https://api2.blaseball.com/sim"
    sim_response = bb_session.get(sim_uri)
    season_id = sim_response.json()["simData"]["currentSeasonId"]
    print(season_id)
    games_uri = "https://api2.blaseball.com/seasons/" + season_id + "/games"
    return bb_session.get(games_uri).json()

def getGamesListMirror():
    games_uri = "https://api2.sibr.dev/mirror/games"
    return requests.get(games_uri).json()

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

def printDayHeader(gamesList):
    lastDay = 0
    foundOngoingGame = False
    for x in gamesList:
        if x["complete"]:
            if x["day"] > lastDay:
                lastDay = x["day"]
        elif x["started"]:
            lastDay = x["day"]
            foundOngoingGame = True
            break
    print("%s of day %d\n" % ("In the midst" if foundOngoingGame else "At the end", lastDay + 1))
