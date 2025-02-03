# NEXT RELEASE

### 1.13.1
* Fix logging of EXIF data when there's an exception attempting to save an image

# 1.13.0
* `purge_non_images_from_dir()` script

### 1.12.1
* Fix bug with `extract_text_from_files` helper tool

# 1.12.0
* Sort files based on unidecoded ASCII text (i.e. without diacritics, accents, umlauts, etc.)
* More default sorting rules

# 1.11.0
* New `--hide-dirs` option
* New `--anonymize-user-dir` option
* Bump `PyPDF` to `5.0.1`
* More default sorting rules

### 1.10.3
* Upgrade `PyPDF` to `4.3.1`
* Handle exceptions arising when trying to extract pages for submission as `PyPDF` bugs
* Fix displaying contents of PDF text by escaping text that looks like a `rich` markup tag
* New default sorting rules

### 1.10.2
* Make `\b` word boundary in a configured `SortRule` also match against underscores (which it doesn't by default)
* New default sorting rules
* Make `RuleMatch` a real class

### 1.10.1
* New default sorting rules

# 1.10.0
* New script `extract_pages_from_pdf` lets you easily rip pages out of a PDF
* Add `--page-range` argument to both `extract_pages_from_pdf` and `extract_text_from_files`
* `pypdf` exceptions will trigger the offending page to be extracted and a suggestion made to the user that they submit the page to the `pypdf` team
* Bump `pypdf` to version 3.14.0 (fixes for many bugs on edge case PDFs)
* Better handling of sort rules that fail to parse
* New crypto sort rules
* Rename `--print-when-parsed` command line option to `--print-as-parsed`
* Suppress `/JBIG2Decode` warning output when decoding PDFs
* Refactor overwrite confirmation, use stderr

### 1.9.2
* Allow `Pillow` 10.0.0
* Reduce required python version to 3.8

### 1.9.1
* Output progress notifications to STDERR when parsing text from very large PDFs
* Fix issue that caused explosive memory growth when parsing large PDFs
* `--print-when-parsed` command line option for `extract_text_from_files`
* Upgrade `pypdf` to 3.12.0 to resolve various PDF parsing failures
* PDFs: Handle various exceptions when enumerating embedded images:
   * `OSError: cannot write mode CMYK as PNG`
   * `ValueError: not enough image data`
   * `TypeError: unhashable type: 'ArrayObject'`
   * `TypeError: unhashable type: 'IndirectObject'`

# 1.9.0
* Parse text from images in PDFs (some PDFs have no text only images)
* Improve `extract_text_from_files` functionality

### 1.8.1
* Actually make `extract_text_from_files` executable

# 1.8.0
* Add a script to extract files
* More default sort rules

### 1.7.1
* Handle 0 byte PDF error
* More default rules

# 1.7.0
* Skip comment rows starting with `#` in rules CSVs.
* New default rules

### 1.6.4
* Crop very long PDF pages when previewing in manual select window
* Fix regexes for wallet addresses
* Gracefully handle failures in file timestamp copying call

### 1.6.3
* Fix bug with manual folder selection
* Refactor `move_to_processed_dir()` and call from `sort_selector.py`.

### 1.6.2
* Add `--force` and `[gui,pdf]` to the `pipx` installation instructions

### 1.6.1
* Make the brackets print in the optional package install instructions
* Only check for `pymupdf` once

## 1.6.0
* PDF previews in manual sorting windows

### 1.5.2
* Override premature release

### 1.5.1
* Fix the install messages for missing packages

## 1.5.0
* Combobox instead of radio buttons for manual fallback directory select
* Replace fewer special characters in filenames
* New default crypto sort rules

### 1.4.1
* Make --manual-fallback and --only-if-match mutually exclusive
* New default crypto sort rules

## 1.4.0
* Add `--manual-fallback` option
* Handle truncated image file binary errors
* Display the string that matched the rule when copying
* Better handling of re-scanning already sorted files
* New crypto sorting rules

### 1.3.3
* Handle more unparseable PDF issues more gracefully
* New crypto sort rules

### 1.3.2
* Make `--rescan-sorted` respect `--all` flag
* Don't append empty string to images that no text was extracted from
* More crypto sort rules

### 1.3.1
* Handle unparseable PDFs with a warning instead of a crash.
* `--yes-overwrite` option should not default to true
* New crypto sort rules (MCB and CUBI now sorted to their own directories instead of 'Banks')

## 1.3.0
* Ask for confirmation before overwriting files (`--yes-overwrite` option to skip the check)
* Check if image's extracted text is already in the filename (important if rescanning)
* New crypto sort rules

## 1.2.0
* `--only-if-match` option
* New crypto sort rules

## 1.1.0
* Filenames for retweets
* New crypto sort rules

### 1.0.1
* New sort rules

# 1.0.0
* Wallet address sorting rules

## 0.9.2
* Apply extracted text to non-Tweets, non-Reddit posts.
* `--delete-originals` option
* `--rescan-sorted` option
* Avoid moving files that start in a sorted location out to the processed dir

## 0.8.0
* `--manual-sort` option
* Couple new sorting rules

## 0.7.0
* Read `CLOWN_SORT_FILENAME_REGEX` default from env.

### 0.6.1
* Fix PySimpleGui packages reqs

## 0.6.0
* Read `CLOWN_SORT_SCREENSHOTS_DIR` and `CLOWN_SORT_DESTINATION_DIR` defaults.
* Use tilde notation for home dir in default args.

## 0.5.1
* Only sort filenames if they match the regex OR have a sorting folder match

## 0.5.0
* Allow multiple rules CSV files
* Allow configuration of rules CSV files via `.clown_sort` file

## O.4.0
* Improve Tweet matching
* Improve logging
* Rename to `clown_sort`

### 0.3.1
* Logging adjustments

## 0.3.0
* `--show-rules` argument, `--debug` argument
* More sorting rules
* Logging adjustments

### 0.2.3
* Logging adjustments.

### 0.2.2
* Copy non image files so they can be sent to multiple folders.

### 0.2.1
* Preserve all timestamps

## 0.2.0
* More command line args

# 0.1.0
* Initial release.
