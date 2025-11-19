# Investigation Log: Create agents/registry.yaml

## Hypotheses
1. Schema mismatch - Registry schema might not match agent metadata - Probability: LOW (schema validated against research)
2. Agent discovery gaps - Some agents might be in non-standard locations - Probability: HIGH (confirmed - 7 agents without frontmatter)
3. YAML syntax errors - Could introduce formatting issues - Probability: LOW (Python script validated)

## Research Findings
- **Research Document**: `docs/.scratch/research-system-audit/modular-prompting-architecture.md`
- **Schema Definition**: Section 4 (lines 447-617)
- **Required Fields**: name, display_name, description, model, tools
- **Optional Fields**: delegates_to, cannot_access, exclusive_access, responsibilities, forbidden

## Test Results

### Test 1: Agent Discovery
- **Command**: `Glob agents/*/*.md`
- **Expected**: Find all agent markdown files
- **Actual**: Found 36 markdown files across agent directories
- **Conclusion**: CONFIRMED - Multiple agents discovered

### Test 2: Frontmatter Extraction
- **Command**: `python3 .scratch/build_registry.py`
- **Expected**: Extract YAML frontmatter from all agents
- **Actual**: 27 agents with valid frontmatter, 7 without frontmatter
- **Conclusion**: PARTIAL - Not all agents have valid frontmatter

### Test 3: YAML Validation
- **Command**: `python3 -c "import yaml; yaml.safe_load(open('agents/registry.yaml'))"`
- **Expected**: No parse errors
- **Actual**: ✅ YAML validation passed
- **Return Code**: 0
- **Conclusion**: CONFIRMED - Valid YAML syntax

## Blockers Encountered
None - All tasks completed successfully

## Root Cause Identified
**Registry Creation Successful**

27 agents registered with valid YAML frontmatter.
7 agents excluded due to missing frontmatter (likely deprecated, WIP, or templates).
Registry created at: `/srv/projects/instructor-workflow/agents/registry.yaml`

## Agents Registered (27 total)

1. Grafana Agent (⚠️ empty tools array)
2. action-agent
3. backend-agent
4. browser-agent
5. cadvisor-agent
6. debug-agent
7. devops-agent
8. docker-agent
9. frappe-erpnext-agent
10. frontend-agent
11. homelab-architect
12. jupyter-agent
13. onrate-agent
14. planning-agent
15. prometheus-agent
16. qa-agent
17. researcher-agent
18. seo-agent
19. software-architect
20. test-auditor-agent
21. test-writer-agent
22. tracking-agent
23. traefik-agent
24. traycer-agent
25. unifios-agent
26. unraid-agent
27. vLLM Agent (⚠️ empty tools array, empty description)

## Agents Without Frontmatter (7 excluded)

1. plane-agent
2. mem0-agent
3. mcp-server-builder-agent
4. git-gitlab-agent
5. dragonfly-agent
6. aws-cli-agent
7. qdrant-agent

## Challenging Agents

### Empty or Incomplete Metadata
1. **Grafana Agent**: Empty tools array in frontmatter
2. **vLLM Agent**: Empty tools array AND empty description

### Naming Inconsistencies
1. **Grafana Agent**: Uses spaces instead of kebab-case (should be "grafana-agent")
2. **vLLM Agent**: Uses spaces instead of kebab-case (should be "vllm-agent")

These will need manual review and correction.

## Manual Enrichment Needed

All 27 agents have empty optional fields with TODO markers:
- `delegates_to: []` - Extract from Task tool usage in prose
- `cannot_access: []` - Extract from "Forbidden" sections
- `exclusive_access: []` - Extract from "Exclusive ownership" sections
- `responsibilities: []` - Extract from "What You Do" sections
- `forbidden: []` - Extract from "What You Don't Do" sections

## Next Steps

1. ✅ Registry created and validated
2. ⚠️ Manual review needed for 2 agents with incomplete metadata
3. ⚠️ Manual enrichment needed for optional fields (delegates_to, responsibilities, etc.)
4. Consider fixing naming inconsistencies (Grafana Agent → grafana-agent, vLLM Agent → vllm-agent)
5. Investigate 7 excluded agents to determine if they should be added

## Validation Results

- **File Created**: `/srv/projects/instructor-workflow/agents/registry.yaml`
- **YAML Syntax**: ✅ Valid (python yaml.safe_load succeeded)
- **Required Fields**: ✅ Present for all 27 agents
- **Optional Fields**: ⚠️ Initialized with empty arrays + TODO comments
- **Total Agent Count**: 27 registered, 7 excluded
