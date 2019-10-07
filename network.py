from gatherData import Dataset, League, Team, Game
import numpy as np
import datetime

# this is import of simple network implemented in the past, just a framework for understanding not final implementation
class neuralNetwork:

	def __init__(self):
		np.random.seed(1)

		self.synaptic_weights = 2 * np.random.random((6, 1)) - 1

	def sigmoid(self, x):
		return 1 / (1 + np.exp(-x))

	def sigmoid_derivative(self, x):
		return x * (1 - x)

	def train(self, training_inputs, training_outputs, training_iterations):

		for iteration in range(training_iterations):
			output = self.think(training_inputs)
			error = training_outputs - output
			adjustments = np.dot(training_inputs.T, error * self.sigmoid_derivative(output))
			self.synaptic_weights += adjustments

def main():
	d = datetime.datetime.today()
	curr_year = int(d.year)

	dataset = Dataset(curr_year)
	# creates the connection to the sqlite3 database
	dataset.create_connection()
	# get stat names and put them into dataset.stats
	dataset.get_statnames()
	dataset.populate_DB()
	dataset.destroy_connection()
	print(dataset.league.team_dict)

	for team in dataset.league.teams:
		print('{}: '.format(team.tag))
		team.show_seasons()
		team.show_roster()

if __name__ == "__main__":
	main()
	

