import os
import sys

def split_file(input_file, lines_per_file, output_folder=None):
    # Validate input file
    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    # Validate lines_per_file argument
    try:
        lines_per_file = int(lines_per_file)
        if lines_per_file <= 0:
            raise ValueError("Number of lines per file must be a positive integer.")
    except ValueError as e:
        print(f"Error: Invalid number of lines per file - {e}")
        return

    # Determine base output filename
    base_filename = os.path.basename(input_file)
    base_filename_without_ext, ext = os.path.splitext(base_filename)
    output_prefix = f"Splitted_{base_filename_without_ext}_"

    # Determine output folder
    if output_folder:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    else:
        output_folder = os.getcwd()

    # Read the original file
    with open(input_file, 'r') as f:
        header = f.readline().strip()  # Read the header
        lines = f.readlines()

    # Split into smaller files
    num_lines = len(lines)
    num_files = (num_lines + lines_per_file - 1) // lines_per_file  # Ceiling division

    for i in range(num_files):
        start_idx = i * lines_per_file
        end_idx = min((i + 1) * lines_per_file, num_lines)
        output_filename = os.path.join(output_folder, f"{output_prefix}{start_idx + 1}-{end_idx}{ext}")

        with open(output_filename, 'w') as fout:
            fout.write(header + '\n')
            fout.writelines(lines[start_idx:end_idx])

        print(f"Created file: {output_filename}")

    print(f"Successfully created {num_files} smaller files.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <input_file> <lines_per_file> [<output_folder>]")
    else:
        input_file = sys.argv[1]
        lines_per_file = sys.argv[2]
        output_folder = sys.argv[3] if len(sys.argv) > 3 else None
        split_file(input_file, lines_per_file, output_folder)

