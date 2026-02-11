import csv
import os
import re
from collections import defaultdict
import sys

def find_matching_files(seed_path):
    directory = os.path.dirname(seed_path)
    if not directory: # Handle cases where the path is just a filename
        directory = '.'
    filename = os.path.basename(seed_path)

    # Regex to capture the prefix, run number, and suffix from the filename.
    match = re.match(r'^(.*?)_(\d+)(_noE\.csv|\.csv)$', filename)
    
    if not match:
        print(f"Warning: Filename '{filename}' does not match the expected multi-run naming pattern. Using this single file only.")
        return [seed_path]

    prefix = match.group(1)
    suffix = match.group(3)
    
    matching_files = []
    try:
        for f in os.listdir(directory):
            current_match = re.match(r'^(.*?)_(\d+)(_noE\.csv|\.csv)$', f)
            if current_match and current_match.group(1) == prefix and current_match.group(3) == suffix:
                matching_files.append(os.path.join(directory, f))
    except FileNotFoundError:
        print(f"Error: Directory '{directory}' not found. Please check the path.")
        return []

    print(f"Found {len(matching_files)} matching files for pattern '{prefix}_*{suffix}': {matching_files}")
    return matching_files

def collect_detect_early_data(seed_path):
    matching_files = find_matching_files(seed_path)
    if not matching_files:
        return set(), set()
        
    all_paths = set()
    detect_early_paths = set()
    
    # Track appearances and timeouts for each path to find those that *always* time out
    path_appearances = defaultdict(int)
    path_timeouts = defaultdict(int)

    for file_path in matching_files:
        try:
            with open(file_path, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row: continue
                    
                    path = row[0]
                    
                    # Track every appearance
                    path_appearances[path] += 1
                    all_paths.add(path)

                    # Skip timed-out or malformed rows for further checks
                    if len(row) <= 5:
                        # Still check for timeout specifically
                        if len(row) > 1 and row[1] == "TIME-OUT-30":
                            path_timeouts[path] += 1
                        continue

                    # Exclude 'Unreal' paths from the final valid set
                    if len(row) > 6 and row[6] == "Unreal":
                        all_paths.discard(path)
                        continue 

                    # Check for "Detect Early" in successful runs
                    if row[5] == "Detect Early":
                        detect_early_paths.add(path)

        except FileNotFoundError:
            print(f"Error: File {file_path} not found, skipping.")
            continue
    
    # Identify paths that ALWAYS timed out
    always_timed_out_paths = set()
    for path, appearance_count in path_appearances.items():
        # Check if the path appeared and if its appearance count matches its timeout count
        if appearance_count > 0 and appearance_count == path_timeouts[path]:
            always_timed_out_paths.add(path)
            
    # The final set of valid paths excludes both "Unreal" and "Always Timed-Out" specs
    final_valid_paths = all_paths - always_timed_out_paths
            
    return final_valid_paths, detect_early_paths

def analyze_detect_early(file1_path):
    print("Processing file group...")
    valid_paths, detect_early_paths = collect_detect_early_data(file1_path)

    # The base set of paths is everything encountered (excluding Unreal and always-timed-out)
    total_paths = len(valid_paths)
    
    # Count "Detect Early" occurrences within the valid base set
    detect_early_count = len(detect_early_paths.intersection(valid_paths))

    # Calculate percentage
    percentage = (detect_early_count / total_paths) * 100 if total_paths > 0 else 0

    print("\n" + "=" * 50)
    print("'Detect Early' Statistics")
    print("Rule: Excludes specs that are 'Unreal' or time out in all runs.")
    print("-" * 50)
    print(f"Total unique paths considered for statistics: {total_paths}")
    print(f"'Detect Early' paths found: {detect_early_count} ({percentage:.2f}%)")
    print("=" * 50)
    print(f"{detect_early_count}/{total_paths}({percentage:.2f}\\%)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)
    file_path = sys.argv[1]
    analyze_detect_early(file_path)