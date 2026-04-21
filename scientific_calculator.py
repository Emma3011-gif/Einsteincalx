import tkinter as tk
from tkinter import font as tkfont
import math
import re
from functools import partial

# ── Button layout ─────────────────────────────────────────────────────────────
BUTTON_ROWS = [
    [("⏮","nav"),  ("◀","nav"),  ("▲","nav"),  ("▼","nav"),  ("▶","nav"),  ("⏭","nav")],
    [("hyp","fn"), ("And","fn"), ("Or","fn"),  ("int","fn"), ("Mode","fn"),("π","fn")],
    [("√x","fn"),  ("log","fn"), ("eng","fn"), ("e^x","fn"), ("ln","fn"),  ("sin","fn")],
    [("Rcl","op"), ("x²","op"),  ("x^","op"),  ("cos","fn"), ("tan","fn"), ("n!","op")],
    [("(-)","op"), ("sin⁻¹","fn"),("10^x","fn"),("MC","op"), ("abs","op"), ("MR","op")],
    [("MS","op"),  ("(","op"),   ("M+","op"),  ("M-","op"),  ("00","op"),  ("ANS","op")],
    [("7","num"),  ("8","num"),  ("9","num"),  ("DEL","del"),("AC","ac"),  ("%","op")],
    [("4","num"),  ("5","num"),  ("6","num"),  ("×","op"),   ("÷","op"),   ("+","op")],
    [("1","num"),  ("2","num"),  ("3","num"),  ("-","op"),   ("^","op"),   ("=","eq")],
    [("0","num"),  (".","num"),  (")","op"),   ("√","fn"),   ("^2","fn"),  ("MS2","op")],
]

COLORS = {
    "bg":           "#1c1c1e",
    "display_bg":   "#161618",
    "display_text": "#ffffff",
    "display_expr": "#888888",
    "fn":           "#2c2c2e",
    "op":           "#3a3a3c",
    "num":          "#48484a",
    "del":          "#e53935",
    "ac":           "#4caf50",
    "eq":           "#4caf50",
    "nav":          "#242426",
    "sep":          "#3a3a3c",
}

NUM_ROWS = len(BUTTON_ROWS)
NUM_COLS = 6


class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("CalcureX fx-120")
        self.root.configure(bg=COLORS["bg"])

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        win_w = max(360, int(sw * 0.40))
        win_h = max(640, int(sh * 0.92))
        x = (sw - win_w) // 2
        y = (sh - win_h) // 2
        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.root.minsize(320, 580)
        self.root.resizable(True, True)

        # ── State ─────────────────────────────────────────────────────────
        self.expression       = ""
        self.current_input    = ""
        self.memory           = 0.0
        self.last_result      = 0
        self.open_parens      = 0
        self._cursor_vis      = True
        self._just_calculated = False

        # ── Fonts ─────────────────────────────────────────────────────────
        self._font_display = tkfont.Font(family="Helvetica Neue", size=42, weight="bold")
        self._font_expr    = tkfont.Font(family="Helvetica Neue", size=11)
        self._font_cursor  = tkfont.Font(family="Helvetica Neue", size=11)
        self._font_fn      = tkfont.Font(family="Helvetica Neue", size=9)
        self._font_num     = tkfont.Font(family="Helvetica Neue", size=13, weight="bold")
        self._font_nav     = tkfont.Font(family="Helvetica Neue", size=9)
        self._font_hdr     = tkfont.Font(family="Helvetica Neue", size=10)

        self._build_ui()
        self._blink_cursor()
        self.root.bind("<Configure>", self._on_resize)
        self.root.after(80, lambda: self._on_resize(None))

    # ─────────────────────────────────────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.outer = tk.Frame(self.root, bg=COLORS["bg"])
        self.outer.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Header
        hdr = tk.Frame(self.outer, bg=COLORS["bg"])
        hdr.pack(side="top", fill="x", padx=14, pady=(10, 0))
        tk.Label(hdr, text="≡", font=self._font_hdr,
                 bg=COLORS["bg"], fg="#555555").pack(side="left")
        tk.Label(hdr, text="Standard", font=self._font_hdr,
                 bg=COLORS["bg"], fg="#666666").pack(side="right")

        # Display panel
        self.disp_frame = tk.Frame(self.outer, bg=COLORS["display_bg"])
        self.disp_frame.pack(side="top", fill="x", padx=0, pady=(6, 0))

        # Expression line
        expr_row = tk.Frame(self.disp_frame, bg=COLORS["display_bg"])
        expr_row.pack(side="top", fill="x", padx=14, pady=(10, 0))
        self.expr_label = tk.Label(
            expr_row, text="",
            font=self._font_expr,
            bg=COLORS["display_bg"], fg=COLORS["display_expr"],
            anchor="e", justify="right")
        self.expr_label.pack(side="left", fill="x", expand=True)
        self.cursor_label = tk.Label(
            expr_row, text="|",
            font=self._font_cursor,
            bg=COLORS["display_bg"], fg="#555555", width=1)
        self.cursor_label.pack(side="left")

        # Main number
        self.display = tk.Label(
            self.disp_frame, text="0",
            font=self._font_display,
            bg=COLORS["display_bg"], fg=COLORS["display_text"],
            anchor="e", justify="right")
        self.display.pack(side="top", fill="x", padx=14, pady=(2, 8))

        # Memory row
        mem_row = tk.Frame(self.disp_frame, bg=COLORS["display_bg"])
        mem_row.pack(side="top", fill="x", padx=14, pady=(0, 6))
        self.mem_lbl = tk.Label(
            mem_row, text="",
            font=self._font_hdr,
            bg=COLORS["display_bg"], fg="#4caf50", anchor="w")
        self.mem_lbl.pack(side="left")

        # Separator
        tk.Frame(self.outer, bg=COLORS["sep"], height=1).pack(
            side="top", fill="x")

        # Button grid
        self.grid_frame = tk.Frame(self.outer, bg=COLORS["bg"])
        self.grid_frame.pack(side="top", fill="both", expand=True,
                             padx=3, pady=3)
        for c in range(NUM_COLS):
            self.grid_frame.grid_columnconfigure(c, weight=1, uniform="col")
        for r in range(NUM_ROWS):
            self.grid_frame.grid_rowconfigure(r, weight=1, uniform="row")

        self._btn_widgets = []
        for r, row_def in enumerate(BUTTON_ROWS):
            for c, (label, ctype) in enumerate(row_def):
                display_label = "MS" if label == "MS2" else label
                bg  = COLORS.get(ctype, COLORS["fn"])
                btn = tk.Button(
                    self.grid_frame,
                    text=display_label,
                    font=self._font_for(ctype),
                    bg=bg,
                    fg=self._fg_for(ctype),
                    activebackground=self._lighten(bg, 0.25),
                    activeforeground="#ffffff",
                    relief="flat", bd=0,
                    cursor="hand2",
                    command=partial(self.on_button_click, label))
                btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
                btn.bind("<Enter>",
                    lambda e, b=btn, col=bg: b.config(
                        bg=self._lighten(col, 0.25)))
                btn.bind("<Leave>",
                    lambda e, b=btn, col=bg: b.config(bg=col))
                self._btn_widgets.append((btn, ctype, bg))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _font_for(self, ctype):
        if ctype == "nav":                       return self._font_nav
        if ctype in ("num", "eq", "del", "ac"): return self._font_num
        return self._font_fn

    def _fg_for(self, ctype):
        return {"nav": "#aaaaaa"}.get(ctype, "#ffffff")

    def _lighten(self, hex_color, pct):
        h   = hex_color.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        new = tuple(min(255, int(c + (255 - c) * pct)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*new)

    # ── Resize ────────────────────────────────────────────────────────────────
    def _on_resize(self, _):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        if w < 50 or h < 50:
            return
        disp_size = max(18, min(52, int(w * 0.10)))
        self._font_display.config(size=disp_size)
        expr_size = max(7, min(14, int(w * 0.028)))
        self._font_expr.config(size=expr_size)
        self._font_cursor.config(size=expr_size)
        hdr_size = max(7, min(13, int(w * 0.024)))
        self._font_hdr.config(size=hdr_size)
        disp_block = disp_size * 2 + 60
        btn_area_h = max(80, h - disp_block - 20)
        row_h      = btn_area_h / NUM_ROWS
        col_w      = w / NUM_COLS
        ref        = min(row_h, col_w)
        self._font_fn.config( size=max(6, min(13, int(ref * 0.30))))
        self._font_num.config(size=max(8, min(20, int(ref * 0.40))), weight="bold")
        self._font_nav.config(size=max(6, min(11, int(ref * 0.26))))

    def _blink_cursor(self):
        self._cursor_vis = not self._cursor_vis
        self.cursor_label.config(text="|" if self._cursor_vis else " ")
        self.root.after(530, self._blink_cursor)

    # ─────────────────────────────────────────────────────────────────────────
    # Button handler
    # ─────────────────────────────────────────────────────────────────────────
    def on_button_click(self, label):
        is_digit = (label in [str(i) for i in range(10)] + [".", "00"])
        if self._just_calculated and is_digit:
            self.expression    = ""
            self.current_input = ""
            self.open_parens   = 0
        self._just_calculated = False

        if   label == "AC":           self._clear_all()
        elif label == "DEL":          self._delete_last()
        elif label == "=":            self._calculate()
        elif label == "×":            self._push_op("×")
        elif label == "÷":            self._push_op("÷")
        elif label == "+":            self._push_op("+")
        elif label == "-":            self._push_op("-")
        elif label == "^":            self._push_op("^")
        elif label == "%":            self._push_op("%")
        elif label == "(-)":          self._negate()
        elif label in ("x²", "^2"):   self._push_postfix_op("^2")
        elif label == "x^":           self._push_op("^")
        elif label in ("√", "√x"):    self._push_func("√(")
        elif label == "sin":          self._push_func("sin(")
        elif label == "cos":          self._push_func("cos(")
        elif label == "tan":          self._push_func("tan(")
        elif label == "sin⁻¹":        self._push_func("asin(")
        elif label == "asin":         self._push_func("asin(")
        elif label == "acos":         self._push_func("acos(")
        elif label == "atan":         self._push_func("atan(")
        elif label == "hyp":          self._push_func("sinh(")
        elif label == "sinh":         self._push_func("sinh(")
        elif label == "cosh":         self._push_func("cosh(")
        elif label == "tanh":         self._push_func("tanh(")
        elif label == "log":          self._push_func("log(")
        elif label == "ln":           self._push_func("ln(")
        elif label == "abs":          self._push_func("abs(")
        elif label == "eng":          self._push_func("eng(")
        elif label == "e^x":          self._push_func("e^(")
        elif label == "10^x":         self._push_func("10^(")
        elif label in ("n!", "!"):    self._push_postfix("!")
        elif label == "(":            self._push_open_paren()
        elif label == ")":            self._push_close_paren()
        elif label == "π":            self._push_constant("π")
        elif label == "MC":           self._mem_clear()
        elif label == "MR":           self._mem_recall()
        elif label == "M+":           self._mem_add()
        elif label == "M-":           self._mem_sub()
        elif label in ("MS", "MS2"):  self._mem_store()
        elif label == "ANS":          self._push_constant(self._fmt(self.last_result))
        elif label == "00":           self._push_digit("00")
        elif label == ".":            self._push_dot()
        elif label in [str(i) for i in range(10)]:
            self._push_digit(label)

        self._update_display()

    # ─────────────────────────────────────────────────────────────────────────
    # Input primitives
    # ─────────────────────────────────────────────────────────────────────────
    def _needs_implicit_multiply(self):
        """
        Returns True when the expression ends with something that would need
        a '*' before an opening parenthesis or constant.
        e.g.  '5'  '3.14'  ')'  'π'
        """
        if not self.expression:
            return False
        last = self.expression[-1]
        return last in "0123456789.)π"

    def _push_digit(self, d):
        if self.current_input in ("", "0") and d not in (".", "00"):
            # Replace a lone zero that follows an operator or is the start
            if (self.expression
                    and self.expression[-1] == "0"
                    and (len(self.expression) == 1
                         or self.expression[-2] in "+-×÷^(!")):
                self.expression    = self.expression[:-1] + d
            else:
                self.expression   += d
            self.current_input = d
        else:
            if d == "00" and not self.current_input:
                d = "0"
            self.expression   += d
            self.current_input += d

    def _push_dot(self):
        if "." in self.current_input:
            return
        if not self.current_input:
            self.expression   += "0."
            self.current_input = "0."
        else:
            self.expression   += "."
            self.current_input += "."

    def _push_op(self, op):
        """Infix binary operator."""
        if not self.expression:
            if op == "-":                   # allow leading minus
                self.expression    = "-"
                self.current_input = ""
            return
        last = self.expression[-1]
        if last in "×÷+-^%":               # replace last operator
            self.expression    = self.expression[:-1] + op
            self.current_input = ""
            return
        self.expression   += op
        self.current_input = ""

    def _push_postfix_op(self, op):
        """Operator that attaches to what's already typed, e.g. ^2."""
        if self.expression:
            self.expression   += op
            self.current_input = ""

    def _push_func(self, func):
        """
        Push a function token.
        If the last char is a digit / ) / constant we insert × first so that
        '5e^(2)' becomes '5*e^(2)' and not '5e^(2)' which Python can't parse.
        """
        if self._needs_implicit_multiply():
            self.expression += "×"
        self.expression   += func
        self.current_input = ""
        self.open_parens  += 1

    def _push_postfix(self, op):
        if self.current_input:
            self.expression   += op
            self.current_input = ""

    def _push_open_paren(self):
        if self._needs_implicit_multiply():
            self.expression += "×"
        self.expression   += "("
        self.current_input = ""
        self.open_parens  += 1

    def _push_close_paren(self):
        if self.open_parens > 0:
            self.expression   += ")"
            self.current_input = ""
            self.open_parens  -= 1

    def _push_constant(self, val):
        if self._needs_implicit_multiply():
            self.expression += "×"
        self.expression   += val
        self.current_input = val

    def _negate(self):
        if self.current_input and not self.current_input.startswith("-"):
            ci  = self.current_input
            neg = "-" + ci
            idx = self.expression.rfind(ci)
            if idx != -1:
                self.expression    = (self.expression[:idx]
                                      + neg
                                      + self.expression[idx + len(ci):])
                self.current_input = neg
        elif self.current_input.startswith("-"):
            ci  = self.current_input
            pos = ci[1:]
            idx = self.expression.rfind(ci)
            if idx != -1:
                self.expression    = (self.expression[:idx]
                                      + pos
                                      + self.expression[idx + len(ci):])
                self.current_input = pos
        else:
            self.expression   += "-"
            self.current_input = ""

    def _delete_last(self):
        if not self.expression:
            return
        multi_tokens = [
            "asin(", "acos(", "atan(",
            "sinh(", "cosh(", "tanh(",
            "sin(", "cos(", "tan(",
            "log(", "ln(",
            "√(", "e^(", "10^(",
            "abs(", "eng(",
            "^2", "00", "π",
            "×(",                           # implicit-multiply prefix
        ]
        for tok in multi_tokens:
            if self.expression.endswith(tok):
                self.expression    = self.expression[:-len(tok)]
                self.current_input = self._extract_last_number()
                if "(" in tok:
                    self.open_parens = max(0, self.open_parens - 1)
                return
        self.expression    = self.expression[:-1]
        self.current_input = self._extract_last_number()

    def _extract_last_number(self):
        buf = ""
        for ch in reversed(self.expression):
            if ch in "0123456789.":
                buf = ch + buf
            else:
                break
        return buf

    def _clear_all(self):
        self.expression       = ""
        self.current_input    = ""
        self.open_parens      = 0
        self._just_calculated = False

    # ─────────────────────────────────────────────────────────────────────────
    # Memory
    # ─────────────────────────────────────────────────────────────────────────
    def _current_value(self):
        if self.current_input:
            try:
                s = self.current_input.replace("π", str(math.pi))
                return float(s)
            except Exception:
                pass
        return float(self.last_result)

    def _mem_clear(self):
        self.memory = 0.0
        self.mem_lbl.config(text="")

    def _mem_store(self):
        try:
            self.memory = self._current_value()
            self.mem_lbl.config(text=f"M = {self._fmt(self.memory)}")
        except Exception:
            pass

    def _mem_recall(self):
        self._push_constant(self._fmt(self.memory))

    def _mem_add(self):
        try:
            self.memory += self._current_value()
            self.mem_lbl.config(text=f"M = {self._fmt(self.memory)}")
        except Exception:
            pass

    def _mem_sub(self):
        try:
            self.memory -= self._current_value()
            self.mem_lbl.config(text=f"M = {self._fmt(self.memory)}")
        except Exception:
            pass

    # ─────────────────────────────────────────────────────────────────────────
    # Evaluator
    # ─────────────────────────────────────────────────────────────────────────
    def _calculate(self):
        if not self.expression:
            return
        try:
            result = self._evaluate(self.expression)
            self.last_result      = result
            self.expression       = self._fmt(result)
            self.current_input    = self._fmt(result)
            self.open_parens      = 0
            self._just_calculated = True
        except Exception as err:
            print(f"[Calc error] {err!r}  expr={self.expression!r}")
            self.display.config(text="Error", fg="#ef5350")
            self.expr_label.config(text=self.expression)
            self.expression       = ""
            self.current_input    = ""
            self.open_parens      = 0

    def _evaluate(self, raw: str) -> float:
        """
        Safely convert the display expression to Python and evaluate it.

        Strategy
        --------
        1.  Replace display symbols (×, ÷, π …) with unique placeholders so
            subsequent substitutions can never corrupt them.
        2.  Expand factorials via regex.
        3.  Restore placeholders to valid Python.
        4.  eval() inside a restricted namespace.
        """
        e = raw

        # ── 1a. Implicit multiply: digit/)/π immediately before ( or π ───
        #   Already inserted at input time via _needs_implicit_multiply(),
        #   but run a final safety pass here as well.
        e = re.sub(r'(\d|[)π])([(πe])', r'\1×\2', e)

        # ── 1b. Display operators ─────────────────────────────────────────
        # Tag every token with a unique placeholder so nothing gets
        # double-substituted later.
        PLACEHOLDERS = [
            # functions  (longest first to avoid partial matches)
            ("asin(",  "§ASIN§"),
            ("acos(",  "§ACOS§"),
            ("atan(",  "§ATAN§"),
            ("sinh(",  "§SINH§"),
            ("cosh(",  "§COSH§"),
            ("tanh(",  "§TANH§"),
            ("sin(",   "§SIN§"),
            ("cos(",   "§COS§"),
            ("tan(",   "§TAN§"),
            ("log(",   "§LOG§"),
            ("ln(",    "§LN§"),
            ("√(",     "§SQRT§"),
            ("abs(",   "§ABS§"),
            ("eng(",   "§ENG§"),
            # special power functions — MUST come before generic ^ handler
            ("e^(",    "§EXP§"),
            ("10^(",   "§TEN§"),
            # constants
            ("π",      "§PI§"),
        ]
        for tok, ph in PLACEHOLDERS:
            e = e.replace(tok, ph)

        # ── 1c. Remaining display operators ──────────────────────────────
        e = e.replace("×", "*").replace("÷", "/")

        # ── 2. ^2 shortcut, then generic ^ ───────────────────────────────
        e = re.sub(r'\^2(?!\d)', '**2', e)
        e = e.replace("^", "**")

        # ── 3. Restore placeholders → Python calls ────────────────────────
        E  = math.e
        PI = math.pi
        RESTORE = [
            ("§SQRT§", "_sqrt("),
            ("§SIN§",  "_dsin("),
            ("§COS§",  "_dcos("),
            ("§TAN§",  "_dtan("),
            ("§ASIN§", "_dasin("),
            ("§ACOS§", "_dacos("),
            ("§ATAN§", "_datan("),
            ("§SINH§", "_sinh("),
            ("§COSH§", "_cosh("),
            ("§TANH§", "_tanh("),
            ("§LOG§",  "_log10("),
            ("§LN§",   "_ln("),
            ("§ABS§",  "_abs("),
            ("§ENG§",  "("),               # eng(x) = x
            # e^( x ) → math.e ** x
            # The placeholder becomes  §EXP§ x )
            # We restore it as  _exp(  so _exp(x) = e**x
            ("§EXP§",  "_exp("),
            ("§TEN§",  "_ten("),           # 10^(x) = 10**x
            ("§PI§",   f"({PI})"),
        ]
        for ph, py in RESTORE:
            e = e.replace(ph, py)

        # ── 4. Factorial  n! ──────────────────────────────────────────────
        e = self._expand_factorials(e)

        # ── 5. percentage  x% → (x/100) ──────────────────────────────────
        e = re.sub(r'(\d+(?:\.\d*)?)\s*%', r'(\1/100)', e)

        # ── 6. Auto-close parentheses ─────────────────────────────────────
        opens  = e.count("(")
        closes = e.count(")")
        if opens > closes:
            e += ")" * (opens - closes)

        # ── 7. Safe eval ──────────────────────────────────────────────────
        safe_ns = {
            "__builtins__": {},
            "_sqrt":  math.sqrt,
            "_dsin":  lambda x: math.sin(math.radians(x)),
            "_dcos":  lambda x: math.cos(math.radians(x)),
            "_dtan":  lambda x: math.tan(math.radians(x)),
            "_dasin": lambda x: math.degrees(math.asin(x)),
            "_dacos": lambda x: math.degrees(math.acos(x)),
            "_datan": lambda x: math.degrees(math.atan(x)),
            "_sinh":  math.sinh,
            "_cosh":  math.cosh,
            "_tanh":  math.tanh,
            "_log10": math.log10,
            "_ln":    math.log,
            "_abs":   abs,
            # e^(x) and 10^(x) are now proper function calls
            "_exp":   lambda x: math.e ** x,
            "_ten":   lambda x: 10.0 ** x,
        }

        print(f"[eval] {e!r}")            # helpful for debugging
        result = eval(e, safe_ns)         # noqa: S307

        if isinstance(result, float):
            result = round(result, 10)
            if abs(result - round(result)) < 1e-9:
                result = int(round(result))
        return result

    # ── Factorial ─────────────────────────────────────────────────────────────
    def _expand_factorials(self, e: str) -> str:
        pattern = re.compile(r'(\d+)!')
        guard   = 0
        while '!' in e and guard < 30:
            m = pattern.search(e)
            if m:
                n   = int(m.group(1))
                val = self._factorial(n)
                e   = e[:m.start()] + str(val) + e[m.end():]
            else:
                e = e.replace('!', '', 1)
            guard += 1
        return e

    def _factorial(self, n: int) -> int:
        if n < 0:
            raise ValueError("factorial of negative number")
        r = 1
        for i in range(2, n + 1):
            r *= i
        return r

    # ─────────────────────────────────────────────────────────────────────────
    # Display
    # ─────────────────────────────────────────────────────────────────────────
    def _fmt(self, value) -> str:
        try:
            f = float(value)
            if f == int(f) and abs(f) < 1e15:
                return str(int(f))
            return f"{f:.10g}"
        except Exception:
            return str(value)

    def _update_display(self):
        # Show the user-facing expression unchanged (it already uses × ÷ etc.)
        self.expr_label.config(text=self.expression)

        text = self.current_input if self.current_input else "0"
        if self.expression == "Error":
            self.display.config(text="Error", fg="#ef5350")
            return
        try:
            f    = float(text.replace("π", str(math.pi)))
            text = self._fmt(f)
        except Exception:
            pass
        self.display.config(text=text, fg=COLORS["display_text"])


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    ScientificCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()