import games
import numpy as np
import numpy.linalg as linalg

nameField = "name"

# Creating dictionary of teams names -> [innings played, runs scored, runs allowed, run differential]
def createScoreDict(completedGames):
    scoreDict = dict()
    for x in completedGames:
        awayTeam = x["awayTeam"][nameField]
        if awayTeam not in scoreDict.keys():
            scoreDict[awayTeam] = [0, 0, 0, 0]
        scoreDict[awayTeam][0] += x["gameStates"][0]["inning"] + 1
        scoreDict[awayTeam][1] += x["gameStates"][0]["awayScore"]
        scoreDict[awayTeam][2] += x["gameStates"][0]["homeScore"]
        scoreDict[awayTeam][3] += x["gameStates"][0]["awayScore"] - x["gameStates"][0]["homeScore"]

        homeTeam = x["homeTeam"][nameField]
        if homeTeam not in scoreDict.keys():
            scoreDict[homeTeam] = [0, 0, 0, 0]
        scoreDict[homeTeam][0] += x["gameStates"][0]["inning"] + 1
        scoreDict[homeTeam][1] += x["gameStates"][0]["homeScore"]
        scoreDict[homeTeam][2] += x["gameStates"][0]["awayScore"]
        scoreDict[homeTeam][3] += x["gameStates"][0]["homeScore"] - x["gameStates"][0]["awayScore"]
    for x in scoreDict.values():
        x.append(x[1] * (9 / x[0]))
        x.append(x[2] * (9 / x[0]))
        x.append(x[3] * (9 / x[0]))
    return scoreDict

def printSRS2(completedGames, scoreDict, nameList):
    n = len(nameList)
    matchupMatrix = np.zeros((n, n))
    for game in completedGames:
        awayIndex = nameList.index(game["awayTeam"][nameField])
        homeIndex = nameList.index(game["homeTeam"][nameField])
        inningCount = game["gameStates"][0]["inning"] + 1
        matchupMatrix[awayIndex][homeIndex] += inningCount
        matchupMatrix[homeIndex][awayIndex] += inningCount
    for i in range(n):
        matchupMatrix[i] /= scoreDict[nameList[i]][0]
    for i in range(n):
        matchupMatrix[i][i] = -1

    scoreVector = np.asarray([scoreDict[nameList[i]][6] for i in range(len(nameList))]) * -1
    finalVector = linalg.solve(matchupMatrix, scoreVector)
    average_val = np.average(finalVector)

    tempList = [[nameList[i], finalVector[i] - average_val, scoreDict[nameList[i]][6]] for i in range(n)]
    tempList.sort(key=lambda x: x[1], reverse=True)
    print("Simple Rating System")
    print("%-25s%8s%8s" % ("Team Name", "Rating", "SOS"))
    for x in tempList:
        print("%-25s%8.2f%8.2f" % (x[0], x[1], x[1] - x[2]))
    print()

def printRunDifferentialChart(scoreDict, nameList):
    tempList = [[x] + scoreDict[x] for x in nameList]
    tempList.sort(key=lambda x: x[4], reverse=True)
    print("Run Differentials")
    print("%-25s%8s%8s%8s%8s%8s%8s%8s" % ("Team Name", "Inn", "RF", "RF/9", "RA", "RA/9", "RD", "RD/9"))
    for x in tempList:
        print("%-25s%8d%8d%8.2f%8d%8.2f%8d%8.2f" % (x[0], x[1], x[2], x[5], x[3], x[6], x[4], x[7]))
    print()

gamesList = games.getGamesListMirror()
nameList = games.createNameList(gamesList, nameField)
completedGames = [x for x in gamesList if (x["complete"] and x["day"] < 90)]
scoreDict = createScoreDict(completedGames)

games.printDayHeader(gamesList, completedGames)
printSRS2(completedGames, scoreDict, nameList)
#printRunDifferentialChart(scoreDict, nameList)
