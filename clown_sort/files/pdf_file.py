"""
Wrapper for PDF files.
"""
from typing import Optional

from pypdf import PdfReader
from pypdf.errors import DependencyError

from clown_sort.config import log_optional_module_warning
from clown_sort.util.logging import log
from clown_sort.files.sortable_file import SortableFile


class PdfFile(SortableFile):
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
        try:
            import fitz
            doc = fitz.open(self.file_path)
        except DependencyError:
            log_optional_module_warning('pdf')

        zoom_matrix = fitz.Matrix(fitz.Identity).prescale(0.4, 0.4)
        page = doc[0].get_pixmap(matrix=zoom_matrix, alpha=False)
        return page.tobytes()

    def _can_be_presented_in_popup(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"PdfFile('{self.file_path}')"
