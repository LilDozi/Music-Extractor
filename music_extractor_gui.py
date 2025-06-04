import os
import sys
import subprocess
import threading
import queue
import shutil
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# Path to the extraction script. Adjust if the filename differs.
EXTRACT_SCRIPT = "extract_audio.py"


def _find_ffmpeg() -> str | None:
    """Return path to ffmpeg or ``None`` if not found."""
    script_dir = Path(__file__).resolve().parent
    exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    local = script_dir / exe
    if local.exists():
        return str(local)
    return shutil.which("ffmpeg")


class ExtractorGUI:
    """Simple Tkinter GUI wrapper for extract_audio.py."""

    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("Music Extractor GUI")

        # Store selected files and output directory
        self.input_files: list[str] = []
        self.output_dir: str | None = None

        # Output format variable (mp3 or wav)
        self.format_var = tk.StringVar(value="mp3")

        # Build UI
        self._build_widgets()

        # Queue for logging messages from worker thread
        self.log_queue: queue.Queue[str] = queue.Queue()
        # Thread handle
        self.worker: threading.Thread | None = None

        # Periodic check for new log messages
        self.master.after(100, self._process_queue)

    def _build_widgets(self) -> None:
        btn_frame = tk.Frame(self.master)
        btn_frame.pack(padx=10, pady=10, fill=tk.X)

        self.input_btn = tk.Button(btn_frame, text="Select Input File(s)", command=self.select_inputs)
        self.input_btn.pack(side=tk.LEFT)

        self.output_btn = tk.Button(btn_frame, text="Select Output Folder", command=self.select_output_dir)
        self.output_btn.pack(side=tk.LEFT, padx=5)

        format_frame = tk.Frame(self.master)
        format_frame.pack(padx=10, anchor="w")
        tk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT)
        tk.Radiobutton(format_frame, text="MP3", variable=self.format_var, value="mp3").pack(side=tk.LEFT)
        tk.Radiobutton(format_frame, text="WAV", variable=self.format_var, value="wav").pack(side=tk.LEFT)

        self.run_btn = tk.Button(self.master, text="Run Extraction", command=self.start_extraction)
        self.run_btn.pack(padx=10, pady=5)

        self.log_text = ScrolledText(self.master, width=80, height=20, state="disabled")
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def select_inputs(self) -> None:
        files = filedialog.askopenfilenames(title="Select input file(s)")
        if files:
            self.input_files = list(files)
            self._append_log(f"Selected {len(files)} file(s).\n")

    def select_output_dir(self) -> None:
        directory = filedialog.askdirectory(title="Select output folder")
        if directory:
            self.output_dir = directory
            self._append_log(f"Output directory set to: {directory}\n")

    def start_extraction(self) -> None:
        if not self.input_files:
            messagebox.showwarning("No Input", "Please select input files first.")
            return
        ffmpeg_path = _find_ffmpeg()
        if ffmpeg_path is None:
            messagebox.showerror(
                "FFmpeg Not Found",
                "FFmpeg is required but was not found.",
            )
            return
        if shutil.which("python") is None:
            messagebox.showerror(
                "Python Not Found",
                "Python executable not found in PATH.",
            )
            return

        # Disable buttons during extraction
        self._set_buttons_state(tk.DISABLED)

        self.worker = threading.Thread(target=self._run_extraction_thread, daemon=True)
        self.worker.start()

    def _run_extraction_thread(self) -> None:
        ffmpeg_path = _find_ffmpeg()
        env = os.environ.copy()
        if ffmpeg_path:
            env["FFMPEG_PATH"] = ffmpeg_path

        for input_path in self.input_files:
            name = Path(input_path).stem
            out_dir = self.output_dir if self.output_dir else str(Path(input_path).parent)
            output_file = os.path.join(out_dir, f"{name}.{self.format_var.get()}")
            log_file = os.path.join(out_dir, f"{name}.log")
            cmd = [
                sys.executable,
                EXTRACT_SCRIPT,
                input_path,
                output_file,
                "--codec",
                self.format_var.get(),
                "--log",
                log_file,
            ]
            self.log_queue.put(f"Running: {' '.join(cmd)}\n")
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env,
                )
            except FileNotFoundError as exc:
                self.log_queue.put(f"Error: {exc}\n")
                messagebox.showerror("Execution Failed", str(exc))
                self.log_queue.put("DONE")
                return

            assert proc.stdout is not None  # for mypy/type hints
            for line in proc.stdout:
                self.log_queue.put(line)
            proc.wait()
            if proc.returncode != 0:
                self.log_queue.put(f"Extraction failed for {input_path}\n")
            else:
                self.log_queue.put(f"Finished {input_path}\n")
        self.log_queue.put("DONE")

    def _process_queue(self) -> None:
        while True:
            try:
                msg = self.log_queue.get_nowait()
            except queue.Empty:
                break
            if msg == "DONE":
                self._set_buttons_state(tk.NORMAL)
                messagebox.showinfo("Extraction Complete", "Processing finished. Check log for details.")
            else:
                self._append_log(msg)
        self.master.after(100, self._process_queue)

    def _append_log(self, text: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def _set_buttons_state(self, state: str) -> None:
        self.input_btn.configure(state=state)
        self.output_btn.configure(state=state)
        self.run_btn.configure(state=state)


def main() -> None:
    root = tk.Tk()
    gui = ExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
