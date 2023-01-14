import requests
import configparser
import numpy as np
import numpy.linalg as linalg
import csv

nameFieldInUse = "name"

def createScoreDict(completedGames):
    scoreDict = dict()
    for x in completedGames:
        awayTeam = x["awayTeam"][nameFieldInUse]
        if awayTeam not in scoreDict.keys():
            scoreDict[awayTeam] = [1, x["gameStates"][0]["awayScore"], x["gameStates"][0]["homeScore"]]
        else:
            scoreDict[awayTeam][0] += 1
            scoreDict[awayTeam][1] += x["gameStates"][0]["awayScore"]
            scoreDict[awayTeam][2] += x["gameStates"][0]["homeScore"]

        homeTeam = x["homeTeam"][nameFieldInUse]
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
        if x["awayTeam"][nameFieldInUse] not in nameList:
            nameList.append(x["awayTeam"][nameFieldInUse])
        if x["homeTeam"][nameFieldInUse] not in nameList:
            nameList.append(x["homeTeam"][nameFieldInUse])
    nameList.sort()
    return nameList

def avgRunDiff(diffList):
    return (diffList[1] - diffList[2]) / diffList[0]

def pygthagWinPerc(diffList):
    return (diffList[1] * diffList[1]) / (diffList[1] * diffList[1] + diffList[2] * diffList[2])

def printGame(game):
    print("Day %d, %s @ %s, %d-%d" % (game["day"] + 1, game["awayTeam"]["shorthand"], game["homeTeam"]
          ["shorthand"], game["gameStates"][0]["awayScore"], game["gameStates"][0]["homeScore"]))

def printDayHeader(gamesList, completedGames):
    lastDay = 0
    foundOngoingGame = False
    for x in gamesList:
        if x["started"] and not x["complete"]:
            lastDay = x["day"]
            foundOngoingGame = True
            break
    if foundOngoingGame:
        print("In the midst of day %d" % (lastDay + 1))
    else:
        for x in completedGames:
            if x["day"] > lastDay:
                lastDay = x["day"]
        print("At the end of day %d" % (lastDay + 1))
    print()

def printSimpleRatingSystem(completedGames, scoreDict, nameList):
    n = len(nameList)
    matchupMatrix = np.asfarray(getMatchupArr(completedGames, nameList))
    for i in range(n):
        matchupMatrix[i] /= matchupMatrix[i].sum()
    for i in range(n):
        matchupMatrix[i][i] = -1

    scoreVector = np.asarray(getAvgRunDiffArr(scoreDict, nameList)) * -1
    finalVector = linalg.solve(matchupMatrix, scoreVector)
    average_val = np.average(finalVector)

    tempList = [[nameList[i], finalVector[i] - average_val, avgRunDiff(scoreDict[nameList[i]])] for i in range(n)]
    tempList.sort(key=lambda x: x[1], reverse=True)
    print("Simple Rating System")
    print("%-25s%8s%8s" % ("Team Name", "Rating", "SOS"))
    for x in tempList:
        print("%-25s%8.2f%8.2f" % (x[0], x[1], x[1] - x[2]))
    print()

def printIterativeSRS(completedGames, scoreDict, nameList, iterations):
    n = len(nameList)
    matchupArr = getMatchupArr(completedGames, nameList)
    teamRatings = [getAvgRunDiffArr(scoreDict, nameList)]

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
    print()

def getMatchupArr(completedGames, nameList):
    matchupArr = [[0 for _ in range(len(nameList))] for _ in range(len(nameList))]
    for x in completedGames:
        awayIndex = nameList.index(x["awayTeam"][nameFieldInUse])
        homeIndex = nameList.index(x["homeTeam"][nameFieldInUse])
        matchupArr[awayIndex][homeIndex] += 1
        matchupArr[homeIndex][awayIndex] += 1
    return matchupArr

def getAvgRunDiffArr(scoreDict, nameList):
    return [avgRunDiff(scoreDict[nameList[i]]) for i in range(len(nameList))]

def printRunDifferentialChart(scoreDict, nameList):
    tempList = [[x, scoreDict[x][0], scoreDict[x][1], scoreDict[x][2], avgRunDiff(scoreDict[x]), pygthagWinPerc(scoreDict[x])] for x in nameList]
    tempList.sort(key=lambda x: x[4], reverse=True)
    print("Run Differentials")
    print("%-25s%8s%8s%8s%8s%8s%8s%8s" % ("Team Name", "RF", "RF/G", "RA", "RA/G", "RD", "RD/G", "Pyth W%"))
    for x in tempList:
        print("%-25s%8d%8.2f%8d%8.2f%8d%8.2f%8.3f" % (x[0], x[2], x[2]/x[1], x[3], x[3]/x[1], x[2]-x[3], x[4], x[5]))
    print()

def printHighestIndividualScoringGames(completedGames):
    highestScore = 0
    games = []
    for x in completedGames:
        topScore = max(x["gameStates"][0]["awayScore"], x["gameStates"][0]["homeScore"])
        if topScore > highestScore:
            games = [x]
            highestScore = topScore
        elif topScore == highestScore:
            games.append(x)
    print("Games with highest single-team score:")
    for x in games:
        printGame(x)
    print()

def printHighestTotalScoringGames(completedGames):
    highestScore = 0
    games = []
    for x in completedGames:
        topScore = x["gameStates"][0]["awayScore"] + x["gameStates"][0]["homeScore"]
        if topScore > highestScore:
            games = [x]
            highestScore = topScore
        elif topScore == highestScore:
            games.append(x)
    print("Games with highest total score:")
    for x in games:
        printGame(x)
    print()

def printLongestGames(completedGames):
    mostInnings = 0
    games = []
    for x in completedGames:
        lastInning = x["gameStates"][0]["inning"] + 1
        if lastInning > mostInnings:
            games = [x]
            mostInnings = lastInning
        elif lastInning == mostInnings:
            games.append(x)
    print("Longest games: " + str(mostInnings) + " innings")
    for x in games:
        printGame(x)
    print()

def printWingsLosses(completedGames):
    lossList = []
    for x in completedGames:
        homeWon = x["gameStates"][0]["homeScore"] > x["gameStates"][0]["awayScore"]
        if (x["awayTeam"]["shorthand"] == "WWMX" and homeWon) or (x["homeTeam"]["shorthand"] == "WWMX" and not homeWon):
            lossList.append(x)
    print("Wings losses:")
    for x in lossList:
        printGame(x)
    print()

def writePitchersInningPitched(completedGames, lastDay):
    filteredGames = []
    for x in completedGames:
        if x["day"] < lastDay:
            filteredGames.append(x)
    pitcherDict = dict()
    for x in filteredGames:
        pitcherDict[x["awayPitcher"][nameFieldInUse]] = pitcherDict.get(x["awayPitcher"][nameFieldInUse], 0) + x["gameStates"][0]["inning"] + 1
        pitcherDict[x["homePitcher"][nameFieldInUse]] = pitcherDict.get(x["homePitcher"][nameFieldInUse], 0) + x["gameStates"][0]["inning"] + 1
    pitcherArr = [[key, value] for key, value in pitcherDict.items()]
    pitcherArr.sort(key=lambda x: x[0])
    with open("pitchersIP.csv", mode="w") as csv_file:
        fieldnames = [nameFieldInUse, "ip"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for x in pitcherArr:
            writer.writerow({nameFieldInUse: x[0], "ip": x[1]})

def writeWLPerTeam(completedGames, nameList):
    n = len(nameList)
    wlArr = [[[0,0] for _ in range(n)] for _ in range(n)]
    for x in completedGames:
        awayIndex = nameList.index(x["awayTeam"][nameFieldInUse])
        homeIndex = nameList.index(x["homeTeam"][nameFieldInUse])
        if (x["gameStates"][0]["awayScore"] > x["gameStates"][0]["homeScore"]):
            wlArr[awayIndex][homeIndex][0] += 1
            wlArr[homeIndex][awayIndex][1] += 1
        else:
            wlArr[awayIndex][homeIndex][1] += 1
            wlArr[homeIndex][awayIndex][0] += 1
    rows = []
    for i in range(n):
        newRow = [nameList[i] + " W%"]
        for x in wlArr[i]:
            if (x[0] + x[1] == 0):
                newRow.append("")
            else:
                newRow.append("%.2f" % (x[0] / (x[0] + x[1])))
        rows.append(newRow)
    with open("wlByTeam.csv", mode="w") as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow([""] + ["vs " + x for x in nameList])
        csvwriter.writerows(rows)

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

gamesList = getGamesListMirror()
completedGames = [x for x in gamesList if x["complete"]]
nameList = createNameList(completedGames)
scoreDict = createScoreDict(completedGames)

printDayHeader(gamesList, completedGames)
printSimpleRatingSystem(completedGames, scoreDict, nameList)
#printIterativeSRS(completedGames, scoreDict, nameList, 6)
#printRunDifferentialChart(scoreDict, nameList)
#printHighestIndividualScoringGames(completedGames)
#printHighestTotalScoringGames(completedGames)
#printLongestGames(completedGames)
#printWingsLosses(completedGames)
#writePitchersInningPitched(completedGames, 95)
#writeWLPerTeam(completedGames, nameList)
