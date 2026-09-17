import customtkinter as ctk
from typing import Callable, Optional
from core.generator import PasswordConfig, PassphraseConfig, PinConfig


class OptionsPanel(ctk.CTkFrame):
    """Customization controls for Random Passwords, Passphrases, and PINs."""

    def __init__(self, master, on_changed: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, corner_radius=14, fg_color=("gray90", "#161b22"), **kwargs)
        self.on_changed = on_changed

        self.grid_columnconfigure(0, weight=1)

        # Mode Tabview
        self.tabview = ctk.CTkTabview(self, corner_radius=10, fg_color=("gray95", "#0d1117"))
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=12, pady=10)

        self.tab_random = self.tabview.add("🎲 Random Password")
        self.tab_passphrase = self.tabview.add("📖 Passphrase")
        self.tab_pin = self.tabview.add("🔢 PIN Code")

        self.tabview.configure(command=self._on_mode_switched)

        # -------------------------------------------------------------
        # 1. Random Password Tab
        # -------------------------------------------------------------
        self._build_random_tab()

        # -------------------------------------------------------------
        # 2. Passphrase Tab
        # -------------------------------------------------------------
        self._build_passphrase_tab()

        # -------------------------------------------------------------
        # 3. PIN Code Tab
        # -------------------------------------------------------------
        self._build_pin_tab()

    def _build_random_tab(self):
        self.tab_random.grid_columnconfigure(0, weight=1)

        # Length Slider Row
        slider_frame = ctk.CTkFrame(self.tab_random, fg_color="transparent")
        slider_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 10))
        slider_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            slider_frame,
            text="Password Length:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.length_label = ctk.CTkLabel(
            slider_frame,
            text="16",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#2563eb", "#58a6ff"),
            width=36
        )
        self.length_label.grid(row=0, column=2, sticky="e", padx=(10, 0))

        self.length_slider = ctk.CTkSlider(
            slider_frame,
            from_=6,
            to=64,
            number_of_steps=58,
            command=self._on_length_slider_changed
        )
        self.length_slider.set(16)
        self.length_slider.grid(row=0, column=1, sticky="ew")

        # Quick preset buttons (12, 16, 24, 32)
        presets_frame = ctk.CTkFrame(self.tab_random, fg_color="transparent")
        presets_frame.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 10))

        ctk.CTkLabel(
            presets_frame,
            text="Quick Presets:",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "#8b949e")
        ).pack(side="left", padx=(0, 6))

        for preset in [12, 16, 20, 24, 32]:
            btn = ctk.CTkButton(
                presets_frame,
                text=str(preset),
                font=ctk.CTkFont(size=11),
                width=38,
                height=24,
                fg_color=("gray80", "#21262d"),
                text_color=("black", "white"),
                hover_color=("gray70", "#30363d"),
                command=lambda p=preset: self._set_length(p)
            )
            btn.pack(side="left", padx=2)

        # Checkboxes Container
        cb_frame = ctk.CTkFrame(self.tab_random, fg_color="transparent")
        cb_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=0)
        cb_frame.grid_columnconfigure(0, weight=1)
        cb_frame.grid_columnconfigure(1, weight=1)

        self.var_upper = ctk.BooleanVar(value=True)
        self.chk_upper = ctk.CTkCheckBox(
            cb_frame,
            text="Uppercase Letters (A-Z)",
            variable=self.var_upper,
            command=self._notify_changed
        )
        self.chk_upper.grid(row=0, column=0, sticky="w", padx=4, pady=4)

        self.var_lower = ctk.BooleanVar(value=True)
        self.chk_lower = ctk.CTkCheckBox(
            cb_frame,
            text="Lowercase Letters (a-z)",
            variable=self.var_lower,
            command=self._notify_changed
        )
        self.chk_lower.grid(row=0, column=1, sticky="w", padx=4, pady=4)

        self.var_digits = ctk.BooleanVar(value=True)
        self.chk_digits = ctk.CTkCheckBox(
            cb_frame,
            text="Digits (0-9)",
            variable=self.var_digits,
            command=self._notify_changed
        )
        self.chk_digits.grid(row=1, column=0, sticky="w", padx=4, pady=4)

        self.var_symbols = ctk.BooleanVar(value=True)
        self.chk_symbols = ctk.CTkCheckBox(
            cb_frame,
            text="Special Symbols (!@#$%)",
            variable=self.var_symbols,
            command=self._notify_changed
        )
        self.chk_symbols.grid(row=1, column=1, sticky="w", padx=4, pady=4)

        self.var_ambiguous = ctk.BooleanVar(value=False)
        self.chk_ambiguous = ctk.CTkCheckBox(
            cb_frame,
            text="Exclude Ambiguous (0, O, 1, l, I, |)",
            variable=self.var_ambiguous,
            command=self._notify_changed
        )
        self.chk_ambiguous.grid(row=2, column=0, columnspan=2, sticky="w", padx=4, pady=4)

    def _build_passphrase_tab(self):
        self.tab_passphrase.grid_columnconfigure(0, weight=1)

        # Word count slider
        slider_frame = ctk.CTkFrame(self.tab_passphrase, fg_color="transparent")
        slider_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 10))
        slider_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            slider_frame,
            text="Word Count:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.words_label = ctk.CTkLabel(
            slider_frame,
            text="4 words",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#2563eb", "#58a6ff"),
            width=60
        )
        self.words_label.grid(row=0, column=2, sticky="e", padx=(10, 0))

        self.words_slider = ctk.CTkSlider(
            slider_frame,
            from_=3,
            to=8,
            number_of_steps=5,
            command=self._on_words_slider_changed
        )
        self.words_slider.set(4)
        self.words_slider.grid(row=0, column=1, sticky="ew")

        # Separator selector
        sep_frame = ctk.CTkFrame(self.tab_passphrase, fg_color="transparent")
        sep_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(
            sep_frame,
            text="Word Separator:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 8))

        self.sep_var = ctk.StringVar(value="-")
        for char, name in [("-", "Hyphen (-)"), (".", "Period (.)"), ("_", "Underscore (_)"), (" ", "Space"), ("/", "Slash (/)")]:
            rb = ctk.CTkRadioButton(
                sep_frame,
                text=name,
                value=char,
                variable=self.sep_var,
                command=self._notify_changed
            )
            rb.pack(side="left", padx=6)

        # Options checkboxes
        cb_frame = ctk.CTkFrame(self.tab_passphrase, fg_color="transparent")
        cb_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(8, 0))

        self.var_cap = ctk.BooleanVar(value=True)
        self.chk_cap = ctk.CTkCheckBox(
            cb_frame,
            text="Capitalize Each Word",
            variable=self.var_cap,
            command=self._notify_changed
        )
        self.chk_cap.pack(side="left", padx=(4, 16))

        self.var_num = ctk.BooleanVar(value=True)
        self.chk_num = ctk.CTkCheckBox(
            cb_frame,
            text="Include Random Number",
            variable=self.var_num,
            command=self._notify_changed
        )
        self.chk_num.pack(side="left", padx=4)

    def _build_pin_tab(self):
        self.tab_pin.grid_columnconfigure(0, weight=1)

        slider_frame = ctk.CTkFrame(self.tab_pin, fg_color="transparent")
        slider_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(12, 10))
        slider_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            slider_frame,
            text="PIN Digits:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.pin_label = ctk.CTkLabel(
            slider_frame,
            text="6 digits",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#2563eb", "#58a6ff"),
            width=60
        )
        self.pin_label.grid(row=0, column=2, sticky="e", padx=(10, 0))

        self.pin_slider = ctk.CTkSlider(
            slider_frame,
            from_=4,
            to=16,
            number_of_steps=12,
            command=self._on_pin_slider_changed
        )
        self.pin_slider.set(6)
        self.pin_slider.grid(row=0, column=1, sticky="ew")

        # Preset buttons for 4, 6, 8, 10
        presets_frame = ctk.CTkFrame(self.tab_pin, fg_color="transparent")
        presets_frame.grid(row=1, column=0, sticky="w", padx=8, pady=4)

        ctk.CTkLabel(
            presets_frame,
            text="Quick Presets:",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "#8b949e")
        ).pack(side="left", padx=(0, 6))

        for preset in [4, 6, 8, 12]:
            btn = ctk.CTkButton(
                presets_frame,
                text=f"{preset} Digits",
                font=ctk.CTkFont(size=11),
                width=64,
                height=24,
                fg_color=("gray80", "#21262d"),
                text_color=("black", "white"),
                hover_color=("gray70", "#30363d"),
                command=lambda p=preset: self._set_pin_length(p)
            )
            btn.pack(side="left", padx=3)

    # -----------------------------------------------------------------
    # Event Handlers
    # -----------------------------------------------------------------
    def _on_mode_switched(self):
        self._notify_changed()

    def _on_length_slider_changed(self, value):
        val = int(round(value))
        self.length_label.configure(text=str(val))
        self._notify_changed()

    def _set_length(self, val: int):
        self.length_slider.set(val)
        self.length_label.configure(text=str(val))
        self._notify_changed()

    def _on_words_slider_changed(self, value):
        val = int(round(value))
        self.words_label.configure(text=f"{val} words")
        self._notify_changed()

    def _on_pin_slider_changed(self, value):
        val = int(round(value))
        self.pin_label.configure(text=f"{val} digits")
        self._notify_changed()

    def _set_pin_length(self, val: int):
        self.pin_slider.set(val)
        self.pin_label.configure(text=f"{val} digits")
        self._notify_changed()

    def _notify_changed(self):
        if self.on_changed:
            self.on_changed()

    # -----------------------------------------------------------------
    # Configuration Getters
    # -----------------------------------------------------------------
    def get_current_mode(self) -> str:
        current = self.tabview.get()
        if "Random" in current:
            return "random"
        elif "Passphrase" in current:
            return "passphrase"
        else:
            return "pin"

    def get_password_config(self) -> PasswordConfig:
        return PasswordConfig(
            length=int(round(self.length_slider.get())),
            use_uppercase=self.var_upper.get(),
            use_lowercase=self.var_lower.get(),
            use_digits=self.var_digits.get(),
            use_symbols=self.var_symbols.get(),
            exclude_ambiguous=self.var_ambiguous.get()
        )

    def get_passphrase_config(self) -> PassphraseConfig:
        return PassphraseConfig(
            word_count=int(round(self.words_slider.get())),
            separator=self.sep_var.get(),
            capitalize=self.var_cap.get(),
            include_number=self.var_num.get()
        )

    def get_pin_config(self) -> PinConfig:
        return PinConfig(
            length=int(round(self.pin_slider.get()))
        )

