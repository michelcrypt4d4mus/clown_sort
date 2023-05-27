# NEXT RELEASE
* Override premature release

# 1.5.0
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
