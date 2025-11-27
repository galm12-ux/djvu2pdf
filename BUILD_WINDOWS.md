# Building DjVu to PDF Converter for Windows

This guide explains how to build a **single-file portable Windows executable** that includes all dependencies.

## Prerequisites

1. **Windows 10/11** (for building the .exe)
2. **Python 3.8+** installed
3. **Ruby** (for pdfbeads gem)

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pyinstaller` - Creates single-file executable
- `tkinterdnd2` - Enables drag-and-drop in GUI

## Step 2: Gather Windows Binaries

Create a `bin/` directory and place these Windows executables inside:

### Required Binaries

| Tool | Download Source | Notes |
|------|----------------|-------|
| **djvused.exe** | [DjVuLibre for Windows](http://djvu.sourceforge.net/) | Part of DjVuLibre suite |
| **ddjvu.exe** | [DjVuLibre for Windows](http://djvu.sourceforge.net/) | Part of DjVuLibre suite |
| **djvu2hocr** | See instructions below | **CRITICAL** - Must use this tool |
| **tiffsplit.exe** | [LibTIFF for Windows](http://gnuwin32.sourceforge.net/packages/tiff.htm) | Part of LibTIFF tools |
| **pdfbeads** | Ruby gem (see below) | Requires Ruby runtime |

### Getting djvu2hocr for Windows

**Option 1: Install ocrodjvu Python package**
```bash
pip install ocrodjvu
```
This installs `djvu2hocr` as a Python script. You can then create a wrapper:

**Option 2: Use WSL/Cygwin version**
If you have WSL or Cygwin, you can copy the djvu2hocr binary.

**Option 3: Build from source**
Clone and build: https://github.com/jwilk/ocrodjvu

### Installing pdfbeads

```bash
# Install Ruby first (from https://rubyinstaller.org/)
gem install pdfbeads
```

The `pdfbeads` command will be in Ruby's bin directory.

### Directory Structure

```
djvu2pdf/
├── bin/
│   ├── djvused.exe
│   ├── ddjvu.exe
│   ├── djvu2hocr.exe (or djvu2hocr Python script)
│   ├── tiffsplit.exe
│   ├── pdfbeads.bat (wrapper for Ruby gem)
│   └── ruby/ (if bundling Ruby runtime)
├── djvu2pdf_gui.py
├── djvu2pdf_converter.py
├── djvu2pdf_toc_parser.py
├── requirements.txt
└── build_windows.spec
```

## Step 3: Build the Executable

Run PyInstaller with the spec file:

```bash
pyinstaller build_windows.spec
```

This creates:
- `dist/djvu2pdf.exe` - **Single portable executable!**

## Step 4: Test the Executable

```bash
# The .exe is completely standalone
dist/djvu2pdf.exe
```

The GUI should open. Test with a DjVu file!

## Important Notes

### About djvu2hocr

The **djvu2hocr** tool is CRITICAL for this converter. It extracts OCR text from DjVu files.

- **Source**: http://jwilk.net/software/ocrodjvu
- **Python package**: `ocrodjvu` (includes djvu2hocr script)
- **Must be accessible** in the bin/ directory or via Python

### Single-File Executable

The PyInstaller spec uses `--onefile` mode:
- All binaries are **embedded** in the .exe
- At runtime, they're extracted to a **temp directory**
- After conversion, temp files are **cleaned up**
- No installation required - just run the .exe!

### File Size

The final .exe will be large (~50-100MB) because it includes:
- Python runtime
- All binary tools (djvu, tiff, ruby/pdfbeads)
- GUI libraries

This is normal for single-file portable applications.

## Troubleshooting

### "djvu2hocr not found"
- Ensure djvu2hocr is in `bin/` directory
- Or install `ocrodjvu` Python package
- Check that it's executable on Windows

### "pdfbeads failed"
- Ensure Ruby is properly installed
- Check that pdfbeads gem is installed: `gem list pdfbeads`
- May need to bundle Ruby runtime with the executable

### GUI doesn't open
- Try running from command line to see error messages
- Ensure all Python dependencies are installed
- Check Windows Defender didn't block the .exe

## Alternative: Console Version

If you want a console version instead of GUI, modify `build_windows.spec`:

```python
exe = EXE(
    ...
    console=True,  # Change this to True
    ...
)
```

Then you can use it from command line:
```bash
djvu2pdf.exe input.djvu output.pdf
```
