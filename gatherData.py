'''This program is intended to gather pertinent data from "basketball-reference.com"
and store it for later use in the network'''

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import re

# gets url for playoff stats from desired team and year
def getPlayoffURL(year, team):
	url = "https://www.basketball-reference.com/teams/{}/{}_games.html#games_playoffs_link".format(team,year)
	
	return url

# returns url of page for individual box scores
# address should always begin with '/boxscores/...'
def getGameURL(address):
	simple_url = "https://www.basketball-reference.com"
	game_url = simple_url + address;
	
	return game_url

# obtains parsed HTML from URL
def getHTML(url):
	print("Getting HTML from URL:{}".format(url))
	html = urlopen(url)
	soup = BeautifulSoup(html, "html.parser")
	
	return soup

#def processHTML(soup):

# somehow we will have to determine starting lineups, this is somewhat
# guarded data so for now hard coding might be easiest solution

year = 2019
team = 'GSW'

url = getPlayoffURL(year, team)
soup = getHTML(url)

# use findAll() to get column headers
soup.findAll('tr', limit=2)

# use getText() to extract the text we need into a list
headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
rows = soup.findAll('tr')[0:]

# determine indeces where we relevant data is located (pseudo-dynamic)
for i in range(0,len(headers)):
	if headers[i] == 'Opponent':
		opponentIndex = i-1
	elif headers[i] == 'Tm':
		scoreIndex = i-1
	elif headers[i] == 'Opp':
		oppscoreIndex = i-1
	elif headers[i] == 'Streak':
		streakIndex = i-1

data = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]
print("Opponent: {} W/L: {} Score: {}-{}".format(data[1][5],data[1][6],data[1][8],data[1][9]))

# this successfully finds all the individual game rows and we move the 
# important data into separate lists
court_list, opponent_list, result_list, score_list, oppScore_list, streak_list = ([] for i in range(6))
for x in range(1,len(data)):
	if not data[x]:
		print("data[{}] list is empty".format(x))
	else:
		court_list.append(data[x][4])
		opponent_list.append(data[x][opponentIndex])
		result_list.append(data[x][6])
		score_list.append(data[x][scoreIndex])
		oppScore_list.append(data[x][oppscoreIndex])
		streak_list.append(data[x][streakIndex])

'''for y in range(0,80):
	print("{} : {} -> {}-{}".format(opponent_list[y], result_list[y], score_list[y], oppScore_list[y]))
'''

''' some important columns to be able to locate:
column 5 OR index 4 -> '' or '@' which shows 
column 6 OR index 5 -> Opponent in form ("City TeamName")
column 7 OR index 6 -> 'W' or 'L' 
column 9 OR index 8 -> Team's Score 
column 10 OR index 9 -> Opponent Score 
column 13 OR index 12 -> Team win streak '''

# we must get the links to the box scores so we can further process this data
links = []
for link in soup.findAll('a', attrs={'href': re.compile("^/boxscores")}):
	links.append(link.get('href'))

# find out how to filter through the reference links to get player stats

# ATTEMPT TO FIND A SPECIFIC BOX SCORE FROM MATCHUP
# game_url = getGameURL(links[1])
# game_soup = getHTML(game_url)

# this provides us with links starting with /boxscores but we must find and add
# the first section of the url FOUND simple htt
# boxScoreURL = 

# exclude columns that are not needed
# headers = headers[1:]
