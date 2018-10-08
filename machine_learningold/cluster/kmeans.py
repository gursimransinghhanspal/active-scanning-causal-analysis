import os

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.cluster import adjusted_mutual_info_score, adjusted_rand_score, completeness_score, \
	fowlkes_mallows_score, homogeneity_score, normalized_mutual_info_score, v_measure_score

from machine_learning.aux.constants import get_cluster_label_header, get_dataset_label_header, \
	get_processed_data_file_header_segregation
from machine_learning.aux.helpers import read_csv_file, read_dataset_csv_file_as_np_arrays


def cluster(in_file: str, out_file: str):
	in_file = os.path.abspath(in_file)
	out_file = os.path.abspath(out_file)

	# read dataset
	x_test, target_y, _ = read_dataset_csv_file_as_np_arrays(in_file, for_training = True)

	kmeans = KMeans(n_clusters = 5, n_init = 100, max_iter = 100)
	kmeans.fit(x_test)

	print('• Percentage of different causes in data:')
	bincount_percent = target_y.shape[0]
	# for x, y in zip(list(range(len(bincount_percent))), bincount_percent):
	# 	print(x, '\t', y)
	# print(bincount_percent)

	# print('• Percentage of data in clusters:')
	# bincount_percent = list(np.divide(np.bincount(kmeans.labels_), kmeans.labels_.shape[0]))
	# for x, y in zip(list(range(len(bincount_percent))), bincount_percent):
	# 	print(x, '\t', y)
	# print()

	for cluster_id in range(5):
		labels = list()
		for id, lab in enumerate(target_y):
			if kmeans.labels_[id] == cluster_id:
				labels.append(lab)
		print(np.divide(np.bincount(np.array(labels)), len(labels)))

	adj_mutual_score = adjusted_mutual_info_score(target_y, kmeans.labels_)
	print('adjusted_mutual_info_score:', adj_mutual_score)
	adj_rand_score = adjusted_rand_score(target_y, kmeans.labels_)
	print('adjusted_rand_score:', adj_rand_score)
	complete_score = completeness_score(target_y, kmeans.labels_)
	print('completeness_score:', complete_score)
	fowlkes_score = fowlkes_mallows_score(target_y, kmeans.labels_)
	print('fowlkes_mallows_score:', fowlkes_score)
	hom_score = homogeneity_score(target_y, kmeans.labels_)
	print('homogeneity_score:', hom_score)
	norm_mutual_score = normalized_mutual_info_score(target_y, kmeans.labels_)
	print('normalized_mutual_info_score:', norm_mutual_score)
	v_score = v_measure_score(target_y, kmeans.labels_)
	print('v_measure_score:', v_score)
	print()

	# data = read_csv_file(in_file)
	# # scatter_matrix(data)
	# parallel_coordinates(x_test, data[])
	# plt.show()
	# plt.savefig('/Users/gursimran/Desktop/parallel_coord.png', format = 'png', dpi = 500)

	dataset_df = read_csv_file(in_file)
	dataset_df[get_cluster_label_header()] = kmeans.labels_
	head_features, head_training, head_properties = get_processed_data_file_header_segregation(for_training = True)
	req_columns = head_features + head_properties + head_training
	req_columns.append(get_dataset_label_header())
	req_columns.append(get_cluster_label_header())
	dataset_df.to_csv(out_file, mode = 'w', columns = req_columns, header = True, index = False)


if __name__ == '__main__':
	cluster(
		'/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase__python/machine_learning/data/cluster/cluster_merged.csv',
		'/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase__python/machine_learning/output/kmeans2.csv'
	)
