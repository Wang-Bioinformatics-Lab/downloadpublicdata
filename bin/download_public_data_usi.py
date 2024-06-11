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
from tqdm import tqdm
import warnings
import time
from sanitize_filename import sanitize

DATASET_CACHE_URL_BASE = "https://datasetcache.gnps2.org"
#DATASET_CACHE_URL_BASE = "http://169.235.26.140:5234"

def _determine_download_url(usi):
    # Getting the path to the original file
    
    # TODO: this likely shoudl be in the datasetcache as well as the dashboard so there is redundancy
    url = "https://dashboard.gnps2.org/downloadlink"
    params = {"usi": usi}
    r = requests.get(url, params=params)

    if r.status_code == 200:
        download_url = r.text
        return download_url

    return None

def _determine_foldername(usi):
    """
    We are going to get the folder name that contains the datasetid together with the original folder structure in the usi
    """ 
    usi_splits = usi.split(":")
    datasetid = usi_splits[1]
    fileportion = usi_splits[2]
    folder_name = os.path.dirname(fileportion)
    dataid_folder = os.path.join(datasetid, folder_name)
    return dataid_folder


def _determine_ms_filename(usi):
    """
    We are going to get the URL and the filename, the URL will be omitted if we can figure it out with an API call
    """

    usi_splits = usi.split(":")
    fileportion = usi_splits[2]

    # Checking if filename is valid extension that we could infer the filename
    lower_fileportion = fileportion.lower()
    if lower_fileportion.endswith(".mzml") or lower_fileportion.endswith(".mzxml") or lower_fileportion.endswith(".mgf") or \
        lower_fileportion.endswith(".d") or lower_fileportion.endswith(".wiff") or lower_fileportion.endswith(".raw"):
        fileportion = os.path.basename(fileportion)

        # make this safe on disk
        fileportion = sanitize(fileportion)

        return fileportion

    # Checking if we can get the filename from the API
    download_url = _determine_download_url(usi)

    print(download_url)

    if download_url is None:
        return None

    if "metabolomicsworkbench.org" in download_url:
        # Lets parse the arguments, using urlparse
        from urllib.parse import urlparse, parse_qs
        parsed_params = urlparse(download_url)
        filename = parse_qs(parsed_params.query)['F'][0]

        filename = os.path.basename(filename)

        # make this safe on disk
        filename = sanitize(filename)

        return filename

    # MassIVE and GNPS
    if "massive.ucsd.edu" in download_url:
        # Lets parse the arguments, using urlparse
        from urllib.parse import urlparse, parse_qs
        parsed_params = urlparse(download_url)
        filename = parse_qs(parsed_params.query)['file'][0]

        filename = os.path.basename(filename)

        # make this safe on disk
        filename = sanitize(filename)

        return filename

    # TODO: Work for PRIDE
    # TODO: Work for Metabolights

    return os.path.basename(download_url)

def _download(mri, target_filename, datafile_extension):
    # checking filename extension
    filename_without_extension, file_extension = os.path.splitext(target_filename)

    if datafile_extension.lower() == ".mzml":
        return _download_mzml(mri, target_filename)
    elif datafile_extension.lower() == ".d":
        return _download_vendor(mri, target_filename)
    elif datafile_extension.lower() == ".wiff":
        return _download_vendor(mri, target_filename)
    elif datafile_extension.lower() == ".raw":
        return _download_vendor(mri, target_filename)
    else:
        raise Exception("Unsupported")
    
    return 0

def _download_mzml(usi, target_filename):
    # here we don't need to do any conversion and can get directly from the source
    download_url = _determine_download_url(usi)

    r = requests.get(download_url, stream=True)
    with open(target_filename, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

    return 0

def _determine_target_subfolder(usi):
    # to determine the target subfolder based on the source of the dataset
    # a dataset starts with "MSV" goes to massive subfolder, a dataset starts with "MTBLS" goes to MTBLS subfolder 
    # and a dataset starts with "ST" goes to ST subfoldre
    target_subfolder = "other"
    if usi.startswith("mzspec:MSV"):
        target_subfolder = "MassIVE"
    elif usi.startswith("mzspec:MTBLS"):
        target_subfolder = "MTBLS"
    elif usi.startswith("mzspec:ST"):
        target_subfolder = "ST"
    else:
        target_subfolder = "other"

    return target_subfolder

    
def _download_vendor(mri, target_filename):
    # we do need to do conversion so we'll hit the conversion service to 
    convert_request_url = "{}/convert/request".format(DATASET_CACHE_URL_BASE)
    params = {}
    params["mri"] = mri

    r = requests.get(convert_request_url, params=params)

    # waiting for the status
    convert_status_url = "{}/convert/status".format(DATASET_CACHE_URL_BASE)

    # lets try waiting 5 min
    for i in range(10):
        r = requests.get(convert_status_url, params=params)
        if r.status_code == 200:
            if r.json()["status"] == True:
                break
            else:
                time.sleep(30)
        else:
            time.sleep(30)

    # Lets download
    download_url = "{}/convert/download".format(DATASET_CACHE_URL_BASE)

    r = requests.get(download_url, params=params, stream=True)
    if r.status_code == 200:
        with open(target_filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
    else:
        print("CONVERSION not ready")
        return "CONVERSION NOT READY"

    return "CONVERTED"

def download_helper(usi, args, extension_filter=None):
    try:
        if len(usi) < 5:
            return None
    
        output_result_dict = {}
        output_result_dict["usi"] = usi
        target_filename = None # This is the target converted filename
        mri_original_extension = None

        # USI Filename
        try:
            ms_filename = _determine_ms_filename(usi)
            target_subfolder_name = _determine_target_subfolder(usi)
            # Filtering extensions
            if extension_filter is not None:
                if not ms_filename.lower().endswith(extension_filter):
                    return None
                
            # Here we determine the actual extension of the ms_filename
            filename_without_extension, file_extension = os.path.splitext(ms_filename)

            mri_original_extension = file_extension
            #target_filename = ms_filename + ".mzML"
            target_filename = ms_filename 
        except:
            return None

        if target_filename is not None:
            # add data source folder to output_folder
            target_folder = os.path.join(args.output_folder, target_subfolder_name) 
            # if args.nestfiles is nest:
            if args.nestfiles == "nest":
                usi_hash = uuid.uuid3(uuid.NAMESPACE_DNS, usi)
                folder_hash = str(usi_hash)[:2]

                #target_dir = os.path.join(args.output_folder, folder_hash)
                target_dir = os.path.join(target_folder, folder_hash)

                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                target_path = os.path.join(target_dir, target_filename)
            elif args.nestfiles == "recreate":
                # recreate the folder structure
                dataset_folder =  _determine_foldername(usi)
                #target_dir = os.path.join(args.output_folder, dataset_folder)
                target_dir = os.path.join(target_folder, dataset_folder)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                target_path = os.path.join(target_dir, target_filename)
                

            else: # flat as default
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)

                target_path = os.path.join(target_folder, target_filename)


            output_result_dict["target_path"] = target_path

            # Checking the cache
            if args.cache_directory is not None and os.path.exists(args.cache_directory):

                namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                hashed_id = str(uuid.uuid3(namespace, usi)).replace("-", "")

                cache_path = os.path.join(args.cache_directory, hashed_id)
                cache_path = os.path.realpath(cache_path)

                cache_filename = cache_path + "-" + target_filename[-50:].rstrip()

                output_result_dict["cache_filename"] = os.path.basename(cache_filename)

                # If we find it in the cache, we can create a link to it
                if os.path.exists(cache_filename):
                    print("Found in cache", cache_path)

                    if not os.path.exists(target_path):
                        os.symlink(cache_filename, target_path)
                        output_result_dict["status"] = "EXISTS_IN_CACHE"
                    else:
                        output_result_dict["status"] = "EXISTS_IN_OUTPUT"
                else:
                    download_url = _determine_download_url(usi)

                    if download_url is None:
                        output_result_dict["status"] = "ERROR"
                    else:
                        # Saving file to cache if we don't
                        
                        try:
                            cache_filename = os.path.join(args.output_folder, cache_filename)
                            
                            _download(usi, cache_filename, mri_original_extension)

                            # Creating symlink
                            if not os.path.exists(target_path):
                                os.symlink(cache_filename, target_path)
                                output_result_dict["status"] = "EXISTS_IN_CACHE"
                            else:
                                output_result_dict["status"] = "EXISTS_IN_OUTPUT"
                        except KeyboardInterrupt:
                            raise

                        except:
                            # We are likely writing to read only file system for the cache
                            try:
                                _download(usi, target_path, mri_original_extension)
                            except KeyboardInterrupt:
                                raise
                            except:
                                output_result_dict["status"] = "DOWNLOAD_ERROR"
                            
            else:
                # if the target path file is already there, then we don't need to do anything
                if os.path.exists(target_path):
                    output_result_dict["status"] = "EXISTS_IN_OUTPUT"
                
                else:
                    download_url = _determine_download_url(usi)

                    if download_url is None:
                        output_result_dict["status"] = "ERROR"
                    else:
                        # download in chunks using requests
                        _download(usi, target_path, mri_original_extension)

                        output_result_dict["status"] = "DOWNLOADED_INTO_OUTPUT_WITHOUT_CACHE"

        else:
            output_result_dict["status"] = "ERROR"
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("Error", e)
        print("Error", e, file=sys.stderr)
        output_result_dict["status"] = "ERROR"
    
    finally:    
        return output_result_dict

def main():
    parser = argparse.ArgumentParser(description='Running library search parallel')
    parser.add_argument('input_download_file', help='input download file, can be a params json from GNPS2 or a tsv file with a usi header')
    parser.add_argument('output_folder', help='output_folder')
    parser.add_argument('output_summary', help='output_summary')
    parser.add_argument('--cache_directory', default=None, help='folder of existing data')
    parser.add_argument('--nestfiles', help='Nest mass spec files in a hashed folder so its not all in the same directory', default='flat')
    parser.add_argument('--threads', default=1, type=int, help="Number of threads")
    parser.add_argument('--progress', help='Show progress bar', action='store_true', default=False)
    parser.add_argument('--extension_filter', default=None, help="Filter to only download certain extensions. Should be formatted as a semicolon separated list")
    parser.add_argument('--raw_usi_input', action='store_true', default=False, help="Specify if input_download_file is a raw USI file")
    args = parser.parse_args()

    if args.threads != 1:
        warnings.warn("The 'threads' argument is deprecated and will be removed in a future version. Only single-threading is supported.", DeprecationWarning)

    # checking the input file exists
    if not os.path.isfile(args.input_download_file):
        print("Input file does not exist")
        exit(0)

    if not os.path.isdir(args.output_folder):
        os.makedirs(args.output_folder, exist_ok=True)

    # Checking the file extension
    if args.raw_usi_input:
        usi_list = [args.input_download_file.strip()]
    else:
        if args.input_download_file.endswith(".yaml"):
            # Loading yaml file
            parameters = yaml.load(open(args.input_download_file), Loader=yaml.SafeLoader)
            try:
                usi_list = parameters["usi"].split("\n")
            except:
                # We have a problem parsing
                usi_list = []
        elif args.input_download_file.endswith(".tsv"):
            df = pd.read_csv(args.input_download_file, sep="\t")
            usi_list = df["usi"].tolist()

        # Cleaning USI list
        usi_list = [usi.lstrip().rstrip() for usi in usi_list]
        
    # Let's download these files
    if args.progress:
        usi_list = tqdm(usi_list)
    
    if args.extension_filter:
        extension_filter = tuple([x.lower() for x in args.extension_filter.split(";")])
    else:
        extension_filter = None

    output_result_list = []
    for usi in usi_list:
        print("Downloading", usi)

        if len(usi) < 5:
            continue

        result = download_helper(usi, args, extension_filter)
        if result is not None:
            output_result_list.append(result)
    
    if len(output_result_list) > 0:
        df = pd.DataFrame(output_result_list)
        df.to_csv(args.output_summary, sep="\t", index=False)

if __name__ == "__main__":
    main()
