import requests
import configparser
import numpy as np
import numpy.linalg as linalg

def createGameIdDict(completedGames):
    gameIdDict = dict()
    for x in completedGames:
        gameIdDict[x["id"]] = x
    return gameIdDict

def createScoreDict(completedGames):
    scoreDict = dict()
    for x in completedGames:
        awayTeam = x["awayTeam"]["name"]
        if awayTeam not in scoreDict.keys():
            scoreDict[awayTeam] = [1, x["gameStates"][0]["awayScore"], x["gameStates"][0]["homeScore"]]
        else:
            scoreDict[awayTeam][0] += 1
            scoreDict[awayTeam][1] += x["gameStates"][0]["awayScore"]
            scoreDict[awayTeam][2] += x["gameStates"][0]["homeScore"]

        homeTeam = x["homeTeam"]["name"]
        if homeTeam not in scoreDict.keys():
            scoreDict[homeTeam] = [1, x["gameStates"][0]["homeScore"], x["gameStates"][0]["awayScore"]]
        else:
            scoreDict[homeTeam][0] += 1
            scoreDict[homeTeam][1] += x["gameStates"][0]["homeScore"]
            scoreDict[homeTeam][2] += x["gameStates"][0]["awayScore"]
    return scoreDict

def createNameList(completedGames):
    nameList = []
    for x in completedGames:
        if x["awayTeam"]["name"] not in nameList:
            nameList.append(x["awayTeam"]["name"])
        if x["homeTeam"]["name"] not in nameList:
            nameList.append(x["homeTeam"]["name"])
    nameList.sort()
    return nameList

def createMatchupMatrix(nameList, completedGames):
    n = len(nameList)
    matchupMatrix = np.zeros((n, n))
    for x in completedGames:
        awayIndex = nameList.index(x["awayTeam"]["name"])
        homeIndex = nameList.index(x["homeTeam"]["name"])
        matchupMatrix[awayIndex][homeIndex] += 1
        matchupMatrix[homeIndex][awayIndex] += 1
    for i in range(n):
        matchupMatrix[i] /= matchupMatrix[i].sum()
    for i in range(n):
        matchupMatrix[i][i] = -1
    return matchupMatrix

def getHighestIndividualScoringMatches(completedGames):
    highestScore = 0
    gameIds = []
    for x in completedGames:
        topScore = max(x["gameStates"][0]["awayScore"], x["gameStates"][0]["homeScore"])
        if topScore > highestScore:
            gameIds = [x["id"]]
            highestScore = topScore
        elif topScore == highestScore:
            gameIds.append(x["id"])
    return gameIds

def getHighestTotalScoringMatches(completedGames):
    highestScore = 0
    gameIds = []
    for x in completedGames:
        topScore = x["gameStates"][0]["awayScore"] + x["gameStates"][0]["homeScore"]
        if topScore > highestScore:
            gameIds = [x["id"]]
            highestScore = topScore
        elif topScore == highestScore:
            gameIds.append(x["id"])
    return gameIds

def getLastDay(completedGames):
    lastDay = 0
    for x in completedGames:
        if x["day"] > lastDay:
            lastDay = x["day"]
    return lastDay
    
def inMiddleOfDay(completedGames, numberOfTeams):
    return len(completedGames) % (numberOfTeams // 2) == 0

def printGame(game):
    print("Day %d, %s @ %s, %d-%d" % (game["day"] + 1, game["awayTeam"]["shorthand"], game["homeTeam"]
          ["shorthand"], game["gameStates"][0]["awayScore"], game["gameStates"][0]["homeScore"]))

def printDayHeader(completedGames, nameList, lastDay):
    if (inMiddleOfDay(completedGames, len(nameList))):
        print("In the midst of day %d" % (lastDay + 1))
    else:
        print("As of the end of day %d" % (lastDay + 1))
    print()

def printSimpleRatingSystem(scoreDict, nameList, matchupMatrix):
    n = len(nameList)
    scoreVector = np.asarray([(scoreDict[nameList[i]][1] - scoreDict[nameList[i]][2]) / scoreDict[nameList[i]][0] for i in range(n)]) * -1
    finalVector = linalg.solve(matchupMatrix, scoreVector)
    average_val = np.average(finalVector)
    tempList = [[nameList[i], finalVector[i] - average_val, (scoreDict[nameList[i]][1] - scoreDict[nameList[i]][2])/scoreDict[nameList[i]][0]] for i in range(n)]
    tempList.sort(key=lambda x: x[1], reverse=True)
    print("Simple Rating System")
    print("%-25s%7s%7s" % ("Team Name", "Rating", "SOS"))
    for x in tempList:
        print("%-25s%7.2f%7.2f" % (x[0], x[1], x[1] - x[2]))
    print()

def printRunDifferential(scoreDict):
    tempList = [[x, (scoreDict[x][1] - scoreDict[x][2])/scoreDict[x][0]] for x in scoreDict.keys()]
    tempList.sort(key=lambda x: x[1], reverse=True)
    print("Teams by run differential per game:")
    for x in tempList:
        print("%-25s%6.2f" % (x[0], x[1]))
    print()

def printHighestIndividualScoringMatches(gameIds, gameIdDict):
    print("Games with highest single-team score:")
    for x in gameIds:
        printGame(gameIdDict[x])
    print()

def printHighestTotalScoringMatches(gameIds, gameIdDict):
    print("Games with highest total score:")
    for x in gameIds:
        printGame(gameIdDict[x])
    print()

def printIterativeSRS(nameList, completedGames, scoreDict, iterations):
    n = len(nameList)
    matchupArr = [[0 for _ in range(n)] for _ in range(n)]
    for x in completedGames:
        awayIndex = nameList.index(x["awayTeam"]["name"])
        homeIndex = nameList.index(x["homeTeam"]["name"])
        matchupArr[awayIndex][homeIndex] += 1
        matchupArr[homeIndex][awayIndex] += 1

    teamRatings = [[(scoreDict[nameList[i]][1] - scoreDict[nameList[i]][2]) / scoreDict[nameList[i]][0] for i in range(n)]]

    print(f"Iterative SRS ({iterations} iterations)")
    for iteration in range(0, iterations):
        teamRatings.append([])
        for i in range(n):
            sum_games = 0
            average_sum = 0
            for j in range(n):
                num_games_opponent = matchupArr[i][j]
                if num_games_opponent != 0 and j != i:
                    sum_games += num_games_opponent
                    average_sum += teamRatings[iteration][j] * num_games_opponent
            teamRatings[iteration + 1].append(teamRatings[0][i] + average_sum / sum_games)

    print("%-25s%7s%7s" % ("Team Name", "Start", "End"))
    val_arr = [[nameList[i], teamRatings[0][i], teamRatings[iterations][i]] for i in range(n)]
    val_arr.sort(key=lambda x: x[2], reverse=True)
    for x in val_arr:
        print("%-25s%7.2f%7.2f" % (x[0], x[1], x[2]))

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

nameList = createNameList(completedGames)
scoreDict = createScoreDict(completedGames)
matchupMatrix = createMatchupMatrix(nameList, completedGames)
highScoreIds = getHighestIndividualScoringMatches(completedGames)
highestTotalScoreIds = getHighestTotalScoringMatches(completedGames)
completeGameIdDict = createGameIdDict(completedGames)
lastDay = getLastDay(completedGames)

printDayHeader(completedGames, nameList, lastDay)
printSimpleRatingSystem(scoreDict, nameList, matchupMatrix)
#printRunDifferential(scoreDict)
#printHighestIndividualScoringMatches(highScoreIds, completeGameIdDict)
#printHighestTotalScoringMatches(highestTotalScoreIds, completeGameIdDict)
#printIterativeSRS(nameList, completedGames, scoreDict, 10)
