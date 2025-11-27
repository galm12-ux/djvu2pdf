# DjVu to PDF Converter - User Guide

## What is this?

This tool converts DjVu ebook files into PDF format while preserving:
- ✅ All images and pages
- ✅ Searchable text (OCR layers)
- ✅ Table of contents/bookmarks
- ✅ High compression (small file size)

## System Requirements

- **Windows 10 or later**
- No other software needed - everything is included!

## How to Use

### Method 1: Drag and Drop (Easiest)

1. **Double-click** `djvu2pdf.exe`
2. **Drag** your DjVu file into the window
3. **Click** "Convert to PDF"
4. **Choose** where to save the PDF
5. **Wait** for conversion to complete
6. **Done!** Your PDF is ready

### Method 2: File Selection

1. **Double-click** `djvu2pdf.exe`
2. **Click** "Select File" button
3. **Browse** to your DjVu file
4. **Click** "Convert to PDF"
5. **Choose** where to save the PDF
6. **Wait** for conversion to complete
7. **Done!** Your PDF is ready

## What Happens During Conversion?

The progress bar shows these steps:

1. **Extracting pages** (10-20%) - Splitting DjVu into individual pages
2. **Processing pages** (20-30%) - Preparing images
3. **Extracting OCR text** (30-90%) - Pulling out searchable text from each page
4. **Generating TOC** (90-95%) - Creating table of contents
5. **Generating PDF** (95-99%) - Combining everything into PDF
6. **Finalizing** (100%) - Writing final file

This can take a few minutes for large files with many pages.

## Tips

### File Size
- Input: `book.djvu` (10 MB)
- Output: `book.pdf` (usually similar size, sometimes smaller!)
- The PDF is highly compressed while maintaining quality

### Speed
- Small files (< 50 pages): ~30 seconds
- Medium files (50-200 pages): 1-3 minutes
- Large files (> 200 pages): 3-10 minutes

Processing speed depends on your computer's CPU.

### Where to Find DjVu Files?
- Digital libraries and archives
- Scanned book collections
- Scientific paper repositories
- Some ebook websites use DjVu format

## Troubleshooting

### "Conversion Failed"
- **Check** that your file is actually a DjVu file (.djvu or .djv extension)
- **Try** a different DjVu file to see if the problem is file-specific
- **Ensure** you have write permission to the output folder

### "File Not Found"
- **Make sure** the input file hasn't been moved or deleted
- **Try** copying the file to your Desktop first

### "Missing OCR HTML"
- Some DjVu files don't have embedded text
- The converter will try anyway, but text search may not work in the PDF

### Program Won't Start
- **Right-click** the .exe and choose "Run as Administrator"
- **Check** if Windows Defender blocked it (click "More info" → "Run anyway")
- Your antivirus might need to allow the program

### Still Having Issues?
- Make sure you're using a valid DjVu file
- Try with a small test file first
- Check that you have enough disk space

## Privacy & Security

- ✅ **100% offline** - no internet connection needed
- ✅ **No data sent** anywhere - everything stays on your computer
- ✅ **Temporary files** are automatically cleaned up after conversion
- ✅ **Open source** - you can inspect the code

## Technical Details

This tool uses:
- **djvu2hocr** - Extracts OCR text layers
- **DjVuLibre** - Handles DjVu format
- **pdfbeads** - Creates compressed PDF

All tools are embedded in the single .exe file.

## License

See LICENSE file for details.

---

**Questions or issues?** Check the project repository for support.
