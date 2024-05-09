test:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/ ./data/summary.tsv

test_raw:
	python ./bin/download_public_data_usi.py ./data/test_download_raw.tsv ./data/filedownloads/ ./data/summary.tsv
