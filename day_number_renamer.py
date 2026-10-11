"""
Day Number Renamer
Move a Day/Lesson/Episode number to the beginning of video filenames.
No AI, API key, or third-party Python packages required.
"""

from __future__ import annotations

import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from dataclasses import dataclass

APP_NAME = "Day Number Renamer"
VERSION = "1.0.0"

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm", ".m4v",
    ".mpg", ".mpeg", ".ts", ".m2ts", ".3gp", ".ogv", ".vob"
}
DAY_PATTERN = re.compile(r"\bday[\s_-]*(\d+)\b", re.IGNORECASE)


@dataclass
class RenameItem:
    source: Path
    destination: Path
    status: str = "Ready"


def build_new_name(path: Path) -> Path | None:
    """Move the last Day N marker to the front, preserving other title text."""
    matches = list(DAY_PATTERN.finditer(path.stem))
    if not matches:
        return None

    match = matches[-1]
    number = int(match.group(1))
    # Remove only the detected "Day N" marker; retain all other title text.
    remaining = path.stem[:match.start()] + " " + path.stem[match.end():]
    remaining = re.sub(r"[\s_-]+", " ", remaining).strip()
    remaining = re.sub(r"\s{2,}", " ", remaining).strip(" _-")

    # If a title exists, separate it from the day label with a space.
    new_stem = f"Day {number:03d}" + (f" {remaining}" if remaining else "")
    if new_stem == path.stem:
        return None
    return path.with_name(new_stem + path.suffix)


class DayNumberRenamer:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_NAME}  •  v{VERSION}")
        self.root.geometry("1050x700")
        self.root.minsize(820, 570)
        self.root.configure(bg="#f4f6fb")
        self.folder: Path | None = None
        self.items: list[RenameItem] = []
        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#f4f6fb")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("TLabel", background="#f4f6fb", foreground="#172033", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground="#172033")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="#657089")
        style.configure("CardTitle.TLabel", background="#ffffff", font=("Segoe UI", 11, "bold"), foreground="#172033")
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 9))
        style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=(12, 8))
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=29, background="#ffffff",
                        fieldbackground="#ffffff", foreground="#172033")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), padding=8,
                        background="#e9edf6", foreground="#303b52")
        style.map("Treeview", background=[("selected", "#dce8ff")], foreground=[("selected", "#172033")])

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=22)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, 17))
        icon = tk.Label(header, text="DN", bg="#365cf5", fg="white",
                        font=("Segoe UI", 16, "bold"), width=4, height=2)
        icon.pack(side="left", padx=(0, 13))
        title_area = ttk.Frame(header)
        title_area.pack(side="left", fill="x", expand=True)
        ttk.Label(title_area, text=APP_NAME, style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_area, text="Put lesson numbers first. Keep your original titles. No AI or API required.",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(3, 0))
        ttk.Label(header, text=f"v{VERSION}", style="Subtitle.TLabel").pack(side="right", anchor="n")

        folder_card = ttk.Frame(outer, style="Card.TFrame", padding=15)
        folder_card.pack(fill="x", pady=(0, 12))
        ttk.Label(folder_card, text="1  •  Choose a folder", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 9))
        row = ttk.Frame(folder_card, style="Card.TFrame")
        row.pack(fill="x")
        self.folder_var = tk.StringVar()
        self.folder_entry = ttk.Entry(row, textvariable=self.folder_var, font=("Segoe UI", 10))
        self.folder_entry.pack(side="left", fill="x", expand=True, ipady=6)
        ttk.Button(row, text="Browse folder…", style="Primary.TButton", command=self.choose_folder).pack(side="left", padx=(9, 0))

        instruction_card = ttk.Frame(outer, style="Card.TFrame", padding=15)
        instruction_card.pack(fill="x", pady=(0, 12))
        ttk.Label(instruction_card, text="2  •  Preview your changes", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(instruction_card, text="Only files in the selected folder are scanned. Subfolders are not changed.",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(4, 10))
        actions = ttk.Frame(instruction_card, style="Card.TFrame")
        actions.pack(fill="x")
        ttk.Button(actions, text="Scan & preview", style="Primary.TButton", command=self.scan).pack(side="left")
        ttk.Button(actions, text="Apply rename", style="Primary.TButton", command=self.apply).pack(side="left", padx=8)
        ttk.Button(actions, text="Clear", style="Secondary.TButton", command=self.clear).pack(side="left")
        self.summary_var = tk.StringVar(value="Choose a folder to get started.")
        ttk.Label(actions, textvariable=self.summary_var, style="Subtitle.TLabel").pack(side="right", padx=(8, 0))

        table_card = ttk.Frame(outer, style="Card.TFrame", padding=12)
        table_card.pack(fill="both", expand=True)
        ttk.Label(table_card, text="Rename preview", style="CardTitle.TLabel").pack(anchor="w", padx=3, pady=(0, 9))
        columns = ("current", "proposed", "status")
        self.table = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="extended")
        self.table.heading("current", text="CURRENT FILENAME")
        self.table.heading("proposed", text="NEW FILENAME")
        self.table.heading("status", text="STATUS")
        self.table.column("current", width=390, minwidth=180)
        self.table.column("proposed", width=390, minwidth=180)
        self.table.column("status", width=105, minwidth=90, anchor="center")
        scrollbar_y = ttk.Scrollbar(table_card, orient="vertical", command=self.table.yview)
        scrollbar_x = ttk.Scrollbar(table_card, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(10, 0))
        ttk.Label(footer, text="Tip: test on a copy first. Existing files are never intentionally overwritten.",
                  style="Subtitle.TLabel").pack(side="left")
        ttk.Label(footer, text="Made for simple, safe batch renaming", style="Subtitle.TLabel").pack(side="right")

    def choose_folder(self):
        selected = filedialog.askdirectory(title="Select the folder containing your videos")
        if selected:
            self.folder = Path(selected)
            self.folder_var.set(selected)
            self.scan()

    def clear(self):
        self.items.clear()
        for row in self.table.get_children():
            self.table.delete(row)
        self.summary_var.set("Preview cleared.")

    def scan(self):
        raw = self.folder_var.get().strip().strip('"')
        if not raw:
            messagebox.showwarning("Choose a folder", "Please select a folder first.")
            return
        folder = Path(raw).expanduser()
        if not folder.is_dir():
            messagebox.showerror("Folder not found", "That path is not a valid folder.")
            return
        self.folder = folder.resolve()
        self.items = []
        for row in self.table.get_children():
            self.table.delete(row)

        files = sorted(
            (p for p in self.folder.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS),
            key=lambda p: p.name.casefold()
        )
        destinations_seen: set[str] = set()
        for source in files:
            destination = build_new_name(source)
            if destination is None:
                continue
            key = destination.name.casefold()
            if key in destinations_seen:
                status = "Name conflict"
            elif destination.exists() and destination.resolve() != source.resolve():
                status = "Already exists"
            else:
                status = "Ready"
            destinations_seen.add(key)
            self.items.append(RenameItem(source, destination, status))
            self.table.insert("", "end", values=(source.name, destination.name, status))

        ready = sum(item.status == "Ready" for item in self.items)
        self.summary_var.set(f"{len(files)} video(s) scanned • {ready} ready • {len(self.items)-ready} skipped")
        if not files:
            messagebox.showinfo("No videos found", "No supported video files were found in this folder.")
        elif not self.items:
            messagebox.showinfo("No Day numbers found", "No supported filenames containing a Day number were found.")

    def apply(self):
        if not self.folder:
            messagebox.showwarning("Choose a folder", "Please select a folder and scan it first.")
            return
        ready = [item for item in self.items if item.status == "Ready"]
        if not ready:
            messagebox.showinfo("Nothing to rename", "There are no conflict-free rename actions in the preview.")
            return
        if not messagebox.askyesno(
            "Confirm rename",
            f"Rename {len(ready)} file(s) in:\n{self.folder}\n\n"
            "The title text and file extension will be preserved. This action changes filenames, not file contents.\n\nContinue?"
        ):
            return

        # Two-phase rename prevents a source name from colliding with another planned target.
        staged: list[tuple[Path, Path, Path]] = []
        renamed = 0
        errors: list[str] = []
        try:
            for index, item in enumerate(ready):
                temp = item.source.with_name(f".__dayrenamer_tmp_{index}_{item.source.name}")
                suffix = 1
                while temp.exists():
                    temp = item.source.with_name(f".__dayrenamer_tmp_{index}_{suffix}_{item.source.name}")
                    suffix += 1
                item.source.rename(temp)
                staged.append((temp, item.source, item.destination))

            for temp, original, destination in staged:
                if destination.exists():
                    temp.rename(original)
                    errors.append(f"Skipped (destination exists): {destination.name}")
                    continue
                temp.rename(destination)
                renamed += 1
        except OSError as exc:
            errors.append(str(exc))
            for temp, original, destination in reversed(staged):
                try:
                    if temp.exists() and not original.exists():
                        temp.rename(original)
                except OSError:
                    pass

        self.scan()
        msg = f"Finished!\nRenamed: {renamed}"
        if errors:
            msg += "\n\nNotes:\n" + "\n".join(errors[:8])
        messagebox.showinfo("Rename complete", msg)


def main():
    root = tk.Tk()
    DayNumberRenamer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
