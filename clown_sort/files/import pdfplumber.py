import pdfplumber

PDF = '/Users/syblius/Pictures/Screenshots/Sorted/Tether/Tether Portfolio Report 2021-03-31 from Ansbacher.pdf'

pdf = pdfplumber.open(PDF)
pdf.pages[5].to_image()

table_settings = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    # "snap_y_tolerance": 5,
    # "intersection_x_tolerance": 15,
}

table = pdf.pages[5].extract_table(table_settings)
