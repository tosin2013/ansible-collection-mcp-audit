# Connection Reuse Fixes

## Overview

This document describes the connection reuse improvements implemented to fix issues with sequential MCP module calls in the `tosin2013.mcp_audit` Ansible collection.

## Problem Statement

**Issue**: The collection failed on subsequent tool calls when running multiple modules sequentially in a playbook with the error:
```
Failed to connect to MCP server via stdio: unhandled errors in a TaskGroup (1 sub-exception)
```

**Root Cause**: Each Ansible module created a new stdio connection which spawned a new server process, and there was no proper cleanup delay or retry mechanism when processes were not fully terminated before the next module call.

## Phase 1 Fixes (Immediate Solution) ✅ IMPLEMENTED

Phase 1 addresses the immediate connection failures with retry logic and cleanup delays.

### 1. Process Cleanup Delays

**File**: `plugins/module_utils/mcp_client.py`

**Changes**:
- Added `asyncio` and `gc` imports for proper cleanup
- Modified the `connect()` method's `finally` block to include:
  - 0.1-second delay after stdio connections close
  - Forced garbage collection to clean up process handles
  - Enhanced error messages for TaskGroup-related errors

**Impact**: Reduces race conditions between sequential module calls by allowing proper process cleanup.

### 2. Retry Logic with Exponential Backoff

**Files Modified**:
- `plugins/modules/mcp_test_tool.py`
- `plugins/modules/mcp_test_resource.py`
- `plugins/modules/mcp_test_prompt.py`
- `plugins/modules/mcp_server_info.py`

**Changes**:
- Added `max_retries` parameter (default: 3) to all async functions
- Implemented retry logic with exponential backoff:
  - Retry delay: 0.5 seconds × (attempt + 1)
  - Only retries on TaskGroup/process cleanup errors
  - Does not retry on other types of errors
- Enhanced error messages showing retry count

**Impact**: Automatically recovers from transient connection failures without user intervention.

### Example Before and After

**Before Phase 1 (Fails)**:
```yaml
- name: Test tool 1
  tosin2013.mcp_audit.mcp_test_tool:
    tool_name: analyze_project_ecosystem
    # Works

- name: Test tool 2
  tosin2013.mcp_audit.mcp_test_tool:
    tool_name: read_file
    # FAILS with TaskGroup error
```

**After Phase 1 (Works)**:
```yaml
- name: Test tool 1
  tosin2013.mcp_audit.mcp_test_tool:
    tool_name: analyze_project_ecosystem
    # Works

- name: Test tool 2
  tosin2013.mcp_audit.mcp_test_tool:
    tool_name: read_file
    # Works! Automatically retries if needed
```

## Testing Phase 1 Fixes

Run the test playbook to verify sequential calls work:

```bash
# Test sequential module calls
ansible-playbook tests/integration/test_sequential_calls.yml

# Expected output: All tests should pass
```

The test playbook (`tests/integration/test_sequential_calls.yml`) runs 4 sequential MCP module calls to verify:
1. First server info call (baseline)
2. Second server info call (tests if cleanup works)
3. First tool call (tests cross-module cleanup)
4. Second tool call (tests repeated tool calls)

## Phase 2 Roadmap (Long-term Solution) 📋 PLANNED

Phase 2 will implement connection pooling for better performance and resource management.

### Planned Components

1. **Connection Manager Singleton**
   - File: `plugins/module_utils/mcp_connection_manager.py`
   - Manages persistent connections across module calls
   - Connection key based on transport + server parameters
   - Thread-safe with asyncio locks

2. **Persistent Connection Methods**
   - Add `connect_persistent()` to MCPClient
   - Add `close()` method for cleanup
   - Store streams and session without context managers

3. **Module Configuration Options**
   ```yaml
   connection_reuse: true      # Enable connection pooling
   connection_timeout: 300      # Timeout in seconds
   max_connection_retries: 3    # Retry attempts
   ```

4. **Benefits**:
   - Eliminates process spawn overhead
   - Reuses connections across multiple tasks
   - Optional feature (backward compatible)
   - Better resource utilization

## Configuration

Currently, Phase 1 fixes are **automatic** and require no configuration. All modules:
- Automatically retry on connection failures (max 3 attempts)
- Include cleanup delays for stdio transport
- Work with all transport types (stdio, SSE, HTTP)

Future Phase 2 will add optional configuration parameters for connection pooling.

## Compatibility

### Backward Compatibility ✅
- All fixes are backward compatible
- No breaking changes to module parameters
- Works with existing playbooks without modification

### Transport Support
- ✅ stdio: Full support (cleanup delays + retry)
- ✅ SSE: Full support (retry logic)
- ⚠️  HTTP: Not yet implemented (pending in original code)

## Performance Impact

### Phase 1
- **Overhead**: Minimal (0.1s cleanup delay per stdio connection)
- **Retry delay**: Only applies when connection fails (0.5-1.5s total for 3 retries)
- **Benefit**: Much more reliable sequential operations

### Phase 2 (Future)
- **Expected improvement**: 50-80% reduction in connection overhead
- **Trade-off**: Slightly more complex connection management

## Troubleshooting

### If sequential calls still fail:

1. **Check MCP server logs** for resource issues
2. **Increase timeout** if server is slow to start:
   ```yaml
   timeout: 60  # Increase from default 30
   ```
3. **Verify server process cleanup** manually:
   ```bash
   # Check for zombie processes
   ps aux | grep [y]our_mcp_server
   ```

### Error Messages

**Before Phase 1**:
```
Failed to connect to MCP server via stdio: unhandled errors in a TaskGroup (1 sub-exception)
```

**After Phase 1**:
```
Failed to connect to MCP server via stdio: unhandled errors in a TaskGroup (1 sub-exception)
This may be caused by a previous connection not being fully cleaned up.
Consider adding a delay between sequential MCP operations.

# After retries exhausted:
Failed to connect after 3 attempts. Last error: ...
```

## Contributing

To contribute to Phase 2 implementation:

1. Review the design in the original issue document
2. Start with `mcp_connection_manager.py` implementation
3. Add tests for connection pooling
4. Ensure backward compatibility
5. Update documentation

## References

- Original Issue: See collection documentation for detailed root cause analysis
- MCP SDK: https://github.com/modelcontextprotocol/python-sdk
- Python AsyncIO: https://docs.python.org/3/library/asyncio.html

## Changelog

### 2025-01-02 - Phase 1 Implementation
- ✅ Added process cleanup delays to `mcp_client.py`
- ✅ Implemented retry logic in all test modules
- ✅ Created sequential call test playbook
- ✅ Enhanced error messages for better debugging
- 📋 Documented fixes and Phase 2 roadmap
