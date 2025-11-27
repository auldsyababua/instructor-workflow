# Epic 12: MCP Code Execution Integration (Placeholder)

**Created**: 2025-11-20
**Status**: Placeholder (not yet planned)
**Priority**: Medium (after Epic 10/11 complete)
**Reference**: https://www.anthropic.com/engineering/code-execution-with-mcp

---

## Context

Epic 10 implements tool execution logging via hooks, capturing tool calls, parameters, and results. This creates a foundation for optimizing MCP server interactions using code execution patterns.

**Current State**:
- IW uses MCP servers for external integrations (GitHub, Supabase, Linear, etc.)
- All MCP tools loaded upfront into context window
- Intermediate tool results pass through model context
- Token consumption scales linearly with tool count

**Problem** (from Anthropic blog):
1. **Tool definitions overload context**: Hundreds of tool definitions loaded upfront (150,000+ tokens)
2. **Intermediate results waste tokens**: Large data flows through context multiple times
3. **Example**: Fetching 10,000-row spreadsheet passes all rows through context before filtering

---

## Proposed Solution

Integrate with `mcp-code-exec-agent` project to present MCP servers as code APIs instead of direct tool calls.

**Location**: `/srv/projects/mcp-code-exec-agent`
**GitHub Reference**: https://github.com/VRSEN/mcp-code-exec-agent/

**Approach** (from Anthropic blog):
```typescript
// Progressive disclosure - load tools on demand
servers/
├── github/
│   ├── createIssue.ts
│   ├── searchCode.ts
│   └── index.ts
├── linear/
│   ├── listIssues.ts
│   ├── updateIssue.ts
│   └── index.ts
└── supabase/
    ├── executeSQL.ts
    └── index.ts

// Example: Filter data in execution environment
const allIssues = await linear.listIssues({ team: 'IW' });
const pending = allIssues.filter(i => i.state === 'Todo');
console.log(`Found ${pending.length} pending issues`);
console.log(pending.slice(0, 5)); // Only log first 5
```

**Benefits**:
- ✅ **98.7% token reduction** (150k → 2k tokens per request)
- ✅ **Context-efficient**: Load only tools needed for current task
- ✅ **Privacy-preserving**: Intermediate data stays in execution environment
- ✅ **State persistence**: Code can save results to workspace files
- ✅ **Reusable skills**: Agents build library of proven implementations

---

## Integration with Epic 10 Tool Logging

Epic 10's tool execution logging provides critical data for optimizing MCP usage:

**Use Case 1: Identify Heavy Token Consumers**
```bash
# Analyze tool logs to find expensive MCP calls
cat logs/tool_execution/tool_*.json | jq -r '
  select(.tool_name | startswith("mcp__")) |
  {tool: .tool_name, tokens: .tokens.total}
' | sort -k2 -nr | head -10
```

**Use Case 2: Detect Repeated MCP Patterns**
```bash
# Find tool chains that should become skills
cat logs/tool_execution/tool_*.json | jq -r '
  select(.tool_name | startswith("mcp__")) |
  .tool_name
' | uniq -c | sort -nr
```

**Use Case 3: Measure Code Execution Impact**
- Before: Log token usage for direct MCP tool calls
- After: Log token usage for code-based MCP interactions
- Compare: Calculate reduction percentage

---

## Placeholder Stories

**Story 1**: Audit Current MCP Usage
- Extract MCP tool call patterns from Epic 10 logs
- Identify high-token-cost operations (spreadsheet fetches, large queries)
- Document current token consumption baseline

**Story 2**: Generate MCP Server File Tree
- Create TypeScript interface files for each MCP server
- Structure: `servers/<mcp-server>/<tool-name>.ts`
- Generate from MCP server schemas automatically

**Story 3**: Build Code Execution Sandbox
- Integrate with `/srv/projects/mcp-code-exec-agent`
- Configure secure execution environment (resource limits, sandboxing)
- Add filesystem access for state persistence

**Story 4**: Implement Progressive Tool Discovery
- Add `search_tools` function for MCP server exploration
- Support detail levels: name-only, name+description, full-schema
- Cache tool definitions in execution environment

**Story 5**: Create Reusable Skills Library
- Save proven MCP code patterns to `./skills/`
- Add SKILL.md documentation for each skill
- Build skill registry for agent discovery

**Story 6**: Token Usage Benchmarking
- Measure before/after token consumption
- Compare latency (time-to-first-token)
- Document cost savings per operation type

---

## Dependencies

**Prerequisites**:
- ✅ Epic 10 complete (tool execution logging operational)
- ✅ `/srv/projects/mcp-code-exec-agent` repository available
- ⚠️ MCP servers configured and operational (GitHub, Linear, Supabase, etc.)

**Technical Requirements**:
- TypeScript execution environment (Node.js 20+)
- Filesystem access for code execution
- MCP client library integration
- Secure sandbox (Docker or similar)

---

## Success Metrics

**Primary**:
- Token reduction: >90% for MCP-heavy workflows
- Latency reduction: <50ms time-to-first-token improvement
- Context efficiency: Load <10% of total tool definitions per request

**Secondary**:
- Skills library: >20 reusable MCP patterns documented
- Privacy: 100% of PII flows through execution environment only
- State persistence: Agent can resume work across sessions

---

## Risks and Mitigations

**Risk 1**: Code execution complexity
- Mitigation: Start with read-only operations, expand gradually
- Mitigation: Use proven sandbox (Docker, Firecracker)

**Risk 2**: Security vulnerabilities in agent-generated code
- Mitigation: Static analysis before execution
- Mitigation: Resource limits (CPU, memory, network)
- Mitigation: Audit all code execution via Epic 10 logging

**Risk 3**: Skills drift (saved code becomes stale)
- Mitigation: Version skills with API compatibility checks
- Mitigation: Automated testing of skill library
- Mitigation: Periodic skill review and deprecation

---

## Open Questions

1. **MCP server compatibility**: Do all our MCP servers support TypeScript interfaces?
2. **Execution environment**: Docker vs Firecracker vs WebAssembly sandbox?
3. **Tokenization strategy**: How to implement privacy-preserving PII handling?
4. **Skills storage**: Git-tracked vs ephemeral workspace?
5. **Fallback behavior**: If code execution fails, revert to direct tool calls?

---

## References

**External**:
- Anthropic Blog: https://www.anthropic.com/engineering/code-execution-with-mcp
- GitHub Implementation: https://github.com/VRSEN/mcp-code-exec-agent/
- Cloudflare "Code Mode": (referenced in blog, find link)
- MCP Specification: https://modelcontextprotocol.io/

**Internal**:
- Epic 10 implementation: `docs/.scratch/epic-10-story-1/`
- Tool execution logs: `logs/tool_execution/`
- MCP code exec agent: `/srv/projects/mcp-code-exec-agent`
- Homelab services catalog: `reference/homelab-services.yaml` (service inventory for MCP integration)

---

## Next Steps (When Epic 12 Activated)

1. Read Anthropic blog post in full detail
2. Audit `/srv/projects/mcp-code-exec-agent` codebase
3. Review Epic 10 tool logs for MCP usage patterns
4. Create detailed story breakdown (RAEP-enriched)
5. Estimate effort and schedule implementation

---

**Status**: Placeholder (parking lot for future work)
**Blocked By**: Epic 10, Epic 11
**Blocks**: None (optional optimization)
**Effort Estimate**: TBD (requires detailed analysis)
