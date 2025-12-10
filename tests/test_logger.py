"""Tests for the logger module."""

import pytest
from unittest.mock import patch
from colorama import Fore, Style

from pymon.logger import log, Color


class TestColor:
    """Tests for Color class constants."""

    def test_green_color(self):
        """Should have green color defined."""
        assert Color.GREEN == Fore.GREEN

    def test_yellow_color(self):
        """Should have yellow bright color defined."""
        assert Color.YELLOW == Fore.YELLOW + Style.BRIGHT

    def test_red_color(self):
        """Should have red color defined."""
        assert Color.RED == Fore.RED

    def test_cyan_color(self):
        """Should have cyan color defined."""
        assert Color.CYAN == Fore.CYAN


class TestLog:
    """Tests for the log function."""

    def test_log_formats_message(self, capsys):
        """Should format message with pymon prefix."""
        log(Color.GREEN, "test message")
        
        captured = capsys.readouterr()
        assert "[pymon]" in captured.out
        assert "test message" in captured.out

    def test_log_includes_color(self, capsys):
        """Should include color codes in output."""
        log(Color.GREEN, "test")
        
        captured = capsys.readouterr()
        assert Fore.GREEN in captured.out

    def test_log_resets_style(self, capsys):
        """Should reset style after message."""
        log(Color.RED, "test")
        
        captured = capsys.readouterr()
        assert Style.RESET_ALL in captured.out

    def test_log_different_colors(self, capsys):
        """Should work with different colors."""
        log(Color.GREEN, "green")
        log(Color.YELLOW, "yellow")
        log(Color.RED, "red")
        log(Color.CYAN, "cyan")
        
        captured = capsys.readouterr()
        assert "green" in captured.out
        assert "yellow" in captured.out
        assert "red" in captured.out
        assert "cyan" in captured.out

    def test_log_empty_message(self, capsys):
        """Should handle empty message."""
        log(Color.GREEN, "")
        
        captured = capsys.readouterr()
        assert "[pymon]" in captured.out

