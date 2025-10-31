# ADR-0016: LiteLLM Integration for End-to-End Testing

**Status:** Accepted

**Date:** 2025-10-30

**Deciders:** Project maintainers

**Priority:** P1 (High Priority for v1.1.0)

## Context

The MCP Audit Ansible Collection currently tests MCP servers in isolation - validating that tools, resources, and prompts are correctly implemented and respond properly to client requests. However, the ultimate goal of MCP servers is to be consumed by Large Language Models (LLMs).

**Gap identified:** We cannot currently validate that:
1. MCP server responses are actually useful to LLMs
2. Tools work correctly when invoked by real LLMs
3. Prompts generate appropriate LLM responses
4. The end-to-end flow (MCP server → LLM → result) functions correctly

**LiteLLM context:** LiteLLM provides a unified Python interface to 100+ LLM providers (OpenAI, Anthropic, Cohere, Azure, AWS Bedrock, Google Vertex AI, vLLM, OpenRouter, etc.) with standardized API calls. This allows testing against multiple LLM providers without provider-specific code.

**Notable providers:**
- **vLLM**: High-throughput serving for local or self-hosted models
- **OpenRouter**: Unified API for multiple LLM providers with fallback routing
- **See [LiteLLM Providers Documentation](https://docs.litellm.ai/docs/providers)** for the complete list of 100+ supported providers

**Ansible advantages:**
- Ansible variables for model selection (`llm_model: "gpt-4"`)
- Ansible Vault for secure API key management (`llm_api_key: !vault |...`)
- Playbook-level configuration without code changes
- Environment-specific credentials (dev vs prod API keys)

## Decision

We will create a **`mcp_test_llm_integration`** module that:

1. **Integrates with LiteLLM** to test MCP servers with real LLM calls
2. **Uses Ansible variables** for model and credential configuration
3. **Supports multiple use cases:**
   - End-to-end tool invocation testing (LLM decides when to call tools)
   - Prompt effectiveness testing (measure LLM response quality)
   - Multi-provider compatibility testing (same MCP server across different LLMs)
   - Resource utilization validation (verify LLMs can understand resource content)

4. **Module parameters:**
```yaml
- name: Test MCP server with LLM integration
  mcp.audit.mcp_test_llm_integration:
    # MCP server connection
    server_command: "{{ python_interpreter }}"
    server_args:
      - "{{ test_servers_path }}/calculator/server.py"
    transport: "stdio"

    # LiteLLM configuration
    llm_provider: "openai"  # openai, anthropic, cohere, azure, bedrock, vllm, openrouter, etc.
    llm_model: "{{ llm_model | default('gpt-4') }}"
    llm_api_key: "{{ llm_api_key }}"  # From Ansible Vault
    llm_base_url: "{{ llm_base_url | default(omit) }}"  # Optional for custom endpoints (vLLM, etc.)

    # Test configuration
    test_prompt: "Calculate the sum of 15 and 27"
    expected_tool_calls: ["add"]  # Optional: verify specific tools were called
    validate_result: true  # Optional: check if LLM's final answer is correct
    expected_answer: "42"  # Optional: expected final answer

    # Advanced options
    max_iterations: 5  # Maximum LLM-tool interaction loops
    timeout: 60  # Timeout in seconds
```

**Example: Testing with vLLM (self-hosted models)**
```yaml
- name: Test MCP server with vLLM
  mcp.audit.mcp_test_llm_integration:
    server_command: "{{ python_interpreter }}"
    server_args:
      - "{{ test_servers_path }}/calculator/server.py"
    transport: "stdio"
    llm_provider: "vllm"
    llm_model: "meta-llama/Llama-2-7b-chat-hf"
    llm_api_key: "dummy"  # vLLM doesn't require API key
    llm_base_url: "http://localhost:8000"  # Your vLLM server
    test_prompt: "Calculate 42 + 58"
```

**Example: Testing with OpenRouter (multi-provider routing)**
```yaml
- name: Test MCP server with OpenRouter
  mcp.audit.mcp_test_llm_integration:
    server_command: "{{ python_interpreter }}"
    server_args:
      - "{{ test_servers_path }}/calculator/server.py"
    transport: "stdio"
    llm_provider: "openrouter"
    llm_model: "anthropic/claude-3-opus"  # OpenRouter model format
    llm_api_key: "{{ openrouter_api_key }}"  # From Ansible Vault
    test_prompt: "What is 15 multiplied by 3?"
```

5. **Credential Management Strategy:**
   - API keys stored in Ansible Vault
   - No hardcoded credentials in playbooks or modules
   - Support for environment variables as fallback
   - Clear documentation on credential best practices

6. **Implementation Phases:**
   - **Phase 1 (v1.1.0):** Basic tool invocation testing
   - **Phase 2 (v1.2.0):** Prompt effectiveness testing
   - **Phase 3 (v1.3.0):** Multi-provider comparison testing

## Alternatives Considered

### Alternative 1: No LLM Integration (Status Quo)
**Pros:**
- Simpler scope, faster v1.0.0 release
- No external API dependencies
- No cost concerns (API calls)

**Cons:**
- Cannot validate real-world MCP usage
- Missing key use case: "Does this actually work with LLMs?"
- Other tools may fill this gap

**Decision:** Rejected for core v1.0.0, but valid for initial release strategy

### Alternative 2: Direct Provider Integration (No LiteLLM)
Implement OpenAI SDK, Anthropic SDK, etc. directly in the module.

**Pros:**
- No intermediate library dependency
- More control over API calls

**Cons:**
- Massive maintenance burden (100+ providers)
- Provider-specific code everywhere
- Cannot easily add new providers
- Reinventing the wheel (LiteLLM already solves this)

**Decision:** Rejected - LiteLLM is the industry standard for unified LLM access

### Alternative 3: Separate Collection
Create `mcp.llm` collection for LiteLLM integration.

**Pros:**
- Clear separation of concerns
- Users can choose core vs LLM features

**Cons:**
- Fragments the ecosystem
- More complex installation (`ansible-galaxy install mcp.audit mcp.llm`)
- Duplicate code for MCP client utilities

**Decision:** Rejected - better as optional module within main collection

### Alternative 4: External Tool (Non-Ansible)
Create a separate Python CLI tool for LLM integration testing.

**Pros:**
- Not constrained by Ansible conventions
- Can use asyncio more freely

**Cons:**
- Loses Ansible variable management and Vault integration
- Separate credential management needed
- Not integrated with existing test suites

**Decision:** Rejected - Ansible integration is the key value proposition

## Consequences

### Positive

1. **Unique Value Proposition**
   - Only tool that combines MCP server testing + real LLM integration + Ansible
   - Fills a critical gap in the MCP ecosystem
   - Positions collection as comprehensive testing solution

2. **Ansible-Native Credential Management**
   - API keys managed via Ansible Vault (industry best practice)
   - Environment-specific configurations easy to manage
   - Integrates with existing Ansible workflows

3. **Multi-Provider Support**
   - Test against any LLM provider LiteLLM supports
   - Compare MCP server behavior across different LLMs
   - Future-proof as new providers emerge

4. **Real-World Validation**
   - Catch issues that unit tests miss
   - Verify tool descriptions are clear enough for LLMs
   - Validate end-to-end workflows

5. **Cost Control**
   - Users control when LLM tests run (not automatic)
   - Can use local/self-hosted models for free testing:
     - **vLLM**: High-performance local model serving
     - **Ollama**: Easy local model deployment
     - **LocalAI**: OpenAI-compatible local inference
   - Optional module - doesn't affect core functionality

### Negative

1. **Increased Complexity**
   - New dependency: `litellm` Python package
   - Requires API keys and configuration
   - More complex test failures to debug

2. **Cost Implications**
   - LLM API calls cost money
   - Users need to understand and accept costs
   - Must document cost estimation

3. **External Service Dependency**
   - Tests depend on external API availability
   - Rate limits and quota management
   - Network connectivity required

4. **Maintenance Burden**
   - Need to track LiteLLM updates
   - Provider-specific quirks may emerge
   - More integration tests needed

5. **Delayed v1.0.0 Release**
   - If implemented before v1.0.0, delays Galaxy publication
   - Mitigation: Implement in v1.1.0 after v1.0.0 ships

### Mitigation Strategies

1. **Cost Management:**
   - Clearly document expected costs per test
   - Support local/free LLM options:
     - vLLM for high-performance local serving
     - Ollama for easy local deployment
     - LocalAI for OpenAI-compatible local inference
   - Make module optional, not required

2. **Complexity Reduction:**
   - Excellent documentation with examples
   - Sensible defaults for common use cases
   - Debug mode to show LLM interactions

3. **Reliability:**
   - Retry logic for transient failures
   - Configurable timeouts
   - Graceful fallback when LLM unavailable

4. **Security:**
   - Extensive documentation on Vault usage
   - Never log API keys
   - Support for credential rotation

## Implementation Strategy

### Phase 1: Core Module (v1.1.0)
**Target: 2-3 weeks after v1.0.0 release**

Tasks:
- [ ] Create `mcp_test_llm_integration.py` module skeleton
- [ ] Integrate LiteLLM Python SDK
- [ ] Implement basic tool invocation testing
- [ ] Add Ansible Vault documentation
- [ ] Write integration tests (with mock LLM for CI)
- [ ] Document cost implications

### Phase 2: Advanced Features (v1.2.0)
**Target: 1-2 months after v1.1.0**

Tasks:
- [ ] Prompt effectiveness testing
- [ ] Resource utilization validation
- [ ] Multi-iteration tool calling (agent loops)
- [ ] Response quality metrics

### Phase 3: Multi-Provider Testing (v1.3.0)
**Target: 2-3 months after v1.2.0**

Tasks:
- [ ] Provider comparison reports
- [ ] Performance benchmarking across providers
- [ ] Cost comparison tooling

## Related ADRs

- **ADR-0002: MCP Python SDK Selection** - Uses same SDK patterns
- **ADR-0003: Module Architecture Pattern** - Follows same module structure
- **ADR-0005: Testing Strategy** - Extends with LLM integration tests
- **ADR-0015: Security Policy** - Credential management aligns with security policy

## References

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LiteLLM Providers List](https://docs.litellm.ai/docs/providers) - Complete list of 100+ supported providers
- [LiteLLM vLLM Provider](https://docs.litellm.ai/docs/providers/vllm) - Self-hosted model serving
- [LiteLLM OpenRouter Provider](https://docs.litellm.ai/docs/providers/openrouter) - Multi-provider routing with fallback
- [Ansible Vault Best Practices](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
- [MCP Specification](https://modelcontextprotocol.io/)

**Note for developers:** To integrate additional LLM providers, refer to the [LiteLLM Providers Documentation](https://docs.litellm.ai/docs/providers). All providers supported by LiteLLM can be used with the `mcp_test_llm_integration` module by setting the appropriate `llm_provider`, `llm_model`, and `llm_base_url` parameters.

## Notes

**Why now?**
- Core modules (v1.0.0) are complete and tested
- Community feedback suggests real-world validation is valuable
- Ansible's credential management is perfect for this use case
- LiteLLM makes multi-provider support tractable

**Why not later?**
- User demand is likely to emerge quickly post-v1.0.0
- Competitive advantage: no other tool does this
- Natural evolution of the collection's capabilities

**User feedback welcome:**
- Which LLM providers are most important?
- What test scenarios are most valuable?
- How should cost be managed/estimated?

## Decision Outcome

**Accepted for implementation in v1.1.0** (post-v1.0.0 Galaxy release)

Module will be:
- ✅ Optional (not required for core functionality)
- ✅ Well-documented (especially credential management)
- ✅ Cost-transparent (clear documentation of API costs)
- ✅ Secure (Ansible Vault integration)
- ✅ Multi-provider (via LiteLLM)

This positions `mcp.audit` as the most comprehensive MCP testing solution available.

## Implementation Status

**Date:** 2025-10-30

**Status:** ✅ **v1.1.0 Core Implementation Complete**

### Tested Providers
- ✅ **Ollama** (phi3.5) - Fully tested with calculator MCP server
  - Basic tool invocation: ✅ Working
  - Multi-iteration loops: ✅ Working (with workaround for Ollama's tool calling limitation)
  - Result validation: ✅ Working
  - Integration tests: ✅ 3/3 passing

### Documented (Not Yet Tested)
- 📝 **OpenRouter** - Examples provided, requires API key for testing
- 📝 **vLLM** - Examples provided, requires self-hosted setup for testing

### Implementation Notes
- **Ollama Tool Calling Workaround**: Ollama has a known limitation where it loops calling tools repeatedly. The module includes a workaround: only pass `tools` parameter on the first iteration, forcing the LLM to respond with text on subsequent iterations.
- **LiteLLM Version**: Tested with litellm>=1.79.0
- **Model Responses**: Smaller models like phi3.5 tend to be verbose but functional. Answers correctly identify results despite verbosity.
