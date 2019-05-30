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
# print(headers)
# we must get the links to the box scores so we can further process this data
links = []
for link in soup.findAll('a', attrs={'href': re.compile("^/boxscores")}):
	links.append(link.get('href'))

# game_url = getGameURL(links[1])
# game_soup = getHTML(game_url)

# this provides us with links starting with /boxscores but we must find and add
# the first section of the url FOUND simple htt
# boxScoreURL = 

# exclude columns that are not needed
# headers = headers[1:]

# print(headers)

# bring relevant data into our dataset
rows = soup.findAll('tr')[0:]

data = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]
print(data)









