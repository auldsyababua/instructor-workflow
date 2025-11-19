# Agent Handoff Protocol Schema

This directory contains XML Schema Definitions (XSD) for validating agent handoff protocols in the Native Orchestrator system.

## Quick Reference

### Validate XML Handoff

```bash
# Validate XML file against schema
xmllint --noout --schema .claude/schemas/agent-handoff-v1.xsd handoff.xml

# Extract XML from Markdown prompt and validate
sed -n '/```xml/,/```/p' prompt.md | sed '1d;$d' > /tmp/handoff.xml
xmllint --noout --schema .claude/schemas/agent-handoff-v1.xsd /tmp/handoff.xml
```

### Parse Handoff Fields

```bash
# Extract specific field values
MODE=$(xmllint --xpath 'string(//mode)' handoff.xml 2>/dev/null)
WORKFLOW=$(xmllint --xpath 'string(//workflow)' handoff.xml 2>/dev/null)
TASK_SUMMARY=$(xmllint --xpath 'string(//current_task_summary)' handoff.xml 2>/dev/null)

# Extract all constraints
xmllint --xpath '//constraint/text()' handoff.xml 2>/dev/null

# Extract deliverable file paths
xmllint --xpath '//file/@path' handoff.xml 2>/dev/null | sed 's/path="//g' | sed 's/"//g'
```

## Minimal Valid Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<agent_request xmlns="http://instructor-workflow.org/agent-handoff/v1">
  <mode>spawn</mode>
  <original_intent>Parent agent's overarching goal</original_intent>
  <current_task_summary>Brief summary of this specific task</current_task_summary>
  <workflow>standard</workflow>
  <task_details>Detailed task instructions go here...</task_details>
  <deliverables>
    <file path="path/to/deliverable.json">Description of expected output</file>
  </deliverables>
</agent_request>
```

## Full Example (With Optional Fields)

See: `/srv/projects/instructor-workflow/docs/.scratch/test-handoff-example.xml`

## Schema Versions

- **v1.0** (`agent-handoff-v1.xsd`) - Initial release (2025-11-19)

## Required Fields

- `mode` - Execution mode (spawn | conversation_only | blocking)
- `original_intent` - Parent agent's goal
- `current_task_summary` - Task summary (1-2 sentences)
- `workflow` - Workflow type (SPIKE | TDD | standard | none)
- `task_details` - Detailed instructions
- `deliverables` - At least one deliverable (file/decision/report)

## Optional Fields

- `constraints` - Hard constraints on execution
- `backlog_notes` - Continuation context

## Optional Attributes

- `version` - Schema version (default: "1.0")
- `session_id` - Session identifier
- `parent_agent` - Agent creating handoff
- `target_agent` - Agent executing task

## More Information

- Full specification: `/srv/projects/instructor-workflow/docs/.scratch/research-system-audit/xml-handoff-protocol.md`
- Validation summary: `/srv/projects/instructor-workflow/docs/.scratch/xsd-validation-summary.md`
- Test examples: `/srv/projects/instructor-workflow/docs/.scratch/test-*.xml`
