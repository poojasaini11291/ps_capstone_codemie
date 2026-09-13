import customtkinter as ctk
from typing import Callable, Optional
from core.clipboard import copy_to_clipboard


class PasswordDisplay(ctk.CTkFrame):
    """Large, modern password display box with Copy, Regenerate, and Masking controls."""

    def __init__(
        self,
        master,
        on_regenerate: Optional[Callable[[], None]] = None,
        on_copied: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(master, corner_radius=14, fg_color=("gray90", "#161b22"), **kwargs)
        self.on_regenerate = on_regenerate
        self.on_copied = on_copied
        self.current_password = ""
        self.is_masked = False

        self.grid_columnconfigure(0, weight=1)

        # Container for password text
        text_container = ctk.CTkFrame(self, fg_color=("white", "#0d1117"), corner_radius=10)
        text_container.grid(row=0, column=0, sticky="ew", padx=14, pady=12)
        text_container.grid_columnconfigure(0, weight=1)

        # Password text display
        self.password_entry = ctk.CTkEntry(
            text_container,
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            fg_color="transparent",
            border_width=0,
            justify="center"
        )
        self.password_entry.grid(row=0, column=0, sticky="ew", padx=16, pady=14)
        self.password_entry.configure(state="readonly")

        # Action Buttons Row
        action_row = ctk.CTkFrame(self, fg_color="transparent")
        action_row.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 12))
        action_row.grid_columnconfigure(1, weight=1)

        # Mask/Unmask Button
        self.btn_mask = ctk.CTkButton(
            action_row,
            text="👁 Hide",
            font=ctk.CTkFont(size=12),
            width=80,
            height=34,
            fg_color=("gray80", "#21262d"),
            text_color=("black", "white"),
            hover_color=("gray70", "#30363d"),
            command=self.toggle_mask
        )
        self.btn_mask.pack(side="left", padx=(0, 6))

        # Regenerate Button
        self.btn_regen = ctk.CTkButton(
            action_row,
            text="🔄 Regenerate",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=130,
            height=34,
            fg_color=("#2563eb", "#1f6feb"),
            hover_color=("#1d4ed8", "#388bfd"),
            command=self._handle_regenerate
        )
        self.btn_regen.pack(side="left", padx=4)

        # Copy Button
        self.btn_copy = ctk.CTkButton(
            action_row,
            text="📋 Copy to Clipboard",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=170,
            height=34,
            fg_color=("#059669", "#238636"),
            hover_color=("#047857", "#2ea043"),
            command=self.copy_password
        )
        self.btn_copy.pack(side="right", padx=(6, 0))

        # Copied Toast Badge (reverts after 2.5s)
        self.toast_job = None

    def set_password(self, password: str):
        self.current_password = password
        self._update_display_text()

    def _update_display_text(self):
        self.password_entry.configure(state="normal")
        self.password_entry.delete(0, "end")
        if self.is_masked:
            self.password_entry.insert(0, "•" * len(self.current_password))
        else:
            self.password_entry.insert(0, self.current_password)
        self.password_entry.configure(state="readonly")

    def toggle_mask(self):
        self.is_masked = not self.is_masked
        self.btn_mask.configure(text="👁 Show" if self.is_masked else "👁 Hide")
        self._update_display_text()

    def _handle_regenerate(self):
        if self.on_regenerate:
            self.on_regenerate()

    def copy_password(self):
        if not self.current_password:
            return

        success = copy_to_clipboard(self.current_password, root_window=self.winfo_toplevel())
        if success:
            self.btn_copy.configure(
                text="✓ Copied!",
                fg_color=("#047857", "#2ea043")
            )
            if self.toast_job:
                self.after_cancel(self.toast_job)
            self.toast_job = self.after(2200, self._reset_copy_button)

            if self.on_copied:
                self.on_copied(self.current_password)

    def _reset_copy_button(self):
        self.btn_copy.configure(
            text="📋 Copy to Clipboard",
            fg_color=("#059669", "#238636")
        )

