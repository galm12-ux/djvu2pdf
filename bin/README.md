# Binary Dependencies for Windows Build

This directory contains Windows executable dependencies needed to build the portable .exe:

## Required Files

Place these files in this directory:

### DjVuLibre (from http://djvu.sourceforge.net/)
- `djvused.exe` - DjVu metadata extraction tool
- `ddjvu.exe` - DjVu to image conversion tool
- `*.dll` - DjVuLibre DLL dependencies

### LibTIFF (from http://gnuwin32.sourceforge.net/packages/tiff.htm)
- `tiffsplit.exe` - TIFF splitting tool
- Required DLL files

### djvu2hocr
- Downloaded automatically from ocrodjvu project

### pdfbeads
- Installed via Ruby gems during build

## How to Add Files

1. Download DjVuLibre for Windows: http://djvu.sourceforge.net/
2. Extract and copy exe and dll files to this directory
3. Download LibTIFF binaries
4. Extract and copy tiffsplit.exe and dlls to this directory
5. Commit and push:
   ```bash
   git add bin/
   git commit -m "Add Windows binaries for build"
   git push
   ```

## Note

If files are present in this directory, the GitHub Actions workflow will use them instead of downloading.
