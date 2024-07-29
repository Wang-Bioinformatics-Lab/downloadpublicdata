test_mzml:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/filedownloads_flat/ ./data/summary.tsv

test_mzml_recreate:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/filedownloads_recreate/ ./data/summary.tsv --nestfiles 'recreate'

test_too_small_files:
	python ./bin/download_public_data_usi.py ./data/test_fail_too_small.tsv ./data/filedownloads/filedownloads_recreate/test_fail_too_small/ ./data/summary_test_fail_too_small.tsv --nestfiles 'recreate'

test_mzml_nest:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/filedownloads_nest/ ./data/summary.tsv --nestfiles 'nest'

test_mzml_cache:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/ ./data/summary.tsv --cache_directory ./data/cache

test_mzml_cache_small:
	python ./bin/download_public_data_usi.py ./data/test_download_small.tsv ./data/filedownloads/ ./data/summary.tsv --cache_directory ./data/cache

test_mzml_dataset_cache_small:
	python ./bin/download_public_data_usi.py ./data/test_download_small.tsv \
	./data/filedownloads/ ./data/summary.tsv \
	--cache_directory ./data/cache \
	--existing_dataset_directory /data/datasets/server


test_raw_small:
	python ./bin/download_public_data_usi.py ./data/test_download_raw_small.tsv ./data/filedownloads/test_raw_small ./data/summary.tsv

test_raw:
	python ./bin/download_public_data_usi.py ./data/test_download_raw.tsv ./data/filedownloads/test_raw ./data/summary.tsv

test_raw_trouble:
	python ./bin/download_public_data_usi.py \
	./data/test_download_raw_trouble.tsv \
	./data/filedownloads/test_raw_trouble \
	./data/summary.tsv

test_raw_trouble_noconversion:
	python ./bin/download_public_data_usi.py \
	./data/test_download_raw_trouble.tsv \
	./data/filedownloads/test_raw_trouble \
	./data/summary.tsv \
	--noconversion

test_invalid:
	python ./bin/download_public_data_usi.py ./data/test_download_invalid.tsv ./data/filedownloads/test_invalid ./data/summary.tsv

test:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/ ./data/summary.tsv
	

clean:
	rm data/cache/* -r | true
	rm data/filedownloads/* -r | true
	rm data/summary.tsv | true
