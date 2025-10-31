# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later OR BSD-2-Clause

"""
MCP Response Validator

This module_utils can be used under either:
- GPL-3.0-or-later (for use in GPL collections)
- BSD-2-Clause (for use in permissively licensed collections)

Provides validation functions for MCP server responses.
"""

import json
from typing import Any, Optional


class ValidationError(Exception):
    """Exception raised when validation fails."""

    pass


class MCPValidator:
    """
    Validator for MCP server responses and data structures.

    Provides methods to validate various MCP response types and ensure
    they conform to expected formats and contain valid data.
    """

    @staticmethod
    def validate_tool_response(response: Any, expected_result: Optional[Any] = None) -> dict[str, Any]:
        """
        Validate a tool call response from an MCP server.

        Args:
            response: The tool response to validate
            expected_result: Optional expected result for comparison

        Returns:
            Dictionary with validation results

        Raises:
            ValidationError: If response is invalid
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "matches_expected": None,
        }

        if response is None:
            validation_result["valid"] = False
            validation_result["errors"].append("Tool response is None")
            return validation_result

        # Check if response has content attribute (MCP SDK structure)
        if hasattr(response, "content"):
            content_items = response.content
            if not isinstance(content_items, list):
                validation_result["valid"] = False
                validation_result["errors"].append(f"Response content is not a list: {type(content_items)}")
                return validation_result

            if len(content_items) == 0:
                validation_result["warnings"].append("Response content is empty")

            # Validate content items
            for idx, item in enumerate(content_items):
                if not hasattr(item, "type"):
                    validation_result["errors"].append(f"Content item {idx} missing 'type' attribute")
                    validation_result["valid"] = False
        else:
            validation_result["warnings"].append("Response does not have standard MCP content structure")

        # Compare with expected result if provided
        if expected_result is not None:
            try:
                actual_value = MCPValidator._extract_response_value(response)
                matches = MCPValidator._compare_values(actual_value, expected_result)
                validation_result["matches_expected"] = matches
                if not matches:
                    validation_result["warnings"].append(
                        f"Response does not match expected result. Expected: {expected_result}, Got: {actual_value}"
                    )
            except Exception as e:
                validation_result["warnings"].append(f"Could not compare with expected result: {e!s}")

        return validation_result

    @staticmethod
    def validate_resource_response(response: Any, expected_content_type: Optional[str] = None) -> dict[str, Any]:
        """
        Validate a resource read response from an MCP server.

        Args:
            response: The resource response to validate
            expected_content_type: Optional expected content type (e.g., 'text/plain')

        Returns:
            Dictionary with validation results

        Raises:
            ValidationError: If response is invalid
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "content_type": None,
        }

        if response is None:
            validation_result["valid"] = False
            validation_result["errors"].append("Resource response is None")
            return validation_result

        # Check for contents attribute (MCP SDK structure)
        if hasattr(response, "contents"):
            contents = response.contents
            if not isinstance(contents, list):
                validation_result["valid"] = False
                validation_result["errors"].append(f"Resource contents is not a list: {type(contents)}")
                return validation_result

            if len(contents) == 0:
                validation_result["warnings"].append("Resource contents is empty")
            else:
                # Validate first content item
                first_content = contents[0]
                if hasattr(first_content, "mimeType"):
                    validation_result["content_type"] = first_content.mimeType
                    if expected_content_type and first_content.mimeType != expected_content_type:
                        validation_result["warnings"].append(
                            f"Content type mismatch. Expected: {expected_content_type}, Got: {first_content.mimeType}"
                        )
                else:
                    validation_result["warnings"].append("Content item missing mimeType attribute")
        else:
            validation_result["valid"] = False
            validation_result["errors"].append("Response does not have 'contents' attribute")

        return validation_result

    @staticmethod
    def validate_prompt_response(response: Any) -> dict[str, Any]:
        """
        Validate a prompt response from an MCP server.

        Args:
            response: The prompt response to validate

        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "has_messages": False,
        }

        if response is None:
            validation_result["valid"] = False
            validation_result["errors"].append("Prompt response is None")
            return validation_result

        # Check for messages attribute
        if hasattr(response, "messages"):
            validation_result["has_messages"] = True
            messages = response.messages
            if not isinstance(messages, list):
                validation_result["valid"] = False
                validation_result["errors"].append(f"Prompt messages is not a list: {type(messages)}")
            elif len(messages) == 0:
                validation_result["warnings"].append("Prompt messages is empty")
        else:
            validation_result["warnings"].append("Response does not have 'messages' attribute")

        return validation_result

    @staticmethod
    def validate_server_info(info: dict[str, Any]) -> dict[str, Any]:
        """
        Validate server information structure.

        Args:
            info: Server information dictionary

        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "has_capabilities": False,
        }

        if not isinstance(info, dict):
            validation_result["valid"] = False
            validation_result["errors"].append(f"Server info is not a dictionary: {type(info)}")
            return validation_result

        # Check for expected fields
        expected_fields = ["server_name", "server_version", "capabilities"]
        for field in expected_fields:
            if field not in info:
                validation_result["warnings"].append(f"Server info missing '{field}' field")
            elif field == "capabilities":
                validation_result["has_capabilities"] = bool(info[field])

        return validation_result

    @staticmethod
    def validate_tool_list(tools: list[Any]) -> dict[str, Any]:
        """
        Validate a list of tools from an MCP server.

        Args:
            tools: List of tool objects

        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "tool_count": 0,
            "tool_names": [],
        }

        if not isinstance(tools, list):
            validation_result["valid"] = False
            validation_result["errors"].append(f"Tools is not a list: {type(tools)}")
            return validation_result

        validation_result["tool_count"] = len(tools)

        if len(tools) == 0:
            validation_result["warnings"].append("Tool list is empty")
            return validation_result

        # Validate each tool
        for idx, tool in enumerate(tools):
            if not hasattr(tool, "name"):
                validation_result["errors"].append(f"Tool {idx} missing 'name' attribute")
                validation_result["valid"] = False
            else:
                validation_result["tool_names"].append(tool.name)

            if not hasattr(tool, "description"):
                validation_result["warnings"].append(
                    f"Tool '{getattr(tool, 'name', idx)}' missing 'description' attribute"
                )

        return validation_result

    @staticmethod
    def _extract_response_value(response: Any) -> Any:
        """
        Extract the actual value from an MCP response.

        Args:
            response: MCP response object

        Returns:
            Extracted value
        """
        if hasattr(response, "content") and len(response.content) > 0:
            first_item = response.content[0]
            if hasattr(first_item, "text"):
                return first_item.text
            elif hasattr(first_item, "data"):
                return first_item.data
        return response

    @staticmethod
    def _compare_values(actual: Any, expected: Any) -> bool:
        """
        Compare actual and expected values with type coercion.

        Args:
            actual: Actual value
            expected: Expected value

        Returns:
            True if values match, False otherwise
        """
        # Direct equality
        if actual == expected:
            return True

        # Try string comparison
        try:
            if str(actual) == str(expected):
                return True
        except Exception:
            pass

        # Try JSON comparison for complex types
        try:
            if isinstance(actual, (dict, list)) and isinstance(expected, (dict, list)):
                return json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)
        except Exception:
            pass

        # Try numeric comparison
        try:
            if float(actual) == float(expected):
                return True
        except (ValueError, TypeError):
            pass

        return False


def validate_response(response_type: str, response: Any, **kwargs: Any) -> dict[str, Any]:
    """
    Validate an MCP response based on its type.

    Args:
        response_type: Type of response ('tool', 'resource', 'prompt', 'server_info', 'tool_list')
        response: The response to validate
        **kwargs: Additional validation parameters

    Returns:
        Dictionary with validation results

    Raises:
        ValueError: If response_type is invalid
    """
    validator = MCPValidator()

    if response_type == "tool":
        return validator.validate_tool_response(response, expected_result=kwargs.get("expected_result"))
    elif response_type == "resource":
        return validator.validate_resource_response(response, expected_content_type=kwargs.get("expected_content_type"))
    elif response_type == "prompt":
        return validator.validate_prompt_response(response)
    elif response_type == "server_info":
        return validator.validate_server_info(response)
    elif response_type == "tool_list":
        return validator.validate_tool_list(response)
    else:
        raise ValueError(
            f"Invalid response_type '{response_type}'. Valid types: tool, resource, prompt, server_info, tool_list"
        )
