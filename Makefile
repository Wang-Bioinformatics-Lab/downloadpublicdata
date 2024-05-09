test_mzml:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/ ./data/summary.tsv

test_mzml_cache:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/ ./data/summary.tsv --cache_directory ./data/cache

test_raw:
	python ./bin/download_public_data_usi.py ./data/test_download_raw.tsv ./data/filedownloads/ ./data/summary.tsv
