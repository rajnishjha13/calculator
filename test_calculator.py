"""
Unit tests for the Calculator application.

Tests cover core calculation logic, input validation, and error handling.
"""

import unittest
from unittest.mock import Mock, patch
import tkinter as tk
from Calculator import Calculator, CalculatorError, ThemeConfig, WindowConfig


class TestCalculatorExpression(unittest.TestCase):
    """Test cases for expression validation and calculation."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window
        self.calc = Calculator(self.root)

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.root.destroy()

    def test_valid_expression_format(self) -> None:
        """Test validation of valid mathematical expressions."""
        valid_expressions = [
            "5+3",
            "10-2",
            "4*5",
            "20/4",
            "1.5+2.5",
            "(5+3)*2"
        ]
        for expr in valid_expressions:
            with self.subTest(expr=expr):
                self.assertTrue(self.calc._validate_expression(expr))

    def test_invalid_expression_format(self) -> None:
        """Test rejection of invalid expressions."""
        invalid_expressions = [
            "abc",
            "5&3",
            "!10"
        ]
        for expr in invalid_expressions:
            with self.subTest(expr=expr):
                self.assertFalse(self.calc._validate_expression(expr))

    def test_safe_eval_addition(self) -> None:
        """Test safe evaluation of addition."""
        result = self.calc._safe_eval("5+3")
        self.assertEqual(result, 8.0)

    def test_safe_eval_subtraction(self) -> None:
        """Test safe evaluation of subtraction."""
        result = self.calc._safe_eval("10-3")
        self.assertEqual(result, 7.0)

    def test_safe_eval_multiplication(self) -> None:
        """Test safe evaluation of multiplication."""
        result = self.calc._safe_eval("4*5")
        self.assertEqual(result, 20.0)

    def test_safe_eval_division(self) -> None:
        """Test safe evaluation of division."""
        result = self.calc._safe_eval("20/4")
        self.assertEqual(result, 5.0)

    def test_safe_eval_division_by_zero(self) -> None:
        """Test that division by zero raises an error."""
        with self.assertRaises(CalculatorError):
            self.calc._safe_eval("5/0")

    def test_safe_eval_complex_expression(self) -> None:
        """Test safe evaluation of complex expressions."""
        result = self.calc._safe_eval("(5+3)*2")
        self.assertEqual(result, 16.0)

    def test_format_result_integer(self) -> None:
        """Test formatting of integer results."""
        result = self.calc._format_result(5.0)
        self.assertEqual(result, "5")

    def test_format_result_float(self) -> None:
        """Test formatting of float results."""
        result = self.calc._format_result(5.5)
        self.assertEqual(result, "5.5")

    def test_format_result_precision(self) -> None:
        """Test precision handling in result formatting."""
        # Test that floating-point precision issues are handled
        result = self.calc._format_result(0.1 + 0.2)
        self.assertIn(result, ["0.3", "0.30000000000000004"])


class TestCalculatorState(unittest.TestCase):
    """Test cases for calculator state management."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        self.calc = Calculator(self.root)

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.root.destroy()

    def test_clear_resets_state(self) -> None:
        """Test that clear resets the expression."""
        self.calc.expression = "123"
        self.calc._clear()
        self.assertEqual(self.calc.expression, "")
        self.assertEqual(self.calc.equation.get(), "0")

    def test_toggle_sign_negative(self) -> None:
        """Test toggling sign on positive number."""
        self.calc.expression = "5"
        self.calc._toggle_sign()
        self.assertEqual(self.calc.expression, "-5")

    def test_toggle_sign_positive(self) -> None:
        """Test toggling sign on negative number."""
        self.calc.expression = "-5"
        self.calc._toggle_sign()
        self.assertEqual(self.calc.expression, "5")

    def test_percentage_conversion(self) -> None:
        """Test percentage conversion."""
        self.calc.expression = "50"
        self.calc._percentage()
        self.assertEqual(self.calc.expression, "0.5")

    def test_press_adds_character(self) -> None:
        """Test that press adds character to expression."""
        self.calc._press("5")
        self.assertEqual(self.calc.expression, "5")
        self.calc._press("+")
        self.assertEqual(self.calc.expression, "5+")

    def test_press_respects_max_length(self) -> None:
        """Test that press respects maximum expression length."""
        self.calc.expression = "1" * 20
        with self.assertRaises(CalculatorError):
            self.calc._press("0")


class TestCalculatorUI(unittest.TestCase):
    """Test cases for UI components."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        self.calc = Calculator(self.root)

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.root.destroy()

    def test_theme_config_initialization(self) -> None:
        """Test theme configuration is properly initialized."""
        self.assertIsInstance(self.calc.theme, ThemeConfig)
        self.assertEqual(self.calc.theme.background, '#2C3E50')
        self.assertEqual(self.calc.theme.display, '#34495E')

    def test_window_config_initialization(self) -> None:
        """Test window configuration is properly initialized."""
        self.assertIsInstance(self.calc.window_config, WindowConfig)
        self.assertEqual(self.calc.window_config.width, 400)
        self.assertEqual(self.calc.window_config.height, 600)
        self.assertEqual(self.calc.window_config.resizable, False)


class TestCalculatorIntegration(unittest.TestCase):
    """Integration tests for calculator functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        self.calc = Calculator(self.root)

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.root.destroy()

    def test_simple_calculation_workflow(self) -> None:
        """Test a simple calculation workflow."""
        self.calc._press("5")
        self.calc._press("+")
        self.calc._press("3")
        self.calc._calculate()
        self.assertEqual(self.calc.expression, "8")

    def test_calculation_with_clear(self) -> None:
        """Test calculation followed by clear."""
        self.calc._press("5")
        self.calc._press("+")
        self.calc._press("3")
        self.calc._calculate()
        self.assertEqual(self.calc.expression, "8")
        self.calc._clear()
        self.assertEqual(self.calc.expression, "")

    def test_consecutive_calculations(self) -> None:
        """Test multiple consecutive calculations."""
        # First calculation
        self.calc._press("1")
        self.calc._press("0")
        self.calc._press("/")
        self.calc._press("2")
        self.calc._calculate()
        self.assertEqual(self.calc.expression, "5")

        # Second calculation using result
        self.calc._press("+")
        self.calc._press("3")
        self.calc._calculate()
        self.assertEqual(self.calc.expression, "8")


if __name__ == "__main__":
    unittest.main()
