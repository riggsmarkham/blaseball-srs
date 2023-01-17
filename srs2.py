import games
import numpy as np
import numpy.linalg as linalg

nameField = "name"

# Creating dictionary of teams names ->
# [innings played, runs scored, runs allowed, run diff, scored/9, allowed/9, diff/9]
def createScoreDict(completedGames):
    scoreDict = dict()
    for x in completedGames:
        innings = x["gameStates"][0]["inning"] + 1
        awayScore = x["gameStates"][0]["awayScore"]
        homeScore = x["gameStates"][0]["homeScore"]

        awayTeam = x["awayTeam"][nameField]
        if awayTeam not in scoreDict.keys():
            scoreDict[awayTeam] = [0, 0, 0, 0]
        scoreDict[awayTeam][0] += innings
        scoreDict[awayTeam][1] += awayScore
        scoreDict[awayTeam][2] += homeScore
        scoreDict[awayTeam][3] += awayScore - homeScore

        homeTeam = x["homeTeam"][nameField]
        if homeTeam not in scoreDict.keys():
            scoreDict[homeTeam] = [0, 0, 0, 0]
        scoreDict[homeTeam][0] += innings
        scoreDict[homeTeam][1] += homeScore
        scoreDict[homeTeam][2] += awayScore
        scoreDict[homeTeam][3] += homeScore - awayScore
    for x in scoreDict.values():
        x.append(x[1] * (9 / x[0])) # runs scored per 9 innings
        x.append(x[2] * (9 / x[0])) # runs allowed per 9 innings
        x.append(x[3] * (9 / x[0])) # run differential per 9 innings
    return scoreDict

# 2nd version of SRS
# works on per 9 inning basis
# also, later, I want it to incorporate pitchers into SOS
# and correct for the run variance issue
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

# quick run differential chart, this time on a per 9 inning basis
def printRunDifferentialChart(scoreDict, nameList):
    tempList = [[x] + scoreDict[x] for x in nameList]
    tempList.sort(key=lambda x: x[4], reverse=True)
    print("Run Differentials")
    print("%-25s%8s%8s%8s%8s%8s%8s%8s" % ("Team Name", "Inn", "RF", "RF/9", "RA", "RA/9", "RD", "RD/9"))
    for x in tempList:
        print("%-25s%8d%8d%8.2f%8d%8.2f%8d%8.2f" % (x[0], x[1], x[2], x[5], x[3], x[6], x[4], x[7]))
    print()

# actually running the functions
gamesList = games.getGamesListMirror()
nameList = games.createNameList(gamesList, nameField)
# getting complete games from the regular season
completedGames = [x for x in gamesList if (x["complete"] and x["day"] < 90)]
scoreDict = createScoreDict(completedGames)

games.printDayHeader(gamesList, completedGames)
printSRS2(completedGames, scoreDict, nameList)
#printRunDifferentialChart(scoreDict, nameList)
