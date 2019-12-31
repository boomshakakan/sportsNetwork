'''
This program is intended to gather pertinent data from "basketball-reference.com"
and store it for later use in the game prediction network
'''
import sys
from termcolor import colored, cprint
from urllib.request import urlopen
from bs4 import BeautifulSoup
from sqlite3 import Error
import pandas as pd
import sqlite3
import datetime
import re
import os

class Stats():
	def __init__(self):
		self.stats = []

class Player():
	def __init__(self, name, team):
		self.name = name
		self.team = team
		self.stats = []
		

	def add_basicStats(self, stats):
		self.stats = stats

	def add_advStats(self, stats):
		self.stats.extend(stats)
		print("{}: {}".format(len(self.stats), self.stats))
		print("stats added for {}".format(self.name))

	def show_stats(self):
		print(self.stats)

class Roster(Player):
	def __init__(self):
		self.players = []
		self.idx = -1

	def find_player(self, name):
		for player in self.players:
			if (player.name == name):
				return True
		return False

	def get_player(self, name):
		for ctr, player in enumerate(self.players):
			if (player.name == name):
				return ctr
		return -1

	def add_player(self, name, team):
		if (self.find_player(name) == False):
			self.players.append(Player(name, team))
			self.idx = self.idx + 1
			return True
		else:
			return False

	def force_add(self, name, team):
		self.players.append(Player(name, team))

	def show_roster(self):
		for player in self.players:
			print(player.name)

class Game(Roster, Player):
	def __init__(self, date, outcome):
		self.date = date
		self.outcome = outcome # outcome == True when home team wins
		print('Game Initialized with date: {}'.format(self.date))

class Season(Game):
	# games list just holds strings of dates ex. (yyyy/mm/dd)
	# includes any possible playoff games
	# include variables for number of games and year for season
	def __init__(self, year):
		self.games = [] 
		self.year = year

	def set_numGames(self, num_games):
		self.num_games = num_games

	def find_game(self, date):
		if date in self.games:
			return True
		return False

	def add_game(self, date):
		self.games.append(date)
		print('game added: {}'.format(date))

class Team(Season, Game, Player):	
	def __init__(self, tag):
		self.roster = [] # instead of using roster object we just hold list of player names
		self.seasons = []
		self.idx = -1 # idx will represent position in league.teams list 
		self.season_idx = 0
		self.tag = tag
		self.roster_built = False
		print('Team Initialized: '+ self.tag)

	def add_player(self, name):
		if name not in self.roster:
			self.roster.append(name)

	def init_season(self, year):
		# because of the way  game data is pulled need to have a season initialized for every team
		self.seasons.append(Season(year))
		self.season_idx += 1
		print('Season initialized for {}'.format(self.tag))

	def show_seasons(self):
		print("{} Seasons for {}...".format(self.season_idx, self.tag))
		for season in self.seasons:
			print("||| {} |||".format(season.year))
			for date in season.games:
				print(date)

	def show_roster(self):
		print("Roster for {}:".format(self.tag))
		for player_name in self.roster:
			print(player_name)

class League(Team, Season, Game):
	def __init__(self, team_list, year):
		self.teams = []
		self.player_list = []
		self.team_dict = {}
		for x in range(0,len(team_list)):
			self.teams.append(Team(team_list[x]))
			self.teams[x].idx = x
			self.teams[x].init_season(year)
		print('League Initialized with {} teams'.format(len(self.teams)))
	
	def find_player(self, name):
		if name in self.player_list:
			return True
		return False

	def add_player(self, name):
		if (self.find_player(name) == False):
			self.player_list.append(name)
		else:
			print("player already in league list")

	def stat_process(self, roster, name, tag, data):
		flag = roster.add_player(name, tag)
		if (flag):
			roster.players[roster.idx].add_basicStats(data)
		else:
			idx = roster.get_player(name)
			if idx != -1:
				roster.players[idx].add_advStats(data[1:])

class Dataset():
	def __init__(self, curr_year):
		# define tags for teams and initialize empty list containers
		self.curr_year = curr_year
		self.simple_url = "https://www.basketball-reference.com"
		self.team_list = ["GSW", "TOR", "CHI", "DEN", "ATL", "BOS", "CHO", "CLE", "DAL", "DET", "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", \
		"MIN", "BRK", "NOP", "NYK", "ORL", "PHI", "PHO", "POR", "SAS", "SAC", "WAS", "OKC", "UTA"]
		# 19/20 season needs year adjustment
		self.league = League(self.team_list, self.curr_year+1)

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
		year = 2020
		
		if self.conn:
			cur = self.conn.cursor()
			
			for team in self.league.teams:
				cur.execute("INSERT INTO teams ('name') VALUES (?)", (team.tag, ))
				team_id = cur.lastrowid

				# loops for years (curr_year - x)
				for x in range(0, 1):
					self.get_TeamURL(team.tag, year-x)
					self.get_HTML(self.team_url)
					# we process the team page and get a list of links 
					self.process_TeamHTML(team)
					
					if team.roster_built == False:
						self.get_roster(team)

					# sample query to find all players from specified team
					# SELECT * FROM players WHERE team_ID = (SELECT team_ID FROM teams WHERE name = 'CHI');
					for player in team.roster:
						self.insert_player(cur, player, team_id)
					
					# inside of process_box is where we will have to insert our game data to database so we pass cursor
					self.process_BoxHTML(cur, team, year-x)

			self.conn.commit()
		else:
			print("No db connection found...")

	def get_statnames(self):
		# we pick an arbitrary team and use it to find names of stats
		tmp_team = self.league.teams[0]

		self.get_TeamURL(tmp_team.tag, self.curr_year)
		self.get_HTML(self.team_url)
		self.process_TeamHTML(tmp_team)
		self.gather_stats(0)

	def get_tag(self, teamName):
		# given full team name return team's tag OR create dictionary entry for relation
	
		if teamName in self.league.team_dict:
			# print('name already in dictionary')
			# print('Tag is: {}'.format(self.league.team_dict[teamName]))
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
		date_stamp = year + '/' + month + '/' + day
		return date_stamp

	def process_TeamHTML(self, team):
		# parses html from team page and extracts useful data into lists
		# use getText() to extract the text content from first row column headers
		self.links = []
		rows = self.soup.findAll('tr')

		# access to most recent game
		self.lastgameLink = (self.soup.find('a', attrs={'href': re.compile("^/boxscores/[0-9]+")})).get('href')
		
		for link in self.soup.findAll('a', attrs={'href': re.compile("^/boxscores/[0-9]+")})[1:]:
			if (link.getText() == 'Box Score'):
				self.links.append(link.get('href'))

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

	def gather_stats(self, idx):
		# peek at the box score page and pull stat names / self.stats contains two lists
		if self.links != []:
			self.stats = []

			self.get_GameURL(self.links[idx])
			self.get_HTML(self.game_url)

			table_headers = self.soup.findAll('thead')
			# find Basic Box Score Stats
			basicStat = [th.getText() for th in table_headers[0].findAll('th', attrs={'data-over-header': "Basic Box Score Stats"})]
			advStat = [th.getText() for th in table_headers[7].findAll('th', attrs={'data-over-header': "Advanced Box Score Stats"})]

			self.stats = basicStat + advStat[1:]
			print(self.stats)

	def get_roster(self, team):
		# process most recent game link and use to generate team roster
		tag_list, team_list = ([] for i in range(2))

		print("Pulling roster for {}".format(team.tag))
		recent_game = self.links[len(self.links)-1] # latest game
		self.get_GameURL(recent_game)
		self.get_HTML(self.game_url)

		body = self.soup.find('body')
		team_names = [team.getText() for team in body.findAll('a', attrs={'href': re.compile("^/teams/"), 'itemprop': "name"})]

		for name in team_names:
			tag = self.get_tag(name)
			tag_list.append(tag)

			if team.tag == tag:
				self.league.teams[team.idx].roster_built = True
				team_list.append(team)
			else:
				# we could potentially use team_dict if all seasons are pre-processed, not yet
				for x in range(0, len(self.league.teams)):
					if self.league.teams[x].tag == tag:
						self.league.teams[x].roster_built = True
						team_list.append(self.league.teams[x])
	
		table_body = self.soup.findAll('tbody')
		# hard coding these values may lead to issues 
		table_list = [table_body[0], table_body[8]]
		
		# table_list[0] -> away basic stats 
		# table_list[1] -> home basic stats

		for table_idx in range(0,len(table_list)):
			rows = table_list[table_idx].findAll('tr')
			# containers for each team's players and stats
			for row in rows:
				# player names are pulled from header and stats skimmed from table
				name = row.find('th').getText()

				if name != 'Reserves':
					if table_idx == 0:
						# away team
						# we add player to team roster and overall league list
						if name not in self.league.teams[team_list[table_idx].idx].roster:
							self.league.teams[team_list[table_idx].idx].add_player(name)
							self.league.add_player(name)
					else:
						# home team
						if name not in self.league.teams[team_list[table_idx].idx].roster:
							self.league.teams[team_list[table_idx].idx].add_player(name)
							self.league.add_player(name)

	def insert_player(self, cur, name, team_id):
		# performs insertions into players table and returns player_ID
		cur.execute('''INSERT INTO players (team_id, name) VALUES (?,?)''', (team_id, name))
		return cur.lastrowid

	def insert_gameStat(self, cur, roster, game_id):
		# when called you are passing a full roster with game_stats
		# adds to player table if no entry is found for listed player
		for player in roster.players:
			cur.execute('''SELECT player_id FROM players WHERE name = ?''', (player.name,))
			tmp_id = cur.fetchone()

			print("{} -> {}".format(player.name, tmp_id))

			if tmp_id is None:
				# since it was not added when rosters were found we add with team_id = -1 indicating that the player may
				# not still play with this team
				player_id = self.insert_player(cur, player.name, -1)
				print("# stats -> {}".format(len(player.stats)))
				
				'''
				cur.execute("INSERT INTO game_stats (game_ID, player_ID, MP, FG, FGA, FGP, TP, TPA, TPP, FT, FTA, FTP,\
					ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS, plusMINUS, TSP, eFGP, TPAr, FTr, ORBP, DRBP, TRBP, ASTP,\
						STLP, BLKP, TOVP, USGP, ORtg, DRtg) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,\
							?,?,?,?,?,?,?,?,?,?)", (game_id, player_id, player.stats[0], player.stats[1], player.stats[2], \
								player.stats[3], player.stats[4], player.stats[5], player.stats[6], player.stats[7], player.stats[8], \
									player.stats[9], player.stats[10], player.stats[11], player.stats[12], player.stats[13], player.stats[14], \
										player.stats[15], player.stats[16], player.stats[17], player.stats[18], player.stats[19], player.stats[20], \
											player.stats[21], player.stats[22], player.stats[23], player.stats[24], player.stats[25], player.stats[26], \
												player.stats[27], player.stats[28], player.stats[29], player.stats[30], player.stats[31], player.stats[32], \
													player.stats[33]))
				'''

				sql = '''INSERT INTO game_stats (MP, FG, FGA, FGP, TP, TPA, TPP, FT, FTA, FTP,\
					ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS, plusMINUS, TSP, eFGP, TPAr, FTr, ORBP, DRBP, TRBP, ASTP,\
						STLP, BLKP, TOVP, USGP, ORtg, DRtg) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,\
							?,?,?,?,?,?,?,?)'''

				cur.execute(sql, player.stats)
					 
				# here insert game_stat for this newly inserted payer
			else:
				player_id = tmp_id[0]

				# insert game_stat
			# cur.execute('''INSERT INTO game_stats (team_id, name) VALUES (?,?)''', (team_id, player))

	def process_BoxHTML(self, cur, team, year):
		# parses html from box score page and pulls useful data from a single game link
		# you must execute processTeamHTML & gatherStats to obtain links and stat names before calling this function
		if self.links:
			# loop over all of team's season game links in self.links
			print(len(self.links))
			for idx in range(0,1):
				tag_list = []
				basic_stat = []
				adv_stat = []
				away_roster = Roster()
				home_roster = Roster()
				home_won = False

				self.get_GameURL(self.links[idx])
				self.get_HTML(self.game_url)
				date = self.get_date(self.links[idx])
				
				if (team.seasons[team.season_idx-1].find_game(date) == False):
					
					body = self.soup.find('body')
					team_names = [name.getText() for name in body.findAll('a', attrs={'href': re.compile("^/teams/"), 'itemprop': "name"})]
					scores = [score.getText() for score in body.findAll('div', attrs={'class': "scores"})]

					table_headers = self.soup.findAll('thead')
					# find Basic Box Score Stats

					basic_stat = [th.getText() for th in table_headers[0].findAll('th', attrs={'data-over-header': "Basic Box Score Stats"})]

					adv_idx = 0
					while adv_stat == []:
						# basic_stat = [th.getText() for th in table_headers[x].findAll('th', attrs={'data-over-header': "Basic Box Score Stats"})]
						
						adv_stat = [th.getText() for th in table_headers[adv_idx].findAll('th', attrs={'data-over-header': "Advanced Box Score Stats"})]

						print("index: {} \nbasic stats -> {}\nadv stats -> {}".format(adv_idx, basic_stat, adv_stat))
						adv_idx = adv_idx + 1
						
					'''
					basic_stat = [th.getText() for th in table_headers[0].findAll('th', attrs={'data-over-header': "Basic Box Score Stats"})]
					test_stat = [th.getText() for th in table_headers[6].findAll('th', attrs={'data-over-header': "Advanced Box Score Stats"})]
					adv_stat = [th.getText() for th in table_headers[7].findAll('th', attrs={'data-over-header': "Advanced Box Score Stats"})]

					print("basic stats -> {}: {}".format(len(basic_stat), basic_stat))
					print("adv stats -> {}: {}".format(len(adv_stat), adv_stat))
					''' 

					if (scores[0] < scores[1]):
						home_won = True
					
					for name in team_names:
						# get tag from team name
						tag = self.get_tag(name)
						tag_list.append(tag)
						for tmp_team in self.league.teams:
							if tag == tmp_team.tag:
								# use a better asymptotic search algorithm to determine if date is in list
								# how to ensure every team has a season initialized before adding game
								print('{} seasons for {}'.format(tmp_team.season_idx, tmp_team.tag))
								tmp_team.seasons[tmp_team.season_idx-1].add_game(date)
					
					cur.execute('INSERT INTO games (away_team, home_team, game_day, home_won) VALUES (?,?,?,?)', (tag_list[0], tag_list[1], date, home_won))
					game_id = cur.lastrowid
					
					table_body = self.soup.findAll('tbody')
					table_list = [table_body[0], table_body[7], table_body[8], table_body[15]]
					'''
					table_list[0] -> away basic stats
					table_list[1] -> away adv stats
					table_list[2] -> home basic stats
					table_list[3] -> home adv stats
					'''
				
					for table_idx in range(0, len(table_list)):
						rows = table_list[table_idx].findAll('tr')
						# containers for each team's players and stats
						for idx, row in enumerate(rows):
							name = row.find('th').getText()
							if idx != 5:
								# use name to find player_id and insert game stats with corresponding id
								row_data = [td.getText() for td in row.findAll('td')]
								if name != 'Reserves':
									if table_idx < 2:
										# away team
										self.league.stat_process(away_roster, name, tag_list[0], row_data)
									else:
										# home team
										self.league.stat_process(home_roster, name, tag_list[1], row_data)

								if (self.league.find_player(name) == False):
									self.league.add_player(name)

					# write function to parse roster object insert stats
					self.insert_gameStat(cur, away_roster, game_id)
					self.insert_gameStat(cur, home_roster, game_id)

		else:
			print("Make sure that processTeamHTML & gatherStats have executed to obtain game links...")

	def clearLists(self):
		# makes all lists empty (never try to save or delete after using clearLists)
		self.lists, self.court_list, self.opponent_list, self.result_list, self.score_list, self.oppScore_list, self.streak_list = ([] for i in range(7))
