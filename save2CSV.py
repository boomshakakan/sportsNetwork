# this file only need be called once when gatherData is working successfully

from gatherData import Dataset
import csv

year = 2019
team = 'GSW'
dataset = Dataset(team)

dataset.getPlayoffURL(year)
dataset.getHTML()
dataset.processHTML()

# now we write the data containers to a csv file in order to keep it locally
# THIS IS SAVING THE NAME STRINGS AND PUTTING COMMAS BETWEEN EACH LETTER
with open("court.txt", 'w') as writeFile:
	for item in dataset.court_list:
		writeFile.write("%s\n" % item)

with open("opponent.txt", 'w') as writeFile:
	for item in dataset.opponent_list:
		writeFile.write("%s\n" % item)

with open("results.txt", 'w') as writeFile:
	for item in dataset.result_list:
		writeFile.write("%s\n" % item)

with open("teamScore.txt", 'w') as writeFile:
	for item in dataset.score_list:
		writeFile.write("%s\n" % item)

with open("oppScore.txt", 'w') as writeFile:
	for item in dataset.oppScore_list:
		writeFile.write("%s\n" % item)

with open("streak.txt", 'w') as writeFile:
	for item in dataset.streak_list:
		writeFile.write("%s\n" % item)