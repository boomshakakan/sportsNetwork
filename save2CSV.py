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
with open("opponent.csv",'w') as resultFile:
	wr = csv.writer(resultFile, dialect='excel')
	wr.writerows(dataset.opponent_list)

