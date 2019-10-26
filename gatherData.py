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

class Player():
	def __init__(self, name, team):
		self.name = name
		self.team = team
		print("Player: {} created for {}".format(name, team))

	def add_stats(self, stats):
		self.game_stats = stats
		
class Game():
	def __init__(self, date):
		self.date = date
		print('Game Initialized with date: {}'.format(self.date))

	def set_victor(self, victory):
		if victory:
			self.won = True
		else:
			self.won = False

class Season(Game):
	# includes any possible playoff games
	# include variables for number of games and year for season
	def __init__(self):
		self.games = [] 

	def set_numGames(self, num_games):
		self.num_games = num_games

	def add_game(self, date):
		make_add = True
		for game in self.games:
			if date == game.date:
				make_add = False
		
		if (make_add):
				print('game added: {}'.format(date))
				self.games.append(Game(date))

class Team(Season, Game, Player):	
	def __init__(self, tag):
		self.roster = []
		self.seasons = []
		self.idx = -1 # idx will represent position in league.teams list 
		self.season_idx = 0
		self.tag = tag
		self.roster_built = False
		print('Team Initialized: '+ self.tag)

	def add_player(self, name, tag):
		make_add = True
		for player in self.roster:
			if name == player.name:
				make_add = False

		if make_add:
			self.roster.append(Player(name, tag))

	def init_season(self):
		# because of the way  game data is pulled need to have a season initialized for every team
		self.seasons.append(Season())
		self.season_idx += 1
		print('Season initialized for {}'.format(self.tag))

	def show_seasons(self):
		for season in self.seasons:
			for game in season.games:
				print(game.date)

	def show_roster(self):
		print("Roster for {}:".format(self.tag))
		for player_name in self.roster:
			print(player_name)

class League(Team, Season, Game):
	def __init__(self, team_list):
		self.teams = []
		self.player_list = []
		self.team_dict = {}
		for x in range(0,len(team_list)):
			self.teams.append(Team(team_list[x]))
			self.teams[x].idx = x
			self.teams[x].init_season()
		print('League Initialized with {} teams'.format(len(team_list)))

	def add_player(self, name, tag):
		make_add = True
		for player in self.player_list:
			if name == player.name:
				make_add = False

		if make_add:
			self.player_list.append(Player(name, tag))

class Dataset():
	def __init__(self, curr_year):
		# define tags for teams and initialize empty list containers
		self.curr_year = curr_year
		self.simple_url = "https://www.basketball-reference.com"
		self.team_list = ["GSW", "TOR", "CHI", "DEN", "ATL", "BOS", "CHO", "CLE", "DAL", "DET", "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", \
		"MIN", "BRK", "NOP", "NYK", "ORL", "PHI", "PHO", "POR", "SAS", "SAC", "WAS", "OKC", "UTA"]
		self.league = League(self.team_list)

		self.lists, self.links, self.dates, self.court_list, self.opponent_list, self.result_list, self.score_list, self.oppScore_list, self.streak_list, self.teams \
		= ([] for i in range(10))

	def create_connection(self):
		# creates the sqlite3 database connection
		try:
			# if no db with this name is found, one will be created in current directory
			self.conn = sqlite3.connect('bball_data')
			print("Database connection created...")
		except Error as e:
			print(e)

	def destroy_connection(self):
		# closes the sqlite db connection
		if self.conn:
			self.conn.close()
			print("Database connection destroyed...")
		else:
			print("No database connection found...")

	def populate_DB(self):
		# this function will take the most recent game roster of all NBA teams and fill tables in our database
		# this is to be only called ONCE, anymore calls to this function will result in data confuscation
		year = 2019
		
		if self.conn:
			cur = self.conn.cursor()
			
			# we will inevitably loop through years in order to pull data
			for team in self.league.teams:
				cur.execute("INSERT INTO teams ('name') VALUES (?)", (team.tag, ))

				self.get_TeamURL(team.tag, year)
				self.get_HTML(self.team_url)
				self.process_TeamHTML(team)
				# we process the team page and get a list of links 

				if year == self.curr_year and team.roster_built == False:
					self.get_roster(team)

				for player_name in team.roster:
					cur.execute('''INSERT INTO players (team_id, name) VALUES (?,?)''', (team.idx+1, player_name))
				
				self.process_BoxHTML(team, year)

			self.conn.commit()
		else:
			print("No db connection found...")

	def get_statnames(self):
		# we pick an arbitrary team and use it to find names of stats
		tmp_team = self.league.teams[0]

		self.get_TeamURL(tmp_team.tag, self.curr_year)
		self.get_HTML(self.team_url)
		self.process_TeamHTML(tmp_team)
		self.gather_stats()

	def get_tag(self, teamName):
		# given full team name return team's tag OR create dictionary entry for relation
	
		if teamName in self.league.team_dict:
			print('name already in dictionary')
			print('Tag is: {}'.format(self.league.team_dict[teamName]))
			return self.league.team_dict[teamName]

		# ELSE SET & GET
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

	def get_TeamURL(self, tag, year):
		# gets url for playoff stats from desired team and year
		self.team_url = "{}/teams/{}/{}_games.html".format(self.simple_url, tag, year)

	def get_GameURL(self, address):
		# returns url of page for individual box scores	
		self.game_url = self.simple_url + address

	def get_HTML(self, url):
		# obtains parsed HTML from URL
		print("Getting HTML from URL:{}".format(url))
		self.html = urlopen(url)
		self.soup = BeautifulSoup(self.html, "html.parser")

	def get_date(self, link):
		# retrieves date from box url link using re 
		print(link)
		r = re.findall(r'\d+', link)
		date = r[0]
		year = date[0:4]
		month = date[4:6]
		day = date[6:8]
		date_stamp = year + '-' + month + '-' + day
		return date_stamp

	def process_TeamHTML(self, team):
		# parses html from team page and extracts useful data into lists
		# use getText() to extract the text content from first row column headers
		self.links = []
		rows = self.soup.findAll('tr')[0:]

		# lastgameLink finds the link for the team's most recently played game which is how we create teams
		self.lastgameLink = (self.soup.find('a', attrs={'href': re.compile("^/boxscores/[0-9]+")})).get('href')
		
		for link in self.soup.findAll('a', attrs={'href': re.compile("^/boxscores/[0-9]+")})[1:]:
			score_link = link.get('href')
			self.links.append(score_link)

		# use the list of links to determine number of games for season
		team.seasons[team.season_idx-1].set_numGames(len(self.links))

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

	def gather_stats(self):
		# peek at the box score page and pull stat names / self.stats contains two lists
		if self.links != []:
			self.stats = []

			self.get_GameURL(self.links[0])
			self.get_HTML(self.game_url)

			table_headers = self.soup.findAll('thead')
			# find Basic Box Score Stats
			basicStat = [th.getText() for th in table_headers[0].findAll('th', attrs={'data-over-header': "Basic Box Score Stats"})]
			advStat = [th.getText() for th in table_headers[1].findAll('th', attrs={'data-over-header': "Advanced Box Score Stats"})]
			self.stats = basicStat + advStat[1:]
			print(self.stats)
			# print("basic stats: {}".format(len(basicStat)))
			# print("adv stats: {}".format(len(advStat)))

	def get_roster(self, team):
		# process most recent game link and use to generate team roster
		tag_list, team_list = ([] for i in range(2))

		print("Pulling team roster for {}".format(team.tag))
		recent_game = self.links[len(self.links)-1] # latest game
		self.get_GameURL(recent_game)
		self.get_HTML(self.game_url)

		body = self.soup.find('body')
		team_names = [team.getText() for team in body.findAll('a', attrs={'href': re.compile("^/teams/"), 'itemprop': "name"})]

		flag = False
		for name in team_names:
			tag = self.get_tag(name)
			tag_list.append(tag)
			# this for error checking may be omitted once verified
			if flag == False:
				flag = True
				print("Away Team: {}".format(tag))
			else:
				print("Home Team: {}".format(tag))
			
			if team.tag == tag:
				self.league.teams[team.idx].roster_built = True
				print('{} seasons for {}'.format(team.season_idx, team.tag))
				team_list.append(team)
			else:
				# we could potentially use team_dict if all seasons are pre-processed, not yet
				for x in range(0, len(self.league.teams)):
					if self.league.teams[x].tag == tag:
						team_list.append(self.league.teams[x])
						self.league.teams[x].roster_built = True
						print('{} seasons for {}'.format(self.league.teams[x].season_idx, self.league.teams[x].tag))
	
		table_body = self.soup.findAll('tbody')
		table_list = [table_body[0], table_body[8]]
		# table_list[0] -> away basic stats 
		# table_list[1] -> home basic stats

		for table_idx in range(0,len(table_list)):
			rows = table_list[table_idx].findAll('tr')
			# containers for each team's players and stats
			for idx, row in enumerate(rows):
				# player names are pulled from header and stats skimmed from table
				name = row.find('th').getText()

				if idx == 5 or name =='Reserves':
					print("row index: {}".format(idx))
				else:
					row_data = [td.getText() for td in row.findAll('td')]
					print("Name: {}\nStats: {}".format(name, row_data))

					if table_idx == 0:
						# add player to specific team list and to list of total players
						if name not in self.league.teams[team_list[table_idx].idx].roster:
							self.league.teams[team_list[table_idx].idx].roster.append(name)
							self.league.add_player(name, tag_list[table_idx])
					else:
						if name not in self.league.teams[team_list[table_idx].idx].roster:
							self.league.teams[team_list[table_idx].idx].roster.append(name)
							self.league.add_player(name, tag_list[table_idx])

	def process_BoxHTML(self, team, year):
		# parses html from box score page and pulls useful data from a single game link
		# you must execute processTeamHTML & gatherStats to obtain links and stat names before calling this function
		if (self.links and self.stats):
			# loop over all of team's season game links in self.links
			for idx in range(0,1):
				self.get_GameURL(self.links[idx])
				self.get_HTML(self.game_url)
				date = self.get_date(self.links[idx])
				body = self.soup.find('body')

				# find names of both teams
				team_names = [team.getText() for team in body.findAll('a', attrs={'href': re.compile("^/teams/"), 'itemprop': "name"})]
				
				for name in team_names:
					# get tag from team name
					tag = self.get_tag(name)
					for team in self.league.teams:
						if tag == team.tag:
							# use a better asymptotic search algorithm to determine if date is in list
							# how to ensure every team has a season initialized before adding game
							print('{} seasons for {}'.format(team.season_idx, team.tag))
							team.seasons[team.season_idx-1].add_game(date)
				
				table_body = self.soup.findAll('tbody')
				# from this we get an array of all the table body and header HTML, total of 4 (2 of each)
				table_list = [table_body[0], table_body[7], table_body[8], table_body[15]]
				# table_list[0] -> away basic stats
				# table_list[1] -> away adv stats 
				# table_list[2] -> home basic stats
				# table_list[3] -> home adv stats
			
				for table_idx in range(0,len(table_list)):
					rows = table_list[table_idx].findAll('tr')
					# containers for each team's players and stats
					for row in rows:
						# player names are pulled from header
						name = row.find('th').getText()
						print("Name: {}".format(name))
						# use name to find player_id and insert game stats with corresponding id
						row_data = [td.getText() for td in row.findAll('td')]
						print(row_data)
		else:
			print("Make sure that processTeamHTML & gatherStats have executed to obtain game links...")

	def clearLists(self):
		# makes all lists empty (never try to save or delete after using clearLists)
		self.lists, self.court_list, self.opponent_list, self.result_list, self.score_list, self.oppScore_list, self.streak_list = ([] for i in range(7))

