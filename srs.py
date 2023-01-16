import numpy as np
import numpy.linalg as linalg
import games

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

def avgRunDiff(diffList):
    return (diffList[1] - diffList[2]) / diffList[0]

def pygthagWinPerc(diffList):
    return (diffList[1] * diffList[1]) / (diffList[1] * diffList[1] + diffList[2] * diffList[2])

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

gamesList = games.getGamesListMirror()
nameList = games.createNameList(gamesList, nameFieldInUse)
completedGames = [x for x in gamesList if x["complete"]]
scoreDict = createScoreDict(completedGames)

games.printDayHeader(gamesList)
printSimpleRatingSystem(completedGames, scoreDict, nameList)
#printIterativeSRS(completedGames, scoreDict, nameList, 6)
printRunDifferentialChart(scoreDict, nameList)
