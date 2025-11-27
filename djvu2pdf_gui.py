#!/usr/bin/env python3
"""
DjVu to PDF Converter - Windows GUI Application
Single-file portable Windows application with embedded dependencies
"""

import os
import sys
import tempfile
import shutil
import zipfile
from pathlib import Path
from tkinter import Tk, Frame, Label, Button, filedialog, StringVar, messagebox
from tkinter.ttk import Progressbar
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading

from djvu2pdf_converter import DjVu2PDFConverter


class BinaryExtractor:
    """Extracts embedded binaries to temporary directory"""

    @staticmethod
    def extract_binaries() -> Path:
        """
        Extract all embedded binary tools to a temporary directory
        Returns the path to the bin directory
        """
        # Check if we're running as a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            bundle_dir = Path(sys._MEIPASS)
        else:
            # Running as script - look for bin directory next to script
            bundle_dir = Path(__file__).parent

        # Check if binaries are in a 'bin' subdirectory
        bin_dir = bundle_dir / 'bin'

        if bin_dir.exists():
            return bin_dir

        # If bin directory doesn't exist, create temp directory
        # This is where we'd extract embedded binaries in the final version
        temp_dir = Path(tempfile.mkdtemp(prefix='djvu2pdf_'))
        return temp_dir


class DjVu2PDFApp:
    """Main GUI application"""

    def __init__(self, root):
        self.root = root
        self.root.title("DjVu to PDF Converter")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Extract binaries on startup
        self.bin_dir = BinaryExtractor.extract_binaries()

        # Variables
        self.input_file = None
        self.output_file = None
        self.status_var = StringVar(value="Drag and drop a DjVu file or click 'Select File'")
        self.is_converting = False

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface"""

        # Title
        title_label = Label(
            self.root,
            text="DjVu to PDF Converter",
            font=("Arial", 18, "bold"),
            pady=20
        )
        title_label.pack()

        # Drop zone frame
        self.drop_frame = Frame(
            self.root,
            width=550,
            height=150,
            relief="groove",
            borderwidth=2,
            bg="#f0f0f0"
        )
        self.drop_frame.pack(pady=10)
        self.drop_frame.pack_propagate(False)

        # Drop zone label
        self.drop_label = Label(
            self.drop_frame,
            text="📄 Drop DjVu file here\n\nor click 'Select File' below",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#666"
        )
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")

        # Enable drag and drop
        try:
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self._on_drop)
        except:
            # tkinterdnd2 not available, just use file selection
            pass

        # Button frame
        button_frame = Frame(self.root)
        button_frame.pack(pady=10)

        # Select file button
        self.select_btn = Button(
            button_frame,
            text="Select File",
            command=self._select_file,
            width=15,
            height=2,
            font=("Arial", 10)
        )
        self.select_btn.pack(side="left", padx=5)

        # Convert button
        self.convert_btn = Button(
            button_frame,
            text="Convert to PDF",
            command=self._start_conversion,
            width=15,
            height=2,
            font=("Arial", 10, "bold"),
            state="disabled",
            bg="#4CAF50",
            fg="white"
        )
        self.convert_btn.pack(side="left", padx=5)

        # Progress bar
        self.progress = Progressbar(
            self.root,
            length=550,
            mode='determinate'
        )
        self.progress.pack(pady=10)

        # Status label
        status_label = Label(
            self.root,
            textvariable=self.status_var,
            font=("Arial", 9),
            wraplength=550,
            fg="#333"
        )
        status_label.pack(pady=5)

        # Footer
        footer = Label(
            self.root,
            text="Converts DjVu files to searchable PDF with embedded text layers",
            font=("Arial", 8),
            fg="#999"
        )
        footer.pack(side="bottom", pady=10)

    def _on_drop(self, event):
        """Handle file drop event"""
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0].strip('{}')
            self._set_input_file(file_path)

    def _select_file(self):
        """Open file dialog to select DjVu file"""
        file_path = filedialog.askopenfilename(
            title="Select DjVu File",
            filetypes=[("DjVu Files", "*.djvu *.djv"), ("All Files", "*.*")]
        )
        if file_path:
            self._set_input_file(file_path)

    def _set_input_file(self, file_path):
        """Set the input file and enable conversion"""
        self.input_file = Path(file_path)

        if not self.input_file.exists():
            messagebox.showerror("Error", f"File not found: {file_path}")
            return

        if self.input_file.suffix.lower() not in ['.djvu', '.djv']:
            messagebox.showwarning("Warning", "Selected file may not be a DjVu file")

        # Update UI
        self.drop_label.config(
            text=f"✓ {self.input_file.name}\n\nReady to convert",
            fg="#4CAF50"
        )
        self.convert_btn.config(state="normal")
        self.status_var.set(f"Selected: {self.input_file.name}")

    def _start_conversion(self):
        """Start the conversion process"""
        if self.is_converting:
            return

        # Ask for output location
        default_name = self.input_file.stem + ".pdf"
        output_path = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )

        if not output_path:
            return

        self.output_file = Path(output_path)

        # Disable buttons during conversion
        self.is_converting = True
        self.select_btn.config(state="disabled")
        self.convert_btn.config(state="disabled")
        self.progress['value'] = 0

        # Run conversion in separate thread
        thread = threading.Thread(target=self._convert)
        thread.daemon = True
        thread.start()

    def _convert(self):
        """Perform the conversion (runs in separate thread)"""
        try:
            def progress_callback(message, percent):
                self.root.after(0, self._update_progress, message, percent)

            converter = DjVu2PDFConverter(
                bin_dir=self.bin_dir,
                progress_callback=progress_callback
            )

            converter.convert(self.input_file, self.output_file)

            # Success
            self.root.after(0, self._conversion_complete, True, None)

        except Exception as e:
            # Error
            self.root.after(0, self._conversion_complete, False, str(e))

    def _update_progress(self, message, percent):
        """Update progress bar and status (called from main thread)"""
        self.progress['value'] = percent
        self.status_var.set(message)
        self.root.update_idletasks()

    def _conversion_complete(self, success, error_msg):
        """Handle conversion completion"""
        self.is_converting = False
        self.select_btn.config(state="normal")
        self.convert_btn.config(state="normal")

        if success:
            self.progress['value'] = 100
            self.status_var.set("Conversion complete!")
            messagebox.showinfo(
                "Success",
                f"PDF created successfully!\n\n{self.output_file}"
            )
            # Reset UI
            self.drop_label.config(
                text="📄 Drop DjVu file here\n\nor click 'Select File' below",
                fg="#666"
            )
            self.convert_btn.config(state="disabled")
            self.progress['value'] = 0
        else:
            self.status_var.set("Conversion failed!")
            messagebox.showerror(
                "Conversion Failed",
                f"An error occurred during conversion:\n\n{error_msg}"
            )


def main():
    """Main entry point"""
    # Use TkinterDnD if available, otherwise fall back to regular Tk
    try:
        root = TkinterDnD.Tk()
    except:
        root = Tk()
        print("Warning: Drag-and-drop not available. Use 'Select File' button.")

    app = DjVu2PDFApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
