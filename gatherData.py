'''This program is intended to gather pertinent data from "basketball-reference.com"
and store it for later use in the game prediction network'''

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import re

class Dataset:
	def __init__(self, team):
		self.team = team
		self.simple_url = "https://www.basketball-reference.com"

	# gets url for playoff stats from desired team and year
	def getPlayoffURL(self, year):
		self.url = "{}/teams/{}/{}_games.html#games_playoffs_link".format(self.simple_url, self.team, year)

	# obtains parsed HTML from URL
	def getHTML(self):
		print("Getting HTML from URL:{}".format(self.url))
		self.html = urlopen(self.url)
		self.soup = BeautifulSoup(self.html, "html.parser")

	# returns url of page for individual box scores
	# address should always begin with '/boxscores/...'
	def getGameURL(self, address):
		self.game_url = self.simple_url + address;

	def processHTML(self):
		# EVERYTHING BELOW COULD BE CONTAINED IN ITS OWN CLASS
		# use getText() to extract the text content from first row column headers
		headers = [th.getText() for th in self.soup.findAll('tr', limit=2)[0].findAll('th')]
		rows = self.soup.findAll('tr')[0:]

		# determine indeces where relevant data is located
		for i in range(0,len(headers)):
			if headers[i] == 'Opponent':
				opponentIndex = i-1
			elif headers[i] == 'Tm':
				scoreIndex = i-1
			elif headers[i] == 'Opp':
				oppscoreIndex = i-1
			elif headers[i] == 'Streak':
				streakIndex = i-1

		self.data = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]
		print("Opponent: {} W/L: {} Score: {}-{}".format(self.data[1][5],self.data[1][6],self.data[1][8],self.data[1][9]))

		self.court_list, self.opponent_list, self.result_list, self.score_list, self.oppScore_list, self.streak_list = ([] for i in range(6))
		# successfully finds all the individual game rows and we move the 
		# important data into separate lists
		for x in range(1,len(self.data)):
			if self.data[x] != []:
				self.court_list.append(self.data[x][4])
				self.opponent_list.append(self.data[x][opponentIndex])
				self.result_list.append(self.data[x][6])
				self.score_list.append(self.data[x][scoreIndex])
				self.oppScore_list.append(self.data[x][oppscoreIndex])
				self.streak_list.append(self.data[x][streakIndex])
			# else:
				# this occurs when we have an empty row that exists for formatting CAN BE OMITTED
				# print("list at data[{}] empty".format(x))

# somehow we will have to determine starting lineups, this is somewhat
# guarded data so for now hard coding might be easiest solution

''' some important columns to be able to locate:
column 5 OR index 4 -> '' or '@' which shows 
column 6 OR index 5 -> Opponent in form ("City TeamName")
column 7 OR index 6 -> 'W' or 'L' 
column 9 OR index 8 -> Team's Score 
column 10 OR index 9 -> Opponent Score 
column 13 OR index 12 -> Team win streak '''

# we must get the links to the box scores so we can process individual player performance
''' links = []
for link in soup.findAll('a', attrs={'href': re.compile("^/boxscores")}):
	links.append(link.get('href'))
'''

# find out how to filter through the reference links to get player stats

# ATTEMPT TO FIND A SPECIFIC BOX SCORE FROM MATCHUP
# game_url = getGameURL(links[1])
# game_soup = getHTML(game_url)

# this provides us with links starting with /boxscores but we must find and add
# the first section of the url FOUND simple htt
# boxScoreURL = 

# exclude columns that are not needed
# headers = headers[1:]
