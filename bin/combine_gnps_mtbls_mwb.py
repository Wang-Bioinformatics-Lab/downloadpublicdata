import sys
import csv
import datetime
import os

# combines all the mris/usis in gnps, mtbls and mwb datasets, ignore the gnps data imported from mtbls and mwb/ST
# Currently also ignore the MTBLS718 and MTBLS719 datasets that are slow to download with http approach. 
# Also ignore the USIs/MRIs that contains ":__MACOSX/" 
def filter_and_write_usi(gnps_filename, mtbls_filename, mwb_filename):
    # Get the original file name without extension as the prefix
    file_prefix = os.path.splitext(os.path.basename(gnps_filename))[0]
    
    # Get current date and time formatted
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Construct output file name with prefix, date/time, and .csv extension
    output_gnps_filename = f"updated_mris_{current_datetime}.csv"

    with open(gnps_filename, 'r', newline='') as csvfile, open(output_gnps_filename, 'w') as output_file:
        reader = csv.DictReader(csvfile)
        writer = csv.writer(output_file)

        # Write header to the output file
        writer.writerow(['usi'])

        for row in reader:
            usi_value = row.get('usi', '').strip()
            
            # Ignore entries containing "/ST" or "/MTBLS", these are gnps dataset imported from mtbls and mwb
            if "/ST" in usi_value or "/MTBLS" in usi_value:
                continue
            
            # Ignore USI/MRI that contains ":__MACOSX/". 
            # These files are the result of Apple storing Resource Forks safe manner
            if ":__MACOSX/" in usi_value:
                continue

            # Write usi value to the output file
            writer.writerow([usi_value])

    with open(mtbls_filename, 'r', newline='') as csvfile, open(output_gnps_filename, 'a') as output_file:
        reader = csv.DictReader(csvfile)
        writer = csv.writer(output_file)


        for row in reader:
            usi_value = row.get('usi', '').strip()
            
            # Ignore USI/MRI that contains ":__MACOSX/". 
            if ":__MACOSX/" in usi_value:
                continue

            # Ignore entries containing "MTBLS718" or "MTBLS719"
            if "MTBLS718" in usi_value or "MTBLS719" in usi_value:
                continue

            # Write usi value to the output file
            writer.writerow([usi_value])
    
    with open(mwb_filename, 'r', newline='') as csvfile, open(output_gnps_filename, 'a') as output_file:
        reader = csv.DictReader(csvfile)
        writer = csv.writer(output_file)

        for row in reader:
            usi_value = row.get('usi', '').strip()
            
            # Ignore USI/MRI that contains ":__MACOSX/". 
            if ":__MACOSX/" in usi_value:
                continue

            # Write usi value to the output file
            writer.writerow([usi_value])


    print(f"Filtered data has been written to {output_gnps_filename}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python combine_gnps_mtbls_mwb.py <gnps_filename> <mtbls_file> <mwb_filename>")
    else:
        gnps_filename = sys.argv[1]
        mtbls_filename = sys.argv[2]
        mwb_filename = sys.argv[3]
        filter_and_write_usi(gnps_filename, mtbls_filename, mwb_filename)

