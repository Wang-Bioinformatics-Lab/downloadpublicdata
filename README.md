This tool is meant to make it easy to download mass spectrometry files from public and private repositories using the universal spectrum identifiers. Currently it supports GNPS/MassIVE, GNPS2, Metabolights, Metabolomics Workbench, and PRIDE.

## Setup

```sh
pip install -r requirements.txt
```

## Running

```sh
python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/ ./data/summary.tsv
```

or to short cut this
```sh
make test
```


### Usage Examples

#### Example 1: Basic Usage

**Command:**

```sh
python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/filedownloads_flat/ ./data/summary.tsv
```

**Description:**

This command downloads the public data specified in the `test_download.tsv` file and saves the files in the `filedownloads_flat` directory. A summary of the download is saved in `summary.tsv`.

**Arguments:**

- `./data/test_download.tsv`: The input download file. This can be a parameters JSON from GNPS2 or a TSV file with a USI header.
- `./data/filedownloads/filedownloads_flat/`: The output folder where the downloaded files will be stored.
- `./data/summary.tsv`: The output summary file that will contain the summary of the downloads.

#### Example 2: Recreate Directory Structure

**Command:**

```sh
python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/filedownloads_recreate/ ./data/summary.tsv --nestfiles 'recreate'
```

**Description:**

This command downloads the public data specified in the `test_download.tsv` file and saves the files in the `filedownloads_recreate` directory, recreating the original directory structure. A summary of the download is saved in `summary.tsv`.

**Arguments:**

- `./data/test_download.tsv`: The input download file.
- `./data/filedownloads/filedownloads_recreate/`: The output folder where the downloaded files will be stored.
- `./data/summary.tsv`: The output summary file.
- `--nestfiles 'recreate'`: Specifies that the downloaded files should be stored in a directory structure that recreates the original structure.

#### Example 3: Nesting Files in Hashed Folders

**Command:**

```sh
python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/filedownloads_nest/ ./data/summary.tsv --nestfiles 'nest'
```

**Description:**

This command downloads the public data specified in the `test_download.tsv` file and saves the files in the `filedownloads_nest` directory, nesting them in hashed folders to avoid placing all files in the same directory. A summary of the download is saved in `summary.tsv`.

**Arguments:**

- `./data/test_download.tsv`: The input download file.
- `./data/filedownloads/filedownloads_nest/`: The output folder where the downloaded files will be stored.
- `./data/summary.tsv`: The output summary file.
- `--nestfiles 'nest'`: Specifies that the downloaded files should be nested in hashed folders.

**Explanation of Hashed Folders:**

When you have a large number of files (e.g., 10,000), placing all of them in a single directory can be inefficient. Some file systems have limits on the number of files per folder, and operations like `ls` can become very slow. Using hashed folders mitigates this by creating a directory tree, where files are distributed across multiple folders. For example:

- `data/aa/file.mzML`
- `data/ab/file2.mzML`

This creates 256 folders at the first level, significantly reducing the number of files per folder and improving file system performance.

#### Example 4: Using Cache Directory

**Command:**

```sh
python ./bin/download_public_data_usi.py ./data/test_download.tsv ./data/filedownloads/ ./data/summary.tsv --cache_directory ./data/cache
```

**Description:**

This command downloads the public data specified in the `test_download.tsv` file and saves the files in the `filedownloads` directory. A summary of the download is saved in `summary.tsv`. The `cache_directory` option is used to specify a folder containing existing data, which can speed up the download process if some of the data is already available in the cache.

**Arguments:**

- `./data/test_download.tsv`: The input download file.
- `./data/filedownloads/`: The output folder where the downloaded files will be stored.
- `./data/summary.tsv`: The output summary file.
- `--cache_directory ./data/cache`: Specifies a folder containing existing data to use as a cache.

#### Example 5: Basic Usage with Raw USI Input

**Command:**

```sh
python ./bin/download_public_data_usi.py ./data/test_download_raw.tsv ./data/filedownloads/test_raw ./data/summary.tsv --raw_usi_input
```

**Description:**

This command downloads the public data specified in the `test_download_raw.tsv` file and saves the files in the `test_raw` directory. A summary of the download is saved in `summary.tsv`.

**Arguments:**

- `./data/test_download_raw.tsv`: The input download file.
- `./data/filedownloads/test_raw`: The output folder where the downloaded files will be stored.
- `./data/summary.tsv`: The output summary file.
- `--raw_usi_input`: Specifies that the `input_download_file` is a raw USI file.

#### Example 6: Disabling Conversion

**Command:**

```sh
python ./bin/download_public_data_usi.py ./data/test_download_raw_trouble.tsv ./data/filedownloads/test_raw_trouble ./data/summary.tsv --noconversion
```

**Description:**

This command downloads the public data specified in the `test_download_raw_trouble.tsv` file and saves the files in the `test_raw_trouble` directory. A summary of the download is saved in `summary.tsv`. The `--noconversion` option is used to turn off file conversion and download the full raw file.

**Arguments:**

- `./data/test_download_raw_trouble.tsv`: The input download file.
- `./data/filedownloads/test_raw_trouble`: The output folder where the downloaded files will be stored.
- `./data/summary.tsv`: The output summary file.
- `--noconversion`: Turn off file conversion and download the full raw file.

### Additional Options

- **`--cache_directory`**

  - **Usage:** `--cache_directory /path/to/cache`
  - **Description:** Specifies a folder containing existing data to use as a cache. This can speed up the download process if some of the data is already available.

- **`--progress`**

  - **Usage:** `--progress`
  - **Description:** Show a progress bar during the download process. Useful for monitoring the progress of large downloads.

- **`--extension_filter`**

  - **Usage:** `--extension_filter '.mzML;.mgf'`
  - **Description:** Filter the downloaded files to only include those with the specified extensions. Should be formatted as a semicolon-separated list.

- **`--raw_usi_input`**

  - **Usage:** `--raw_usi_input`
  - **Description:** Specify if the `input_download_file` is a raw USI file.

- **`--noconversion`**

  - **Usage:** `--noconversion`
  - **Description:** Turn off file conversion and download the full raw file.

---

These examples and explanations should help users understand how to use the different options available with the command-line tool for various scenarios.
