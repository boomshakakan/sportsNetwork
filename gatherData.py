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

class Dataset():
	def __init__(self):
		# define names for teams a and initialize empty list containers
		self.simple_url = "https://www.basketball-reference.com"
		self.name_list = ["court", "opponent", "results", "teamScore", "oppScore", "streak", "links"]
		self.team_list = ["GWS", "TOR", "CHI", "DEN", "ATL", "BOS", "CHO", "CLE", "DAL", "DET", "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", \
		"MIN", "BRK", "NOP", "NYK", "ORL", "PHI", "PHX", "POR", "SAS", "SAC", "WAS", "DAL", "UTA"]
		self.lists, self.links, self.dates, self.court_list, self.opponent_list, self.result_list, self.score_list, self.oppScore_list, self.streak_list, self.teams \
		= ([] for i in range(10))

	def createConnection(self):
		# creates the sqlite3 database connection
		try:
			self.conn = sqlite3.connect('bball_data.db')
			print("Database connection created...")
		except Error as e:
			print(e)

	def destroyConnection(self):
		# closes the sqlite db connection
		self.conn.close()
		print("Database connection destroyed...")

	def createTeams(self):
		# this function will take the most recent game roster of all NBA teams and create a database for each 

		if self.conn:
			cur = self.conn.cursor()
			
			for idx, team in enumerate(self.team_list):
				print(team)
				sql = 
				''
				cur.execute('INSERT INTO teams (team_ID, name) VALUES (?,?);', (idx+1,team,))
				
			self.conn.commit()
			return cur.lastrowid

	def destroyTeams(self, cursor):
		# drops TEAMS table from database (this should be done before recreating db)
		sql = 'DROP TABLE IF EXISTS teams;'
		cursor.execute(sql)
		print("Table dropped from database...")

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

	def processTeamHTML(self):
		# parses html from team page and extracts useful data into lists
		# use getText() to extract the text content from first row column headers
		table_body = self.soup.findAll('tbody')
		headers = [th.getText() for th in self.soup.findAll('tr', limit=2)[0].findAll('th')]
		rows = self.soup.findAll('tr')[0:]

		# lastgameLink finds the link for the team's most recently played game which is how we create teams
		self.lastgameLink = (self.soup.find('a', attrs={'href': re.compile("^/boxscores/[0-9]+")})).get('href')
		
		for link in self.soup.findAll('a', attrs={'href': re.compile("^/boxscores/[0-9]+")})[1:]:
	
			score_link = link.get('href')
			self.links.append(score_link)
			print(score_link)
			#print(re.search('/(.+?){}'))
		# the links themselves contain information about the date so we may use these to obtain dates

		self.text_data = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]

		''' some important columns to be able to locate:
		column 1 or index 0 -> date
		column 5 OR index 4 -> '' or '@' which shows 
		column 6 OR index 5 -> Opponent in form ("City TeamName")
		column 7 OR index 6 -> 'W' or 'L' 
		column 9 OR index 8 -> Team's Score 
		column 10 OR index 9 -> Opponent Score 
		column 13 OR index 12 -> Team win streak '''

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
			print("basic stats: {}".format(len(basicStat)))
			print("adv stats: {}".format(len(advStat)))
			print(self.stats)

	def processBoxHTML(self):
		# parses html from box score page and pulls useful data 
		# you must execute processTeamHTML & gatherStats to obtain links and stat names before calling this function
		if (self.links and self.stats):
			for link in range(0,1):
				self.getGameURL(self.links[link])
				self.getHTML(self.game_url)
				
				body = self.soup.find('body')
				# find name of teams 
				# teams = body.findAll('a', attrs={'href': re.compile("^/teams/"), 'itemprop': "name"})
				teams = [team.getText() for team in body.findAll('a', attrs={'href': re.compile("^/teams/"), 'itemprop': "name"})]
				date = [meta.getText() for meta in body.findAll('div', attrs={'class': "scorebox_meta"})]
				table_headers = self.soup.findAll('thead')
				print(len(date))
				table_body = self.soup.findAll('tbody')
				# from this we get an array of all the table body and header HTML, total of 4

				if len(table_headers) == len(table_body):
					stat_data = []
					for table in range(0,len(table_body)):
						rows = table_body[table].findAll('tr')
						for row in rows:
							name = row.find('th').getText()
							print("Name: {}".format(name))
							row_data = [td.getText() for td in row.findAll('td')]
							print(row_data)

	# def createTeams(self):
		# method will create all team rosters using team_list and most recent box scores

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

