#!/usr/bin/env python3
"""
DjVu to PDF Converter - Simple GUI version
Works on Linux, Mac, and Windows - no building required!
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from pathlib import Path
import subprocess
import tempfile
import shutil
import threading


class SimpleDjVu2PDF:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("DjVu to PDF Converter")
        self.window.geometry("500x300")

        # Title
        tk.Label(
            self.window,
            text="DjVu to PDF Converter",
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        # File info
        self.file_label = tk.Label(
            self.window,
            text="No file selected",
            wraplength=450
        )
        self.file_label.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="Select DjVu File",
            command=self.select_file,
            width=15,
            height=2
        ).pack(side="left", padx=5)

        self.convert_btn = tk.Button(
            btn_frame,
            text="Convert to PDF",
            command=self.convert,
            width=15,
            height=2,
            state="disabled",
            bg="#4CAF50",
            fg="white"
        )
        self.convert_btn.pack(side="left", padx=5)

        # Progress
        self.progress = Progressbar(self.window, length=450)
        self.progress.pack(pady=10)

        self.status = tk.Label(self.window, text="Ready")
        self.status.pack(pady=5)

        self.input_file = None

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select DjVu File",
            filetypes=[("DjVu Files", "*.djvu *.djv"), ("All Files", "*.*")]
        )
        if file_path:
            self.input_file = Path(file_path)
            self.file_label.config(text=f"Selected: {self.input_file.name}")
            self.convert_btn.config(state="normal")

    def convert(self):
        if not self.input_file:
            return

        output_path = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            initialfile=self.input_file.stem + ".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not output_path:
            return

        self.output_file = Path(output_path)
        self.convert_btn.config(state="disabled")

        # Run in thread
        thread = threading.Thread(target=self.do_convert)
        thread.daemon = True
        thread.start()

    def do_convert(self):
        try:
            # Just call the original bash script!
            script_dir = Path(__file__).parent
            bash_script = script_dir / "djvu2pdf"

            self.update_status("Converting...", 50)

            result = subprocess.run(
                [str(bash_script), str(self.input_file), str(self.output_file)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.update_status("Done!", 100)
                self.window.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"PDF created!\n{self.output_file}"
                ))
            else:
                raise Exception(result.stderr or "Conversion failed")

        except Exception as e:
            self.update_status("Failed", 0)
            self.window.after(0, lambda: messagebox.showerror(
                "Error",
                f"Conversion failed:\n{str(e)}"
            ))
        finally:
            self.window.after(0, lambda: self.convert_btn.config(state="normal"))

    def update_status(self, msg, progress):
        self.window.after(0, lambda: self.status.config(text=msg))
        self.window.after(0, lambda: self.progress.config(value=progress))

    def run(self):
        self.window.mainloop()


if __name__ == '__main__':
    app = SimpleDjVu2PDF()
    app.run()
