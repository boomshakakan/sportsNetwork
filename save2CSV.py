from gatherData import Dataset
import csv

year = 2019
team = 'GSW'
dataset = Dataset(team)

dataset.getPlayoffURL(year)
dataset.getHTML()
dataset.processHTML()

print(type(dataset.court_list))
# now we write the data containers to a csv file in order to keep it locally

with open("court.csv",'w') as resultFile:
	wr = csv.writer(resultFile, dialect='excel')
	wr.writerows(dataset.court_list)

with open("opponent.csv",'w') as resultFile:
	wr = csv.writer(resultFile, dialect='excel')
	wr.writerows(dataset.opponent_list)

with open("result.csv",'w') as resultFile:
	wr = csv.writer(resultFile, dialect='excel')
	wr.writerows(dataset.result_list)

with open("teamScore.csv",'w') as resultFile:
	wr = csv.writer(resultFile, dialect='excel')
	wr.writerows(dataset.score_list)

with open("oppScore.csv",'w') as resultFile:
	wr = csv.writer(resultFile, dialect='excel')
	wr.writerows(dataset.oppScore_list)

with open("streak.csv",'w') as resultFile:
	wr = csv.writer(resultFile, dialect='excel')
	wr.writerows(dataset.streak_list)
