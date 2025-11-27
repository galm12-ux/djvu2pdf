#!/usr/bin/env python3
"""
DjVu to PDF converter - Windows portable version
Converts DjVu files to searchable PDF with embedded text layers
"""

import os
import sys
import tempfile
import shutil
import subprocess
import re
import io
from pathlib import Path
from typing import Optional, Callable
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import xml.etree.ElementTree as ET


class DjVu2PDFConverter:
    """Handles DjVu to PDF conversion using external tools"""

    def __init__(self, bin_dir: Optional[Path] = None, progress_callback: Optional[Callable] = None):
        """
        Initialize converter

        Args:
            bin_dir: Directory containing binary tools (djvused, ddjvu, etc.)
                    If None, assumes tools are in system PATH
            progress_callback: Function to call with progress updates (message, percent)
        """
        self.bin_dir = bin_dir
        self.progress_callback = progress_callback or (lambda msg, pct: None)

    def _run_command(self, cmd: list, shell: bool = False, **kwargs) -> subprocess.CompletedProcess:
        """Run a command and return the result"""
        if self.bin_dir and not shell:
            # Prepend bin_dir to first command if it's not an absolute path
            if not os.path.isabs(cmd[0]):
                cmd_name = cmd[0]
                # On Windows, use .bat extension for pdfbeads
                if sys.platform == "win32" and cmd_name == "pdfbeads":
                    cmd_name = f"{cmd_name}.bat"
                cmd[0] = str(self.bin_dir / cmd_name)

        try:
            return subprocess.run(cmd, shell=shell, check=True, capture_output=True, text=True, **kwargs)
        except subprocess.CalledProcessError as e:
            # Provide detailed error message with stderr output
            error_msg = f"Command failed: {' '.join(str(c) for c in cmd)}\n"
            if e.stderr:
                error_msg += f"Error output: {e.stderr}"
            raise RuntimeError(error_msg) from e
        except FileNotFoundError as e:
            # Command executable not found
            error_msg = f"Command not found: {cmd[0]}\n"
            error_msg += f"Full command: {' '.join(str(c) for c in cmd)}\n"
            if self.bin_dir:
                error_msg += f"Bin directory: {self.bin_dir}\n"
                error_msg += f"Bin directory exists: {self.bin_dir.exists()}\n"
                if self.bin_dir.exists():
                    error_msg += f"Contents: {', '.join(f.name for f in self.bin_dir.iterdir())}"
            raise RuntimeError(error_msg) from e

    def _update_progress(self, message: str, percent: int):
        """Update progress"""
        self.progress_callback(message, percent)

    def _extract_text_with_djvused(self, input_file: Path, page: int) -> str:
        """
        Extract text from a page using djvused and generate simple hOCR

        Args:
            input_file: Path to DjVu file
            page: Page number (1-indexed)

        Returns:
            Basic hOCR output as string
        """
        # Get page size and text content using djvused
        cmd = ["djvused", "-e", f"select {page}; size; print-txt", str(input_file)]
        result = self._run_command(cmd)

        lines = result.stdout.strip().split('\n')
        if len(lines) < 2:
            # No text on this page, return empty hOCR
            return self._generate_empty_hocr()

        # Parse page size (first two lines: width=X\nheight=Y)
        try:
            width = int(lines[0].split('=')[1])
            height = int(lines[1].split('=')[1])
        except:
            width = height = 0

        # Extract all text content (skip size lines)
        text_content = '\n'.join(lines[2:]) if len(lines) > 2 else ""

        # Parse s-expression and extract text
        words = self._parse_djvu_text(text_content)

        # Generate simple hOCR HTML
        return self._generate_hocr(width, height, words)

    def _parse_djvu_text(self, sexpr_text: str) -> list:
        """
        Simple s-expression parser to extract text and coordinates
        Returns list of (text, x0, y0, x1, y1) tuples
        """
        words = []
        # Simple regex to find strings and coordinates in s-expressions
        # Format: (word x0 y0 x1 y1 "text")
        import re
        pattern = r'\(word\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+"([^"]*)"\)'
        matches = re.findall(pattern, sexpr_text)

        for match in matches:
            x0, y0, x1, y1, text = match
            words.append((text, int(x0), int(y0), int(x1), int(y1)))

        return words

    def _generate_hocr(self, width: int, height: int, words: list) -> str:
        """Generate hOCR HTML from extracted words"""
        hocr_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" ',
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
            '<html xmlns="http://www.w3.org/1999/xhtml">',
            '<head>',
            '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />',
            '<meta name="ocr-system" content="djvused" />',
            '<title>DjVu OCR</title>',
            '</head>',
            '<body>',
            f'<div class="ocr_page" title="bbox 0 0 {width} {height}">',
        ]

        # Add words
        for text, x0, y0, x1, y1 in words:
            # Escape HTML entities
            text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
            hocr_lines.append(
                f'<span class="ocr_word" title="bbox {x0} {y0} {x1} {y1}">{text}</span> '
            )

        hocr_lines.extend([
            '</div>',
            '</body>',
            '</html>'
        ])

        return '\n'.join(hocr_lines)

    def _generate_empty_hocr(self) -> str:
        """Generate empty hOCR for pages with no text"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>DjVu OCR</title>
</head>
<body>
<div class="ocr_page" title="bbox 0 0 0 0"></div>
</body>
</html>'''

    def _create_pdf_with_text_layer(self, page_pairs: list, output_pdf: Path, toc_file: Path):
        """
        Create PDF from TIFF images with OCR text layer using reportlab

        Args:
            page_pairs: List of (tiff_path, html_path) tuples
            output_pdf: Output PDF file path
            toc_file: Table of contents file (currently not implemented)
        """
        c = canvas.Canvas(str(output_pdf))

        for i in range(0, len(page_pairs), 2):
            tiff_path = Path(page_pairs[i])
            html_path = Path(page_pairs[i + 1])

            # Open image to get dimensions
            with Image.open(tiff_path) as img:
                width, height = img.size

            # Set page size to match image
            c.setPageSize((width, height))

            # Draw the image
            c.drawImage(str(tiff_path), 0, 0, width=width, height=height)

            # Add invisible text layer from hOCR
            if html_path.exists():
                self._add_text_layer(c, html_path, height)

            c.showPage()

        c.save()

    def _add_text_layer(self, pdf_canvas, html_path: Path, page_height: int):
        """
        Add invisible text layer to PDF page from hOCR HTML

        Args:
            pdf_canvas: ReportLab canvas object
            html_path: Path to hOCR HTML file
            page_height: Height of the page (needed for coordinate conversion)
        """
        try:
            # Parse hOCR HTML
            tree = ET.parse(str(html_path))
            root = tree.getroot()

            # Find all word elements
            # Handle both with and without namespace
            words = root.findall(".//*[@class='ocr_word']")
            if not words:
                # Try with namespace
                ns = {'html': 'http://www.w3.org/1999/xhtml'}
                words = root.findall(".//html:*[@class='ocr_word']", ns)

            for word_elem in words:
                title = word_elem.get('title', '')
                text = ''.join(word_elem.itertext()).strip()

                if not text or not title:
                    continue

                # Parse bbox from title attribute
                # Format: "bbox x0 y0 x1 y1"
                bbox_match = re.search(r'bbox\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', title)
                if not bbox_match:
                    continue

                x0, y0, x1, y1 = map(int, bbox_match.groups())

                # Convert coordinates (hOCR uses top-left origin, PDF uses bottom-left)
                pdf_x = x0
                pdf_y = page_height - y1
                text_width = x1 - x0
                text_height = y1 - y0

                # Calculate font size to fit the bbox
                font_size = text_height * 0.8  # Approximate

                # Add invisible text
                pdf_canvas.saveState()
                pdf_canvas.setFillColorRGB(0, 0, 0, alpha=0)  # Invisible
                pdf_canvas.setFont("Helvetica", font_size)

                # Scale text to fit width
                text_obj = pdf_canvas.beginText(pdf_x, pdf_y)
                text_obj.textLine(text)
                pdf_canvas.drawText(text_obj)

                pdf_canvas.restoreState()

        except Exception as e:
            # If text layer fails, just skip it (image will still be in PDF)
            pass

    def convert(self, input_file: Path, output_file: Path) -> None:
        """
        Convert DjVu file to PDF

        Args:
            input_file: Path to input .djvu file
            output_file: Path to output .pdf file
        """
        input_file = Path(input_file).resolve()
        output_file = Path(output_file).resolve()

        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Create temporary directory for conversion
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            original_dir = Path.cwd()

            try:
                os.chdir(tmpdir)

                # Copy input file to temp directory with ASCII-safe name
                # This avoids issues with Unicode/special characters in filenames
                temp_input = tmpdir / "input.djvu"
                shutil.copy2(input_file, temp_input)

                self._perform_conversion(temp_input, output_file, tmpdir)
            finally:
                os.chdir(original_dir)

    def _perform_conversion(self, input_file: Path, output_file: Path, tmpdir: Path):
        """Perform the actual conversion steps"""

        # Step 1: Extract TIFF pages
        self._update_progress("Extracting pages from DjVu...", 10)
        multipage_tiff = tmpdir / "tmp_multipage.tiff"

        cmd = ["ddjvu", "-format=tiff", str(input_file), str(multipage_tiff)]
        self._run_command(cmd)

        # Step 2: Split TIFF into individual pages
        self._update_progress("Splitting pages...", 20)
        cmd = ["tiffsplit", str(multipage_tiff), "tmp_page_"]
        self._run_command(cmd)
        multipage_tiff.unlink()  # Remove temporary multipage tiff

        # Step 3: Get number of pages and rename files
        self._update_progress("Processing pages...", 30)
        cmd = ["djvused", "-e", "n", str(input_file)]
        result = self._run_command(cmd)
        num_pages = int(result.stdout.strip())
        strlen_num_pages = len(str(num_pages))

        # Rename split pages with proper numbering
        page_files = sorted(tmpdir.glob("tmp_page_*"))
        for i, page_file in enumerate(page_files, start=1):
            page_num = str(i).zfill(strlen_num_pages)
            new_name = tmpdir / f"tmp_page_{page_num}.tiff"
            page_file.rename(new_name)

        # Step 4: Extract OCR content for each page
        self._update_progress("Extracting OCR text...", 40)
        for i in range(1, num_pages + 1):
            page_num = str(i).zfill(strlen_num_pages)
            html_file = tmpdir / f"tmp_page_{page_num}.html"

            # Extract text using djvused and generate hOCR
            ocr_output = self._extract_text_with_djvused(input_file, i)

            # Apply sed-like substitution: s/ocrx/ocr/g (for compatibility)
            ocr_content = ocr_output.replace("ocrx", "ocr")
            html_file.write_text(ocr_content, encoding='utf-8')

            # Update progress for OCR extraction
            ocr_progress = 40 + int(50 * i / num_pages)
            self._update_progress(f"Extracting OCR text... ({i}/{num_pages})", ocr_progress)

        # Step 5: Generate TOC
        self._update_progress("Generating table of contents...", 90)
        toc_file = tmpdir / "toc.txt"
        cmd = ["djvused", "-e", "print-outline", str(input_file)]
        result = self._run_command(cmd)
        toc_file.write_text(result.stdout, encoding='utf-8')

        # Parse TOC using the Python parser
        from djvu2pdf_toc_parser import parse_sexp
        toc_input = toc_file.read_text(encoding='utf-8')
        toc_output_file = tmpdir / "toc.out.txt"

        if len(toc_input) > 0:
            prefix = '(bookmarks'
            if len(toc_input) > len(prefix):
                toc_output = []
                parse_sexp(toc_input[len(prefix):], toc_output, '', 0)
                toc_output_file.write_text('\n'.join(toc_output), encoding='utf-8')
        else:
            toc_output_file.write_text('', encoding='utf-8')

        # Step 6: Generate final PDF using Python-based generator
        self._update_progress("Generating PDF...", 95)

        # Build page pairs (tiff, html) for PDF generation
        page_tiffs = sorted(tmpdir.glob("tmp_page_*.tiff"))
        page_pairs = []

        for tiff_file in page_tiffs:
            html_file = tiff_file.with_suffix('.html')
            if not html_file.exists():
                raise FileNotFoundError(f"Missing OCR HTML for page {tiff_file}")
            page_pairs.extend([str(tiff_file), str(html_file)])

        if not page_pairs:
            raise RuntimeError("No page TIFF files were generated")

        output_pdf = tmpdir / "output.pdf"

        # Create PDF with text layer using Python (replaces pdfbeads)
        self._create_pdf_with_text_layer(page_pairs, output_pdf, toc_output_file)

        # Step 7: Move output to final destination
        self._update_progress("Finalizing...", 99)
        shutil.move(str(output_pdf), str(output_file))
        self._update_progress("Conversion complete!", 100)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: djvu2pdf_converter.py <input.djvu> <output.pdf>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    def progress(msg, pct):
        print(f"[{pct:3d}%] {msg}")

    converter = DjVu2PDFConverter(progress_callback=progress)

    try:
        converter.convert(input_file, output_file)
        print(f"Successfully converted {input_file} to {output_file}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
