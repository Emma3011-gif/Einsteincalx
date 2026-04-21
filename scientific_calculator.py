import tkinter as tk
from tkinter import font
import math
from functools import partial

class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.geometry("420x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#1E1E2E")

        # Colors - Updated dark theme
        self.colors = {
            "bg": "#1a1a1a",
            "display_bg": "#1a1a1a",
            "display_text": "#FFFFFF",
            "display_expr": "#aaaaaa",
            "function": "#2a2a2a",      # Dark function buttons (scientific)
            "operator": "#3d3d3d",      # Medium gray (operators, parentheses, memory)
            "number": "#4a4a4a",        # Numeric buttons (lighter)
            "del": "#e53935",            # DEL - vivid red
            "ac": "#43a047",            # AC - vivid green
            "nav": "#2a2a2a",           # Navigation buttons
        }

        # State variables
        self.expression = ""
        self.current_input = ""
        self.memory = 0
        self.last_result = 0
        self.angle_mode = "degrees"

        # Setup UI
        self.create_display()
        self.create_buttons()

    def create_display(self):
        # Container frame for display area
        display_frame = tk.Frame(self.root, bg=self.colors["display_bg"])
        display_frame.grid(row=0, column=0, columnspan=6, sticky="ew", padx=12, pady=(20, 10))
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_rowconfigure(1, weight=1)

        # Expression display (smaller, gray, above main)
        self.expr_label = tk.Label(
            display_frame,
            text="",
            font=("Segoe UI", 13, "normal"),
            bg=self.colors["display_bg"],
            fg=self.colors["display_expr"],
            anchor="e",
            padx=10,
            pady=(10, 5)
        )
        self.expr_label.grid(row=0, column=0, sticky="ew")

        # Cursor label (blinking)
        self.cursor_label = tk.Label(
            display_frame,
            text="|",
            font=("Segoe UI", 13, "normal"),
            bg=self.colors["display_bg"],
            fg=self.colors["display_expr"],
            pady=(10, 5)
        )
        self.cursor_label.grid(row=0, column=1, sticky="w")
        self.blink_cursor()

        # Main display (large result)
        self.display = tk.Label(
            display_frame,
            text="0",
            font=("Segoe UI", 52, "bold"),
            bg=self.colors["display_bg"],
            fg=self.colors["display_text"],
            anchor="e",
            padx=10,
            pady=(5, 15)
        )
        self.display.grid(row=1, column=0, columnspan=2, sticky="ew")

    def blink_cursor(self):
        """Blink the cursor"""
        current = self.cursor_label.cget("text")
        self.cursor_label.config(text="" if current == "|" else "|")
        self.root.after(500, self.blink_cursor)

    def create_buttons(self):
        # Button layout with new design - includes navigation row
        buttons = [
            # Row 1 - Navigation (cursor buttons)
            ("◀", 1, 0, "nav"), ("▲", 1, 1, "nav"), ("▼", 1, 2, "nav"),
            ("▶", 1, 3, "nav"), ("⏮", 1, 4, "nav"), ("⏭", 1, 5, "nav"),

            # Row 2 - Scientific functions (dark function buttons)
            ("sin", 2, 0, "function"), ("cos", 2, 1, "function"),
            ("tan", 2, 2, "function"), ("log", 2, 3, "function"),
            ("ln", 2, 4, "function"), ("π", 2, 5, "function"),

            # Row 3 - More scientific
            ("hyp", 3, 0, "function"), ("int", 3, 1, "function"),
            ("Mode", 3, 2, "function"), ("eng", 3, 3, "function"),
            ("(", 3, 4, "operator"), (")", 3, 5, "operator"),

            # Row 4 - Memory and operators
            ("MC", 4, 0, "operator"), ("MR", 4, 1, "operator"),
            ("M+", 4, 2, "operator"), ("M-", 4, 3, "operator"),
            ("%", 4, 4, "operator"), ("AC", 4, 5, "ac"),

            # Row 5
            ("7", 5, 0, "number"), ("8", 5, 1, "number"), ("9", 5, 2, "number"),
            ("DEL", 5, 3, "del"), ("abs", 5, 4, "operator"), ("n!", 5, 5, "operator"),

            # Row 6
            ("4", 6, 0, "number"), ("5", 6, 1, "number"), ("6", 6, 2, "number"),
            ("×", 6, 3, "number"), ("÷", 6, 4, "number"), ("+", 6, 5, "number"),

            # Row 7
            ("1", 7, 0, "number"), ("2", 7, 1, "number"), ("3", 7, 2, "number"),
            ("-", 7, 3, "number"), ("^", 7, 4, "number"), ("=", 7, 5, "number"),

            # Row 8
            ("00", 8, 0, "operator"), ("0", 8, 1, "number"), (".", 8, 2, "number"),
            ("ANS", 8, 3, "operator"), ("√", 8, 4, "function"), ("^2", 8, 5, "function"),
        ]

        for btn_text, row, col, color_type in buttons:
            self.create_button(btn_text, row, col, color_type)

    def create_button(self, text, row, col, color_type, span=1):
        bg_color = self.colors.get(color_type, self.colors["number"])

        btn = tk.Button(
            self.root,
            text=text,
            font=("Arial", 14, "bold"),
            bg=bg_color,
            fg="white",
            activebackground=self.lighten_color(bg_color, 0.15),
            activeforeground="white",
            relief="flat",
            bd=0,
            pady=8,
            command=partial(self.on_button_click, text)
        )

        btn.grid(row=row, column=col, columnspan=span, sticky="nsew", padx=3, pady=3)

        # Bind hover events
        btn.bind("<Enter>", lambda e: btn.configure(bg=self.lighten_color(bg_color, 0.15)))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg_color))

    def lighten_color(self, hex_color, percent):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(min(255, int(c + (255 - c) * percent)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*new_rgb)

    def on_button_click(self, text):
        if text == "AC":
            self.clear_all()
        elif text == "DEL":
            self.delete_last()
        elif text == "=":
            self.calculate()
        elif text == "×":
            self.add_operator("*")
        elif text == "÷":
            self.add_operator("/")
        elif text == "√":
            self.add_function("sqrt(")
        elif text == "^":
            self.add_operator("**")
        elif text == "x²":
            self.add_operator("**2")
        elif text == "%":
            self.add_operator("/100*")
        elif text == "sin":
            self.add_function("sin(")
        elif text == "cos":
            self.add_function("cos(")
        elif text == "tan":
            self.add_function("tan(")
        elif text == "asin":
            self.add_function("asin(")
        elif text == "acos":
            self.add_function("acos(")
        elif text == "atan":
            self.add_function("atan(")
        elif text == "sinh":
            self.add_function("sinh(")
        elif text == "cosh":
            self.add_function("cosh(")
        elif text == "tanh":
            self.add_function("tanh(")
        elif text == "log":
            self.add_function("log10(")
        elif text == "ln":
            self.add_function("log(")
        elif text == "!":
            self.add_operator("!")
        elif text == "π":
            self.add_number(str(math.pi))
        elif text == "e":
            self.add_number(str(math.e))
        elif text == "ANS":
            self.add_number(str(self.last_result))
        elif text == "MC":
            self.memory = 0
        elif text == "MR":
            self.add_number(str(self.memory))
        elif text == "M+":
            try:
                current = float(self.current_input) if self.current_input else self.last_result
                self.memory += current
            except:
                pass
        else:
            self.add_number(text)

        self.update_display()

    def add_number(self, num):
        if self.current_input == "0" and num != ".":
            self.current_input = num
        else:
            self.current_input += num
        self.expression += num

    def add_operator(self, op):
        if op == "!":
            if self.current_input:
                self.expression += "!"
                self.current_input = ""
        else:
            self.expression += op
            self.current_input = ""

    def add_function(self, func):
        self.expression += func
        self.current_input = ""

    def delete_last(self):
        if self.expression:
            # Check if we need to remove a function name
            functions = ["sin(", "cos(", "tan(", "log10(", "log(", "sqrt(", "asin(", "acos(", "atan(", "sinh(", "cosh(", "tanh("]
            for func in functions:
                if self.expression.endswith(func):
                    self.expression = self.expression[:-len(func)]
                    self.current_input = ""
                    return
            self.expression = self.expression[:-1]
            # Try to reconstruct current_input
            if self.expression:
                parts = self.expression.replace("+", " ").replace("-", " ").replace("*", " ").replace("/", " ").replace("**", " ").split()
                if parts:
                    self.current_input = parts[-1]
                else:
                    self.current_input = ""
            else:
                self.current_input = ""

    def clear_all(self):
        self.expression = ""
        self.current_input = ""

    def calculate(self):
        if not self.expression:
            return

        try:
            # Prepare expression for evaluation
            expr = self.expression

            # Replace display operators with Python operators
            expr = expr.replace("×", "*").replace("÷", "/")

            # Handle factorial
            if "!" in expr:
                parts = expr.split("!")
                new_parts = []
                for i, part in enumerate(parts[:-1]):
                    if part:
                        # Get the number before !
                        num = eval(part)
                        new_parts.append(str(self.factorial(int(num))))
                new_parts.append(parts[-1])
                expr = "".join(new_parts)

            # Handle trigonometric functions (convert to radians if needed)
            # Since we'll evaluate in degrees, we need to convert
            trig_funcs = ["sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh"]

            # Add math. prefix and convert degrees to radians for trig functions
            for func in trig_funcs:
                if func + "(" in expr:
                    if func in ["asin", "acos", "atan"]:
                        # Inverse trig: result is in radians, convert to degrees
                        expr = expr.replace(func + "(", f"math.degrees(math.{func}(") + ")"
                    else:
                        # Forward trig: input is in degrees, convert to radians
                        expr = expr.replace(func + "(", f"math.{func}(math.radians(") + ")"

            # Handle sqrt
            expr = expr.replace("sqrt(", "math.sqrt(")

            # Handle log10
            expr = expr.replace("log10(", "math.log10(")

            # Evaluate
            result = eval(expr)

            # Round to avoid floating point errors
            if isinstance(result, float):
                result = round(result, 10)
                if result == int(result):
                    result = int(result)

            self.last_result = result
            self.expression = str(result)
            self.current_input = str(result)

        except Exception as e:
            self.expression = "Error"
            self.current_input = ""
            self.last_result = 0

    def factorial(self, n):
        if n < 0:
            return float('nan')
        if n == 0 or n == 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    def update_display(self):
        # Update expression label
        display_expr = self.expression
        display_expr = display_expr.replace("**", "^")
        display_expr = display_expr.replace("*", "×")
        display_expr = display_expr.replace("/", "÷")

        self.expr_label.config(text=display_expr)

        # Update main display
        display_text = self.current_input if self.current_input else "0"
        if display_text == "Error":
            self.display.config(text="Error")
        else:
            # Format the number nicely
            try:
                if display_text and display_text != "Error":
                    num = float(display_text)
                    if num == int(num):
                        display_text = str(int(num))
            except:
                pass
            self.display.config(text=display_text)

def main():
    root = tk.Tk()
    app = ScientificCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()