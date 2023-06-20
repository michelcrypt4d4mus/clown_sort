#!/usr/bin/env python3
# Extract text from a single file or from all files in a given directory. Can accept
# multiple paths as arguments.

import sys
from pathlib import Path

from clown_sort import build_sortable_file
from clown_sort.util.rich_helper import console
from clown_sort.util.filesystem_helper import files_in_dir


console.line()

if len(sys.argv) <= 1:
    print("Provide at least one filename to extract.")
    sys.exit()

files_to_process = []

for file_path in sys.argv[1:]:
    if Path(file_path).is_dir():
        files_to_process.extend(files_in_dir(file_path))
    else:
        files_to_process.append(file_path)

for file_path in files_to_process:
    build_sortable_file(file_path).print_extracted_text()
    console.line(2)
