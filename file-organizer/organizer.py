"""
File Organizer - A portfolio project for automation.

Features:
1. Sort files into folders by type (images, documents, videos, etc.)
2. Detect and report duplicate files using content hashing
3. Rename files based on their last-modified date
4. Generate a summary report of folder contents

Usage:
    python organizer.py /path/to/folder --sort
    python organizer.py /path/to/folder --find-duplicates
    python organizer.py /path/to/folder --rename-by-date
    python organizer.py /path/to/folder --report
    python organizer.py /path/to/folder --all
"""

import argparse
import hashlib
import os
import shutil
import sys
from collections import defaultdict
from datetime import datetime

# Map file extensions to category folders
CATEGORY_MAP = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".md", ".xlsx", ".pptx", ".csv"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv"],
    "Audio": [".mp3", ".wav", ".flac", ".aac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".js", ".html", ".css", ".json", ".java", ".cpp", ".c"],
}


def get_category(filename):
    """Return the category folder name for a given file, based on extension."""
    ext = os.path.splitext(filename)[1].lower()
    for category, extensions in CATEGORY_MAP.items():
        if ext in extensions:
            return category
    return "Other"


def sort_files(folder):
    """Move each file in `folder` into a subfolder based on its type."""
    moved_count = 0
    for entry in os.listdir(folder):
        full_path = os.path.join(folder, entry)

        # Skip directories and the script itself
        if os.path.isdir(full_path):
            continue

        category = get_category(entry)
        category_folder = os.path.join(folder, category)
        os.makedirs(category_folder, exist_ok=True)

        destination = os.path.join(category_folder, entry)
        # Avoid overwriting a file with the same name
        destination = _unique_path(destination)

        shutil.move(full_path, destination)
        moved_count += 1
        print(f"Moved: {entry} -> {category}/")

    print(f"\nDone. {moved_count} file(s) organized.")


def _unique_path(path):
    """If `path` already exists, append a counter until it doesn't."""
    if not os.path.exists(path):
        return path

    base, ext = os.path.splitext(path)
    counter = 1
    new_path = f"{base}_{counter}{ext}"
    while os.path.exists(new_path):
        counter += 1
        new_path = f"{base}_{counter}{ext}"
    return new_path


def _hash_file(path, block_size=65536):
    """Return the SHA-256 hash of a file's contents."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(block_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicates(folder):
    """Scan `folder` recursively and report groups of duplicate files."""
    hashes = defaultdict(list)

    for root, _, files in os.walk(folder):
        for filename in files:
            full_path = os.path.join(root, filename)
            try:
                file_hash = _hash_file(full_path)
                hashes[file_hash].append(full_path)
            except (OSError, PermissionError) as e:
                print(f"Skipping {full_path}: {e}")

    duplicates_found = False
    for file_hash, paths in hashes.items():
        if len(paths) > 1:
            duplicates_found = True
            print(f"\nDuplicate group (hash: {file_hash[:10]}...):")
            for p in paths:
                print(f"  - {p}")

    if not duplicates_found:
        print("No duplicate files found.")

    return hashes


def rename_by_date(folder):
    """Rename each file in `folder` to include its last-modified date."""
    renamed_count = 0
    for entry in os.listdir(folder):
        full_path = os.path.join(folder, entry)
        if os.path.isdir(full_path):
            continue

        mtime = os.path.getmtime(full_path)
        date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        name, ext = os.path.splitext(entry)

        # Don't re-prefix a file that's already been renamed
        if name.startswith(date_str):
            continue

        new_name = f"{date_str}_{name}{ext}"
        new_path = _unique_path(os.path.join(folder, new_name))

        os.rename(full_path, new_path)
        renamed_count += 1
        print(f"Renamed: {entry} -> {os.path.basename(new_path)}")

    print(f"\nDone. {renamed_count} file(s) renamed.")


def generate_report(folder):
    """Print a summary of file counts and total size per category."""
    stats = defaultdict(lambda: {"count": 0, "size": 0})

    for root, _, files in os.walk(folder):
        for filename in files:
            full_path = os.path.join(root, filename)
            category = get_category(filename)
            try:
                size = os.path.getsize(full_path)
            except OSError:
                continue
            stats[category]["count"] += 1
            stats[category]["size"] += size

    print(f"\n{'Category':<12} {'Files':>8} {'Size':>12}")
    print("-" * 34)

    total_count = 0
    total_size = 0
    for category, data in sorted(stats.items()):
        total_count += data["count"]
        total_size += data["size"]
        print(f"{category:<12} {data['count']:>8} {_human_size(data['size']):>12}")

    print("-" * 34)
    print(f"{'TOTAL':<12} {total_count:>8} {_human_size(total_size):>12}")


def _human_size(num_bytes):
    """Convert a byte count into a human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f}{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f}TB"


def main():
    parser = argparse.ArgumentParser(
        description="Organize, deduplicate, rename, and report on files in a folder."
    )
    parser.add_argument("folder", help="Path to the folder to process")
    parser.add_argument("--sort", action="store_true", help="Sort files into category folders")
    parser.add_argument("--find-duplicates", action="store_true", help="Find duplicate files")
    parser.add_argument("--rename-by-date", action="store_true", help="Rename files with their modified date")
    parser.add_argument("--report", action="store_true", help="Print a summary report")
    parser.add_argument("--all", action="store_true", help="Run report, then sort, then find duplicates")

    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print(f"Error: '{args.folder}' is not a valid folder.")
        sys.exit(1)

    if not any([args.sort, args.find_duplicates, args.rename_by_date, args.report, args.all]):
        parser.print_help()
        sys.exit(0)

    if args.all:
        generate_report(args.folder)
        sort_files(args.folder)
        find_duplicates(args.folder)
        return

    if args.report:
        generate_report(args.folder)
    if args.rename_by_date:
        rename_by_date(args.folder)
    if args.sort:
        sort_files(args.folder)
    if args.find_duplicates:
        find_duplicates(args.folder)


if __name__ == "__main__":
    main()
