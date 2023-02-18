# Screenshot Sorter
Sort screenshots, PDFs, etc. based on their name and/or their contents into folders based on a list of rules.

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

# Usage
The default is to sort cryptocurrency related content but you can define your own CSV of rules with two columns `folder` and `regex`. The value in `folder` specifies the subdirectory to sort into and `regex` is the pattern to match against. See [the default crypto related configuration](image_namer/sorting_rules/crypto.csv) for an example. An explanation of regular expressions is beyond the scope of this README but many resources are available to help. if you're not good at regexes just remember that any alphanumeric string is a regex that will match that string. [pythex](http://pythex.org/) is a great website for testing your regexes.
