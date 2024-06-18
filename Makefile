test_mzml:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/filedownloads_flat/ ./data/summary.tsv

test_mzml_recreate:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/filedownloads_recreate/ ./data/summary.tsv --nestfiles 'recreate'

test_mzml_nest:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/filedownloads_nest/ ./data/summary.tsv --nestfiles 'nest'


test_mzml_MWB:
	python ./bin/download_public_data_usi.py ./data/uniquemri_MWB_10000.csv ./data/filedownloads/filedownloads_recreate_MWB/ ./data/summary_MWB.tsv --nestfiles 'recreate'

test_mzml_MTBLS:
	python ./bin/download_public_data_usi.py ./data/uniquemri_MTBLS_10000.csv ./data/filedownloads/filedownloads_recreate_MTBLS/ ./data/summary_MTBLS.tsv --nestfiles 'recreate'

test_mzml_cache:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/ ./data/summary.tsv --cache_directory ./data/cache

test_raw_small:
	python ./bin/download_public_data_usi.py ./data/test_download_raw_small.tsv ./data/filedownloads/ ./data/summary.tsv

test_raw:
	python ./bin/download_public_data_usi.py ./data/test_download_raw.tsv ./data/filedownloads/ ./data/summary.tsv

test:
	python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/ ./data/summary.tsv
	
test_mzml_recreate_failed:
	python ./bin/download_public_data_usi.py ./data/test_download_with_failed.tsv ./data/filedownloads/filedownloads_recreate_with_failed/ ./data/summary.tsv --nestfiles 'recreate'

