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

def main():
	dataset = Dataset()

	team = 'GSW'
	year = 2019
	
	dataset.createConnection()
	dataset.getTeamURL(team, year)
	dataset.getHTML(dataset.team_url)
	# process the HTML from passed url
	dataset.processTeamHTML()
	dataset.gatherStats()
	dataset.createTeams()
	dataset.processBoxHTML()

	dataset.destroyConnection()

if __name__ == "__main__":
	main()
	

