from gatherData import Dataset
import numpy as np

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

if __name__ == "__main__":
	
	year = 2019
	team = 'GSW'

	dataset = Dataset()
	
	# dataset.createConnection()
	# dataset.createTables()

	#dataset.process10Years()
	dataset.getTeamURL(team, year)
	dataset.getHTML(dataset.team_url)
	dataset.processTeamHTML()

	dataset.gatherStats()
	dataset.processBoxHTML()
	# dataset.destroyConnection()
	# dataset.deleteDB()

