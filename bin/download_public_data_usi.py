#!/usr/bin/python
import sys
import os
import json
import argparse
from collections import defaultdict
import csv
import pandas as pd
import glob
import shutil
import requests
import yaml
import uuid


def _determine_download_url(usi):
    # Getting the path to the original file
    url = "https://dashboard.gnps2.org/downloadlink"
    params = {"usi": usi}
    r = requests.get(url, params=params)

    if r.status_code == 200:
        download_url = r.text
        return download_url

    return None


def _determine_ms_filename(usi):
    """
    We are going to get the URL and the filename, the URL will be omitted if we can figure it out with an API call
    """

    usi_splits = usi.split(":")
    fileportion = usi_splits[2]

    # Checking if filename is valid extension that we could infer the filename
    lower_fileportion = fileportion.lower()
    if lower_fileportion.endswith(".mzml") or lower_fileportion.endswith(".mzxml") or lower_fileportion.endswith(".mgf"):
        return os.path.basename(fileportion)

    # Checking if we can get the filename from the API
    download_url = _determine_download_url(usi)

    if download_url is None:
        return None

    if "metabolomicsworkbench.org" in download_url:
        # Lets parse the arguments, using urlparse
        from urllib.parse import urlparse, parse_qs
        parsed_params = urlparse(download_url)
        filename = parse_qs(parsed_params.query)['F'][0]

        return os.path.basename(filename)

    # MassIVE and GNPS
    if "massive.ucsd.edu" in download_url:
        # Lets parse the arguments, using urlparse
        from urllib.parse import urlparse, parse_qs
        parsed_params = urlparse(download_url)
        filename = parse_qs(parsed_params.query)['file'][0]

        return os.path.basename(filename)

    # TODO: Work for PRIDE
    # TODO: Work for Metabolights

    return os.path.basename(download_url)

        

def main():
    parser = argparse.ArgumentParser(description='Running library search parallel')
    parser.add_argument('input_download_file', help='input download file, can be a params json from GNPS2 or a tsv file with a usi header')
    parser.add_argument('output_folder', help='output_folder')
    parser.add_argument('output_summary', help='output_summary')
    parser.add_argument('--cache_directory', default=None, help='folder of existing data')
    parser.add_argument('--nestfiles', help='Nest mass spec files in a hashed folder so its not all in the same directory', action='store_true', default=False)
    args = parser.parse_args()

    # checking the input file exists
    if not os.path.isfile(args.input_download_file):
        print("Input file does not exist")
        exit(0)

    # Checking the file extension
    if args.input_download_file.endswith(".yaml"):
        # Loading yaml file
        parameters = yaml.load(open(args.input_download_file), Loader=yaml.SafeLoader)
        usi_list = parameters["usi"].split("\n")
    elif args.input_download_file.endswith(".tsv"):
        df = pd.read_csv(args.input_download_file, sep="\t")
        usi_list = df["usi"].tolist()

    # Cleaning USI list
    usi_list = [usi.lstrip().rstrip() for usi in usi_list]

    output_result_list = []

    # Lets download these files
    for usi in usi_list:
        if len(usi) < 5:
            continue

        output_result_dict = {}
        output_result_dict["usi"] = usi

        # USI Filename
        try:
            target_filename = _determine_ms_filename(usi)
        except:
            continue

        if target_filename is not None:

            if args.nestfiles is False:
                target_path = os.path.join(args.output_folder, target_filename)
            else:
                usi_hash = uuid.uuid3(uuid.NAMESPACE_DNS, usi)
                folder_hash = str(usi_hash)[:2]

                target_dir = os.path.join(args.output_folder, folder_hash)

                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                target_path = os.path.join(target_dir, target_filename)

            output_result_dict["target_path"] = target_path

            # Checking the cache
            if args.cache_directory is not None and os.path.exists(args.cache_directory):
                
                namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                hashed_id = str(uuid.uuid3(namespace, usi)).replace("-", "")

                cache_path = os.path.join(args.cache_directory, hashed_id)
                cache_path = os.path.realpath(cache_path)
                
                cache_filename = cache_path + "-" + target_filename[-50:].rstrip()

                output_result_dict["cache_filename"] = os.path.basename(cache_filename)

                # If we find it, we can create a link to it
                if os.path.exists(cache_filename):
                    print("Found in cache", cache_path)
                    
                    if not os.path.exists(target_path):
                        os.symlink(cache_filename, target_path)
                        output_result_dict["status"] = "EXISTS_IN_CACHE"
                    else:
                        output_result_dict["status"] = "DUPLICATE_FILENAME"
                else:
                    download_url = _determine_download_url(usi)

                    if download_url is None:
                        output_result_dict["status"] = "ERROR"
                    else:
                        # Saving file to cache if we don't
                        r = requests.get(download_url, stream=True)
                        try:
                            with open(os.path.join(args.output_folder, cache_filename), 'wb') as fd:
                                for chunk in r.iter_content(chunk_size=128):
                                    fd.write(chunk)
                                
                            # Creating symlink
                            if not os.path.exists(target_path):
                                os.symlink(cache_filename, target_path)
                                output_result_dict["status"] = "EXISTS_IN_CACHE"
                            else:
                                output_result_dict["status"] = "DUPLICATE_FILENAME"
                        except:
                            # We are likely writing to read only file system for the cache
                            with open(target_path, 'wb') as fd:
                                for chunk in r.iter_content(chunk_size=128):
                                    fd.write(chunk)

                        # Checking the status code
                        if r.status_code == 200:
                            output_result_dict["status"] = "DOWNLOADED_INTO_CACHE"
                        else:
                            # TODO: we should remove the file
                            output_result_dict["status"] = "DOWNLOAD_ERROR"
            else:
                download_url = _determine_download_url(usi)

                if download_url is None:
                    output_result_dict["status"] = "ERROR"
                    
                else:
                    # download in chunks using requests
                    r = requests.get(download_url, stream=True)
                    with open(target_path, 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=128):
                            fd.write(chunk)

                    output_result_dict["status"] = "DOWNLOADED_INTO_OUTPUT_WITHOUT_CACHE"

        else:
            output_result_dict["status"] = "ERROR"

        output_result_list.append(output_result_dict)

    if len(output_result_list) > 0:
        df = pd.DataFrame(output_result_list)
        df.to_csv(args.output_summary, sep="\t", index=False)

if __name__ == "__main__":
    main()
