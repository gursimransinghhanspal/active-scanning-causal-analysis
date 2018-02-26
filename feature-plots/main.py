import data_pre_processing as dpp
import feature_importance_plot as fip

training_data = dpp.get_training_data()
data = training_data['data']
target = training_data['target']
features = training_data['features']
features_entities = training_data['features_entities']
target_names = training_data['target_names']

for feature_idx, feature in enumerate(features):
	for target_val, target_name in enumerate(target_names):
		if type(data[0, feature_idx]) is int or type(data[0, feature_idx]) is float:
			fip.plot_graph(data[:, feature_idx], target, feature, True,
			               features_entities[feature], target_name, target_val)
		else:
			fip.plot_graph(data[:, feature_idx], target, feature, False,
			               features_entities[feature], target_name, target_val)
