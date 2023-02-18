"""
Wrapper for PDF files.
"""
from typing import Optional

from pypdf import PdfReader

from social_arsenal.files.sortable_file import SortableFile


class PdfFile(SortableFile):
    def extracted_text(self) -> Optional[str]:
        """Use Tesseract to OCR the text in the image, which is returned as a string."""
        if self.text_extraction_attempted:
            return self._extracted_text

        pdf_reader = PdfReader(self.file_path)
        self._extracted_text = '\\n\\n'.join([page.extract_text() for page in pdf_reader.pages])
        self.text_extraction_attempted = True
        return self._extracted_text

    def __repr__(self) -> str:
        return f"PdfFile('{self.file_path}')"
