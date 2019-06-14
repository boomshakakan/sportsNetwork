'''This program is intended to gather pertinent data from "basketball-reference.com"
and store it for later use in the game prediction network'''

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import re
import os

'''
class gameStats:
	def __init__(self, stats):
		if stats != []:
			for stat in stats:


class League:
	def __init__(self, teams):
		self.teams = []
		if teams != []:
			for team in teams:
				print(team)
				self.teams.append(Team(team))
'''

class Player:
	def __init__(self, name, team):
		self.games = []
		self.name = name
		self.team = team





class Dataset():
	def __init__(self):
		# define names for teams a and initialize empty list containers
		self.simple_url = "https://www.basketball-reference.com"
		self.lineup_url = "http://nbastartingfive.com/"
		self.name_list = ["court", "opponent", "results", "teamScore", "oppScore", "streak", "links"]
		self.team_list = ["GWS", "TOR", "CHI", "DEN", "ATL", "BOS", "CHO", "CLE", "DAL", "DET", "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", \
		"MIN", "BRK", "NOP", "NYK", "ORL", "PHI", "PHX", "POR", "SAS", "SAC", "WAS", "DAL", "UTA"]
		self.lists, self.links, self.court_list, self.opponent_list, self.result_list, self.score_list, self.oppScore_list, self.streak_list, self.teams \
		= ([] for i in range(9))

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
		headers = [th.getText() for th in self.soup.findAll('tr', limit=2)[0].findAll('th')]
		rows = self.soup.findAll('tr')[0:]

		''' some important columns to be able to locate:
		column 5 OR index 4 -> '' or '@' which shows 
		column 6 OR index 5 -> Opponent in form ("City TeamName")
		column 7 OR index 6 -> 'W' or 'L' 
		column 9 OR index 8 -> Team's Score 
		column 10 OR index 9 -> Opponent Score 
		column 13 OR index 12 -> Team win streak '''

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

		for link in self.soup.findAll('a', attrs={'href': re.compile("^/boxscores/[0-9]+")}):
			self.links.append(link.get('href'))
		# figure out why links has extra element
		print(len(self.links))

		self.text_data = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]

		# print("Opponent: {} W/L: {} Score: {}-{}".format(self.data[1][5],self.data[1][6],self.data[1][8],self.data[1][9]))
		# successfully finds all the individual game rows and we move the important data into separate lists
		for x in range(1,len(self.text_data)):
			if self.text_data[x] != []:
				
				self.court_list.append(self.text_data[x][4])
				self.opponent_list.append(self.text_data[x][opponentIndex])
				self.result_list.append(self.text_data[x][6])
				self.score_list.append(self.text_data[x][scoreIndex])
				self.oppScore_list.append(self.text_data[x][oppscoreIndex])
				self.streak_list.append(self.text_data[x][streakIndex])

		# make list of all lists
		self.lists = [self.court_list, self.opponent_list, self.result_list, self.score_list, self.oppScore_list, self.streak_list, self.links]

	def processBoxHTML(self):
		# parses html from box score page and pulls useful data 
		# you must execute processTeamHTML to obtain links before calling this function
		if self.links != []:
			for link in range(0,1):
				self.getGameURL(self.links[link])
				self.getHTML(self.game_url)
				
				body = self.soup.find('body')
				# find name of teams 
				# teams = body.findAll('a', attrs={'href': re.compile("^/teams/"), 'itemprop': "name"})
				teams = [team.getText() for team in body.findAll('a', attrs={'href': re.compile("^/teams/"), 'itemprop': "name"})]
				# print(teams)
				table_headers = self.soup.findAll('thead')
				table_body = self.soup.findAll('tbody')
				# from this we get an array of all the tbody elements, total of 4
				if len(table_headers) == len(table_body):
					stat_data = []
					for table in range(0,len(table_body)):
						rows = table_body[table].findAll('tr')
						if table % 2 == 1:
							stats = [th.getText() for th in table_headers[table].findAll('th', attrs={'data-over-header': "Advanced Box Score Stats"})]
							stat_data.append(stats)
						else:
							header = [th.getText() for th in table_headers[table].findAll('th', attrs={'data-over-header': "Basic Box Score Stats"})]
							stat_data.append(header)
						for row in rows:
							name = row.find('th').getText()
							print(name)
							row_data = [td.getText() for td in row.findAll('td')]

	def createTeams(self):
		# method will create all team rosters using team_list and most recent box scores
		for x in range(0,len())


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
