"""
Advanced Calculator Application with GUI.

This module provides a professional calculator with GUI built using tkinter.
It follows industry standards with type hints, error handling, and clean architecture.
"""

import tkinter as tk
from tkinter import ttk
import re
import logging
from typing import Optional, Dict, Callable, List, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CalculatorError(Exception):
    """Custom exception for calculator-related errors."""
    pass


class OperatorType(Enum):
    """Enumeration for calculator operators."""
    ADD = '+'
    SUBTRACT = '-'
    MULTIPLY = '×'
    DIVIDE = '÷'
    PERCENTAGE = '%'
    EQUALS = '='
    CLEAR = 'C'
    TOGGLE_SIGN = '±'


@dataclass
class ThemeConfig:
    """Configuration for calculator theme colors."""
    background: str = '#2C3E50'
    display: str = '#34495E'
    button_normal: str = '#3498DB'
    button_hover: str = '#2980B9'
    text_primary: str = '#FFFFFF'
    text_secondary: str = '#ECF0F1'


@dataclass
class WindowConfig:
    """Configuration for calculator window."""
    title: str = "Advanced Calculator"
    width: int = 400
    height: int = 600
    resizable: bool = False


class Calculator:
    """Professional calculator application with GUI."""

    # Constants
    MAX_EXPRESSION_LENGTH: int = 20
    DISPLAY_FONT: Tuple[str, int, str] = ('Arial', 24, 'bold')
    BUTTON_FONT: Tuple[str, int, str] = ('Arial', 18, 'bold')

    def __init__(self, master: tk.Tk) -> None:
        """
        Initialize the calculator application.

        Args:
            master: Root tkinter window

        Raises:
            CalculatorError: If initialization fails
        """
        try:
            self.master = master
            self.theme = ThemeConfig()
            self.window_config = WindowConfig()
            self.expression: str = ""
            self.equation: tk.StringVar = tk.StringVar()

            self._setup_window()
            self._create_ui()
            self._setup_keyboard_bindings()

            logger.info("Calculator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize calculator: {e}")
            raise CalculatorError(f"Initialization error: {e}") from e

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.master.title(self.window_config.title)
        self.master.geometry(
            f"{self.window_config.width}x{self.window_config.height}"
        )
        self.master.resizable(
            self.window_config.resizable,
            self.window_config.resizable
        )
        self.master.configure(bg=self.theme.background)

    def _setup_keyboard_bindings(self) -> None:
        """Set up keyboard event bindings."""
        self.master.bind('<Key>', self._handle_keypress)
        self.master.bind('<Return>', lambda e: self._button_click('='))
        self.master.bind('<BackSpace>', self._handle_backspace)
        self.master.bind('<Escape>', lambda e: self._clear())

    def _handle_keypress(self, event: tk.Event) -> str:
        """
        Handle keyboard input events.

        Args:
            event: Tkinter event object

        Returns:
            'break' to prevent further event propagation
        """
        key = event.char

        if key in '0123456789.+-*/%':
            self._press(key)

        return 'break'

    def _handle_backspace(self, event: tk.Event) -> None:
        """
        Handle backspace key press.

        Args:
            event: Tkinter event object
        """
        if self.expression:
            self.expression = self.expression[:-1]
            self.equation.set(self.expression or '0')

    def _create_ui(self) -> None:
        """Create the user interface components."""
        display_frame = self._create_display()
        display_frame.pack(pady=10, padx=10, fill='x')

        buttons_frame = self._create_buttons()
        buttons_frame.pack(pady=10, padx=10, expand=True, fill='both')

    def _create_display(self) -> tk.Frame:
        """
        Create the display frame.

        Returns:
            Frame containing the calculator display
        """
        display_frame = tk.Frame(self.master, bg=self.theme.background)

        result_display = tk.Entry(
            display_frame,
            textvariable=self.equation,
            font=self.DISPLAY_FONT,
            justify='right',
            bg=self.theme.display,
            fg=self.theme.text_primary,
            borderwidth=0,
            readonlybackground=self.theme.display,
            state='readonly'
        )
        result_display.pack(fill='x', expand=True)

        return display_frame

    def _create_buttons(self) -> tk.Frame:
        """
        Create the button grid.

        Returns:
            Frame containing calculator buttons
        """
        buttons_frame = tk.Frame(self.master, bg=self.theme.background)

        button_layout: List[List[str]] = [
            ['C', '±', '%', '÷'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=']
        ]

        for row, button_row in enumerate(button_layout):
            for col, button_text in enumerate(button_row):
                button = self._create_button(buttons_frame, button_text, row, col)
                button.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)

        for i in range(5):
            buttons_frame.grid_rowconfigure(i, weight=1)
            buttons_frame.grid_columnconfigure(i, weight=1)

        return buttons_frame
    def _create_button(
        self,
        parent: tk.Frame,
        text: str,
        row: int,
        col: int
    ) -> tk.Button:
        """
        Create a styled button.

        Args:
            parent: Parent widget
            text: Button text/label
            row: Grid row position
            col: Grid column position

        Returns:
            Configured Button widget
        """
        button_style: Dict[str, any] = {
            'text': text,
            'font': self.BUTTON_FONT,
            'bg': self.theme.button_normal,
            'fg': self.theme.text_primary,
            'activebackground': self.theme.button_hover,
            'relief': 'raised',
            'bd': 1
        }

        button = tk.Button(
            parent,
            **button_style,
            command=lambda t=text: self._button_click(t)
        )

        # Add hover effects
        button.bind(
            '<Enter>',
            lambda e, b=button: b.configure(bg=self.theme.button_hover)
        )
        button.bind(
            '<Leave>',
            lambda e, b=button: b.configure(bg=self.theme.button_normal)
        )

        return button

    def _button_click(self, value: str) -> None:
        """
        Handle button click events.

        Args:
            value: The button value/operator
        """
        try:
            if value == 'C':
                self._clear()
            elif value == '=':
                self._calculate()
            elif value == '±':
                self._toggle_sign()
            elif value == '%':
                self._percentage()
            else:
                self._press(value)
        except CalculatorError as e:
            logger.error(f"Calculator error: {e}")
            self.equation.set("Error")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.equation.set("Error")

    def _press(self, value: str) -> None:
        """
        Add a character to the expression.

        Args:
            value: Character to add

        Raises:
            CalculatorError: If input validation fails
        """
        if len(self.expression) >= self.MAX_EXPRESSION_LENGTH:
            logger.warning("Expression exceeds maximum length")
            raise CalculatorError("Expression too long")

        self.expression += str(value)
        self.equation.set(self.expression)

    def _clear(self) -> None:
        """Clear the calculator display and expression."""
        self.expression = ""
        self.equation.set("0")
        logger.debug("Calculator cleared")

    def _calculate(self) -> None:
        """
        Calculate and display the result.

        Raises:
            CalculatorError: If expression is invalid or calculation fails
        """
        try:
            if not self.expression:
                raise CalculatorError("No expression to calculate")

            # Replace display symbols with Python operators
            expression = self.expression.replace('÷', '/').replace('×', '*')

            # Validate expression format
            if not self._validate_expression(expression):
                raise CalculatorError("Invalid expression format")

            # Evaluate using eval with restricted namespace for safety
            result = self._safe_eval(expression)

            # Format result
            formatted_result = self._format_result(result)
            self.equation.set(formatted_result)
            self.expression = formatted_result

            logger.info(f"Calculation: {expression} = {formatted_result}")

        except (ValueError, ZeroDivisionError, SyntaxError) as e:
            logger.error(f"Calculation error: {e}")
            raise CalculatorError(f"Calculation failed: {e}") from e

    def _validate_expression(self, expression: str) -> bool:
        """
        Validate the mathematical expression.

        Args:
            expression: Expression to validate

        Returns:
            True if valid, False otherwise
        """
        # Allow digits, operators, decimal point, and parentheses
        pattern = r'^[\d+\-*/.() ]+$'
        return bool(re.match(pattern, expression))

    def _safe_eval(self, expression: str) -> float:
        """
        Safely evaluate a mathematical expression.

        Args:
            expression: Expression to evaluate

        Returns:
            Calculated result

        Raises:
            CalculatorError: If evaluation fails
        """
        try:
            # Use restricted namespace for security
            result = eval(expression, {"__builtins__": {}}, {})
            if not isinstance(result, (int, float)):
                raise CalculatorError("Invalid result type")
            return float(result)
        except Exception as e:
            raise CalculatorError(f"Evaluation error: {e}") from e

    @staticmethod
    def _format_result(result: float) -> str:
        """
        Format the calculation result.

        Args:
            result: Numeric result

        Returns:
            Formatted result string
        """
        # Round to avoid floating-point precision issues
        rounded = round(result, 10)

        # Remove unnecessary decimal places
        if rounded == int(rounded):
            return str(int(rounded))
        else:
            return str(rounded)

    def _toggle_sign(self) -> None:
        """Toggle the sign of the current expression."""
        if not self.expression:
            return

        if self.expression[0] == '-':
            self.expression = self.expression[1:]
        else:
            self.expression = '-' + self.expression

        self.equation.set(self.expression)
        logger.debug(f"Sign toggled: {self.expression}")

    def _percentage(self) -> None:
        """Convert the current expression to a percentage."""
        try:
            if not self.expression:
                raise CalculatorError("No value to convert")

            result = float(self.expression) / 100
            formatted_result = self._format_result(result)
            self.equation.set(formatted_result)
            self.expression = formatted_result

            logger.info(f"Percentage calculation: {self.expression}")

        except ValueError as e:
            logger.error(f"Percentage error: {e}")
            raise CalculatorError("Invalid value for percentage") from e


def main() -> None:
    """Main entry point for the calculator application."""
    try:
        root = tk.Tk()
        root.title("Advanced Calculator")

        # Try to set icon if available
        try:
            root.iconbitmap('calculator_icon.ico')
        except (tk.TclError, FileNotFoundError):
            logger.debug("Icon file not found, using default")

        app = Calculator(root)
        root.mainloop()

    except CalculatorError as e:
        logger.error(f"Fatal calculator error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        raise


if __name__ == "__main__":
    main()