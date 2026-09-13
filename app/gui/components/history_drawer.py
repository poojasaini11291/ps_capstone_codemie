import time
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import List, Optional
from core.clipboard import copy_to_clipboard
from core.strength_checker import check_password_strength, StrengthReport
from core.generator import generate_batch, PasswordConfig


class HistoryRow(ctk.CTkFrame):
    """A single history entry with copy button, strength badge, and mask toggle."""

    def __init__(self, master, password: str, **kwargs):
        super().__init__(master, corner_radius=8, fg_color=("gray95", "#161b22"), **kwargs)
        self.password = password
        self.is_masked = True

        self.grid_columnconfigure(1, weight=1)

        # Timestamp
        timestamp = time.strftime("%H:%M:%S")
        self.time_label = ctk.CTkLabel(
            self,
            text=timestamp,
            font=ctk.CTkFont(size=10),
            text_color=("gray40", "#8b949e"),
            width=50
        )
        self.time_label.grid(row=0, column=0, padx=(8, 4), pady=6)

        # Password Text
        self.pass_entry = ctk.CTkEntry(
            self,
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            fg_color="transparent",
            border_width=0
        )
        self.pass_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=6)
        self.pass_entry.insert(0, "•" * len(password))
        self.pass_entry.configure(state="readonly")

        # Strength Badge
        report = check_password_strength(password)
        self.badge = ctk.CTkLabel(
            self,
            text=f"{report.score}%",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=report.color,
            text_color="white",
            corner_radius=4,
            width=36,
            padx=4,
            pady=1
        )
        self.badge.grid(row=0, column=2, padx=4, pady=6)

        # Mask toggle
        self.btn_eye = ctk.CTkButton(
            self,
            text="👁",
            font=ctk.CTkFont(size=11),
            width=28,
            height=24,
            fg_color=("gray80", "#21262d"),
            text_color=("black", "white"),
            hover_color=("gray70", "#30363d"),
            command=self.toggle_mask
        )
        self.btn_eye.grid(row=0, column=3, padx=2, pady=6)

        # Copy button
        self.btn_copy = ctk.CTkButton(
            self,
            text="📋 Copy",
            font=ctk.CTkFont(size=11),
            width=60,
            height=24,
            fg_color=("#2563eb", "#1f6feb"),
            hover_color=("#1d4ed8", "#388bfd"),
            command=self.copy
        )
        self.btn_copy.grid(row=0, column=4, padx=(2, 8), pady=6)

    def toggle_mask(self):
        self.is_masked = not self.is_masked
        self.pass_entry.configure(state="normal")
        self.pass_entry.delete(0, "end")
        if self.is_masked:
            self.pass_entry.insert(0, "•" * len(self.password))
        else:
            self.pass_entry.insert(0, self.password)
        self.pass_entry.configure(state="readonly")

    def copy(self):
        copy_to_clipboard(self.password, root_window=self.winfo_toplevel())
        self.btn_copy.configure(text="✓ Copied!", fg_color=("#059669", "#238636"))
        self.after(1800, lambda: self.btn_copy.configure(text="📋 Copy", fg_color=("#2563eb", "#1f6feb")))


class HistoryPanel(ctk.CTkFrame):
    """Session history viewer and batch password generation panel."""

    def __init__(self, master, get_current_config_fn, **kwargs):
        super().__init__(master, corner_radius=14, fg_color=("gray90", "#161b22"), **kwargs)
        self.get_current_config_fn = get_current_config_fn
        self.history_items: List[str] = []

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header Bar
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="📜 Session History & Batch",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        btn_batch = ctk.CTkButton(
            header,
            text="⚡ Batch Generate",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=120,
            height=28,
            fg_color=("#059669", "#238636"),
            hover_color=("#047857", "#2ea043"),
            command=self.open_batch_dialog
        )
        btn_batch.grid(row=0, column=1, padx=(0, 6))

        btn_clear = ctk.CTkButton(
            header,
            text="Clear",
            font=ctk.CTkFont(size=11),
            width=50,
            height=28,
            fg_color=("gray80", "#21262d"),
            text_color=("black", "white"),
            hover_color=("gray70", "#30363d"),
            command=self.clear_history
        )
        btn_clear.grid(row=0, column=2, padx=0)

        # Scrollable list for history
        self.scroll_list = ctk.CTkScrollableFrame(self, fg_color=("white", "#0d1117"), corner_radius=10)
        self.scroll_list.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.scroll_list.grid_columnconfigure(0, weight=1)

        self.empty_label = ctk.CTkLabel(
            self.scroll_list,
            text="No passwords generated yet in this session.",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "#8b949e")
        )
        self.empty_label.pack(pady=40)

    def add_password(self, password: str):
        if not password or (self.history_items and self.history_items[0] == password):
            return

        if self.empty_label.winfo_ismapped():
            self.empty_label.pack_forget()

        self.history_items.insert(0, password)
        # Limit history to 50 items
        if len(self.history_items) > 50:
            self.history_items.pop()

        self._refresh_history_ui()

    def clear_history(self):
        self.history_items.clear()
        for widget in self.scroll_list.winfo_children():
            widget.destroy()
        self.empty_label = ctk.CTkLabel(
            self.scroll_list,
            text="No passwords generated yet in this session.",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "#8b949e")
        )
        self.empty_label.pack(pady=40)

    def _refresh_history_ui(self):
        for widget in self.scroll_list.winfo_children():
            widget.destroy()

        for idx, pwd in enumerate(self.history_items):
            row = HistoryRow(self.scroll_list, pwd)
            row.pack(fill="x", padx=2, pady=3)

    def open_batch_dialog(self):
        """Open popup window to generate 5, 10, or 20 passwords at once."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Batch Password Generator")
        dialog.geometry("520x440")
        dialog.minsize(440, 360)
        dialog.grab_set()

        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(2, weight=1)

        # Header
        ctk.CTkLabel(
            dialog,
            text="⚡ Batch Password Generator",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        # Controls Row
        ctrl_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        ctrl_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        ctk.CTkLabel(ctrl_frame, text="Generate count:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 6))

        count_var = ctk.StringVar(value="10")
        count_combo = ctk.CTkComboBox(
            ctrl_frame,
            values=["5", "10", "20", "50"],
            variable=count_var,
            width=80
        )
        count_combo.pack(side="left", padx=4)

        # Textbox for batch results
        textbox = ctk.CTkTextbox(
            dialog,
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=8,
            wrap="none"
        )
        textbox.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 10))

        def _do_batch_generate():
            try:
                count = int(count_var.get())
            except ValueError:
                count = 10
            config = self.get_current_config_fn()
            passwords = generate_batch(config, count=count)
            textbox.delete("1.0", "end")
            textbox.insert("end", "\n".join(passwords))

        btn_run = ctk.CTkButton(
            ctrl_frame,
            text="Generate Now",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=110,
            command=_do_batch_generate
        )
        btn_run.pack(side="left", padx=(10, 0))

        # Bottom actions: Copy All & Export
        action_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        action_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))

        def _copy_all():
            content = textbox.get("1.0", "end-1c")
            if content:
                copy_to_clipboard(content, root_window=dialog)
                messagebox.showinfo("Copied", "All passwords copied to clipboard!", parent=dialog)

        def _export_txt():
            content = textbox.get("1.0", "end-1c")
            if not content:
                return
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                parent=dialog
            )
            if filepath:
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    messagebox.showinfo("Saved", f"Passwords saved to:\n{filepath}", parent=dialog)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {e}", parent=dialog)

        ctk.CTkButton(
            action_frame,
            text="📋 Copy All",
            width=100,
            command=_copy_all
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            action_frame,
            text="💾 Save to File",
            width=100,
            fg_color=("gray80", "#21262d"),
            text_color=("black", "white"),
            hover_color=("gray70", "#30363d"),
            command=_export_txt
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            action_frame,
            text="Close",
            width=80,
            fg_color=("gray80", "#21262d"),
            text_color=("black", "white"),
            hover_color=("gray70", "#30363d"),
            command=dialog.destroy
        ).pack(side="right", padx=0)

        _do_batch_generate()

