"""Tests for the MCP server functionality."""

import json

from synx.mcp_server import run


class TestMCPServer:
    """Test cases for MCP server functionality."""

    def test_run_tool_simple_code(self):
        """Test running simple Python code."""
        code = "result = 2 + 2"
        result = run(code)

        # Parse the JSON result
        parsed_result = json.loads(result)

        assert parsed_result["success"] is True
        assert parsed_result["stdout"] == ""
        assert parsed_result["stderr"] == ""
        assert parsed_result["variables"]["result"] == 4
        assert parsed_result["execution_count"] == 1

    def test_run_tool_with_output(self):
        """Test running code that produces output."""
        code = "print('Hello, World!')"
        result = run(code)

        # Parse the JSON result
        parsed_result = json.loads(result)

        assert parsed_result["success"] is True
        assert parsed_result["stdout"] == "Hello, World!\n"
        assert parsed_result["stderr"] == ""
        assert parsed_result["execution_count"] == 1

    def test_run_tool_with_error(self):
        """Test running code that produces an error."""
        code = "1 / 0"
        result = run(code)

        # Parse the JSON result
        parsed_result = json.loads(result)

        assert parsed_result["success"] is False
        assert "division by zero" in parsed_result["error"]
        assert parsed_result["execution_count"] == 1

    def test_run_tool_with_session_id(self):
        """Test running code with session ID for state persistence."""
        session_id = "test_session"

        # First execution
        code1 = "x = 10"
        result1 = run(code1, session_id)
        parsed_result1 = json.loads(result1)

        assert parsed_result1["success"] is True
        assert parsed_result1["variables"]["x"] == 10
        assert parsed_result1["session_id"] == session_id
        assert parsed_result1["execution_count"] == 1

        # Second execution in same session
        code2 = "y = x * 2"
        result2 = run(code2, session_id)
        parsed_result2 = json.loads(result2)

        assert parsed_result2["success"] is True
        assert parsed_result2["variables"]["y"] == 20
        assert parsed_result2["session_id"] == session_id
        assert parsed_result2["execution_count"] == 2

    def test_run_tool_without_session_id(self):
        """Test running code without session ID."""
        code = "z = 42"
        result = run(code)

        # Parse the JSON result
        parsed_result = json.loads(result)

        assert parsed_result["success"] is True
        assert parsed_result["variables"]["z"] == 42
        assert parsed_result["session_id"] is None
        assert parsed_result["execution_count"] == 1

    def test_run_tool_complex_code(self):
        """Test running more complex Python code."""
        code = """
import math
numbers = [1, 2, 3, 4, 5]
squared = [x**2 for x in numbers]
total = sum(squared)
sqrt_total = math.sqrt(total)
print(f"Sum of squares: {total}")
print(f"Square root: {sqrt_total}")
"""
        result = run(code)

        # Parse the JSON result
        parsed_result = json.loads(result)

        assert parsed_result["success"] is True
        assert "Sum of squares: 55" in parsed_result["stdout"]
        assert "Square root: 7.416" in parsed_result["stdout"]
        assert parsed_result["variables"]["total"] == 55
        assert abs(parsed_result["variables"]["sqrt_total"] - 7.416) < 0.1
