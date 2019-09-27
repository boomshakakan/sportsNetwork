DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS game_stats;
DROP TABLE IF EXISTS adv_stats;

CREATE TABLE IF NOT EXISTS teams (
	team_ID INTEGER PRIMARY KEY AUTOINCREMENT,
	name VARCHAR(5)
	);

CREATE TABLE IF NOT EXISTS players (
	player_ID INTEGER PRIMARY KEY AUTOINCREMENT,
	team_ID INTEGER,
	name VARCHAR(40),
	FOREIGN KEY (team_ID) REFERENCES teams(team_ID)
	);

CREATE TABLE IF NOT EXISTS games (
	game_ID INTEGER PRIMARY KEY AUTOINCREMENT,
	home_team VARCHAR(5),
	away_team VARCHAR(5),
	game_day DATE
	);

CREATE TABLE IF NOT EXISTS game_stats (
	game_ID INTEGER,
	player_ID INTEGER,
	stats INTEGER,
	FOREIGN KEY (game_ID) REFERENCES games(game_ID)
	FOREIGN KEY (player_ID) REFERENCES players(player_ID)
	);

CREATE TABLE IF NOT EXISTS adv_stats (
	game_ID INTEGER,
	player_ID INTEGER
	);
