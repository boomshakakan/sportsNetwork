'''
This program is intended to gather pertinent data from "basketball-reference.com"
and store it for later use in the game prediction network
'''

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
		print('Game Initialized with date: {}'.format(self.date))

# team object holds a list of games
class Team(Game):
	def __init__(self, tag):
		self.games = []
		self.roster = []
		self.tag = tag
		self.team_built = False
		print('Team Initialized: '+ self.tag)

	def addGame(self, date):
		make_add = True
		for game in self.games:
			if (date == game.date):
				make_add = False
		
			if (make_add):
				print('Adding game date to list of games')
				self.games.append(Game(date))

	def showGames(self):
		for game in self.games:
			print(game.date)

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
		# define tags for teams and initialize empty list containers
		self.simple_url = "https://www.basketball-reference.com"
		self.team_list = ["GSW", "TOR", "CHI", "DEN", "ATL", "BOS", "CHO", "CLE", "DAL", "DET", "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", \
		"MIN", "BRK", "NOP", "NYK", "ORL", "PHI", "PHO", "POR", "SAS", "SAC", "WAS", "OKC", "UTA"]
		self.league = League(self.team_list)

		self.lists, self.links, self.dates, self.court_list, self.opponent_list, self.result_list, self.score_list, self.oppScore_list, self.streak_list, self.teams \
		= ([] for i in range(10))

	def createConnection(self):
		# creates the sqlite3 database connection
		try:
			# if no db with this name is found, one will be created in current directory
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
			
			for team in self.league.teams:
				# we want to create roster using self.lastgamelink only for most recent year 
				self.getTeamURL(team.tag, 2019)
				self.getHTML(self.team_url)
				self.processTeamHTML()
				self.gatherStats()
				self.processBoxHTML(team)
				print(len(self.links))

			# next we add player information to player table
			self.conn.commit()

	def getTag(self, teamName):
		# given full team name return team's tag OR create dictionary entry for relation
	
		if teamName in self.league.team_dict:
			print('name already in dictionary')
			print('Tag is: {}'.format(self.league.team_dict[teamName]))
			return self.league.team_dict[teamName]
			
		else:
			# here we observe the teamName to find matches to tags and populate dictionary to correspond
			# a messy reverse engineer to relate all team names to tags
			name = teamName.split(" ")
			name_length = len(name)
			for team in self.league.teams:
				if (name[0][0:3].upper() == team.tag):
					self.league.team_dict[teamName] = team.tag
					return self.league.team_dict[teamName]
					
				elif (name_length == 3):
					tmp_name = name[0][0] + name[1][0] + name[2][0]
					if (tmp_name.upper() == team.tag):
						self.league.team_dict[teamName] = team.tag
						return self.league.team_dict[teamName]
					elif (name[0] == 'Oklahoma'):
						self.league.team_dict[teamName] = 'OKC'
						return self.league.team_dict[teamName]

				else:
					if (name_length == 2):
						tmp_name = name[0][0] + name[1][0] + name[1][1]
						if (tmp_name.upper() == team.tag):
							self.league.team_dict[teamName] = team.tag
							return self.league.team_dict[teamName]
						elif (name[0] == 'Brooklyn'):
							self.league.team_dict[teamName] = 'BRK'
							return self.league.team_dict[teamName]

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
		# retrieves date from box url link using re 
		print(link)
		r = re.findall(r'\d+', link)
		date = r[0]
		year = date[0:4]
		month = date[4:6]
		day = date[6:8]
		date_stamp = year + '-' + month + '-' + day
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
		# peek at the box score page and pull stat names / self.stats contains two lists
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
			print(self.stats)
			print("basic stats: {}".format(len(basicStat)))
			print("adv stats: {}".format(len(advStat)))

	def processBoxHTML(self, team):
		# parses html from box score page and pulls useful data from a single game link
		# you must execute processTeamHTML & gatherStats to obtain links and stat names before calling this function
		# we pass in the team object so we can populate necesary fields
		
		if (self.links and self.stats):
			# loop over all of team's season game links in self.links
			for idx in range(0,1):
				self.getGameURL(self.links[idx])
				self.getHTML(self.game_url)
				date = self.getDate(self.links[idx])
				body = self.soup.find('body')

				# find names of both teams
				teams = [team.getText() for team in body.findAll('a', attrs={'href': re.compile("^/teams/"), 'itemprop': "name"})]
				# print(teams)

				for name in teams:
					tag = self.getTag(name)
					for team in self.league.teams:
						if (tag == team.tag):
							# use a better asymptotic search algorithm to determine if date is in list
							team.addGame(date)								
		
				table_headers = self.soup.findAll('thead')
				table_body = self.soup.findAll('tbody')
				# from this we get an array of all the table body and header HTML, total of 4 (2 of each)
			
				x = 0
				if len(table_headers) == len(table_body):
					for table in range(0,len(table_body)):
						rows = table_body[table].findAll('tr')
						for row in rows:
							# player names are pulled from header
							name = row.find('th').getText()
							print("Name: {}".format(name))
							# reserves is the last value of name before the stat type changes (in below order)
							# 1) team[0] basic stats
							# 2) team[1] basic stats
							# 3) team[0] adv stats
							# 4) team[1] adv stats
							if (name == 'Reserves'):
								print('we need to create data containers to separate our data')
								x = x+1
							row_data = [td.getText() for td in row.findAll('td')]
							print(row_data)

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

