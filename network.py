from gatherData import Dataset, League, Team, Game
import numpy as np
import datetime

def main():
	d = datetime.datetime.today()
	curr_year = int(d.year)

	dataset = Dataset(curr_year)
	# creates the connection to the sqlite3 database
	dataset.create_connection()
	# get stat names and put them into dataset.stats
	# dataset.get_statnames()
	dataset.populate_DB()
	dataset.destroy_connection()
	#print(dataset.league.team_dict)
	print(len(dataset.league.player_list))
	print(dataset.league.player_list)

	'''
	for team in dataset.league.teams:
		team.show_seasons()
		team.show_roster()
	'''

if __name__ == "__main__":
	main()
	

