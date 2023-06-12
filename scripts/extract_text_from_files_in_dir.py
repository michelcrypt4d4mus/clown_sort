import pytesseract
from PIL import Image

from clown_sort.util.filesystem_helper import (IMAGE_FILE_EXTENSIONS, files_in_dir, is_image,
      is_pdf, set_timestamp_based_on_screenshot_filename)


for f in files_in_dir("/Users/syblius/Screenshots/binance_us_wallets/"):
    extracted_text = pytesseract.image_to_string(Image.open(f))
    print(f"\n\n\n\n\n\n\n\n\n\nFILE: '{f}'")
    print(extracted_text)
