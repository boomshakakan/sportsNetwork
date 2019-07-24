
CREATE TABLE IF NOT EXISTS teams (
	team_ID INTEGER,
	name VARCHAR(5),
	PRIMARY KEY (team_ID)
	);

CREATE TABLE IF NOT EXISTS players (
	player_ID INTEGER,
	name VARCHAR(40),
	team_ID INTEGER,
	FOREIGN KEY (team_ID) REFERENCES teams(team_ID)
	);

CREATE TABLE IF NOT EXISTS games (
	game_ID INTEGER,
	home_team VARCHAR(5),
	away_team VARCHAR(5),
	day DATE,
	PRIMARY KEY (game_ID)
	);

CREATE TABLE IF NOT EXISTS game_stats (
	game_ID INTEGER,
	player_ID INTEGER,
	FOREIGN KEY (game_ID) REFERENCES games(game_ID)
	FOREIGN KEY (player_ID) REFERENCES players(player_ID)
	);
