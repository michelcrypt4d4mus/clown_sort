# Screenshot Sorter
Sort screenshots, PDFs, etc. based on their name and/or their contents based on a list of rules. The default is to sort cryptocurrency related content but you can define your own CSV of rules with two columns `folder`, `regex`. See [the default crypto related configuration](image_namer/sorting_rules/crypto.csv).

# Setup
You may need to install:
* Python TK: `brew install python-tk@3.10`
* ExifTool: `brew install exiftool` or download from https://exiftool.org

### Quick Start
```sh
pipx install screenshots_sorter

# Get help
sort_screenshots -h

# Dry run (don't actually move anything)
sort_screenshots

# Execute
sort_screenshots -e
```
