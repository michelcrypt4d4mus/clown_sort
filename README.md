![Python Version](https://img.shields.io/pypi/pyversions/clown_sort)
![Release](https://img.shields.io/pypi/v/clown_sort)
![Downloads](https://img.shields.io/pypi/dm/clown_sort)

# CLOWN SORT
Sometimes someone is being a clown on the internet. Somewhere on your hard drive is the perfect screenshot to prove to the world that the clown in question is a fool, a hypocrite, a criminal, or worse. But then - horrors - you can't find the screenshot! It has been lost in your vast archive of screenshots of clowns clowning themselves on the internet.

Clown Sort[^1] solves this.


## What It Do
It sorts screenshots, PDFs, etc. based on their name and/or their textual contents into folders based on a list of rules. The contents of the tweet/reddit post/whatever are prepended to the filename and the `ImageDescription` EXIF tag is set to the OCR text. As you can configure your own arbitrary rules and run it against any set of images it works on many things other than screenshots of social media clowns, though the default configuration is for cryptocurrency clowns.

For example this screenshot of a tweet by a noteworthy cryptocurrency "reporter"[^2] on the eve of FTX's implosion:

![](doc/larry_cermak_on_alameda_and_ftx.png)

Would be renamed from `Screen Shot 2023-02-17 at 7.11.37 PM.png` to

```
Tweet by @lawmaster: "I will say though before this thread gets taken over: 1. I do believe Alameda has the size to easily buy Binance\'s FIT OTC 2. I think the chance of FTX insolvency is near" Screen Shot 2023-02-17 at 7.11.37 PM.png
```

Other stuff that happens:
* The `ImageDescription` EXIF tag will be written (for images).
* All timestamps will be preserved.
* Files that match multiple patterns will be copied to multiple destination folders.
* The original file will be moved into a `Processed/` directory after it has been handled.

Note also that:
* This works on images that are more substantive than just self-clowning screenshots.
* So far only Tweets and Reddit screenshots have special handling beyond OCR text extraction.
* PDFs can be sorted by contents or filename, e.g. a PDF named `Norton Anthology of Crypto Bro Poetry.pdf` containing iambic verse like _["Fuck u justin sun  and fuck ur dick face... u all play with investing and money of the people !!!!"](https://universeodon.com/@cryptadamist/109642431382653023)_ by the noted bard JOKER_OF_CRYPTO will be copied to the `Justin Sun/` folder but not renamed.
* Videos are not OCRed and can only be moved based on filename matches, e.g. a file called `SBF is a big fat liar.mov` will be moved to the `FTX/` folder but otherwise left alone.

## Quick Start
```sh
# Installation with pipx is preferred if you have it but you can also use pip which comes standard
# on almost all systems. pipx is only a noticeably better answer if you're a python programmer who
# is concerned about side effects of pip upgrading system python packages.
pip install clown_sort[gui,pdf]

# Get help
sort_screenshots -h

# Dry run with default cryptocurrency sort rules (dry runs don't actually move anything,
# they just show you what will happen if you run again with the --execute flag)
sort_screenshots

# Execute default cryptocurrency sort rules against ~/Pictures/Screenshots with debug logging
sort_screenshots --execute --debug

# Sort a different directory of screenshots
sort_screenshots --screenshots-dir /Users/hrollins/Pictures/get_in_the_van/tourphotos --execute

# Sort with custom rules
sort_screenshots --rules-csv /Users/hrollins/my_war.csv --execute

# Sort PDFs
sort_screenshots -f '.*pdf$' -e

# Sort all files; use the manual folder selector window if file doesn't match any sort rules (may only work on macOS)
sort_screenshots -a -mf -e
```

# Setup
[pipx](https://pypa.github.io/pipx/) is recommended because it keeps your system python environment safe but you can also just use `pip`.

```sh
# Install with all packages including GUI and PDF handlers:
pipx install 'clown_sort[gui,pdf]'

# Install with optional GUI packages (required for --manual-fallback and --manual-sort options):
pipx install 'clown_sort[gui]' --force

# Install the minimal setup (no GUI, no encrypted PDF parsing):
pipx install 'clown_sort'
```

Some (not many) PDFs require the `pycryptodome` package to be parsed. This is installed when you install `clown_sort[pdf]`. If you don't install it these PDFS will not have their contents parsed and only the filename will be used for sorting.

Updating to the latest version can be accomplished with `pipx upgrade clown_sort`.


### Configuring With `.clown_sort` File
If there are command line options you find yourself specifying repeatedly you can place them in a `.clown_sort` file. When you invoke `sort_screenshots` the following locations will be checked for `.clown_sort`:

1. The current directory
2. Your home directory

See [the example](.clown_sort.example) for more information on what can be configured this way.

### Optional Components
If you want to use the popup window to manually tag you _may_ need to install:
* Python TK: `brew install python-tk@3.10` (if you don't have [homebrew](https://brew.sh/) you need to install it to run `brew install`)

Not required for standard PNG, JPG, etc. images but you may optionally install `exiftool` for other file types if you want excessive debugging.
* ExifTool: `brew install exiftool` or download from https://exiftool.org


# Usage
The default is for the tool to run in "dry run" mode, meaning it doesn't actually do anything - it just shows you what it _would_ do if you added the `--execute` flag. **YOU ARE ADVISED TO MAKE A BACKUP OF YOUR SCREENSHOTS FOLDER BEFORE HITTING THE `--execute` FLAG.**

While every effort has been made to use Python's cross platform `Pathlib` module as much as possible sometimes shit gets wonky on other platforms. This is 100x as true on Windows - Clown Sort has never been tested on a Windows platform.

### Help Screen
![](doc/sort_screenshots_help.png)

(In my personal usuage I tend to run the tool with the `--all` and `--manual-fallback` options.)

### Custom Sorting Rules
The default is to sort cryptocurrency related content but you can define your own CSV of rules with two columns, `folder` and `regex`.

* Lines whose first non-whitespace character is `#` will be considered to be comments and skipped as will empty lines
* `folder` specifies the subdirectory to sort into
* `regex` is the pattern to match against. See [the default crypto related configuration](clown_sort/sorting_rules/crypto.csv) for an example. An explanation of regular expressions is beyond the scope of this README but many resources are available to help. If you're not good at regexes just remember that any alphanumeric string is a regex that will match that string. [pythex](http://pythex.org/) is a great website for testing your regexes.

You can tell ClownSort to use your custom sorting rules file(s) either with the `--rules-csv` command line option or by setting `RULES_CSV_PATHS` in a `.clown_sort` file (see above).

### Example Output (Automated Sorting)
![](doc/output_example.png)


## Manually Sorting (Experimental)
**This is an experimental feature.** It's only been tested on macOS.

If you run with the `--manual-sort` command line the behavior is quite different. Rather than automatically sort files for you for every image file you will be greeted with a popup asking you for a desired filename and a radio button select of possible subdirectories off your `Sorted/` directory.

A related command line option is `--manual-fallback` which will popup a window only when the file is an image and has not matched any of the configured sorting rules.

To use this feature you must install the optional `PySimpleGUI` package which can be accomplished like this:
```sh
pipx install clown_sort[gui]
```

![](doc/manual_select_box.png)


## One Off Extractions
There are several utilities / convenience scripts / whatever you want to call them that are installed along with `clown_sort`. They work with the same toolset as `sort_screenshots` but use it to simplify the extraction of text from images (or PDFs that are actually just a set of page sized images).

#### Extracting text
`extract_text_from_files` is a convenient script you can use to extract text from a single file, multiple files, or all the files in a given directory using Google's best in class Tesseract library.

![](doc/extract_text_from_files_help.png)

As an example for extracting multiple files and/or directories:

```
extract_text_from_files MY_FILE1 MY_FILE2 SOME_DIR3
```

This will parse and display the text in `MY_FILE1`, `MY_FILE2`, and all the files in `SOME_DIR3`.

#### Extracting pages of a PDF to a new PDF
`extract_pages_from_pdf` is a small script that can extract page ranges (e.g. "10-25") from PDFs on the command line.
![](doc/extract_pages_from_pdf_help.png)

#### Purging PDFs for a directory
`purge_non_images_from_dir` is a small script that will remove PDFs from a directory as long as there is at least one other copy of that PDF in the sorted file hierarchy.


# Contributing
Feel free to file issues or open pull requests.

This package is managed with [Python Poetry](http://python-poetry.org/). To get going:
1. Install Poetry.
1. `git clone` this repo.
1. `cd clown_sort`
1. `poetry install`
1. Optional components can be install with `poetry install --all-extras`

Only requirement is that tests should pass before you open it which you can check by running `pytest`.

### Running Tests
Test suite can be launched with `pytest`. If you do some development and something goes weird and you're continually running into errors about non-empty directories try clearing out the test suite's temp directory by deleting the contents of `tests/tmp/` (`rm -fr tests/tmp/*` on Linux or macOS etc.).

[^1]: The name `clown_sort` was suggested by [ParrotCapital](http://twitter.com/ParrotCapital) and while the tool can work on any kind of screenshot it was too good not to use.

[^2]: Perhaps notable that the "reporter" in question for years maintained a private list of the blockchain addresses of Sam Bankman-Fried's various scams as part of his commitment to "unrivaled transparency".
