import os
import requests

def download_raw_mri(mri, target_file, cache_url="https://datasetcache.gnps2.org"):
    # lets get the extension of the filename
    mri_splits = mri.split(":")
    
    dataset_accession = mri_splits[1]

    filename = mri_splits[2]
    raw_filename = os.path.basename(filename)
    extension = filename.split(".")[-1]

    path_to_full_raw_filename = target_file

    if extension == "d":
        # We need to go to the dataset cache and grab all the files
        #https://datasetcache.gnps2.org/datasette/database/filename.json?_sort=usi&dataset__exact=MSV000093337&filepath__startswith=ccms_parameters%2Fparams.xml
        
        params = {}
        params["_shape"] = "array"
        params["dataset__exact"] = mri_splits[1]
        params["filepath__startswith"] = filename

        url =  "{}/datasette/database/filename.json".format(cache_url)

        r = requests.get(url, params=params)

        if r.status_code == 200:
            # lets get all he files
            file_rows = r.json()

            for file_row in file_rows:
                mri_specific_usi = file_row["usi"]
                mri_specific_filepath = file_row["filepath"]

                if mri_specific_filepath.lower().endswith(".zip"):
                    continue

                # file relative file path to original filename
                relative_filepath = os.path.relpath(mri_specific_filepath, filename)
                target_specific_filepath = os.path.join(target_file, relative_filepath)

                if relative_filepath == ".":
                    continue

                os.makedirs(os.path.dirname(target_specific_filepath), exist_ok=True)

                # Now we need to figure out how to get this file given the MRI
                url = "https://dashboard.gnps2.org/downloadlink"
                params = {}
                params["usi"] = mri_specific_usi

                #print("GETTING Dashboard Download link")

                r = requests.get(url, params=params)

                # This gives us the download
                if r.status_code == 200:
                    download_url = r.text

                    print("DOWNLOAD LINK", download_url)

                    r = requests.get(download_url)

                    if r.status_code == 200:
                        with open(target_specific_filepath, "wb") as f:
                            f.write(r.content)
                    else:
                        import sys
                        print("Error downloading", download_url, file=sys.stderr)

    elif extension == "wiff":
        # We need to go to the dataset cache and grab all the files
        #https://datasetcache.gnps2.org/datasette/database/filename.json?_sort=usi&dataset__exact=MSV000093337&filepath__startswith=MSV000093337%2Fccms_parameters%2Fparams.xml
        params = {}
        params["_shape"] = "array"
        params["dataset__exact"] = mri_splits[1]
        params["filepath__startswith"] = filename

        url =  "{}/datasette/database/filename.json".format(cache_url)

        r = requests.get(url, params=params)

        if r.status_code == 200:
            # lets get all he files
            file_rows = r.json()

            for file_row in file_rows:
                mri_specific_usi = file_row["usi"]
                mri_specific_filepath = file_row["filepath"]

                target_specific_filepath = os.path.join(conversion_folder, os.path.basename(mri_specific_filepath))

                # Now we need to figure out how to get this file given the MRI
                url = "https://dashboard.gnps2.org/downloadlink"
                params = {}
                params["usi"] = mri_specific_usi

                #print("GETTING Dashboard Download link")

                r = requests.get(url, params=params)

                # This gives us the download
                if r.status_code == 200:
                    download_url = r.text

                    #print("DOWNLOAD LINK", download_url)

                    r = requests.get(download_url)

                    if r.status_code == 200:
                        with open(target_specific_filepath, "wb") as f:
                            f.write(r.content)
                    else:
                        import sys
                        #print("Error downloading", download_url, file=sys.stderr)
            

    elif extension == "raw":
        # Now we need to figure out how to get this file given the MRI
        url = "https://dashboard.gnps2.org/downloadlink"
        params = {}
        params["usi"] = mri

        r = requests.get(url, params=params)

        # This gives us the download
        if r.status_code == 200:
            download_url = r.text

            print("DOWNLOAD LINK", download_url)

            r = requests.get(download_url)

            # TODO: Maybe we should stream this? 
            if r.status_code == 200:
                with open(path_to_full_raw_filename, "wb") as f:
                    f.write(r.content)
            else:
                import sys
                print("Error downloading", download_url, file=sys.stderr)

    return path_to_full_raw_filename