"""Tests for config file loading and merging."""

import json
import pytest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch, mock_open

from pymon.main import load_config, merge_config


class TestLoadConfig:
    """Tests for the load_config function."""

    def test_load_pymonrc(self, tmp_path, monkeypatch):
        """Should load config from .pymonrc file."""
        monkeypatch.chdir(tmp_path)

        config_data = {"watch": ["*.py", "*.json"], "debug": True}
        config_file = tmp_path / ".pymonrc"
        config_file.write_text(json.dumps(config_data))

        config, name = load_config()

        assert name == ".pymonrc"
        assert config == config_data

    def test_load_pymon_json(self, tmp_path, monkeypatch):
        """Should load config from pymon.json file."""
        monkeypatch.chdir(tmp_path)

        config_data = {"watch": ["src/*.py"], "ignore": ["*.log"]}
        config_file = tmp_path / "pymon.json"
        config_file.write_text(json.dumps(config_data))

        config, name = load_config()

        assert name == "pymon.json"
        assert config == config_data

    def test_pymonrc_takes_priority(self, tmp_path, monkeypatch):
        """Should prefer .pymonrc over pymon.json when both exist."""
        monkeypatch.chdir(tmp_path)

        pymonrc_data = {"watch": ["from_pymonrc"]}
        pymon_json_data = {"watch": ["from_pymon_json"]}

        (tmp_path / ".pymonrc").write_text(json.dumps(pymonrc_data))
        (tmp_path / "pymon.json").write_text(json.dumps(pymon_json_data))

        config, name = load_config()

        assert name == ".pymonrc"
        assert config["watch"] == ["from_pymonrc"]

    def test_no_config_file(self, tmp_path, monkeypatch):
        """Should return empty config when no config file exists."""
        monkeypatch.chdir(tmp_path)

        config, name = load_config()

        assert config == {}
        assert name is None

    def test_invalid_json(self, tmp_path, monkeypatch, capsys):
        """Should handle invalid JSON gracefully."""
        monkeypatch.chdir(tmp_path)

        config_file = tmp_path / ".pymonrc"
        config_file.write_text("{ invalid json }")

        config, name = load_config()

        assert config == {}
        assert name is None

    def test_empty_config_file(self, tmp_path, monkeypatch):
        """Should handle empty config object."""
        monkeypatch.chdir(tmp_path)

        config_file = tmp_path / ".pymonrc"
        config_file.write_text("{}")

        config, name = load_config()

        assert config == {}
        assert name == ".pymonrc"


class TestMergeConfig:
    """Tests for the merge_config function."""

    def create_args(self, **kwargs):
        """Helper to create a Namespace with default values."""
        defaults = {
            "command": "app.py",
            "watch": None,
            "ignore": [],
            "debug": False,
            "clean": False,
            "exec": False,
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def test_config_sets_watch(self):
        """Config should set watch patterns when CLI doesn't specify."""
        args = self.create_args(watch=None)
        config = {"watch": ["src/*.py", "*.json"]}

        result = merge_config(args, config)

        assert result.watch == ["src/*.py", "*.json"]

    def test_cli_watch_overrides_config(self):
        """CLI watch should override config watch."""
        args = self.create_args(watch=["cli/*.py"])
        config = {"watch": ["config/*.py"]}

        result = merge_config(args, config)

        assert result.watch == ["cli/*.py"]

    def test_default_watch_when_no_config(self):
        """Should use default *.py when no CLI or config watch."""
        args = self.create_args(watch=None)
        config = {}

        result = merge_config(args, config)

        assert result.watch == ["*.py"]

    def test_config_sets_ignore(self):
        """Config should set ignore patterns when CLI doesn't specify."""
        args = self.create_args(ignore=[])
        config = {"ignore": ["*.log", "*__pycache__*"]}

        result = merge_config(args, config)

        assert result.ignore == ["*.log", "*__pycache__*"]

    def test_cli_ignore_overrides_config(self):
        """CLI ignore should override config ignore."""
        args = self.create_args(ignore=["cli_ignore"])
        config = {"ignore": ["config_ignore"]}

        result = merge_config(args, config)

        assert result.ignore == ["cli_ignore"]

    def test_config_sets_debug(self):
        """Config should set debug when CLI doesn't specify."""
        args = self.create_args(debug=False)
        config = {"debug": True}

        result = merge_config(args, config)

        assert result.debug is True

    def test_cli_debug_overrides_config(self):
        """CLI debug should override config debug."""
        args = self.create_args(debug=True)
        config = {"debug": False}

        result = merge_config(args, config)

        assert result.debug is True

    def test_config_sets_clean(self):
        """Config should set clean when CLI doesn't specify."""
        args = self.create_args(clean=False)
        config = {"clean": True}

        result = merge_config(args, config)

        assert result.clean is True

    def test_config_sets_exec(self):
        """Config should set exec when CLI doesn't specify."""
        args = self.create_args(exec=False)
        config = {"exec": True}

        result = merge_config(args, config)

        assert result.exec is True

    def test_empty_config_uses_defaults(self):
        """Empty config should result in default values."""
        args = self.create_args()
        config = {}

        result = merge_config(args, config)

        assert result.watch == ["*.py"]
        assert result.ignore == []
        assert result.debug is False
        assert result.clean is False
        assert result.exec is False

    def test_partial_config(self):
        """Should handle partial config with some fields."""
        args = self.create_args()
        config = {"watch": ["*.py", "*.json"], "debug": True}

        result = merge_config(args, config)

        assert result.watch == ["*.py", "*.json"]
        assert result.debug is True
        assert result.ignore == []
        assert result.clean is False
        assert result.exec is False
