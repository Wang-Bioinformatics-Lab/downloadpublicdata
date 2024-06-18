test_mzml:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/filedownloads_flat/ ./data/summary.tsv

test_mzml_recreate:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/filedownloads_recreate/ ./data/summary.tsv --nestfiles 'recreate'

test_mzml_nest:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/filedownloads_nest/ ./data/summary.tsv --nestfiles 'nest'

test_mzml_cache:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/ ./data/summary.tsv --cache_directory ./data/cache

test_raw_small:
	python ./bin/download_public_data_usi.py ./data/test_download_raw_small.tsv ./data/filedownloads/ ./data/summary.tsv

test_raw:
	python ./bin/download_public_data_usi.py ./data/test_download_raw.tsv ./data/filedownloads/ ./data/summary.tsv

test:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/ ./data/summary.tsv
	
