#!/usr/bin/python
import sys
import os
import argparse
from collections import defaultdict
import pandas as pd
import shutil
import requests
import yaml
import uuid
from tqdm import tqdm
import time

import download_raw
from sanitize_filename import sanitize

DATASET_CACHE_URL_BASE = "https://datasetcache.gnps2.org"

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

def _determine_dataset_reconstructed_foldername(usi):
    """
    We are going to get the folder name that contains the datasetid together with the original folder structure in the usi
    """ 

    print("XXX", usi)


    usi_splits = usi.split(":")
    dataset_id = usi_splits[1]
    fileportion = usi_splits[2]
    folder_name = os.path.dirname(fileportion)
    data_folder = os.path.join(dataset_id, folder_name)

    print(data_folder)

    return data_folder

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
    
    # Norman
    if "files.dsfp.norman-data.eu" in download_url:
        # Lets parse the arguments, using urlparse
        from urllib.parse import urlparse, parse_qs
        # removing parameters
        parsed_params = urlparse(download_url)
        filename = parsed_params.path
        
        filename = os.path.basename(filename)

        # make this safe on disk
        filename = sanitize(filename)

        return filename

    # TODO: Work for PRIDE
    # TODO: Work for Metabolights

    return os.path.basename(download_url)

def _determine_caching_paths(usi, cache_directory, target_filename):
    # Make sure usi is actually only the MRI portions, or else we can get a bunch of repetition
    stripped_mri = ":".join(usi.split(":")[0:3])

    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
    hashed_id = str(uuid.uuid3(namespace, stripped_mri)).replace("-", "")

    # embedding with one level of hierarchy
    hash_folder = hashed_id[:2]

    cache_path = os.path.join(cache_directory, hash_folder)
    cache_path = os.path.realpath(cache_path)

    cache_filename = os.path.join(cache_path, hashed_id + "-" + target_filename[-50:].rstrip())

    return cache_filename, cache_path

def _download(mri, target_filename, datafile_extension):

    temp_mangled_filename = "temp_" + str(uuid.uuid4())
    if datafile_extension.lower() == ".mzml":
        return_value = _download_mzml(mri, temp_mangled_filename)
    elif datafile_extension.lower() == ".mzxml":
        return_value = _download_mzml(mri, temp_mangled_filename)
    elif datafile_extension.lower() == ".mgf":
        return_value = _download_mzml(mri, temp_mangled_filename)
    elif datafile_extension.lower() == ".d":
        return_value = _download_vendor(mri, temp_mangled_filename)
    elif datafile_extension.lower() == ".wiff":
        return_value = _download_vendor(mri, temp_mangled_filename)
    elif datafile_extension.lower() == ".raw":
        return_value = _download_vendor(mri, temp_mangled_filename)
    else:
         raise Exception("Unsupported")

    
    # Now we can try to move this file from the temp to the target
    # return_value is 0 even when the mri is invalid. 
    # And when the mri is invalid, MassIVE returns a html file that contains error message
    # and MTBLS return a small file that contains a message indicating that the no permission to access the requested resource
    # and the ST/MWB returns nothing
    # we will check the size of the downloaded temp file, if the size is > 10K, then move it to final location,
    # otherwise just delete the temp file
    # Get the size of the file in bytes
    
    file_size = os.path.getsize(temp_mangled_filename)
    if(file_size < 10000):
        print(f"{mri} downloading failed, remove temporary file {temp_mangled_filename}")
        return_value = 99
        os.remove(temp_mangled_filename)
    else:
        print(f"{mri} downloaded successfully to target location at {target_filename}")
        shutil.move(temp_mangled_filename, target_filename)
    return return_value

def _download_mzml(usi, target_filename):
    # here we don't need to do any conversion and can get directly from the source
    download_url = _determine_download_url(usi)
    
    r = requests.get(download_url, stream=True)
    with open(target_filename, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    
    # is it possible to check if the download failed or not and return different value accordingly
    return 0

def _determine_target_subfolder(usi):
    # to determine the target subfolder based on the source of the dataset
    # a dataset starts with "MSV" goes to massive subfolder, a dataset starts with "MTBLS" goes to MTBLS subfolder 
    # and a dataset starts with "ST" goes to ST subfoldre
    target_subfolder = "other"
    if usi.startswith("mzspec:MSV"):
        target_subfolder = "MassIVE" # GNPS is also MassIVE
    elif usi.startswith("mzspec:MTBLS"):
        target_subfolder = "MTBLS"
    elif usi.startswith("mzspec:ST"):
        target_subfolder = "ST"
    elif usi.startswith("mzspec:NORMAN"):
        target_subfolder = "NORMAN"
    else:
        target_subfolder = "other"

    return target_subfolder

    
def _download_vendor(mri, target_filename):
    # we do need to do conversion so we'll hit the conversion service to 
    convert_request_url = "{}/convert/request".format(DATASET_CACHE_URL_BASE)
    params = {}
    params["mri"] = mri

    print("Requesting Conversion")
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
        # change the return value from "CONVERSION NOT READY" to 98
        return 98

    # change return value to 0 from original "CONVERTED"
    return 0

def download_helper(usi, args, extension_filter=None, noconversion=False, dryrun=False):
    processdownloadraw = False

    print("ZZZZZZZ")

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

            print(target_subfolder_name)
                
            # Filtering extensions
            if extension_filter is not None:
                if not ms_filename.lower().endswith(extension_filter):
                    return None
                
            # Here we determine the actual extension of the ms_filename
            filename_without_extension, file_extension = os.path.splitext(ms_filename)
            mri_original_extension = file_extension

            if mri_original_extension.lower() in [".d", ".wiff", ".raw"]:
                if noconversion:
                    target_filename = ms_filename
                    processdownloadraw = True
                else:
                    target_filename = filename_without_extension + ".mzML"
            else:
                target_filename = ms_filename 
        except:
            print("Error determining ms filename for", usi, file=sys.stderr)
            return None

        if target_filename is not None:
            target_folder = args.output_folder 

            if args.nestfiles == "nest":
                usi_hash = uuid.uuid3(uuid.NAMESPACE_DNS, usi)
                folder_hash = str(usi_hash)[:2]

                target_dir = os.path.join(target_folder, folder_hash)

                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                target_path = os.path.join(target_dir, target_filename)
            elif args.nestfiles == "recreate":
                target_folder = os.path.join(args.output_folder, target_subfolder_name)
                if target_subfolder_name == "other":
                    return None
                
                # recreate the folder structure
                # add data source folder to output_folder
                print("YYYYYYYYYYYY", usi)
                dataset_folder = _determine_dataset_reconstructed_foldername(usi)
                target_dir = os.path.join(target_folder, dataset_folder)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                target_path = os.path.join(target_dir, target_filename)
            else: # flat as default
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)

                target_path = os.path.join(target_folder, target_filename)

            output_result_dict["target_path"] = target_path

            if os.path.exists(target_path):
                output_result_dict["status"] = "EXISTS_IN_OUTPUT"

            # Checking if the file is already in the dataset directory
            if args.existing_dataset_directory is not None:
                # Checking
                print("Checking existing dataset directory")
                path_in_dataset_folder = _determine_dataset_reconstructed_foldername(usi)
                collection_name = _determine_target_subfolder(usi)

                dataset_filepath = os.path.join(args.existing_dataset_directory, collection_name, path_in_dataset_folder, target_filename)

                # Checking if this exists
                if os.path.exists(dataset_filepath):
                    print(dataset_filepath, "exists")

                    # Let's make a symlink
                    if not os.path.exists(target_path):
                        os.symlink(dataset_filepath, target_path)

                    output_result_dict["status"] = "EXISTS_IN_DATASET"

                    return output_result_dict

            # Checking the cache
            if args.cache_directory is not None and os.path.exists(args.cache_directory):
                print("Checking in the cache now")

                cache_filename, cache_directory = _determine_caching_paths(usi, args.cache_directory, target_filename)

                output_result_dict["cache_filename"] = os.path.basename(cache_filename)

                # If we find it in the cache, we can create a link to it
                if os.path.exists(cache_filename):
                    print("Found in cache", cache_filename)

                    if not os.path.exists(target_path):
                        os.symlink(cache_filename, target_path)
                        output_result_dict["status"] = "EXISTS_IN_CACHE"
                else:
                    download_url = _determine_download_url(usi)

                    if download_url is None:
                        output_result_dict["status"] = "ERROR"
                    else:
                        # Saving file to cache if we don't have it in the cache
                        
                        try:
                            # Making sure the cache directory exists
                            if not os.path.exists(cache_directory):
                                os.makedirs(cache_directory, exist_ok=True)

                            if not dryrun:
                                _download(usi, cache_filename, mri_original_extension)
                            else:
                                print("Would have downloaded", usi, "to", cache_filename)
                                output_result_dict["status"] = "DRYRUN_TO_DOWNLOAD"

                                return output_result_dict


                            # Creating symlink
                            if not os.path.exists(target_path):
                                os.symlink(cache_filename, target_path)
                                output_result_dict["status"] = "DOWNLOADED_INTO_OUTPUT_WITH_CACHE"

                        except KeyboardInterrupt:
                            raise

                        except:
                            # We are likely writing to read only file system for the cache
                            try:
                                if not dryrun:
                                    _download(usi, target_path, mri_original_extension)
                                else:
                                    print("Would have downloaded", usi, "to", cache_filename)
                                    output_result_dict["status"] = "DRYRUN_TO_DOWNLOAD"

                                    return output_result_dict
                                

                                output_result_dict["status"] = "CACHE_ERROR_DOWNLOAD_DIRECT"
                            except KeyboardInterrupt:
                                raise
                            except:
                                output_result_dict["status"] = "DOWNLOAD_ERROR"

            # No Caching
            else:
                # if the target path file is already there, then we don't need to do anything
                if os.path.exists(target_path):
                    output_result_dict["status"] = "EXISTS_IN_OUTPUT"
                else:
                    if processdownloadraw:
                        print("Downloading the raw data without conversion", target_path)

                        if not dryrun:
                            download_raw.download_raw_mri(usi, target_path)
                        else:
                            print("Would have downloaded", usi, "to", target_path)
                            output_result_dict["status"] = "DRYRUN_TO_DOWNLOAD"

                            return output_result_dict
                        
                        # TODO: I think we might have to update this
                        return output_result_dict

                    download_url = _determine_download_url(usi)

                    if download_url is None:
                        output_result_dict["status"] = "ERROR"
                    else:
                        
                        if not dryrun:
                            # download in chunks using requests
                            return_value = _download(usi, target_path, mri_original_extension)
                        else:
                            print("Would have downloaded", usi, "to", target_path)
                            output_result_dict["status"] = "DRYRUN_TO_DOWNLOAD"

                            return output_result_dict
                        
                        if return_value == 0:
                            output_result_dict["status"] = "DOWNLOADED_INTO_OUTPUT_WITHOUT_CACHE"
                        elif return_value == 99:
                            # downloaded data file is too small
                            print(f"File size might be too small")
                            output_result_dict["status"] = "ERROR_DATA_TOO_SMALL"
                        elif return_value == 98:
                            # data file conversion is incorrect
                            print(f"Vendor conversion not ready")
                            output_result_dict["status"] = "ERROR_CONVERSION_NOT_READY"


        else:
            output_result_dict["status"] = "ERROR"
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("Error", e, file=sys.stderr)
        output_result_dict["status"] = "ERROR"
    finally:    
        return output_result_dict

def main():
    parser = argparse.ArgumentParser(description='Running library search parallel')
    parser.add_argument('input_download_file', help='input download file, can be a params json from GNPS2 or a tsv file with a usi header')
    parser.add_argument('output_folder', help='Output Folder where the data goes')
    parser.add_argument('output_summary', help='Output Summary for all the data downloads')
    
    parser.add_argument('--raw_mri_input', action='store_true', default=False, help="Specify if input_download_file is just an MRI by itself")

    parser.add_argument('--cache_directory', default=None, help='cache folder of existing data')

    parser.add_argument('--existing_dataset_directory', default=None, help='Directory with a proper dataset structure to avoid downloading the same dataset multiple times')

    parser.add_argument('--nestfiles', help='Nest mass spec files in a hashed folder so its not all in the same directory', default='flat')
    parser.add_argument('--progress', help='Show progress bar', action='store_true', default=False)
    
    parser.add_argument('--extension_filter', default=None, help="Filter to only download certain extensions. Should be formatted as a semicolon separated list")
    
    parser.add_argument('--noconversion', action='store_true', default=False, help="Specifying to turn off conversion and download the full raw file")

    parser.add_argument('--dryrun', action='store_true', default=False, help="This is a dry run flag that does not do the actual download, but reports what is to be downloaded and what has been downloaded")


    args = parser.parse_args()

    # checking the input file exists
    if not os.path.isfile(args.input_download_file):
        print("Input file does not exist")
        exit(0)

    if not os.path.isdir(args.output_folder):
        os.makedirs(args.output_folder, exist_ok=True)

    # Checking the file extension
    if args.raw_mri_input:
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
        else:
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

        result = download_helper(usi, args, extension_filter, noconversion=args.noconversion, dryrun=args.dryrun)
        if result is not None:
            output_result_list.append(result)
    
    if len(output_result_list) > 0:
        df = pd.DataFrame(output_result_list)
        df.to_csv(args.output_summary, sep="\t", index=False)

if __name__ == "__main__":
    main()
