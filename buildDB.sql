
CREATE TABLE IF NOT EXISTS teams (
	team_ID INT,
	name VARCHAR(5),
	PRIMARY KEY (team_ID)
	);

CREATE TABLE IF NOT EXISTS players (
	player_ID INT,
	team_ID INT,
	name VARCHAR(40),
	PRIMARY KEY (player_ID),
	FOREIGN KEY (team_ID) REFERENCES teams(team_ID)
	);

CREATE TABLE IF NOT EXISTS games (
	game_ID INT,
	home_team VARCHAR(5),
	away_team VARCHAR(5),
	day DATE,
	PRIMARY KEY (game_ID)
	);

CREATE TABLE IF NOT EXISTS game_stats (
	game_ID INT,
	player_ID INT,
	stats INT,
	FOREIGN KEY (game_ID) REFERENCES games(game_ID)
	FOREIGN KEY (player_ID) REFERENCES players(player_ID)
	);
