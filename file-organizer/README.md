# File Organizer

A command-line tool written in Python that automates common file-management
tasks: sorting files by type, finding duplicates, renaming by date, and
generating summary reports.

## Features

- **Sort by type** — moves files into `Images/`, `Documents/`, `Videos/`,
  `Audio/`, `Archives/`, `Code/`, or `Other/` based on extension.
- **Find duplicates** — scans a folder (recursively) and groups files with
  identical content using SHA-256 hashing.
- **Rename by date** — prefixes filenames with their last-modified date
  (`YYYY-MM-DD_filename.ext`).
- **Generate report** — prints a table of file counts and total size per
  category.

## Why I built this

I wanted a small but genuinely useful project to practice core Python skills:
file I/O, the standard library (`os`, `shutil`, `hashlib`, `argparse`), and
writing a clean CLI. It's also something I actually use to clean up my own
Downloads folder.

## Installation

No external dependencies — just Python 3.8+.

```bash
git clone <your-repo-url>
cd file-organizer
```

## Usage

```bash
# Show a summary report of a folder
python organizer.py /path/to/folder --report

# Sort files into category subfolders
python organizer.py /path/to/folder --sort

# Find duplicate files
python organizer.py /path/to/folder --find-duplicates

# Rename files with their last-modified date
python organizer.py /path/to/folder --rename-by-date

# Run report, then sort, then find duplicates, in sequence
python organizer.py /path/to/folder --all
```

## Example output

```
Category        Files         Size
----------------------------------
Code                3        4.2KB
Documents           5       128.0KB
Images              12       3.4MB
----------------------------------
TOTAL               20       3.5MB
```

## Possible extensions

- Add a `--undo` option that reverses the last sort operation
- Add a simple GUI with `tkinter`
- Support custom category rules via a config file
- Add unit tests with `pytest`

## License

MIT
