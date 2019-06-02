from gatherData import Dataset
import numpy as np

year = 2019
team = 'GSW'

dataset = Dataset(team)

dataset.getPlayoffURL(year)
dataset.getHTML()
dataset.processHTML()

print(dataset.opponent_list)
'''
for y in range(0,80):
	print("{} : {} -> {}-{}".format(dataset.opponent_list[y], dataset.result_list[y], dataset.score_list[y], dataset.oppScore_list[y]))
'''
