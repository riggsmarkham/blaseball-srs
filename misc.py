import csv
import games

# Prints out game in a format good for indicating records
def printGame(game):
    print("Day %d, %s @ %s, %d-%d" % (game["day"] + 1, game["awayTeam"]["shorthand"], game["homeTeam"]
          ["shorthand"], game["gameStates"][0]["awayScore"], game["gameStates"][0]["homeScore"]))

# Prints out all the games that hold/tie the record for one team scoring the most runs
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

# Prints out all the games that hold/tie the record for two teams scoring the most runs combined
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

# Prints out all the games that hold/tie the record for most innings
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

# Prints out all the games that the Mexico City Wild Wings lost
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

# Writes pitchers' names and their innings pitched to pitchersIP.csv
def writePitchersInningPitched(completedGames, lastDay):
    filteredGames = []
    for x in completedGames:
        if x["day"] < lastDay:
            filteredGames.append(x)
    pitcherDict = dict()
    for x in filteredGames:
        pitcherDict[x["awayPitcher"]["name"]] = pitcherDict.get(x["awayPitcher"]["name"], 0) + x["gameStates"][0]["inning"] + 1
        pitcherDict[x["homePitcher"]["name"]] = pitcherDict.get(x["homePitcher"]["name"], 0) + x["gameStates"][0]["inning"] + 1
    pitcherArr = [[key, value] for key, value in pitcherDict.items()]
    pitcherArr.sort(key=lambda x: x[0])
    with open("pitchersIP.csv", mode="w") as csv_file:
        fieldnames = ["name", "ip"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for x in pitcherArr:
            writer.writerow({"name": x[0], "ip": x[1]})

# Writes a table showing the win percentage of each team against each other to wlByTeam.csv
def writeWLPerTeam(completedGames, nameList):
    n = len(nameList)
    wlArr = [[[0,0] for _ in range(n)] for _ in range(n)]
    for x in completedGames:
        awayIndex = nameList.index(x["awayTeam"]["shorthand"])
        homeIndex = nameList.index(x["homeTeam"]["shorthand"])
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

# part that actually gets the data and runs the functions
gamesList = games.getGamesListMirror()
nameList = games.createNameList(gamesList, "shorthand")
completedGames = [x for x in gamesList if x["complete"]]

games.printDayHeader(gamesList)
printHighestIndividualScoringGames(completedGames)
printHighestTotalScoringGames(completedGames)
printLongestGames(completedGames)
printWingsLosses(completedGames)
#writePitchersInningPitched(completedGames, 95)
#writeWLPerTeam(completedGames, nameList)
