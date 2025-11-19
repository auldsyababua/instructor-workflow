# XSD Schema Validation Summary

**Date**: 2025-11-19
**Task**: Create XML Schema Definition (XSD) for Agent Handoff Protocol
**Status**: COMPLETE

---

## Deliverables

### 1. Schema File Created
**Location**: `/srv/projects/instructor-workflow/.claude/schemas/agent-handoff-v1.xsd`
**Size**: 5.6KB (154 lines)
**Format**: XML Schema Definition (XSD) 1.0
**Namespace**: `http://instructor-workflow.org/agent-handoff/v1`

### 2. Schema Components

**Required Fields** (minOccurs=1, maxOccurs=1):
- `mode` - Enum: spawn, conversation_only, blocking
- `original_intent` - String (parent agent's goal)
- `current_task_summary` - String (task summary)
- `workflow` - Enum: SPIKE, TDD, standard, none
- `task_details` - String (detailed instructions)
- `deliverables` - Container (1+ file/decision/report elements)

**Optional Fields** (minOccurs=0):
- `constraints` - Container (0+ constraint elements)
- `backlog_notes` - String (continuation context)

**Optional Attributes** (for metadata):
- `version` - String (default: "1.0")
- `session_id` - String
- `parent_agent` - String
- `target_agent` - String

**Deliverable Types**:
- `file` - Path attribute (required), required attribute (boolean, default true)
- `decision` - String
- `report` - String

---

## Validation Results

### Test 1: Schema Self-Validation
**Command**: `xmllint --noout agent-handoff-v1.xsd`
**Result**: PASS - Schema syntax is valid
**Output**: No errors

### Test 2: Full Example Validation
**File**: `docs/.scratch/test-handoff-example.xml` (Planning → Backend Agent)
**Command**: `xmllint --noout --schema agent-handoff-v1.xsd test-handoff-example.xml`
**Result**: PASS - Validates successfully
**Output**: "docs/.scratch/test-handoff-example.xml validates"

**Example includes**:
- All required fields
- Optional constraints (4 constraints)
- Multiple deliverables (3 files + 1 decision)
- Optional backlog_notes
- Custom attributes (version, session_id, parent_agent, target_agent)

### Test 3: Minimal Example Validation
**File**: `docs/.scratch/test-minimal-example.xml`
**Command**: `xmllint --noout --schema agent-handoff-v1.xsd test-minimal-example.xml`
**Result**: PASS - Validates successfully with minimal required fields
**Output**: "docs/.scratch/test-minimal-example.xml validates"

**Example includes**:
- Only required fields (no optional constraints or backlog_notes)
- Single deliverable (file)
- No custom attributes

### Test 4: Error Detection (Invalid Enum)
**File**: `docs/.scratch/test-invalid-mode.xml` (mode="invalid-mode")
**Command**: `xmllint --noout --schema agent-handoff-v1.xsd test-invalid-mode.xml`
**Result**: FAIL (as expected) - Schema correctly rejects invalid enum value
**Error**: "Element 'mode': [facet 'enumeration'] The value 'invalid-mode' is not an element of the set {'spawn', 'conversation_only', 'blocking'}"
**Exit Code**: 3

---

## Schema Design Decisions

### 1. Namespace Strategy
- Target namespace: `http://instructor-workflow.org/agent-handoff/v1`
- Enables agent-specific extensions via custom namespaces
- Version included in namespace for future evolution

### 2. Element Cardinality
- Required fields enforce minimum handoff quality
- Optional fields allow flexibility without breaking validation
- Deliverables container allows 0+ of each type (file/decision/report)

### 3. Enumeration Values
**Mode types**:
- `spawn` - Create new tmux session for child agent
- `conversation_only` - Provide context, no session creation
- `blocking` - Parent waits for completion before proceeding

**Workflow types**:
- `SPIKE` - Research/exploration phase, no production changes
- `TDD` - Test-driven development with QA oversight
- `standard` - Normal implementation workflow
- `none` - No specific workflow required

### 4. Extension Mechanism
- Custom attributes allowed on root `<agent_request>` element
- Namespace support for agent-specific child elements
- Backwards compatible with future schema versions

---

## Integration with Session Manager

The schema enables pre-spawn validation in `session-manager.sh`:

```bash
# Extract XML from Markdown
sed -n '/```xml/,/```/p' prompt.md | sed '1d;$d' > /tmp/handoff.xml

# Validate against schema
if ! xmllint --noout --schema .claude/schemas/agent-handoff-v1.xsd /tmp/handoff.xml 2>&1; then
  echo "❌ Invalid XML handoff in prompt file" >&2
  exit 1
fi

# Parse specific fields
MODE=$(xmllint --xpath 'string(//mode)' /tmp/handoff.xml 2>/dev/null)
WORKFLOW=$(xmllint --xpath 'string(//workflow)' /tmp/handoff.xml 2>/dev/null)
```

---

## Example XML (From Research Doc Section 6.1)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<agent_request
  xmlns="http://instructor-workflow.org/agent-handoff/v1"
  version="1.0"
  session_id="20251119-160000-backend-api"
  parent_agent="planning-agent"
  target_agent="backend-agent">

  <mode>spawn</mode>
  <original_intent>
    Build authentication system for IW platform to enable agent identity verification
  </original_intent>
  <current_task_summary>
    Implement POST /api/v1/auth/login endpoint with JWT token generation
  </current_task_summary>
  <workflow>TDD</workflow>
  <task_details>
    Create authentication endpoint with the following requirements:
    1. Endpoint: POST /api/v1/auth/login
    2. Request body: { "username": string, "password": string }
    3. Response: { "token": string (JWT), "expires_at": ISO8601 }
    ...
  </task_details>
  <constraints>
    <constraint>No database migrations without Planning Agent approval</constraint>
    <constraint>Use existing bcrypt library (do not add new dependencies)</constraint>
  </constraints>
  <deliverables>
    <file path="src/api/routes/auth.py" required="true">
      FastAPI route handler for /api/v1/auth/login endpoint
    </file>
    <decision>
      Whether database schema changes are needed for user authentication
    </decision>
  </deliverables>
  <backlog_notes>
    Next steps after completion: Implement token refresh endpoint...
  </backlog_notes>
</agent_request>
```

---

## Files Created

1. `/srv/projects/instructor-workflow/.claude/schemas/agent-handoff-v1.xsd` - Schema definition
2. `/srv/projects/instructor-workflow/docs/.scratch/test-handoff-example.xml` - Full example (validates)
3. `/srv/projects/instructor-workflow/docs/.scratch/test-minimal-example.xml` - Minimal example (validates)
4. `/srv/projects/instructor-workflow/docs/.scratch/test-invalid-mode.xml` - Invalid example (fails validation)
5. `/srv/projects/instructor-workflow/docs/.scratch/xsd-creation-investigation.md` - RCA investigation log
6. `/srv/projects/instructor-workflow/docs/.scratch/xsd-validation-summary.md` - This summary

---

## Success Criteria Met

- ✅ Valid XSD syntax (verified with xmllint)
- ✅ File created at: `.claude/schemas/agent-handoff-v1.xsd`
- ✅ Schema validates successfully against example XML
- ✅ All fields from research specification included:
  - ✅ mode (enum: spawn/conversation_only/blocking)
  - ✅ original_intent, current_task_summary, workflow
  - ✅ task_details, constraints, deliverables, backlog_notes
- ✅ Extension mechanism (custom attributes, namespaces)
- ✅ Test validation with example XML from Section 6 - PASSED
- ✅ Error detection working (invalid enum values rejected)

---

## Next Steps

1. Update `docs/architecture/native-orchestrator-spec.md` with Section C.4 (XML Handoff Protocol)
2. Integrate validation into `scripts/ops/session-manager.sh`
3. Create helper scripts for parsing handoff fields
4. Document XML handoff usage in Planning Agent persona
5. Test with pilot agents (DevOps, Backend, Test)

---

**Validation Status**: ALL TESTS PASSED
**Schema Version**: 1.0
**Ready for Integration**: YES
