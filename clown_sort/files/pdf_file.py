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
from rich.panel import Panel

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

        log.debug(f"Extracting text from '{self.file_path}'...")
        extracted_pages = []

        try:
            pdf_reader = PdfReader(self.file_path)

            for page_number, page in enumerate(pdf_reader.pages):
                page_text = str(Panel(f"Page {page_number}", style='reverse', width=30)) + "\n"
                page_text += page.extract_text().strip()

                for image_number, image in enumerate(page.images, start=1):
                    image_name = f"PAGE_{page_number + 1}_Image_{image_number}"
                    image_obj = Image.open(io.BytesIO(image.data))
                    image_text = ImageFile.extract_text(image_obj, image_name) or ''
                    page_text += f"\n\n{image_name}\n-------------------\n{image_text.strip()}"

                console.print(page_text)
                extracted_pages.append(page_text)
        except DependencyError:
            log_optional_module_warning('pdf')
        except EmptyFileError:
            log.warn("Skipping empty file!")
        except (KeyError, TypeError):
            # TODO: failure on KeyError: '/Root' seems to have been fixed but not released yet
            # https://github.com/py-pdf/pypdf/pull/1784
            log.warn(f"Failed to parse PDF: '{self.file_path}'!")

        self.text_extraction_attempted = True
        self._extracted_text = "\n\n".join(extracted_pages).strip()
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
