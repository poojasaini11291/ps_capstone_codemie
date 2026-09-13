import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Optional

from core.vault import (
    VaultError,
    vault_exists,
    init_vault,
    unlock_vault,
    add_entry,
    list_entries,
    get_entry_password,
    delete_entry
)
from core.clipboard import copy_to_clipboard


class VaultEntryRow(ctk.CTkFrame):
    """A single vault entry row with reveal, copy, and delete controls."""

    def __init__(self, master, entry, on_reveal, on_delete, **kwargs):
        super().__init__(master, corner_radius=8, fg_color=("gray95", "#161b22"), **kwargs)
        self.entry = entry
        self.on_reveal = on_reveal
        self.on_delete = on_delete
        self.revealed_password: Optional[str] = None

        self.grid_columnconfigure(0, weight=1)

        info = ctk.CTkFrame(self, fg_color="transparent")
        info.grid(row=0, column=0, sticky="w", padx=(10, 4), pady=8)

        title = entry.label + (f"  ·  {entry.username}" if entry.username else "")
        ctk.CTkLabel(info, text=title, font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(anchor="w")

        self.pass_label = ctk.CTkLabel(
            info,
            text="••••••••",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=("gray40", "#8b949e"),
            anchor="w"
        )
        self.pass_label.pack(anchor="w")

        self.btn_reveal = ctk.CTkButton(
            self, text="👁 Reveal", font=ctk.CTkFont(size=11), width=80, height=28,
            fg_color=("gray80", "#21262d"), text_color=("black", "white"),
            hover_color=("gray70", "#30363d"), command=self._handle_reveal
        )
        self.btn_reveal.grid(row=0, column=1, padx=4, pady=8)

        self.btn_copy = ctk.CTkButton(
            self, text="📋 Copy", font=ctk.CTkFont(size=11), width=70, height=28,
            fg_color=("#2563eb", "#1f6feb"), hover_color=("#1d4ed8", "#388bfd"),
            command=self._handle_copy
        )
        self.btn_copy.grid(row=0, column=2, padx=4, pady=8)

        self.btn_delete = ctk.CTkButton(
            self, text="🗑", font=ctk.CTkFont(size=12), width=36, height=28,
            fg_color=("#dc2626", "#8b1a1a"), hover_color=("#b91c1c", "#6e1414"),
            command=self._handle_delete
        )
        self.btn_delete.grid(row=0, column=3, padx=(4, 10), pady=8)

    def _handle_reveal(self):
        if self.revealed_password is None:
            password = self.on_reveal(self.entry.id)
            if password is None:
                return
            self.revealed_password = password
            self.pass_label.configure(text=password)
            self.btn_reveal.configure(text="🙈 Hide")
        else:
            self.revealed_password = None
            self.pass_label.configure(text="••••••••")
            self.btn_reveal.configure(text="👁 Reveal")

    def _handle_copy(self):
        password = self.revealed_password or self.on_reveal(self.entry.id)
        if not password:
            return
        copy_to_clipboard(password, root_window=self.winfo_toplevel())
        self.btn_copy.configure(text="✓ Copied!", fg_color=("#059669", "#238636"))
        self.after(1800, lambda: self.btn_copy.configure(text="📋 Copy", fg_color=("#2563eb", "#1f6feb")))

    def _handle_delete(self):
        if messagebox.askyesno(
            "Delete entry", f"Delete '{self.entry.label}' from the vault?", parent=self.winfo_toplevel()
        ):
            self.on_delete(self.entry.id)


class VaultPanel(ctk.CTkFrame):
    """Encrypted local password vault: unlock/create screen, saved-entry list, save-current-password."""

    def __init__(self, master, get_current_password_fn: Optional[Callable[[], str]] = None, **kwargs):
        super().__init__(master, corner_radius=14, fg_color=("gray90", "#161b22"), **kwargs)
        self.get_current_password_fn = get_current_password_fn
        self.session = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_locked_view()

    # ------------------------------------------------------------------
    # Locked / unlock-create screen
    # ------------------------------------------------------------------
    def _build_locked_view(self):
        self.locked_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.locked_frame.grid(row=0, column=0, sticky="nsew")
        self.locked_frame.grid_rowconfigure(0, weight=1)
        self.locked_frame.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self.locked_frame, corner_radius=14, fg_color=("white", "#0d1117"), width=380)
        card.grid(row=0, column=0)
        card.grid_columnconfigure(0, weight=1)

        is_new = not vault_exists()
        title = "🔐 Create Your Vault" if is_new else "🔐 Unlock Your Vault"
        subtitle = (
            "Set a master password to start saving generated passwords locally, encrypted."
            if is_new else
            "Enter your master password to view saved entries."
        )

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=24, pady=(24, 4)
        )
        ctk.CTkLabel(
            card, text=subtitle, font=ctk.CTkFont(size=12),
            text_color=("gray40", "#8b949e"), wraplength=320, justify="center"
        ).grid(row=1, column=0, padx=24, pady=(0, 16))

        self.pw_entry = ctk.CTkEntry(card, placeholder_text="Master password", show="•", width=280, height=38)
        self.pw_entry.grid(row=2, column=0, padx=24, pady=(0, 8))

        self.confirm_entry = None
        if is_new:
            self.confirm_entry = ctk.CTkEntry(
                card, placeholder_text="Confirm master password", show="•", width=280, height=38
            )
            self.confirm_entry.grid(row=3, column=0, padx=24, pady=(0, 8))

        self.error_label = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=11), text_color="#f85149")
        self.error_label.grid(row=4, column=0, padx=24, pady=(0, 4))

        action = self._create_vault if is_new else self._unlock
        btn = ctk.CTkButton(
            card, text=("Create Vault" if is_new else "Unlock"),
            font=ctk.CTkFont(size=13, weight="bold"), width=280, height=38,
            fg_color=("#2563eb", "#1f6feb"), hover_color=("#1d4ed8", "#388bfd"), command=action
        )
        btn.grid(row=5, column=0, padx=24, pady=(4, 24))

        self.pw_entry.bind("<Return>", lambda e: action())
        if self.confirm_entry:
            self.confirm_entry.bind("<Return>", lambda e: action())

        self.pw_entry.focus_set()

    def _create_vault(self):
        master = self.pw_entry.get()
        confirm = self.confirm_entry.get() if self.confirm_entry else master

        if len(master) < 8:
            self.error_label.configure(text="Master password must be at least 8 characters.")
            return
        if master != confirm:
            self.error_label.configure(text="Passwords do not match.")
            return

        try:
            init_vault(master)
            self.session = unlock_vault(master)
        except VaultError as e:
            self.error_label.configure(text=str(e))
            return

        self._show_unlocked_view()

    def _unlock(self):
        master = self.pw_entry.get()
        try:
            self.session = unlock_vault(master)
        except VaultError as e:
            self.error_label.configure(text=str(e))
            return

        self._show_unlocked_view()

    # ------------------------------------------------------------------
    # Unlocked view
    # ------------------------------------------------------------------
    def _show_unlocked_view(self):
        self.locked_frame.destroy()

        self.unlocked_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.unlocked_frame.grid(row=0, column=0, sticky="nsew")
        self.unlocked_frame.grid_rowconfigure(2, weight=1)
        self.unlocked_frame.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self.unlocked_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="🔐 Saved Passwords", font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header, text="🔒 Lock", font=ctk.CTkFont(size=11), width=70, height=28,
            fg_color=("gray80", "#21262d"), text_color=("black", "white"),
            hover_color=("gray70", "#30363d"), command=self._lock
        ).grid(row=0, column=1)

        # Save-current-password row
        save_row = ctk.CTkFrame(self.unlocked_frame, corner_radius=10, fg_color=("gray95", "#161b22"))
        save_row.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 10))
        save_row.grid_columnconfigure((0, 1), weight=1)

        self.label_entry = ctk.CTkEntry(save_row, placeholder_text="Label (e.g. Gmail, Bank)")
        self.label_entry.grid(row=0, column=0, sticky="ew", padx=(10, 4), pady=10)

        self.username_entry = ctk.CTkEntry(save_row, placeholder_text="Username (optional)")
        self.username_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=10)

        ctk.CTkButton(
            save_row, text="💾 Save Current Password", font=ctk.CTkFont(size=12, weight="bold"),
            width=190, height=32, fg_color=("#059669", "#238636"), hover_color=("#047857", "#2ea043"),
            command=self._save_current
        ).grid(row=0, column=2, padx=(4, 10), pady=10)

        self.save_status = ctk.CTkLabel(save_row, text="", font=ctk.CTkFont(size=11))
        self.save_status.grid(row=1, column=0, columnspan=3, sticky="w", padx=10, pady=(0, 8))

        # Entry list
        self.scroll_list = ctk.CTkScrollableFrame(
            self.unlocked_frame, fg_color=("white", "#0d1117"), corner_radius=10
        )
        self.scroll_list.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.scroll_list.grid_columnconfigure(0, weight=1)

        self._refresh_entries()

    def _lock(self):
        self.session = None
        self.unlocked_frame.destroy()
        self._build_locked_view()

    def _save_current(self):
        label = self.label_entry.get().strip()
        username = self.username_entry.get().strip() or None
        password = self.get_current_password_fn() if self.get_current_password_fn else None

        if not password:
            self.save_status.configure(text="No password to save — generate one first.", text_color="#f85149")
            return
        if not label:
            self.save_status.configure(text="A label is required.", text_color="#f85149")
            return

        try:
            add_entry(self.session, label, password, username=username)
        except VaultError as e:
            self.save_status.configure(text=str(e), text_color="#f85149")
            return

        self.label_entry.delete(0, "end")
        self.username_entry.delete(0, "end")
        self.save_status.configure(text=f"Saved '{label}' to the vault.", text_color="#3fb950")
        self._refresh_entries()

    def _refresh_entries(self):
        for widget in self.scroll_list.winfo_children():
            widget.destroy()

        entries = list_entries(self.session)
        if not entries:
            ctk.CTkLabel(
                self.scroll_list, text="No saved passwords yet.",
                font=ctk.CTkFont(size=12), text_color=("gray40", "#8b949e")
            ).pack(pady=40)
            return

        for entry in entries:
            row = VaultEntryRow(self.scroll_list, entry, on_reveal=self._reveal, on_delete=self._delete)
            row.pack(fill="x", padx=2, pady=3)

    def _reveal(self, entry_id: int) -> Optional[str]:
        try:
            return get_entry_password(self.session, entry_id)
        except VaultError as e:
            messagebox.showerror("Vault Error", str(e), parent=self.winfo_toplevel())
            return None

    def _delete(self, entry_id: int):
        delete_entry(self.session, entry_id)
        self._refresh_entries()
