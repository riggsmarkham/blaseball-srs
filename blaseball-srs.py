import requests
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

login_uri = "https://api2.blaseball.com//auth/sign-in"
login_payload = {"email": config["login"]["email"], "password": config["login"]["password"]}
bb_session = requests.Session()
bb_session.post(login_uri, login_payload)

sim_uri = "https://api2.blaseball.com/sim"
sim_response = bb_session.get(sim_uri)
season_id = sim_response.json()["simData"]["currentSeasonId"]
games_uri = "https://api2.blaseball.com/seasons/" + season_id + "/games"
games_response = bb_session.get(games_uri)

completedGames = [x for x in games_response.json() if x["complete"]]

completeGameIdDict = dict()
for x in completedGames:
    completeGameIdDict[x["id"]] = x

scoreDict = dict()
for x in completedGames:
    awayTeam = x["awayTeam"]["shorthand"]
    if awayTeam not in scoreDict.keys():
        scoreDict[awayTeam] = [1, x["gameStates"][0]["awayScore"], x["gameStates"][0]["homeScore"]]
    else:
        scoreDict[awayTeam][0] += 1
        scoreDict[awayTeam][1] += x["gameStates"][0]["awayScore"]
        scoreDict[awayTeam][2] += x["gameStates"][0]["homeScore"]

    homeTeam = x["homeTeam"]["shorthand"]
    if homeTeam not in scoreDict.keys():
        scoreDict[homeTeam] = [1, x["gameStates"][0]["homeScore"], x["gameStates"][0]["awayScore"]]
    else:
        scoreDict[homeTeam][0] += 1
        scoreDict[homeTeam][1] += x["gameStates"][0]["homeScore"]
        scoreDict[homeTeam][2] += x["gameStates"][0]["awayScore"]

highestScore = 0
highScoreIds = []
for x in completedGames:
    topScore = max(x["gameStates"][0]["awayScore"], x["gameStates"][0]["homeScore"])
    if topScore > highestScore:
        highScoreIds = [x["id"]]
        highestScore = topScore
    elif topScore == highestScore:
        highScoreIds.append(x["id"])

highestTotalScore = 0
highestTotalScoreIds = []
for x in completedGames:
    totalScore = x["gameStates"][0]["awayScore"] + x["gameStates"][0]["homeScore"]
    if totalScore > highestTotalScore:
        highestTotalScoreIds = [x["id"]]
        highestTotalScore = totalScore
    elif totalScore == highestTotalScore:
        highestTotalScoreIds.append(x["id"])

def printGame(game):
    print("Day %d, %s @ %s, %d-%d" % (game["day"] + 1, game["awayTeam"]["shorthand"], game["homeTeam"]
          ["shorthand"], game["gameStates"][0]["awayScore"], game["gameStates"][0]["homeScore"]))

print("Teams by run differential per game:")
temp_list = [[x, (scoreDict[x][1] - scoreDict[x][2])/scoreDict[x][0]] for x in scoreDict.keys()]
temp_list.sort(key=lambda x: x[1], reverse=True)
for x in temp_list:
    print("%-4s%6.2f" % (x[0], x[1]))
print()

print("Games with highest single-team score:")
for x in highScoreIds:
    printGame(completeGameIdDict[x])
print()

print("Games with highest total score:")
for x in highestTotalScoreIds:
    printGame(completeGameIdDict[x])
