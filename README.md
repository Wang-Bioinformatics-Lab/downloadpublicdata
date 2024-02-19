This tool is meant to make it easy to download mass spectrometry files from public and private repositories using the universal spectrum identifiers. Currently it supports GNPS/MassIVE, GNPS2, Metabolights, Metabolomics Workbench, and PRIDE. 

## Setup

```
pip install -r requirements.txt
```

## Running

```
python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/ ./data/summary.tsv
```

or to short cut this
```
make test
```
