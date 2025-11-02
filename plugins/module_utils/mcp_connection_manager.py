# Copyright: (c) 2025, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later OR BSD-2-Clause

"""
MCP Connection Manager

This module_utils can be used under either:
- GPL-3.0-or-later (for use in GPL collections)
- BSD-2-Clause (for use in permissively licensed collections)

Provides connection pooling and lifecycle management for MCP clients
to enable connection reuse across multiple module calls.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import asyncio
import hashlib
import time
from typing import Any, Dict, Optional

from ansible_collections.tosin2013.mcp_audit.plugins.module_utils.mcp_client import (
    MCPClient,
    MCPClientError,
)


class MCPConnectionError(Exception):
    """Exception raised for connection management errors."""

    pass


class MCPConnectionManager:
    """
    Singleton connection manager for MCP clients.

    Manages a pool of persistent MCP connections to enable reuse across
    multiple Ansible module calls. Connections are keyed by their configuration
    (transport type, server command/URL, etc.) to ensure the same server
    reuses the same connection.

    Features:
    - Connection pooling with automatic lifecycle management
    - Thread-safe with asyncio locks
    - Automatic timeout and cleanup
    - Connection health checking
    - Graceful shutdown support

    Example:
        manager = MCPConnectionManager()
        client = MCPClient(transport="stdio", server_command="python", ...)

        # Get or create a persistent connection
        persistent_client = await manager.get_or_create_connection(client)

        # Use the connection
        result = await persistent_client.call_tool("my_tool", {})

        # Connection is automatically reused on next call
        result2 = await persistent_client.call_tool("another_tool", {})

        # Cleanup when done
        await manager.close_connection(client)
    """

    _instance: Optional["MCPConnectionManager"] = None
    _initialized: bool = False

    def __new__(cls):
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the connection manager (only once)."""
        if not self._initialized:
            self._connections: Dict[str, MCPClient] = {}
            self._locks: Dict[str, asyncio.Lock] = {}
            self._connection_times: Dict[str, float] = {}
            self._connection_use_counts: Dict[str, int] = {}
            self._default_timeout = 300  # 5 minutes
            self._initialized = True

    def _get_connection_key(self, client: MCPClient) -> str:
        """
        Generate unique key for connection based on server parameters.

        Args:
            client: MCPClient instance to generate key for

        Returns:
            Unique connection key (MD5 hash of connection parameters)
        """
        if client.transport == "stdio":
            # Key includes command and all arguments
            key_data = f"{client.transport}:{client.server_command}:{':'.join(client.server_args)}"
        elif client.transport in ("sse", "http"):
            # Key includes URL and headers (for auth)
            headers_str = ":".join(f"{k}={v}" for k, v in sorted(client.server_headers.items()))
            key_data = f"{client.transport}:{client.server_url}:{headers_str}"
        else:
            # Fallback for unknown transports
            key_data = f"{client.transport}:unknown"

        # Return MD5 hash for consistent key length
        return hashlib.md5(key_data.encode()).hexdigest()

    async def get_or_create_connection(
        self, client: MCPClient, timeout: Optional[int] = None, enable_reuse: bool = True
    ) -> MCPClient:
        """
        Get existing connection or create a new persistent one.

        Args:
            client: MCPClient instance with connection parameters
            timeout: Connection timeout in seconds (uses default if None)
            enable_reuse: If False, always creates a new connection without pooling

        Returns:
            Connected MCPClient instance (either from pool or newly created)

        Raises:
            MCPConnectionError: If connection creation fails
        """
        if not enable_reuse:
            # Connection reuse disabled, create temporary connection
            # This will use the regular context manager
            return client

        key = self._get_connection_key(client)
        connection_timeout = timeout or self._default_timeout

        # Ensure we have a lock for this connection key
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()

        async with self._locks[key]:
            # Check if connection exists and is still valid
            if key in self._connections:
                connection = self._connections[key]

                # Check connection age
                connection_age = time.time() - self._connection_times[key]
                if connection_age > connection_timeout:
                    # Connection too old, close and create new one
                    await self._close_connection_internal(key)
                else:
                    # Connection still valid, increment use count and return
                    self._connection_use_counts[key] = self._connection_use_counts.get(key, 0) + 1
                    return connection

            # Create new persistent connection
            try:
                connection = await client.connect_persistent()
                self._connections[key] = connection
                self._connection_times[key] = time.time()
                self._connection_use_counts[key] = 1
                return connection
            except Exception as e:
                raise MCPConnectionError(f"Failed to create persistent connection: {e!s}") from e

    async def close_connection(self, client: MCPClient) -> None:
        """
        Close a specific connection.

        Args:
            client: MCPClient instance to close
        """
        key = self._get_connection_key(client)
        if key in self._locks:
            async with self._locks[key]:
                await self._close_connection_internal(key)

    async def _close_connection_internal(self, key: str) -> None:
        """
        Internal method to close connection (must be called with lock held).

        Args:
            key: Connection key to close
        """
        if key in self._connections:
            try:
                await self._connections[key].close()
            except Exception:
                # Ignore errors during cleanup
                pass
            finally:
                del self._connections[key]
                if key in self._connection_times:
                    del self._connection_times[key]
                if key in self._connection_use_counts:
                    del self._connection_use_counts[key]

    async def close_all(self) -> None:
        """
        Close all connections in the pool.

        Useful for cleanup during module shutdown or error recovery.
        """
        # Get all keys to avoid modifying dict during iteration
        keys = list(self._connections.keys())

        for key in keys:
            if key in self._locks:
                async with self._locks[key]:
                    await self._close_connection_internal(key)

    async def cleanup_stale_connections(self, max_age: Optional[int] = None) -> int:
        """
        Close connections older than max_age seconds.

        Args:
            max_age: Maximum connection age in seconds (uses default timeout if None)

        Returns:
            Number of connections closed
        """
        max_age = max_age or self._default_timeout
        current_time = time.time()
        closed_count = 0

        # Get all keys to avoid modifying dict during iteration
        keys = list(self._connections.keys())

        for key in keys:
            if key in self._locks and key in self._connection_times:
                async with self._locks[key]:
                    connection_age = current_time - self._connection_times[key]
                    if connection_age > max_age:
                        await self._close_connection_internal(key)
                        closed_count += 1

        return closed_count

    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current connections.

        Returns:
            Dictionary containing connection pool statistics
        """
        current_time = time.time()
        stats = {
            "total_connections": len(self._connections),
            "connections": [],
        }

        for key, connection in self._connections.items():
            connection_age = current_time - self._connection_times.get(key, current_time)
            stats["connections"].append(
                {
                    "key": key,
                    "age_seconds": round(connection_age, 2),
                    "use_count": self._connection_use_counts.get(key, 0),
                    "transport": connection.transport,
                }
            )

        return stats

    def set_default_timeout(self, timeout: int) -> None:
        """
        Set default timeout for connections.

        Args:
            timeout: Timeout in seconds
        """
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        self._default_timeout = timeout

    def get_default_timeout(self) -> int:
        """
        Get current default timeout.

        Returns:
            Default timeout in seconds
        """
        return self._default_timeout


# Singleton instance for easy access
_connection_manager = MCPConnectionManager()


def get_connection_manager() -> MCPConnectionManager:
    """
    Get the singleton connection manager instance.

    Returns:
        Singleton MCPConnectionManager instance
    """
    return _connection_manager
