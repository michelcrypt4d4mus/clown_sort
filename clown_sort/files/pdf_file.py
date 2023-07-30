"""
Wrapper for PDF files.
"""
import io
import os
from pathlib import Path
from typing import Optional

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.errors import DependencyError, EmptyFileError
from rich.console import Console
from rich.panel import Panel

from clown_sort.config import Config, check_for_pymupdf, log_optional_module_warning
from clown_sort.files.image_file import ImageFile
from clown_sort.files.sortable_file import SortableFile
from clown_sort.util.constants import MIN_PDF_SIZE_TO_LOG_PROGRESS_TO_STDERR, PDF_ERRORS
from clown_sort.util.filesystem_helper import create_dir_if_it_does_not_exist, insert_suffix_before_extension
from clown_sort.util.logging import log
from clown_sort.util.rich_helper import WARNING, console, stderr_console

DEFAULT_PDF_ERRORS_DIR = Path.cwd().joinpath(PDF_ERRORS)
MAX_DISPLAY_HEIGHT = 600
SCALE_FACTOR = 0.4


class PdfFile(SortableFile):
    is_presentable_in_popup = None

    def extracted_text(self) -> Optional[str]:
        """Use Tesseract to OCR the text in the image, which is returned as a string."""
        if self.text_extraction_attempted:
            return self._extracted_text

        log.debug(f"Extracting text from '{self.file_path}'...")
        already_extracted_page_numbers = []
        extracted_pages = []

        try:
            pdf_reader = PdfReader(self.file_path)
            page_count = len(pdf_reader.pages)
            log.debug(f"PDF Page count: {page_count}")

            for page_number, page in enumerate(pdf_reader.pages, start=1):
                self._log_to_stderr(f"Parsing page {page_number}...")
                page_buffer = Console(file=io.StringIO())
                page_buffer.print(Panel(f"PAGE {page_number}", padding=(0, 15), expand=False))
                page_buffer.print(page.extract_text().strip())
                image_number = 1

                # Extracting images is a bit fraught (lots of PIL and pypdf exceptions have come from here)
                try:
                    for image_number, image in enumerate(page.images, start=1):
                        image_name = f"Page {page_number}, Image {image_number}"
                        self._log_to_stderr(f"   Processing {image_name}...")
                        page_buffer.print(Panel(image_name, expand=False))
                        image_obj = Image.open(io.BytesIO(image.data))
                        image_text = ImageFile.extract_text(image_obj, f"{self.file_path} ({image_name})")
                        page_buffer.print((image_text or '').strip())
                except (OSError, NotImplementedError, TypeError, ValueError) as e:
                    stderr_console.print(f"WARNING: {type(e).__name__}: {e} while parsing embedded image {image_number} on page {page_number}...")

                    # Dump an error PDF and encourage user to report to pypdf team.
                    if 'JBIG2Decode' not in str(e):
                        stderr_console.print_exception()

                        # Avoid dumping multiple times if multiple images fail on same page
                        if page_number not in already_extracted_page_numbers:
                            # Handle case where Config.configure() wasn't called by defaulting to current dir
                            if 'pdf_errors_dir' in dir(Config):
                                create_dir_if_it_does_not_exist(Config.pdf_errors_dir)
                                destination_dir = Config.pdf_errors_dir
                            else:
                                destination_dir = DEFAULT_PDF_ERRORS_DIR

                            extracted_file = self.extract_page_range(page_number, destination_dir=destination_dir)
                            stderr_console.print(f"Extracted page causing the issue to '{extracted_file}'.")
                            stderr_console.print(f"Please visit 'https://github.com/py-pdf/pypdf/issues' to report a bug.")
                            stderr_console.print(f"(Providing the devs with the extracted page will help improve pypdf.)")
                            already_extracted_page_numbers.append(page_number)

                page_text = page_buffer.file.getvalue()
                extracted_pages.append(page_text)
                log.debug(page_text)

                if Config.print_as_parsed:
                    print(f"{page_text}")
        except DependencyError:
            log_optional_module_warning('pdf')
        except EmptyFileError:
            log.warn("Skipping empty file!")

        self._extracted_text = "\n\n".join(extracted_pages).strip()
        self.text_extraction_attempted = True
        return self._extracted_text

    def thumbnail_bytes(self) -> Optional[bytes]:
        """Return bytes for a thumbnail."""
        import fitz  # TODO: Can we do this without PyMuPDF dependency?
        try:
            doc = fitz.open(self.file_path)
        except fitz.fitz.EmptyFileError:
            log.warning(f"Failed to get bytes for '{self.file_path}'")
            return None

        # Resize the thumbnail to fit the screen
        log.debug(f"Getting bytes for '{self.file_path}'...")
        zoom_matrix = fitz.Matrix(fitz.Identity).prescale(SCALE_FACTOR, SCALE_FACTOR)
        page = doc[0]
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

    def extract_page_range(
            self,
            first_page_number: int,
            last_page_number: Optional[int] = None,
            destination_dir: Optional[Path] = None
        ) -> Path:
        """Extract a range of pages to a new PDF file (or 1 page if last_page_number not provided.)"""
        last_page_number = last_page_number or first_page_number + 1
        destination_dir = destination_dir or DEFAULT_PDF_ERRORS_DIR

        if last_page_number < first_page_number:
            raise ValueError(f"last_page_number {last_page_number} is before first_page_number {first_page_number}")
        elif last_page_number <= first_page_number + 1:
            if last_page_number == first_page_number:
                log.warning(f"First and last pages are both {first_page_number}. Adjusting to extract 1 page...")

            last_page_number = first_page_number + 1
            file_suffix = f"page {first_page_number}"
        else:
            file_suffix = f"pages {first_page_number}-{last_page_number - 1}"

        extracted_pages_pdf_basename = insert_suffix_before_extension(self.file_path, file_suffix).name
        extracted_pages_pdf_path = destination_dir.joinpath(extracted_pages_pdf_basename)
        stderr_console.print(f"Attempting to extract {file_suffix} from '{self.file_path}' to '{extracted_pages_pdf_path}'...")
        pdf_writer = PdfWriter()

        with open(self.file_path, 'rb') as source_pdf:
            pdf_writer.append(fileobj=source_pdf, pages=(first_page_number, last_page_number))

        if SortableFile.confirm_file_overwrite(extracted_pages_pdf_path):
            with open(extracted_pages_pdf_path, 'wb') as extracted_pages_pdf:
                pdf_writer.write(extracted_pages_pdf)

        stderr_console.print(f"Wrote new PDF '{extracted_pages_pdf_path}'.")
        return extracted_pages_pdf_path

    def _can_be_presented_in_popup(self) -> bool:
        if type(self).is_presentable_in_popup is None:
            type(self).is_presentable_in_popup = check_for_pymupdf()

        if not type(self).is_presentable_in_popup:
            console.line()
            msg = WARNING.append(f"File '{self.basename}' is not displayable without pymupdf...\n")
            console.print(msg)

        return type(self).is_presentable_in_popup

    def _log_to_stderr(self, msg: str) -> None:
        """When parsing very large PDFs it can be useful to log progress and other messages to STDERR."""
        if self.file_size() < MIN_PDF_SIZE_TO_LOG_PROGRESS_TO_STDERR:
            return

        stderr_console.print(msg)

    def __repr__(self) -> str:
        return f"PdfFile('{self.file_path}')"
