"""
Wrapper for PDF files.
"""
import logging
from sys import exit
from typing import Optional

from pypdf import PdfReader
from pypdf.errors import DependencyError, EmptyFileError

from clown_sort.config import check_for_pymupdf, log_optional_module_warning
from clown_sort.util.rich_helper import WARNING, console
from clown_sort.util.logging import log
from clown_sort.files.sortable_file import SortableFile

MAX_DISPLAY_HEIGHT = 600
SCALE_FACTOR = 0.4


class PdfFile(SortableFile):
    is_presentable_in_popup = None

    def extracted_text(self) -> Optional[str]:
        """Use Tesseract to OCR the text in the image, which is returned as a string."""
        if self.text_extraction_attempted:
            return self._extracted_text

        self._extracted_text = None

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

        self.text_extraction_attempted = True
        return self._extracted_text

    def thumbnail_bytes(self) -> bytes:
        """Return bytes for a thumbnail."""
        import fitz

        try:
            doc = fitz.open(self.file_path)
        except fitz.fitz.EmptyFileError:
            return b''

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
