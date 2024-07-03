# Import bin folder

import sys
sys.path.append('../bin')
import download_public_data_usi

def test():

    print(download_public_data_usi._determine_dataset_reconstructed_foldername("mzspec:MSV000086206:ccms_peak/raw/S_N3.mzML"))
    
    cachepath, cachefolder = download_public_data_usi._determine_caching_paths("mzspec:MSV000086206:ccms_peak/raw/S_N3.mzML", "./data/cache", "S_N3.mzML")
    cachepath2, _ = download_public_data_usi._determine_caching_paths("mzspec:MSV000086206:ccms_peak/raw/S_N3.mzML:scan:1", "./data/cache", "S_N3.mzML")

    print(cachefolder)

    assert(cachepath == cachepath2)
    
def main():
    test()

if __name__ == "__main__":
    main()