# How to Download Windows Binaries

Since automated downloads from SourceForge are unreliable, please download these files manually and add them to this `bin/` directory.

## Step 1: Download DjVuLibre for Windows

**Option A: Direct from SourceForge** (Recommended)
1. Go to: https://sourceforge.net/projects/djvu/files/DjVuLibre_Win32/3.5.28/
2. Download: `djvulibre-3.5.28-win.zip` (direct download link)
3. Extract the ZIP file
4. From `djvulibre-3.5.28/bin/`, copy these files to this `bin/` directory:
   - `djvused.exe`
   - `ddjvu.exe`
   - `libdjvulibre.dll`
   - `msvcr90.dll` (and any other DLL files)

**Option B: From Archive.org Mirror**
1. Go to: https://archive.org/download/djvulibre-3.5.28-win
2. Download the archive
3. Extract and copy the exe and dll files as above

## Step 2: Download LibTIFF Tools

1. Go to: https://sourceforge.net/projects/gnuwin32/files/tiff/3.8.2-1/
2. Download: `tiff-3.8.2-1-bin.zip`
3. Download: `tiff-3.8.2-1-dep.zip` (dependencies)
4. Extract both ZIP files
5. From the `bin/` folder, copy to this directory:
   - `tiffsplit.exe`
   - `libtiff3.dll`
   - `jpeg62.dll`
   - `zlib1.dll` (and other DLL files)

## Step 3: Verify Files

After copying, your `bin/` directory should contain:
```
bin/
├── djvused.exe
├── ddjvu.exe
├── tiffsplit.exe
├── libdjvulibre.dll
├── msvcr90.dll
├── libtiff3.dll
├── jpeg62.dll
├── zlib1.dll
└── (other DLL files)
```

## Step 4: Commit to Repository

```bash
cd /path/to/djvu2pdf
git add bin/
git commit -m "Add Windows binaries for automated build"
git push
```

Once pushed, GitHub Actions will use these binaries automatically!

## Alternative: Use Pre-Made Binary Package

If you have trouble downloading, let me know and I can provide alternative sources or help troubleshoot.

## Notes

- These binaries are from the official DjVuLibre and LibTIFF projects
- They are safe and open source
- Total size: ~5-10 MB
- Once in the repo, builds will be fast and reliable
