"""
Wrapper for PDF files.
"""
import io
import logging
from sys import exit
from typing import Optional

import pytesseract
from PIL import Image
from PIL.ExifTags import TAGS
from pypdf import PdfReader
from pypdf.errors import DependencyError, EmptyFileError

from clown_sort.config import check_for_pymupdf, log_optional_module_warning
from clown_sort.files.image_file import ImageFile
from clown_sort.files.sortable_file import SortableFile
from clown_sort.util.logging import log
from clown_sort.util.rich_helper import WARNING, console, warning_text

MAX_DISPLAY_HEIGHT = 600
SCALE_FACTOR = 0.4


class PdfFile(SortableFile):
    is_presentable_in_popup = None

    def extracted_text(self) -> Optional[str]:
        """Use Tesseract to OCR the text in the image, which is returned as a string."""
        if self.text_extraction_attempted:
            return self._extracted_text

        self._extracted_text = None
        log.debug(f"Extracting text from '{self.file_path}'...")

        try:
            pdf_reader = PdfReader(self.file_path)
            self._extracted_text = '\\n\\n'.join([page.extract_text() for page in pdf_reader.pages])
        except DependencyError:
            log_optional_module_warning('pdf')
        except EmptyFileError:
            log.warn("Skipping empty file!")
        except (KeyError, TypeError):
            # TODO: failure on KeyError: '/Root' seems to have been fixed but not released yet
            # https://github.com/py-pdf/pypdf/pull/1784
            log.warn("Failed to parse PDF!")

        if self._extracted_text is not None:
            self._extracted_text = self._extracted_text.strip()

        if self._extracted_text is None or len(self._extracted_text):
            log.warn("Attempting PDF image extraction for '{self.file_path}'...")
            self._extracted_text = self._extract_text_from_images_pdf()

        self.text_extraction_attempted = True
        return self._extracted_text

    def thumbnail_bytes(self) -> Optional[bytes]:
        """Return bytes for a thumbnail."""
        import fitz
        log.debug(f"Getting bytes for '{self.file_path}'...")

        try:
            doc = fitz.open(self.file_path)
        except fitz.fitz.EmptyFileError:
            return None

        zoom_matrix = fitz.Matrix(fitz.Identity).prescale(SCALE_FACTOR, SCALE_FACTOR)
        page = doc[0]
        bottom_right = page.rect.br
        page_height = bottom_right[1]
        page_width = bottom_right[0]

        # Check for PDFs with very long pages and crop them
        if SCALE_FACTOR * page_height > MAX_DISPLAY_HEIGHT:
            logging.debug(f"PDF page is {page_height} pixels high so cropping...")
            clip = fitz.Rect((0, 0), (MAX_DISPLAY_HEIGHT / SCALE_FACTOR, page_width))
        else:
            clip = fitz.Rect((0, 0), bottom_right)

        return page.get_pixmap(matrix=zoom_matrix, clip= clip, alpha=False).tobytes()

    def _can_be_presented_in_popup(self) -> bool:
        if type(self).is_presentable_in_popup is None:
            type(self).is_presentable_in_popup = check_for_pymupdf()

        if not type(self).is_presentable_in_popup:
            console.line()
            msg = WARNING.append(f"File '{self.basename}' is not displayable without pymupdf...\n")
            console.print(msg)

        return type(self).is_presentable_in_popup

    def __repr__(self) -> str:
        return f"PdfFile('{self.file_path}')"

    def _extract_text_from_images_pdf(self) -> str:
        """Some PDFs have a big image for each page instead of extractable text."""
        import fitz
        pdf_file = fitz.open(self.file_path)
        extracted_pages = []

        #iterate over PDF pages
        for page_index in range(pdf_file.page_count):
            page = pdf_file[page_index]
            image_li = page.get_images()

            if image_li:
                log.debug(f"[+] Found a total of {len(image_li)} images in page {page_index + 1}")
            else:
                log.debug(f"[!] No images found on page {page_index + 1}")

            for image_index, img in enumerate(page.get_images(), start=1):
                xref = img[0]
                base_image = pdf_file.extract_image(xref)
                image_extension = base_image["ext"]
                image = Image.open(io.BytesIO(base_image["image"]))
                image_name =  f"PAGE_{page_index+1}_Image_{image_index}.{image_extension}"

                try:
                    extracted_pages.append(ImageFile.extract_text(image, image_name))
                except OSError as e:
                    if 'truncated' in str(e):
                        console.print(warning_text(f"Truncated image file! '{self.file_path}'!"))
                    else:
                        console.print_exception()
                        console.print(f"Error while extracting '{self.file_path}'!", style='bright_red')
                        raise e
                except Exception as e:
                    console.print_exception()
                    console.print(f"Error while extracting '{self.file_path}'!", style='bright_red')
                    raise e

        return '\\n\\n'.join(extracted_pages)
