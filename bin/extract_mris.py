import csv
import sys
import os

# Allowed sample types and file extensions
allowed_sample_types = {'GNPS', 'MTBLS', 'MWB'}
allowed_extensions = {'.mzXML', '.mzML', '.mzml', '.mzxml'}

def filter_and_output_usi(input_csv, output_file):
    with open(input_csv, mode='r') as infile, open(output_file, mode='w') as outfile:
        reader = csv.DictReader(infile)
        for row in reader:
            # Check if sample_type is one of the allowed types
            if row['sample_type'] in allowed_sample_types:
                usi = row['usi']
                # Check if usi ends with an allowed extension
                if any(usi.endswith(ext) for ext in allowed_extensions):
                    outfile.write(usi + '\n')

if __name__ == "__main__":
    # Ensure the script is called with the input file name as an argument
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input_csv_file>")
        sys.exit(1)

    # Get the input file name from command line
    input_csv = sys.argv[1]

    # Generate the output file name by adding the prefix 'mri_'
    output_file = f"mri_{os.path.basename(input_csv)}"

    # Process the CSV file and output the filtered USIs
    filter_and_output_usi(input_csv, output_file)
    print(f"Filtered USIs have been written to {output_file}")

