import csv
from statistics import quantiles, geometric_mean
import math
import os
import re
from collections import defaultdict
import csv
import os
import re
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

def collect_paths_and_timeouts(seed_path, is_file1):
    matching_files = find_matching_files(seed_path)
    if not matching_files:
        return set(), set()

    timed_out_paths = set()
    all_paths = set()

    for file_path in matching_files:
        try:
            with open(file_path, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row: continue
                    
                    path = row[0]
                    # path = normalize_path_prefix(row[0])
                    all_paths.add(path)

                    # Check for timeout
                    if len(row) > 1 and row[1] == "TIME-OUT-30":
                        timed_out_paths.add(path)
                    
                    if is_file1 and len(row) > 6 and row[6] == "Unreal":
                        all_paths.discard(path) # Use discard to avoid errors

        except FileNotFoundError:
            print(f"Error: File {file_path} not found, skipping.")
            continue
            
    return timed_out_paths, all_paths


def analyze_timeouts(file1_path, file2_path):
    """
    Analyzes and prints timeout statistics, including percentages, between two groups of files.
    """
    print("Processing file group 1...")
    file1_timed_out, file1_all_paths = collect_paths_and_timeouts(file1_path, is_file1=True)

    print("\nProcessing file group 2...")
    file2_timed_out, _ = collect_paths_and_timeouts(file2_path, is_file1=False)

    base_paths = file1_all_paths
    total_paths = len(base_paths)
    
    timeout_count1 = len(file1_timed_out.intersection(base_paths))

    common_timeouts_in_file2 = file2_timed_out.intersection(base_paths)
    timeout_count2 = len(common_timeouts_in_file2)

    percent1 = (timeout_count1 / total_paths) * 100 if total_paths > 0 else 0
    percent2 = (timeout_count2 / total_paths) * 100 if total_paths > 0 else 0


    return percent1, percent2



def find_matching_files(seed_path):
   
    directory = os.path.dirname(seed_path)
    if not directory: # Handle cases where the path is just a filename
        directory = '.'
    filename = os.path.basename(seed_path)

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

def load_and_average_data(seed_path, is_file1):
    matching_files = find_matching_files(seed_path)
    if not matching_files:
        return {}
        
    # Temporary dictionary to store lists of raw values for each path.
    # Structure: {path: {'counts': [c1, c2, ...], 'times': [t1, t2, ...]}}
    temp_data = defaultdict(lambda: {'counts': [], 'times': []})

    for file_path in matching_files:
        try:
            with open(file_path, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row: continue # Skip empty rows
                    
                    path = row[0]
                    # path = normalize_path_prefix(row[0])
                    
                    if row[1] == "TIME-OUT-30":
                        continue
                    
                    try:
                        if is_file1:
                            if row[6] == "Unreal":
                                continue
                            exec_count = int(row[2])
                            exec_time = int(row[3])
                        else:  # is_file2
                            exec_count = int(row[1])
                            exec_time = int(row[2])
                        
                        temp_data[path]['counts'].append(exec_count)
                        temp_data[path]['times'].append(exec_time)
                    except (ValueError, IndexError) as e:
                        print(f"Warning: Skipping malformed row in file {file_path}: {row}. Error: {e}")

        except FileNotFoundError:
            print(f"Error: File {file_path} not found, skipping.")
            continue
            
    # Calculate the average values
    averaged_data = {}
    for path, data in temp_data.items():
        if data['counts'] and data['times']:
            avg_count = sum(data['counts']) / len(data['counts'])
            avg_time = sum(data['times']) / len(data['times'])
            averaged_data[path] = (avg_count, avg_time)
            
    return averaged_data

def calculate_quartiles_by_time_group(file1_path, file2_path):
    # Load and average data from the first set of files
    print("Processing file group 1...")
    file1_data = load_and_average_data(file1_path, is_file1=True)

    # Load and average data from the second set of files
    print("\nProcessing file group 2...")
    file2_data = load_and_average_data(file2_path, is_file1=False)

    time_groups = {
        'lt_1s':        {'count_ratios': [], 'time_ratios': [], 'range': (0, 1000)},
        '1s_to_10s':    {'count_ratios': [], 'time_ratios': [], 'range': (1000, 10000)},
        '10s_to_30s':   {'count_ratios': [], 'time_ratios': [], 'range': (10000, 30000)},
        '30s_to_1min':  {'count_ratios': [], 'time_ratios': [], 'range': (30000, 60000)},
        '1min_to_5min': {'count_ratios': [], 'time_ratios': [], 'range': (60000, 300000)},
        '5min_to_10min':{'count_ratios': [], 'time_ratios': [], 'range': (300000, 600000)},
        '10min_to_30min':{'count_ratios': [], 'time_ratios': [], 'range': (600000, 1800000)},
        '30min_to_60min':{'count_ratios': [], 'time_ratios': [], 'range': (1800000, 3600000)}
    }

    all_time_ratios = []

    def safe_geometric_mean(data):
        if not data: return None
        positive_data = [x for x in data if x > 0]
        if not positive_data: return None
        if len(positive_data) != len(data):
            print(f"Warning: {len(data) - len(positive_data)} non-positive values were excluded from geometric mean calculation.")
        try:
            return geometric_mean(positive_data)
        except Exception:
            try:
                log_sum = sum(math.log(x) for x in positive_data)
                return math.exp(log_sum / len(positive_data))
            except Exception:
                return None

    for path in file1_data:
        if path in file2_data:
            _         , exec_time1 = file1_data[path]
            _         , exec_time2 = file2_data[path]
            
            if exec_time1 < 0 or exec_time2 < 0:
                continue
            
            time_ratio = exec_time1 / exec_time2 if exec_time2 != 0 else float('inf')

            if time_ratio == float('inf'):
                continue

            all_time_ratios.append(time_ratio)

            for group_name, group_data in time_groups.items():
                min_time, max_time = group_data['range']
                if min_time <= exec_time2 < max_time:
                    group_data['time_ratios'].append(time_ratio)
                    break

    total_time_geomean = safe_geometric_mean(all_time_ratios)
    
    print("\n" + "=" * 50)
    total_count = len(all_time_ratios)
    
    if total_time_geomean is not None:
        print(f"OVERALL GEOMETRIC MEAN (All Time Groups):& {total_time_geomean:.2f}^{{{total_count}}} ")
        if total_time_geomean < 1.0:
            allOutput = f"& $\\textbf{{{total_time_geomean:.2f}}}^{{{total_count}}}$ "
        else:
            allOutput = f"& ${total_time_geomean:.2f}^{{{total_count}}}$ "
    else:
        print("OVERALL GEOMETRIC MEAN (All Time Groups):& {---}")
        allOutput = "& {---} "
    print("=" * 50)
    
    result = {}
    for group_name, group_data in time_groups.items():
        time_ratios = group_data['time_ratios']
        time_geomean = safe_geometric_mean(time_ratios)
        result[group_name] = {
            'execution_time': {
                'geometric_mean': time_geomean,
                'count': len(time_ratios)
            }
        }
    return result, allOutput


def normalize_path_prefix(raw_path):
    match = re.search(r'(\d+_Pre/)', raw_path)
    if match:
        start_index = raw_path.rfind(match.group(1))
        if start_index != -1:
            return raw_path[start_index:]
    return raw_path



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <file1_path> <file2_path>")
        sys.exit(1)

    file1_path = sys.argv[1]
    file2_path = sys.argv[2]

    quartiles_results, allOutput = calculate_quartiles_by_time_group(file1_path, file2_path)

    output = "& "
    time_group_names = {
        'lt_1s': '< 1s',
        '1s_to_10s': '1s - 10s',
        '10s_to_30s': '10s - 30s',
        '30s_to_1min': '30s - 1min',
        '1min_to_5min': '1min - 5min',
        '5min_to_10min': '5min - 10min',
        '10min_to_30min': '10min - 30min',
        '30min_to_60min': '30min - 60min'
    }

    for time_group, stats in quartiles_results.items():
        values = stats['execution_time']
        count = values['count']
        geomean = values.get('geometric_mean')

        if count > 0 and geomean is not None:
            if geomean < 1.0:
                output += f"& $\\textbf{{{geomean:.2f}}}^{{{count}}}$ "
            else:
                output += f"& ${geomean:.2f}^{{{count}}}$ "
        else:
            output += "& {---} "

    output += allOutput
    percent1, percent2 = analyze_timeouts(file1_path, file2_path)
    output += f"& {percent1:.2f}\\% & {percent2:.2f}\\% \\\\ \n"

    column_labels = [
        "Index",
        "<1s",
        "1–10s",
        "10–30s",
        "30s–1m",
        "1–5m",
        "5–10m",
        "10–30m",
        "30–60m",
        "All",
        "Our(TimeOut)",
        "Baseline(TimeOut)"
    ]
    print("\n" + "=" * 50)
    print("Column labels:")
    print(" | ".join(column_labels))
    print("=" * 50)
    print(output)




