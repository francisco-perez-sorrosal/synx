"""Tests for the main CLI application."""

from typer.testing import CliRunner

from synx.config import AppConfig, LogLevel, load_config
from synx.logger import LogConfig
from synx.main import app


class TestMain:
    """Test cases for main CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_app_help(self):
        """Test that the CLI help is displayed correctly."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Synx - Synapse Executor" in result.output

    def test_version_command(self):
        """Test the version command."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Synx v0.0.1" in result.output

    def test_main_command_default(self):
        """Test main command with default options."""
        result = self.runner.invoke(app, ["main"])
        assert result.exit_code == 0
        assert "Welcome to Synx" in result.output

    def test_main_command_with_debug(self):
        """Test main command with debug flag."""
        result = self.runner.invoke(app, ["main", "--debug"])
        assert result.exit_code == 0
        assert "Debug Mode: True" in result.output

    def test_main_command_with_log_level(self):
        """Test main command with custom log level."""
        result = self.runner.invoke(app, ["main", "--log-level", "DEBUG"])
        assert result.exit_code == 0
        assert "Log Level: DEBUG" in result.output


class TestConfig:
    """Test cases for configuration loading."""

    def test_load_config_default(self):
        """Test loading default configuration."""
        config = load_config()
        assert config.debug is False
        assert config.log_level == LogLevel.INFO

    def test_app_config_validation(self):
        """Test AppConfig Pydantic validation."""
        # Valid config
        config = AppConfig(debug=True, log_level=LogLevel.DEBUG)
        assert config.debug is True
        assert config.log_level == LogLevel.DEBUG

        # Test string output method
        config_str = str(config)
        assert "AppConfig(debug=True, log_level=LogLevel.DEBUG" in config_str

    def test_log_config_validation(self):
        """Test LogConfig Pydantic validation."""
        # Valid config
        config = LogConfig(level=LogLevel.DEBUG)
        assert config.level == LogLevel.DEBUG

        # Test string output method
        config_str = str(config)
        assert "LogConfig(level=LogLevel.DEBUG" in config_str
