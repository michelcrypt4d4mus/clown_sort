"""
Wrapper for PDF files.
"""
import io
import logging
from typing import Optional

from PIL import Image
from pypdf import PdfReader
from pypdf.errors import DependencyError, EmptyFileError
from rich.console import Console
from rich.panel import Panel

from clown_sort.config import MIN_PDF_SIZE_TO_LOG_PROGRESS_TO_STDERR, check_for_pymupdf, log_optional_module_warning
from clown_sort.files.image_file import ImageFile
from clown_sort.files.sortable_file import SortableFile
from clown_sort.util.logging import log
from clown_sort.util.rich_helper import WARNING, console, stderr_console

MAX_DISPLAY_HEIGHT = 600
SCALE_FACTOR = 0.4


class PdfFile(SortableFile):
    is_presentable_in_popup = None

    def extracted_text(self) -> Optional[str]:
        """Use Tesseract to OCR the text in the image, which is returned as a string."""
        if self.text_extraction_attempted:
            return self._extracted_text

        log.debug(f"Extracting text from '{self.file_path}'...")
        console_buffer = Console(file=io.StringIO())
        extracted_pages = []

        try:
            pdf_reader = PdfReader(self.file_path)
            page_count = len(pdf_reader.pages)
            log.debug(f"PDF Page count: {page_count}")

            for page_number, page in enumerate(pdf_reader.pages, start=1):
                self._log_to_stderr(f"Parsing page {page_number}...")
                console_buffer.print(Panel(f"PAGE {page_number}", padding=(0, 15), expand=False))
                console_buffer.print(page.extract_text().strip())
                image_enumerator = enumerate(page.images, start=1)
                image_number = 1

                # Iterate like this because the page enumerator sometimes barfs with a handleable exception
                while True:
                    iterator_exception = True

                    try:
                        (image_number, image) = next(image_enumerator)
                        iterator_exception = False
                        image_name = f"Page {page_number}, Image {image_number}"
                        self._log_to_stderr(f"   Processing {image_name}...")
                        console_buffer.print(Panel(image_name, expand=False))
                        image_obj = Image.open(io.BytesIO(image.data))
                        image_text = ImageFile.extract_text(image_obj, f"{self.file_path} ({image_name})")
                        console_buffer.print((image_text or '').strip())
                    except StopIteration:
                        break
                    except (NotImplementedError, UnboundLocalError, ValueError) as e:
                        stderr_console.print_exception()
                        print(f"WARNING: {type(e).__name__}: {e} while parsing embedded image {image_number} on page {page_number}...")

                    except Exception as e:
                        stderr_console.print_exception()
                        print(f"WARNING: UNKNOWN exception {type(e).__name__}: {e} while parsing embedded image {image_number} on page {page_number}...")

                        # If the iterator threw the exception we need to stop iterating
                        if iterator_exception:
                            break

                page_text = console_buffer.file.getvalue()
                # TODO: add CLI option to print as we go
                # print(f"{page_text}")
                log.debug(page_text)
                extracted_pages.append(page_text)
        except DependencyError:
            log_optional_module_warning('pdf')
        except EmptyFileError:
            log.warn("Skipping empty file!")

        self.text_extraction_attempted = True
        self._extracted_text = "\n\n".join(extracted_pages).strip()
        return self._extracted_text

    def thumbnail_bytes(self) -> Optional[bytes]:
        """Return bytes for a thumbnail."""
        import fitz  # TODO: Can we do this without PyMuPDF dependency?
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

    def _log_to_stderr(self, msg: str) -> None:
        """When parsing very large PDFs it can be useful to log progress and other messages to STDERR."""
        if self.file_size() < MIN_PDF_SIZE_TO_LOG_PROGRESS_TO_STDERR:
            return

        stderr_console.print(msg)

    def __repr__(self) -> str:
        return f"PdfFile('{self.file_path}')"
