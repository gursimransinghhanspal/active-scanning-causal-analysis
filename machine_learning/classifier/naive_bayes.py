from sklearn.naive_bayes import GaussianNB

from machine_learning.aux.train_classifier import train_classifier_using_grid_search


def learn(training_data_infile, trained_model_outfile = None, display_metrics: bool = False, gs_verbose: int = 0,
          n_jobs = 1):
	"""
	Trains a Gaussian Naive Bayes classifier

	:param training_data_infile: Csv file containing training data (labeled)
								 • The last column should be training labels
								 • Csv file can contain header (line 1 is skipped)
								 • Use: machine_learning.aux.preprocessor.create_training_dataset

	:param trained_model_outfile: where to save the model
	:param display_metrics: whether to print model metrics or not
	:param gs_verbose: verbosity of GridSearch
	:param n_jobs: GridSearch parallel jobs
	:return:
	"""

	# testing parameters
	params = {}

	return train_classifier_using_grid_search(
		classifier_name = 'Gaussian Naive Bayes',
		classifier_object = GaussianNB,
		gs_params = params,
		training_data_infile = training_data_infile,
		trained_model_outfile = trained_model_outfile,
		display_metrics = display_metrics,
		gs_verbose = gs_verbose,
		n_jobs = n_jobs,
		normalize = False
	)


if __name__ == '__main__':
	pass
