import tkinter as tk
import customtkinter as ctk
from typing import Optional

from core.generator import (
    PasswordConfig,
    generate_password,
    generate_passphrase,
    generate_pin
)
from core.strength_checker import check_password_strength
from core.clipboard import copy_to_clipboard
from gui.components.password_display import PasswordDisplay
from gui.components.strength_meter import StrengthMeter
from gui.components.options_panel import OptionsPanel
from gui.components.history_drawer import HistoryPanel
from gui.components.vault_panel import VaultPanel


# Set CustomTkinter default theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class KeyCraftApp(ctk.CTk):
    """Main Application Window for KeyCraft Password Generator & Strength Analyzer."""

    def __init__(self):
        super().__init__()

        self.title("KeyCraft - Password Generator & Strength Analyzer")
        self.geometry("1020x720")
        self.minsize(920, 640)

        # Build UI layout
        self._build_ui()

        # Keyboard bindings
        self.bind("<Control-r>", lambda e: self.generate_current())
        self.bind("<Control-R>", lambda e: self.generate_current())

        # Generate initial password
        self.generate_current()

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # -------------------------------------------------------------
        # 1. Header Bar
        # -------------------------------------------------------------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))
        header.grid_columnconfigure(0, weight=1)

        # Title Box
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        app_title = ctk.CTkLabel(
            title_box,
            text="✨ KeyCraft",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        app_title.pack(side="left", padx=(0, 10))

        app_badge = ctk.CTkLabel(
            title_box,
            text="PRO v1.0",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#e2e8f0", "#30363d"),
            text_color=("gray40", "#8b949e"),
            corner_radius=6,
            padx=8,
            pady=2
        )
        app_badge.pack(side="left", padx=(0, 10))

        subtitle = ctk.CTkLabel(
            title_box,
            text="Cryptographically Secure Password Generator & Real-Time Strength Analyzer",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "#8b949e")
        )
        subtitle.pack(side="left")

        # Theme Switcher
        self.theme_switch = ctk.CTkSwitch(
            header,
            text="Dark Mode",
            font=ctk.CTkFont(size=12),
            command=self._toggle_theme
        )
        self.theme_switch.select()
        self.theme_switch.grid(row=0, column=1, sticky="e")

        # -------------------------------------------------------------
        # 2. Main Navigation Tabs
        # -------------------------------------------------------------
        self.main_tabs = ctk.CTkTabview(self, corner_radius=12, fg_color="transparent")
        self.main_tabs.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 16))

        self.tab_gen = self.main_tabs.add("⚡ Generator")
        self.tab_analyzer = self.main_tabs.add("🔍 Test Any Password")
        self.tab_history = self.main_tabs.add("📜 History & Batch")
        self.tab_vault = self.main_tabs.add("🔐 Vault")

        # Build each tab's view
        self._build_generator_tab()
        self._build_analyzer_tab()
        self._build_history_tab()
        self._build_vault_tab()

    # -----------------------------------------------------------------
    # Tab 1: Password Generator
    # -----------------------------------------------------------------
    def _build_generator_tab(self):
        self.tab_gen.grid_rowconfigure(1, weight=1)
        self.tab_gen.grid_columnconfigure(0, weight=5)  # Left options
        self.tab_gen.grid_columnconfigure(1, weight=5)  # Right strength meter

        # 1. Top Password Display Card
        self.display = PasswordDisplay(
            self.tab_gen,
            on_regenerate=self.generate_current,
            on_copied=self._on_password_copied
        )
        self.display.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 10))

        # 2. Left Options Panel
        self.options_panel = OptionsPanel(
            self.tab_gen,
            on_changed=self.generate_current
        )
        self.options_panel.grid(row=1, column=0, sticky="nsew", padx=(4, 6), pady=0)

        # 3. Right Live Strength Meter
        self.strength_meter = StrengthMeter(
            self.tab_gen,
            title="Live Generated Strength"
        )
        self.strength_meter.grid(row=1, column=1, sticky="nsew", padx=(6, 4), pady=0)

    # -----------------------------------------------------------------
    # Tab 2: Dedicated Strength Analyzer
    # -----------------------------------------------------------------
    def _build_analyzer_tab(self):
        self.tab_analyzer.grid_rowconfigure(1, weight=1)
        self.tab_analyzer.grid_columnconfigure(0, weight=1)

        # Tester Card
        tester_card = ctk.CTkFrame(self.tab_analyzer, corner_radius=14, fg_color=("gray90", "#161b22"))
        tester_card.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 12))
        tester_card.grid_columnconfigure(0, weight=1)

        # Header
        ctk.CTkLabel(
            tester_card,
            text="Type or paste any password below to test its strength and security score:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))

        # Input Row
        input_row = ctk.CTkFrame(tester_card, fg_color="transparent")
        input_row.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 14))
        input_row.grid_columnconfigure(0, weight=1)

        self.analyzer_entry = ctk.CTkEntry(
            input_row,
            placeholder_text="Enter password to test (e.g. MyP@ssw0rd!)...",
            font=ctk.CTkFont(family="Consolas", size=16),
            height=44
        )
        self.analyzer_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.analyzer_entry.bind("<KeyRelease>", self._on_analyzer_text_changed)

        # Paste Button
        btn_paste = ctk.CTkButton(
            input_row,
            text="📋 Paste",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=80,
            height=44,
            fg_color=("#2563eb", "#1f6feb"),
            hover_color=("#1d4ed8", "#388bfd"),
            command=self._paste_into_analyzer
        )
        btn_paste.grid(row=0, column=1, padx=(0, 4))

        # Clear Button
        btn_clear = ctk.CTkButton(
            input_row,
            text="Clear",
            font=ctk.CTkFont(size=12),
            width=60,
            height=44,
            fg_color=("gray80", "#21262d"),
            text_color=("black", "white"),
            hover_color=("gray70", "#30363d"),
            command=self._clear_analyzer
        )
        btn_clear.grid(row=0, column=2, padx=0)

        # Full Analyzer Strength Meter
        self.custom_strength_meter = StrengthMeter(
            self.tab_analyzer,
            title="Custom Password Security Breakdown"
        )
        self.custom_strength_meter.grid(row=1, column=0, sticky="nsew", padx=4, pady=0)

        # Initial analysis with empty placeholder
        self._on_analyzer_text_changed()

    # -----------------------------------------------------------------
    # Tab 3: History & Batch Generator
    # -----------------------------------------------------------------
    def _build_history_tab(self):
        self.tab_history.grid_rowconfigure(0, weight=1)
        self.tab_history.grid_columnconfigure(0, weight=1)

        self.history_panel = HistoryPanel(
            self.tab_history,
            get_current_config_fn=self.options_panel.get_password_config
        )
        self.history_panel.grid(row=0, column=0, sticky="nsew", padx=4, pady=0)

    # -----------------------------------------------------------------
    # Tab 4: Encrypted Local Vault
    # -----------------------------------------------------------------
    def _build_vault_tab(self):
        self.tab_vault.grid_rowconfigure(0, weight=1)
        self.tab_vault.grid_columnconfigure(0, weight=1)

        self.vault_panel = VaultPanel(
            self.tab_vault,
            get_current_password_fn=lambda: self.display.current_password
        )
        self.vault_panel.grid(row=0, column=0, sticky="nsew", padx=4, pady=0)

    # -----------------------------------------------------------------
    # Generation & Analysis Logic
    # -----------------------------------------------------------------
    def generate_current(self):
        """Generate a new password based on active tab and settings."""
        mode = self.options_panel.get_current_mode()

        if mode == "passphrase":
            cfg = self.options_panel.get_passphrase_config()
            new_password = generate_passphrase(cfg)
        elif mode == "pin":
            cfg = self.options_panel.get_pin_config()
            new_password = generate_pin(cfg.length)
        else:
            cfg = self.options_panel.get_password_config()
            new_password = generate_password(cfg)

        # Update Display Box
        self.display.set_password(new_password)

        # Update Live Strength Meter
        report = check_password_strength(new_password)
        self.strength_meter.update_report(report)

        # Add to session history
        self.history_panel.add_password(new_password)

    def _on_password_copied(self, password: str):
        pass

    def _on_analyzer_text_changed(self, event=None):
        text = self.analyzer_entry.get()
        report = check_password_strength(text)
        self.custom_strength_meter.update_report(report)

    def _paste_into_analyzer(self):
        try:
            pasted = self.clipboard_get()
            self.analyzer_entry.delete(0, "end")
            self.analyzer_entry.insert(0, pasted)
            self._on_analyzer_text_changed()
        except Exception:
            pass

    def _clear_analyzer(self):
        self.analyzer_entry.delete(0, "end")
        self._on_analyzer_text_changed()

    def _toggle_theme(self):
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
            self.theme_switch.configure(text="Dark Mode")
        else:
            ctk.set_appearance_mode("light")
            self.theme_switch.configure(text="Light Mode")

