# Render the --help output to a .png file in the doc/ directory.

RENDER_HELP_FORMAT=png RENDER_HELP_OUTPUT_DIR=doc/ sort_screenshots -h
RENDER_HELP_FORMAT=png RENDER_HELP_OUTPUT_DIR=doc/ extract_text_from_files -h
RENDER_HELP_FORMAT=png RENDER_HELP_OUTPUT_DIR=doc/ extract_pages_from_pdf -h
