from utils.db_utils import initialize_db
from utils.filename_utils import compare_file_names
from utils.hash_utils import find_duplicates 
import argparse
import os 

def main():
    initialize_db()  # 初始化数据库

    parser = argparse.ArgumentParser(description="SmartFileSweep: Remove duplicated or similar files")
    parser.add_argument("directory", type=str, help="Directory to scan")
    parser.add_argument("--action", choices=["list", "delete"], default="list",
                        help="Action to take on duplicates (default: list)")
    args = parser.parse_args()

    directory = args.directory
    action = args.action

    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    print(f"Scanning directory: {directory}")
    duplicates = find_duplicates(directory)
    print_duplicates(action, duplicates)

    similar_files = compare_file_names(directory)
    print_similar_files(similar_files)

def print_duplicates(action, duplicates):
    if not duplicates:
        print("No duplicate files found.")
    else:
        print("Duplicate files:")
        for dup, copies in duplicates:
            print(f" - {dup} has duplicates: {', '.join(copies)}")

        if action == "delete":
            for dup, copies in duplicates:
                os.remove(dup)
            print("Duplicates deleted.")

def print_similar_files(similar_files):
    for file1, file2, similarity in similar_files:
        print(f"{file1} <--> {file2} (Similarity: {similarity:.2f})")

if __name__ == "__main__":
    main()
    print("done...")