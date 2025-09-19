"""
Wrapper for PDF files.
"""
import io
from pathlib import Path
from typing import List, Optional

from pdfalyzer.decorators.pdf_file import PdfFile as PdfalyzerFile

from clown_sort.config import Config, check_for_pymupdf
from clown_sort.files.sortable_file import SortableFile
from clown_sort.lib.page_range import PageRange
from clown_sort.util.constants import PDF_ERRORS
from clown_sort.util.logging import log
from clown_sort.util.rich_helper import WARNING, console, print_error

DEFAULT_PDF_ERRORS_DIR = Path.cwd().joinpath(PDF_ERRORS)
MAX_DISPLAY_HEIGHT = 600
SCALE_FACTOR = 0.4


class PdfFile(SortableFile):
    """
    Wrapper for PDF files.

    Attributes:
        text_extraction_attempted (bool): Whether text extraction has been attempted.
        _extracted_text (Optional[str]): The extracted text from the PDF.
        _page_numbers_of_errors (List[int]): List of page numbers where errors occurred during extraction.
        _is_presentable_in_popup (Optional[bool]): `[class variable]` Cached value indicating if the PDF
            can be presented in a popup.
    """

    _is_presentable_in_popup = None

    def extracted_text(self, page_range: Optional[PageRange] = None) -> Optional[str]:
        """Use PyPDF to extract text page by page and use Tesseract to OCR any embedded images."""
        if self.text_extraction_attempted:
            return self._extracted_text


        pdf_file = PdfalyzerFile(self.file_path)
        self._extracted_text = pdf_file.extract_text(page_range, log, Config.print_as_parsed)
        self.text_extraction_attempted = True
        return self._extracted_text

    def thumbnail_bytes(self) -> Optional[bytes]:
        """Return bytes for a thumbnail image."""
        import fitz  # TODO: Can we do this without PyMuPDF dependency?

        try:
            doc = fitz.open(self.file_path)
        except fitz.EmptyFileError:
            log.warning(f"EmptyFileError: Failed to get bytes for '{self.file_path}'")
            return None

        try:
            # Attempt to resize the thumbnail to fit the screen
            log.debug(f"Getting bytes for '{self.file_path}'...")
            zoom_matrix = fitz.Matrix(fitz.Identity).prescale(SCALE_FACTOR, SCALE_FACTOR)
            page = doc[0]
        except IndexError as e:
            print_error(f"Error getting thumbnail for PDF file '{self.file_path}': {e}")
            return None

        bottom_right = page.rect.br
        page_height = bottom_right[1]
        page_width = bottom_right[0]

        # Check for PDFs with very long pages and crop them
        if SCALE_FACTOR * page_height > MAX_DISPLAY_HEIGHT:
            log.debug(f"PDF page is {page_height} pixels high so cropping...")
            clip = fitz.Rect((0, 0), (MAX_DISPLAY_HEIGHT / SCALE_FACTOR, page_width))
        else:
            clip = fitz.Rect((0, 0), bottom_right)

        return page.get_pixmap(matrix=zoom_matrix, clip= clip, alpha=False).tobytes()

    def print_extracted_text(self, page_range: Optional[PageRange] = None) -> None:
        console.print(self._filename_panel())
        console.print(self.extracted_text(page_range=page_range))

    def can_be_presented_in_popup(self) -> bool:
        """A PDF can be presented in a popup window if PyMuPDF is installed."""
        if type(self)._is_presentable_in_popup is None:
            type(self)._is_presentable_in_popup = check_for_pymupdf()

        if not type(self)._is_presentable_in_popup:
            console.line()
            msg = WARNING.append(f"File '{self.basename}' is not displayable without pymupdf...\n")
            console.print(msg)

        return bool(type(self)._is_presentable_in_popup)

    def __repr__(self) -> str:
        return f"PdfFile('{self.file_path}')"
