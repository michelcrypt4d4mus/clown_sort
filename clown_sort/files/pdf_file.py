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
            import pdb;pdb.set_trace()
            log_optional_module_warning('pycryptodome')
        except KeyError:
            # TODO: failure on KeyError: '/Root' seems to have been fixed but not released yet
            # https://github.com/py-pdf/pypdf/pull/1784
            log.warn("Failed to parse PDF!")

        if self._extracted_text is not None:
            self._extracted_text = self._extracted_text.strip()

        self.text_extraction_attempted = True
        return self._extracted_text

    def __repr__(self) -> str:
        return f"PdfFile('{self.file_path}')"
