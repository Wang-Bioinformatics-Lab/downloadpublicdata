import sys
import csv
import datetime
import os

def filter_and_write_usi(gnps_filename, mtbls_filename, mwb_filename):
    # Get the original file name without extension as the prefix
    file_prefix = os.path.splitext(os.path.basename(gnps_filename))[0]
    
    # Get current date and time formatted
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Construct output file name with prefix, date/time, and .csv extension
    output_gnps_filename = f"{file_prefix}_{current_datetime}.csv"

    with open(gnps_filename, 'r', newline='') as csvfile, open(output_gnps_filename, 'w') as output_file:
        reader = csv.DictReader(csvfile)
        writer = csv.writer(output_file)

        # Write header to the output file
        writer.writerow(['usi'])

        for row in reader:
            usi_value = row.get('usi', '').strip()
            
            # Ignore entries containing "/ST" or "/MTBLS"
            if "/ST" in usi_value or "/MTBLS" in usi_value:
                continue

            # Write usi value to the output file
            writer.writerow([usi_value])

    print(f"Filtered data has been written to {output_gnps_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <gnps_filename>")
    else:
        gnps_filename = sys.argv[1]
        mtbls_filename = sys.argv[2]
        mwb_filename = sys.argv[3]
        filter_and_write_usi(gnps_filename, mtbls_filename, mwb_filename)

