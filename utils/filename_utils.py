import os
from difflib import SequenceMatcher
import fnmatch


def load_ignore_patterns(config_path="config/ignore_files.txt"):
    """Load ignore patterns from the config file."""
    if not os.path.exists(config_path):
        print(f"Config file {config_path} not found. No files will be ignored.")
        return []

    with open(config_path, "r") as f:
        patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return patterns

def should_ignore(file_name, ignore_patterns):
    """Check if a file should be ignored based on patterns."""
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(file_name, pattern):
            return True
    return False

def compare_file_names(file_paths, threshold=0.8):
    ignore_patterns = load_ignore_patterns()
    
    """Compare file and folder names for similarity"""
    similar_files = []

    # Separate files and folders
    entries = []
    for root, _, files in os.walk(file_paths):
        for path in files:
            if should_ignore(path, ignore_patterns):
                continue  # Skip this file 
            print('path ', path)
            if os.path.isdir(path):
                # Add folder names
                entries.append((os.path.basename(path) + "/", path))
            else:
                # Add file names
                entries.append((os.path.basename(path), path))

    # Compare all entries (files and folders)
    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            name1, path1 = entries[i]
            name2, path2 = entries[j]
            similarity = SequenceMatcher(None, name1, name2).ratio()
            if similarity >= threshold:
                similar_files.append((path1, path2, similarity))

    return similar_files