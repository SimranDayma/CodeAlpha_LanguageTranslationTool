"""
CodeAlpha Internship - Task 1: Language Translation Tool
Author: Simran
Description: A GUI-based language translation tool using deep-translator library
"""

# ── IMPORTS ──────────────────────────────────────────────────────────────────
import tkinter as tk                          # For building the GUI window
from tkinter import ttk, messagebox          # ttk = styled widgets, messagebox = popups
from deep_translator import GoogleTranslator  # Free Google Translate wrapper
import threading                              # To run translation without freezing the UI


# ── LANGUAGE LIST ─────────────────────────────────────────────────────────────
# Dictionary of language name → language code
LANGUAGES = { 
    "Auto Detect"  : "auto",
    "English"      : "en",
    "Hindi"        : "hi",
    "Gujarati"     : "gu",
    "Spanish"      : "es",
    "French"       : "fr",
    "German"       : "de",
    "Arabic"       : "ar",
    "Chinese"      : "zh-CN",
    "Japanese"     : "ja",
    "Korean"       : "ko",
    "Portuguese"   : "pt",
    "Russian"      : "ru",
    "Italian"      : "it",
    "Turkish"      : "tr",
    "Dutch"        : "nl",
    "Bengali"      : "bn",
    "Tamil"        : "ta",
    "Telugu"       : "te",
    "Urdu"         : "ur",
}

LANG_NAMES = list(LANGUAGES.keys())   # Just the names for the dropdown


# ── MAIN APP CLASS ─────────────────────────────────────────────────────────────
class TranslationApp:
    """
    Main application class.
    Everything related to UI and logic lives here.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("🌐 Language Translator — CodeAlpha")
        self.root.geometry("750x580")
        self.root.resizable(True, True)
        self.root.configure(bg="#1a1a2e")   # Dark navy background

        self._build_ui()

    # ── UI BUILDER ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        """Creates all the widgets on the window."""

        # ── Color scheme ──
        BG        = "#1a1a2e"   # Dark navy
        PANEL     = "#16213e"   # Slightly lighter panel
        ACCENT    = "#0f3460"   # Accent blue
        BTN       = "#e94560"   # Red-pink button
        BTN_HOV   = "#c73652"   # Darker on hover
        TEXT      = "#eaeaea"   # Light text
        SUBTEXT   = "#a8a8b3"   # Muted text

        # ── Title bar ──
        title_frame = tk.Frame(self.root, bg=BG)
        title_frame.pack(fill="x", padx=20, pady=(20, 5))

        tk.Label(
            title_frame, text="🌐  Language Translator",
            font=("Segoe UI", 20, "bold"), bg=BG, fg=TEXT
        ).pack(side="left")

        tk.Label(
            title_frame, text="Powered by Google Translate",
            font=("Segoe UI", 10), bg=BG, fg=SUBTEXT
        ).pack(side="left", padx=10, pady=8)

        # ── Language selectors row ──
        lang_frame = tk.Frame(self.root, bg=BG)
        lang_frame.pack(fill="x", padx=20, pady=10)

        # Source language
        tk.Label(lang_frame, text="From:", font=("Segoe UI", 11),
                 bg=BG, fg=SUBTEXT).pack(side="left")

        self.src_lang = ttk.Combobox(
            lang_frame, values=LANG_NAMES, width=16,
            font=("Segoe UI", 11), state="readonly"
        )
        self.src_lang.set("Auto Detect")
        self.src_lang.pack(side="left", padx=(5, 15))

        # Swap button
        swap_btn = tk.Button(
            lang_frame, text="⇌", font=("Segoe UI", 14, "bold"),
            bg=ACCENT, fg=TEXT, relief="flat", cursor="hand2",
            padx=8, command=self._swap_languages
        )
        swap_btn.pack(side="left", padx=5)

        # Target language
        tk.Label(lang_frame, text="To:", font=("Segoe UI", 11),
                 bg=BG, fg=SUBTEXT).pack(side="left", padx=(15, 0))

        self.tgt_lang = ttk.Combobox(
            lang_frame, values=LANG_NAMES[1:], width=16,   # No "Auto Detect" for target
            font=("Segoe UI", 11), state="readonly"
        )
        self.tgt_lang.set("Hindi")
        self.tgt_lang.pack(side="left", padx=(5, 0))

        # ── Text panels ──
        panels = tk.Frame(self.root, bg=BG)
        panels.pack(fill="both", expand=True, padx=20, pady=5)

        # Left panel — input
        left = tk.Frame(panels, bg=PANEL, bd=0)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(left, text="Enter text", font=("Segoe UI", 10),
                 bg=PANEL, fg=SUBTEXT).pack(anchor="w", padx=10, pady=(8, 2))

        self.input_text = tk.Text(
            left, font=("Segoe UI", 13), bg=PANEL, fg=TEXT,
            insertbackground=TEXT, relief="flat",
            wrap="word", padx=10, pady=8, height=12
        )
        self.input_text.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # Right panel — output
        right = tk.Frame(panels, bg=PANEL, bd=0)
        right.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(right, text="Translation", font=("Segoe UI", 10),
                 bg=PANEL, fg=SUBTEXT).pack(anchor="w", padx=10, pady=(8, 2))

        self.output_text = tk.Text(
            right, font=("Segoe UI", 13), bg=PANEL, fg="#4ecca3",  # Teal output
            relief="flat", wrap="word", padx=10, pady=8, height=12,
            state="disabled"   # User cannot type here
        )
        self.output_text.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # ── Buttons row ──
        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(fill="x", padx=20, pady=(5, 10))

        # Translate button
        self.translate_btn = tk.Button(
            btn_frame, text="  Translate  ▶",
            font=("Segoe UI", 13, "bold"),
            bg=BTN, fg="white", relief="flat",
            padx=20, pady=8, cursor="hand2",
            command=self._start_translation
        )
        self.translate_btn.pack(side="left")

        # Bind hover effect
        self.translate_btn.bind("<Enter>", lambda e: self.translate_btn.config(bg=BTN_HOV))
        self.translate_btn.bind("<Leave>", lambda e: self.translate_btn.config(bg=BTN))

        # Clear button
        clear_btn = tk.Button(
            btn_frame, text="  Clear",
            font=("Segoe UI", 12),
            bg=ACCENT, fg=TEXT, relief="flat",
            padx=15, pady=8, cursor="hand2",
            command=self._clear_all
        )
        clear_btn.pack(side="left", padx=10)

        # Copy button
        copy_btn = tk.Button(
            btn_frame, text="  📋 Copy",
            font=("Segoe UI", 12),
            bg=ACCENT, fg=TEXT, relief="flat",
            padx=15, pady=8, cursor="hand2",
            command=self._copy_translation
        )
        copy_btn.pack(side="left")

        # Status label (shows "Translating..." etc.)
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            btn_frame, textvariable=self.status_var,
            font=("Segoe UI", 10), bg=BG, fg=SUBTEXT
        ).pack(side="right", padx=10)

        # ── Keyboard shortcut: Ctrl+Enter to translate ──
        self.root.bind("<Control-Return>", lambda e: self._start_translation())

    # ── TRANSLATION LOGIC ──────────────────────────────────────────────────────
    def _start_translation(self):
        """
        Runs translation in a background thread so the UI doesn't freeze.
        """
        text = self.input_text.get("1.0", "end").strip()  # Get all text from input box

        if not text:
            messagebox.showwarning("Empty Input", "Please enter some text to translate.")
            return

        # Disable button while translating
        self.translate_btn.config(state="disabled", text="Translating...")
        self.status_var.set("⏳ Translating...")

        # Run in background thread (so UI stays responsive)
        thread = threading.Thread(target=self._do_translation, args=(text,))
        thread.daemon = True
        thread.start()

    def _do_translation(self, text):
        """
        The actual translation call — runs in a background thread.
        """
        try:
            src_name = self.src_lang.get()
            tgt_name = self.tgt_lang.get()

            src_code = LANGUAGES[src_name]   # e.g. "auto"
            tgt_code = LANGUAGES[tgt_name]   # e.g. "hi"

            # Call Google Translate
            translated = GoogleTranslator(source=src_code, target=tgt_code).translate(text)

            # Update UI from main thread (Tkinter rule)
            self.root.after(0, self._show_result, translated)

        except Exception as error:
            self.root.after(0, self._show_error, str(error))

    def _show_result(self, translated_text):
        """Displays the translated text in the output box."""
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", translated_text)
        self.output_text.config(state="disabled")

        self.translate_btn.config(state="normal", text="  Translate  ▶")
        self.status_var.set("✅ Done!")

    def _show_error(self, error_msg):
        """Shows an error popup if translation fails."""
        self.translate_btn.config(state="normal", text="  Translate  ▶")
        self.status_var.set("❌ Error")
        messagebox.showerror("Translation Error",
                             f"Something went wrong:\n\n{error_msg}\n\nCheck your internet connection.")

    # ── HELPER ACTIONS ─────────────────────────────────────────────────────────
    def _swap_languages(self):
        """Swaps source and target language selections."""
        src = self.src_lang.get()
        tgt = self.tgt_lang.get()
        if src != "Auto Detect":
            self.src_lang.set(tgt)
            self.tgt_lang.set(src)

    def _clear_all(self):
        """Clears both text boxes."""
        self.input_text.delete("1.0", "end")
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")
        self.status_var.set("Ready")

    def _copy_translation(self):
        """Copies the translated text to clipboard."""
        result = self.output_text.get("1.0", "end").strip()
        if result:
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            self.status_var.set("📋 Copied!")
        else:
            messagebox.showinfo("Nothing to copy", "Translate something first!")


# ── RUN THE APP ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationApp(root)
    root.mainloop()   # Starts the GUI event loop
