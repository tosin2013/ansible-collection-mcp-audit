# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later OR BSD-2-Clause

"""
MCP Reporter

This module_utils can be used under either:
- GPL-3.0-or-later (for use in GPL collections)
- BSD-2-Clause (for use in permissively licensed collections)

Provides reporting functions for MCP test results in JSON and YAML formats.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class MCPReporter:
    """
    Reporter for MCP test results and execution data.

    Provides methods to format and export test results in various formats
    (JSON, YAML) following the structure defined in ADR-0006.
    """

    @staticmethod
    def create_module_result(
        success: bool,
        status: str,
        response: Optional[Any] = None,
        execution_time: float = 0.0,
        error: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        changed: bool = False,
    ) -> dict[str, Any]:
        """
        Create a standard module result structure.

        Args:
            success: Whether the operation succeeded
            status: Status string ('ok', 'failed', 'skipped', etc.)
            response: The actual response from the MCP server
            execution_time: Execution time in seconds
            error: Error message if operation failed
            metadata: Additional metadata dictionary
            changed: Whether the operation changed anything

        Returns:
            Dictionary with standardized module result structure
        """
        result = {
            "success": success,
            "changed": changed,
            "status": status,
            "response": response,
            "execution_time": round(execution_time, 3),
            "error": error,
            "metadata": metadata or {},
        }

        # Add timestamp if not in metadata
        if "timestamp" not in result["metadata"]:
            result["metadata"]["timestamp"] = datetime.utcnow().isoformat() + "Z"

        return result

    @staticmethod
    def create_test_report(
        summary: dict[str, int],
        tests: list[dict[str, Any]],
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Create a test suite report structure.

        Args:
            summary: Summary statistics (total_tests, passed, failed, skipped)
            tests: List of individual test results
            metadata: Additional metadata about the test run

        Returns:
            Dictionary with test report structure
        """
        report = {
            "summary": {
                "total_tests": summary.get("total_tests", 0),
                "passed": summary.get("passed", 0),
                "failed": summary.get("failed", 0),
                "skipped": summary.get("skipped", 0),
                "success_rate": 0.0,
                "total_duration": sum(test.get("execution_time", 0) for test in tests),
            },
            "tests": tests,
            "metadata": metadata or {},
        }

        # Calculate success rate
        total = report["summary"]["total_tests"]
        if total > 0:
            passed = report["summary"]["passed"]
            report["summary"]["success_rate"] = round((passed / total) * 100, 2)

        # Add timestamp if not in metadata
        if "timestamp" not in report["metadata"]:
            report["metadata"]["timestamp"] = datetime.utcnow().isoformat() + "Z"

        return report

    @staticmethod
    def format_tool_result(
        tool_name: str,
        success: bool,
        response: Any,
        execution_time: float,
        arguments: Optional[dict[str, Any]] = None,
        expected_result: Optional[Any] = None,
        validation_result: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Format a tool test result.

        Args:
            tool_name: Name of the tool that was tested
            success: Whether the test succeeded
            response: Tool response
            execution_time: Execution time in seconds
            arguments: Arguments passed to the tool
            expected_result: Expected result for comparison
            validation_result: Validation result dictionary

        Returns:
            Formatted tool result dictionary
        """
        result = {
            "test_type": "tool",
            "tool_name": tool_name,
            "success": success,
            "execution_time": round(execution_time, 3),
            "arguments": arguments or {},
            "response": MCPReporter._serialize_response(response),
            "validation": validation_result,
        }

        if expected_result is not None:
            result["expected_result"] = expected_result
            result["matches_expected"] = (
                validation_result.get("matches_expected", False) if validation_result else False
            )

        return result

    @staticmethod
    def format_resource_result(
        resource_uri: str,
        success: bool,
        response: Any,
        execution_time: float,
        expected_content_type: Optional[str] = None,
        validation_result: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Format a resource test result.

        Args:
            resource_uri: URI of the resource that was tested
            success: Whether the test succeeded
            response: Resource response
            execution_time: Execution time in seconds
            expected_content_type: Expected content type
            validation_result: Validation result dictionary

        Returns:
            Formatted resource result dictionary
        """
        result = {
            "test_type": "resource",
            "resource_uri": resource_uri,
            "success": success,
            "execution_time": round(execution_time, 3),
            "response": MCPReporter._serialize_response(response),
            "validation": validation_result,
        }

        if expected_content_type:
            result["expected_content_type"] = expected_content_type

        if validation_result:
            result["content_type"] = validation_result.get("content_type")

        return result

    @staticmethod
    def format_prompt_result(
        prompt_name: str,
        success: bool,
        response: Any,
        execution_time: float,
        arguments: Optional[dict[str, str]] = None,
        validation_result: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Format a prompt test result.

        Args:
            prompt_name: Name of the prompt that was tested
            success: Whether the test succeeded
            response: Prompt response
            execution_time: Execution time in seconds
            arguments: Arguments passed to the prompt
            validation_result: Validation result dictionary

        Returns:
            Formatted prompt result dictionary
        """
        return {
            "test_type": "prompt",
            "prompt_name": prompt_name,
            "success": success,
            "execution_time": round(execution_time, 3),
            "arguments": arguments or {},
            "response": MCPReporter._serialize_response(response),
            "validation": validation_result,
        }

    @staticmethod
    def to_json(data: dict[str, Any], pretty: bool = True) -> str:
        """
        Convert data to JSON string.

        Args:
            data: Data dictionary to convert
            pretty: Whether to format with indentation

        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(data, indent=2, sort_keys=True, default=str)
        return json.dumps(data, default=str)

    @staticmethod
    def to_yaml(data: dict[str, Any]) -> str:
        """
        Convert data to YAML string.

        Args:
            data: Data dictionary to convert

        Returns:
            YAML string

        Raises:
            ImportError: If PyYAML is not available
        """
        if not HAS_YAML:
            raise ImportError("PyYAML is required for YAML output. Install it with: pip install PyYAML")

        return yaml.dump(data, default_flow_style=False, sort_keys=True)

    @staticmethod
    def _serialize_response(response: Any) -> Any:
        """
        Serialize an MCP response for JSON/YAML output.

        Args:
            response: Response object to serialize

        Returns:
            Serialized response (dict, list, str, or other JSON-compatible type)
        """
        if response is None:
            return None

        # Handle MCP SDK response objects
        if hasattr(response, "model_dump"):
            # Pydantic model - use mode='json' to ensure all types are JSON-compatible
            return response.model_dump(mode="json")
        elif hasattr(response, "__dict__"):
            # Regular object with __dict__
            return {
                k: MCPReporter._serialize_response(v) for k, v in response.__dict__.items() if not k.startswith("_")
            }
        elif isinstance(response, list):
            return [MCPReporter._serialize_response(item) for item in response]
        elif isinstance(response, dict):
            return {k: MCPReporter._serialize_response(v) for k, v in response.items()}
        else:
            # Primitive types (str, int, float, bool, etc.)
            return response


def create_result(
    success: bool,
    status: str,
    response: Optional[Any] = None,
    execution_time: float = 0.0,
    error: Optional[str] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Convenience function to create a module result.

    Args:
        success: Whether the operation succeeded
        status: Status string
        response: Response data
        execution_time: Execution time in seconds
        error: Error message if failed
        **kwargs: Additional fields (metadata, changed, etc.)

    Returns:
        Module result dictionary
    """
    return MCPReporter.create_module_result(
        success=success,
        status=status,
        response=response,
        execution_time=execution_time,
        error=error,
        metadata=kwargs.get("metadata"),
        changed=kwargs.get("changed", False),
    )
