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
from pathlib import Path
from typing import Optional, Callable


class DjVu2PDFConverter:
    """Handles DjVu to PDF conversion using external tools"""

    def __init__(self, bin_dir: Optional[Path] = None, progress_callback: Optional[Callable] = None):
        """
        Initialize converter

        Args:
            bin_dir: Directory containing binary tools (djvused, ddjvu, djvu2hocr, etc.)
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
                # On Windows, use .bat extension for djvu2hocr and pdfbeads
                if sys.platform == "win32" and cmd_name in ["djvu2hocr", "pdfbeads"]:
                    cmd_name = f"{cmd_name}.bat"
                cmd[0] = str(self.bin_dir / cmd_name)

        return subprocess.run(cmd, shell=shell, check=True, capture_output=True, text=True, **kwargs)

    def _update_progress(self, message: str, percent: int):
        """Update progress"""
        self.progress_callback(message, percent)

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

            # Run djvu2hocr for this page
            cmd = ["djvu2hocr", str(input_file), "-p", str(i)]
            result = self._run_command(cmd)

            # Apply sed-like substitution: s/ocrx/ocr/g
            ocr_content = result.stdout.replace("ocrx", "ocr")
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

        # Step 6: Generate final PDF with pdfbeads
        self._update_progress("Generating PDF...", 95)

        # Build page pairs (tiff, html) for pdfbeads
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
        cmd = ["pdfbeads", "--toc", str(toc_output_file), "-o", str(output_pdf)] + page_pairs

        try:
            self._run_command(cmd)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"pdfbeads failed to generate the final PDF: {e.stderr}")

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
