import customtkinter as ctk
from typing import Optional
from core.strength_checker import StrengthReport


class StrengthMeter(ctk.CTkFrame):
    """Real-time visual strength analyzer component with progress bar, scorecards & suggestions."""

    def __init__(self, master, title: str = "Password Strength Analysis", **kwargs):
        super().__init__(master, corner_radius=14, fg_color=("gray90", "#161b22"), **kwargs)
        self.grid_columnconfigure(0, weight=1)

        # Header Row
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))
        header_row.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            header_row,
            text=f"🛡️  {title}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        # Strength Badge
        self.badge_level = ctk.CTkLabel(
            header_row,
            text="STRONG",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#238636",
            text_color="white",
            corner_radius=6,
            padx=10,
            pady=3
        )
        self.badge_level.grid(row=0, column=1, sticky="e")

        # Score & Entropy Label
        self.score_label = ctk.CTkLabel(
            header_row,
            text="85% (64.2 bits)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray40", "#8b949e"),
            anchor="e"
        )
        self.score_label.grid(row=0, column=2, sticky="e", padx=(8, 0))

        # Strength Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=10,
            corner_radius=5,
            progress_color="#3fb950"
        )
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        self.progress_bar.set(0.85)

        # -------------------------------------------------------------
        # Estimated Crack Time Card
        # -------------------------------------------------------------
        self.crack_card = ctk.CTkFrame(self, fg_color=("white", "#0d1117"), corner_radius=10)
        self.crack_card.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))
        self.crack_card.grid_columnconfigure(1, weight=1)

        crack_icon = ctk.CTkLabel(
            self.crack_card,
            text="⏳",
            font=ctk.CTkFont(size=20),
            width=36
        )
        crack_icon.grid(row=0, column=0, rowspan=2, padx=(12, 6), pady=8)

        crack_title = ctk.CTkLabel(
            self.crack_card,
            text="ESTIMATED TIME TO CRACK",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("gray40", "#8b949e"),
            anchor="w"
        )
        crack_title.grid(row=0, column=1, sticky="w", padx=0, pady=(6, 0))

        self.crack_value = ctk.CTkLabel(
            self.crack_card,
            text="Centuries",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#059669", "#3fb950"),
            anchor="w"
        )
        self.crack_value.grid(row=1, column=1, sticky="w", padx=0, pady=(0, 6))

        # -------------------------------------------------------------
        # Security Criteria Checklist Badges
        # -------------------------------------------------------------
        criteria_frame = ctk.CTkFrame(self, fg_color="transparent")
        criteria_frame.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 8))
        for i in range(6):
            criteria_frame.grid_columnconfigure(i, weight=1)

        self.crit_length = self._create_crit_badge(criteria_frame, "12+ Chars", 0)
        self.crit_upper = self._create_crit_badge(criteria_frame, "Uppercase (A-Z)", 1)
        self.crit_lower = self._create_crit_badge(criteria_frame, "Lowercase (a-z)", 2)
        self.crit_digit = self._create_crit_badge(criteria_frame, "Numbers (0-9)", 3)
        self.crit_symbol = self._create_crit_badge(criteria_frame, "Symbols (!@#)", 4)
        self.crit_pattern = self._create_crit_badge(criteria_frame, "No Patterns", 5)

        # -------------------------------------------------------------
        # Actionable Suggestions / Warning Area
        # -------------------------------------------------------------
        self.tips_frame = ctk.CTkFrame(self, fg_color=("gray95", "#0d1117"), corner_radius=10)
        self.tips_frame.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 12))
        self.tips_frame.grid_columnconfigure(0, weight=1)

        self.tips_label = ctk.CTkLabel(
            self.tips_frame,
            text="✓ Excellent password security!",
            font=ctk.CTkFont(size=11),
            text_color=("#059669", "#3fb950"),
            anchor="w",
            justify="left",
            wraplength=480
        )
        self.tips_label.grid(row=0, column=0, sticky="w", padx=12, pady=8)

    def _create_crit_badge(self, master, text: str, col: int) -> ctk.CTkLabel:
        badge = ctk.CTkLabel(
            master,
            text=f"✓ {text}",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=("#dcfce7", "#13231b"),
            text_color=("#15803d", "#3fb950"),
            corner_radius=6,
            padx=4,
            pady=3
        )
        badge.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
        return badge

    def _update_badge_state(self, badge: ctk.CTkLabel, text: str, ok: bool):
        if ok:
            badge.configure(
                text=f"✓ {text}",
                fg_color=("#dcfce7", "#13231b"),
                text_color=("#15803d", "#3fb950")
            )
        else:
            badge.configure(
                text=f"✕ {text}",
                fg_color=("#fee2e2", "#2e1215"),
                text_color=("#b91c1c", "#f85149")
            )

    def update_report(self, report: StrengthReport):
        # 1. Level & Score
        self.badge_level.configure(
            text=report.level.upper(),
            fg_color=report.color
        )
        self.score_label.configure(
            text=f"{report.score}% ({report.entropy_bits:.1f} bits)"
        )
        self.progress_bar.configure(progress_color=report.color)
        self.progress_bar.set(report.progress_val)

        # 2. Crack Time
        self.crack_value.configure(
            text=report.estimated_crack_time,
            text_color=report.color
        )

        # 3. Criteria Badges
        self._update_badge_state(self.crit_length, "12+ Chars", report.length >= 12)
        self._update_badge_state(self.crit_upper, "Uppercase", report.has_uppercase)
        self._update_badge_state(self.crit_lower, "Lowercase", report.has_lowercase)
        self._update_badge_state(self.crit_digit, "Numbers", report.has_digits)
        self._update_badge_state(self.crit_symbol, "Symbols", report.has_symbols)
        
        has_bad_pattern = report.is_common or report.has_repeated_chars or report.has_sequential_chars or report.has_keyboard_walk
        self._update_badge_state(self.crit_pattern, "No Patterns", not has_bad_pattern)

        # 4. Suggestions
        if report.warning:
            self.tips_label.configure(
                text=f"⚠️ {report.warning}\n" + "\n".join(f"• {s}" for s in report.suggestions[:3]),
                text_color="#f85149"
            )
        elif report.suggestions:
            if report.score >= 80:
                self.tips_label.configure(
                    text="✓ " + "\n".join(report.suggestions[:2]),
                    text_color=("#059669", "#3fb950")
                )
            else:
                self.tips_label.configure(
                    text="💡 Suggestions to improve:\n" + "\n".join(f"• {s}" for s in report.suggestions[:3]),
                    text_color=("#d97706", "#d29922")
                )
        else:
            self.tips_label.configure(
                text="✓ Strong and secure password.",
                text_color=("#059669", "#3fb950")
            )

