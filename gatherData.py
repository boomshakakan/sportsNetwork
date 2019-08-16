'''This program is intended to gather pertinent data from "basketball-reference.com"
and store it for later use in the game prediction network'''

from urllib.request import urlopen
from bs4 import BeautifulSoup
from sqlite3 import Error
import pandas as pd
import sqlite3
import datetime
import re
import os

# game object holds date of game
class Game():
	def __init__(self, date):
		self.date = date
		print('Game Initialized')

# team object holds onto a list of games 
class Team(Game):
	def __init__(self, tag):
		self.games = []
		self.roster = []
		self.tag = tag
		print('Team Initialized: '+ self.tag)

class League(Team, Game):
	def __init__(self, team_list):
		self.teams = []
		self.player_list = []
		self.team_dict = {}
		for x in range(0,len(team_list)):
			self.teams.append(Team(team_list[x]))
		print('League Initialized')

class Dataset():
	def __init__(self):
		# define names for teams a and initialize empty list containers
		self.simple_url = "https://www.basketball-reference.com"
		self.name_list = ["court", "opponent", "results", "teamScore", "oppScore", "streak", "links"]
		self.team_list = ["GSW", "TOR", "CHI", "DEN", "ATL", "BOS", "CHO", "CLE", "DAL", "DET", "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", \
		"MIN", "BRK", "NOP", "NYK", "ORL", "PHI", "PHO", "POR", "SAS", "SAC", "WAS", "DAL", "UTA"]
		self.league = League(self.team_list)

		self.lists, self.links, self.dates, self.court_list, self.opponent_list, self.result_list, self.score_list, self.oppScore_list, self.streak_list, self.teams \
		= ([] for i in range(10))

	def createConnection(self):
		# creates the sqlite3 database connection
		try:
			# if no db with this name is found, one will be created
			self.conn = sqlite3.connect('bball_data.db')
			print("Database connection created...")
		except Error as e:
			print(e)

	def destroyConnection(self):
		# closes the sqlite db connection
		if self.conn:
			self.conn.close()
			print("Database connection destroyed...")
		else:
			print("No database connection found...")

	def populateDB(self):
		# this function will take the most recent game roster of all NBA teams and fill tables in our database
		# this is to be only called ONCE, anymore calls to this function will result in data confuscation
		
		if self.conn:
			cur = self.conn.cursor()
			
			for x in range(0, len(self.league.teams)):

				# we want to create roster using self.lastgamelink only for most recent year 
	
				self.getTeamURL(self.league.teams[x].tag, 2019)
				self.getHTML(self.team_url)
				self.processTeamHTML()
				self.gatherStats()
				self.processBoxHTML()
				print(len(self.links))

			# next we add player information to player table
			self.conn.commit()

	def getTag(self, teamName):
		# given full team name (locality Name) create dictionary to team's tag
		if teamName in self.league.team_dict:
			print('name already in dictionary')
			print('Tag is: {}'.format(self.league.team_dict[teamName]))
			return self.league.team_dict[teamName]
		else:
			# here we observe the teamName to find matches to tags and populate dictionary to correspond
			# there are a few ways that tags are generated
			# 1) first 3 letters of locality
			name = teamName.split(" ")
			for x in range(0, len(self.team_list)):
				if (name[0][0:3].upper() == self.team_list[x][0:3]):
					print('Match Found!')
					print('{}:{}'.format(name[0][0:3], self.team_list[x][0:3]))
					print('{}:{}'.format(name, self.team_list[x]))
					self.league.team_dict[teamName] = self.team_list[x]
				elif (len(name) == 3):
					tmp = name[0][0] + name[1][0] + name[2][0]
					if (tmp.upper() == self.team_list[x]):
						print('Match Found!')
						print('{}:{}'.format(tmp, self.team_list[x]))
						self.league.team_dict[teamName] = self.team_list[x]
				else:
					print('Not included {}'.format(teamName))


	def getTeamURL(self, team, year):
		# gets url for playoff stats from desired team and year
		self.team_url = "{}/teams/{}/{}_games.html".format(self.simple_url, team, year)

	def getGameURL(self, address):
		# returns url of page for individual box scores	
		self.game_url = self.simple_url + address

	def getHTML(self, url):
		# obtains parsed HTML from URL
		print("Getting HTML from URL:{}".format(url))
		self.html = urlopen(url)
		self.soup = BeautifulSoup(self.html, "html.parser")

	def getDate(self, link):
		# retrieves date from box url link using regex
		print(link)
		r = re.findall(r'\d+', link)
		date = r[0]
		year = date[0:4]
		month = date[4:6]
		day = date[6:8]
		date_stamp = year + '-' + month + '-' + day
		print(date_stamp)
		return date_stamp

	def processTeamHTML(self):
		# parses html from team page and extracts useful data into lists
		# use getText() to extract the text content from first row column headers
		self.links = []
		table_body = self.soup.findAll('tbody')
		headers = [th.getText() for th in self.soup.findAll('tr', limit=2)[0].findAll('th')]
		rows = self.soup.findAll('tr')[0:]

		# lastgameLink finds the link for the team's most recently played game which is how we create teams
		self.lastgameLink = (self.soup.find('a', attrs={'href': re.compile("^/boxscores/[0-9]+")})).get('href')
		
		for link in self.soup.findAll('a', attrs={'href': re.compile("^/boxscores/[0-9]+")})[1:]:
	
			score_link = link.get('href')
			self.links.append(score_link)
		# the links themselves contain information about the date so we may use these to obtain dates

		self.text_data = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]

		''' 
		some important columns to be able to locate:
		column 1 or index 0 -> date
		column 5 OR index 4 -> '' or '@' which shows 
		column 6 OR index 5 -> Opponent in form ("City TeamName")
		column 7 OR index 6 -> 'W' or 'L' 
		column 9 OR index 8 -> Team's Score 
		column 10 OR index 9 -> Opponent Score 
		column 13 OR index 12 -> Team win streak 
		'''

		# successfully finds all the individual game rows and we move the important data into separate lists
		for x in range(0,len(self.text_data)):
			if self.text_data[x] != []:

				self.court_list.append(self.text_data[x][4])
				self.opponent_list.append(self.text_data[x][5])
				self.result_list.append(self.text_data[x][6])
				self.score_list.append(self.text_data[x][8])
				self.oppScore_list.append(self.text_data[x][9])
				self.streak_list.append(self.text_data[x][12])

		# make list of all lists
		self.lists = [self.dates, self.court_list, self.opponent_list, self.result_list, self.score_list, self.oppScore_list, self.streak_list, self.links]

	def gatherStats(self):
		# peek at the box score page and pull stats to make dictionaries, self.stats is an array of two lists
		if self.links != []:
			self.stats = []

			self.getGameURL(self.links[0])
			self.getHTML(self.game_url)

			table_headers = self.soup.findAll('thead')
			# find Basic Box Score Stats
			basicStat = [th.getText() for th in table_headers[0].findAll('th', attrs={'data-over-header': "Basic Box Score Stats"})]
			self.stats.append(basicStat)
			advStat = [th.getText() for th in table_headers[1].findAll('th', attrs={'data-over-header': "Advanced Box Score Stats"})]
			self.stats.append(advStat[1:])
			# print(self.stats)
			print("basic stats: {}".format(len(basicStat)))
			print("adv stats: {}".format(len(advStat)))

	def processBoxHTML(self):
		# parses html from box score page and pulls useful data 
		# you must execute processTeamHTML & gatherStats to obtain links and stat names before calling this function
		if (self.links and self.stats):
			for idx in range(0,1):
				self.getGameURL(self.links[idx])
				self.getHTML(self.game_url)
				self.getDate(self.links[idx])
				
				body = self.soup.find('body')
				# find name of teams
				teams = [team.getText() for team in body.findAll('a', attrs={'href': re.compile("^/teams/"), 'itemprop': "name"})]
				print(teams)
				for x in range(0,len(teams)):
					self.getTag(teams[x])

				table_headers = self.soup.findAll('thead')
				table_body = self.soup.findAll('tbody')
				# from this we get an array of all the table body and header HTML, total of 4 (2 of each)

				if len(table_headers) == len(table_body):
					for table in range(0,len(table_body)):
						rows = table_body[table].findAll('tr')
						for row in rows:
							name = row.find('th').getText()
							# print("Name: {}".format(name))
							row_data = [td.getText() for td in row.findAll('td')]
							# print(row_data)




	def process10Years(self):
		# uses class methods to obtain team data from past 10 years

		d = datetime.datetime.today()
		currYear = int(d.year)
		# collects data from the past decade into containers
		for x in range(0,10):

			self.getTeamURL(currYear - x)
			self.getHTML(self.team_url)
			self.processTeamHTML()

	def clearLists(self):
		# makes all lists empty (never try to save or delete after using clearLists)
		self.lists, self.court_list, self.opponent_list, self.result_list, self.score_list, self.oppScore_list, self.streak_list = ([] for i in range(7))

	def save(self):
		# loops over contents of lists and saves to text file
		if self.lists != []:
			for x in range(0,len(self.name_list)):
				fileName = "{}.txt".format(self.name_list[x])
				with open(fileName, 'w') as writeFile:
					for item in self.lists[x]:
						writeFile.write("%s\n" % item)

	def delete(self):
		# deletes the .txt files generated by save method (only works after execution of save)
		if self.lists != []:
			for y in range(0,len(self.name_list)):
				fileName = "{}.txt".format(self.name_list[y])
				os.remove(fileName)

	def deleteDB(self):
		os.remove('bball_data.db')

