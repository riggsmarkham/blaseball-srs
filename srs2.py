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
# works on per 9 inning basis, accounts for some teams playing more games than others
# also, later, I want it to incorporate pitchers into SOS
# and correct for the run variance issue
def printSRS2(completedGames, scoreDict, nameList, markdownTable):
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
    # made it normalized based on the average rating (weighted per inning played)
    average_val = np.average(finalVector, weights=[scoreDict[x][0] for x in nameList])

    tempList = [[nameList[i], finalVector[i] - average_val, scoreDict[nameList[i]][6]] for i in range(n)]
    tempList.sort(key=lambda x: x[1], reverse=True)
    print("Simple Rating System v2")
    if markdownTable:
        print("Team Name|Rating|SOS")
        print("-|-|-")
        for x in tempList:
            print("%s|%.2f|%.2f" % (x[0], x[1], x[1] - x[2]))
    else:
        print("%-25s%8s%8s" % ("Team Name", "Rating", "SOS"))
        for x in tempList:
            print("%-25s%8.2f%8.2f" % (x[0], x[1], x[1] - x[2]))
    print()

# 2nd version of SRS
# should give results identical to those of the other SRS algorithm
# runs until it reaches the desired precision or until it reaches the maximum allowed iterations
def printIterativeSRS2(completedGames, scoreDict, nameList, precision, maxIterations):
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
    teamRatings = [[scoreDict[nameList[i]][6] for i in range(len(nameList))]]

    reachedPrecision = False
    iteration = 0
    while iteration < maxIterations and not reachedPrecision:
        reachedPrecision = True
        teamRatings.append([])
        for i in range(n):
            sum_innings = 0
            sum_weighted_ratings = 0
            for j in range(n):
                num_innings_opponent = matchupMatrix[i][j]
                if num_innings_opponent > 0:
                    sum_innings += num_innings_opponent
                    sum_weighted_ratings += teamRatings[iteration][j] * num_innings_opponent
            teamRatings[iteration + 1].append(teamRatings[0][i] + sum_weighted_ratings / sum_innings)
            if round(teamRatings[iteration][i], precision) != round(teamRatings[iteration + 1][i], precision):
                reachedPrecision = False
        iteration += 1
    print(f"Iterative SRS v2 ({iteration} iterations)")
    if iteration <= maxIterations:
        val_arr = [[nameList[i], teamRatings[0][i], teamRatings[iteration][i]] for i in range(n)]
        val_arr.sort(key=lambda x: x[2], reverse=True)
        print("%-25s%8s%8s" % ("Team Name", "Start", "End"))
        for x in val_arr:
            print("%-25s%8.2f%8.2f" % (x[0], x[1], x[2]))
    else:
        print(f"Unable to reach desired precision in {maxIterations} iterations.")
    print()

# actually running the functions
gamesList = games.getGamesList(2)
nameList = games.createNameList(gamesList, nameField)
# getting complete games from the regular season
completedGames = [x for x in gamesList if x["complete"]]
# completedGames = [x for x in gamesList if (x["complete"] and x["day"] < 90)]
if len(completedGames) > 0:
    scoreDict = createScoreDict(completedGames)

    games.printDayHeader(gamesList, completedGames)
    printSRS2(completedGames, scoreDict, nameList, False)
    # printIterativeSRS2(completedGames, scoreDict, nameList, 2, 1000)
else:
    print("No Games Completed.")
