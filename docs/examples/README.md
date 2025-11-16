# IW Integration Examples

This directory contains practical examples demonstrating Instructor Workflow (IW) patterns and integrations.

## Available Examples

### planning-agent-validated-delegation.py

**Purpose**: Demonstrates Layer 5 integration - how Planning Agent uses instructor validation to generate quality-assured handoffs to specialist agents.

**Features**:
- Automatic validation of agent names, task descriptions, file paths
- Automatic retry on validation failures with LLM self-correction
- Security checks (blocks absolute paths, parent traversal)
- Cross-field consistency validation

**Usage**:
```bash
# Set API key
export ANTHROPIC_API_KEY='your-key-here'

# Run examples
python docs/examples/planning-agent-validated-delegation.py
```

**Examples Included**:
1. Frontend authentication UI delegation
2. Backend API endpoint delegation
3. DevOps CI/CD pipeline delegation
4. Validation auto-correction demonstration

**Requirements**:
- Python 3.9+
- instructor library (`pip install instructor`)
- Anthropic API key

## Running Examples

### Prerequisites

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API Key**:
   ```bash
   export ANTHROPIC_API_KEY='your-anthropic-api-key'
   ```

3. **Verify Setup**:
   ```bash
   python3 -c "import instructor; print('Instructor installed')"
   ```

### Example Workflow

```bash
# 1. Set up environment
export ANTHROPIC_API_KEY='sk-ant-...'

# 2. Run Planning Agent delegation example
python docs/examples/planning-agent-validated-delegation.py

# 3. Review output
# - Validated handoffs generated
# - Agent selection based on task type
# - Automatic validation and retry
# - Security checks applied
```

## Understanding the Examples

### Layer 5 Integration Pattern

**OLD (Manual)**:
```python
# Manually construct handoff (error-prone)
delegation = {
    "agent_name": "frontend",  # Could be typo
    "task_description": "fix stuff",  # Vague
    "file_paths": ["/home/user/project/src/main.py"]  # Absolute!
}
```

**NEW (Validated)**:
```python
# Instructor validates and auto-retries
handoff = client.chat.completions.create(
    response_model=AgentHandoff,
    messages=[{"role": "user", "content": user_request}],
    max_retries=3
)
# Guaranteed valid handoff
```

### What Gets Validated

1. **Agent Names**: Must be from available agents list (frontend, backend, devops, etc.)
2. **Task Descriptions**: Min 20 chars, no vague terms ("fix stuff", "do something")
3. **File Paths**: Must be repo-relative (no /home/, /Users/, /srv/)
4. **Acceptance Criteria**: Must be testable, not vague ("works", "done")
5. **Cross-Field Consistency**:
   - File-modifying agents (frontend, backend) must have file_paths
   - Implementation tasks must have acceptance_criteria
   - Research/tracking agents should NOT have file_paths

### Automatic Retry Behavior

When validation fails:

1. **Validation Error**: Pydantic raises ValidationError with detailed message
2. **Error to LLM**: Instructor sends error message back to Claude
3. **LLM Self-Correction**: Claude regenerates handoff based on error guidance
4. **Retry**: Process repeats up to max_retries
5. **Success or Escalate**: Either succeeds or escalates to user after max attempts

**Example**:
```
Attempt 1: agent_name='invalid-agent' → ValidationError
           "Invalid agent name. Available: frontend, backend..."

Attempt 2: agent_name='frontend', task='fix stuff' → ValidationError
           "Task description too short. Provide detailed description..."

Attempt 3: agent_name='frontend', task='Implement login form...' → ✅ Success
```

## Related Documentation

- **Validation Models**: `/srv/projects/instructor-workflow/scripts/handoff_models.py`
- **Usage Guide**: `/srv/projects/instructor-workflow/docs/instructor-validation-usage.md`
- **Agent Templates**: `/srv/projects/instructor-workflow/docs/shared-ref-docs/agent-spawn-templates.md`
- **Planning Agent**: `/srv/projects/instructor-workflow/agents/planning/planning-agent.md`

## Adding New Examples

To add a new example:

1. **Create Python file** in `docs/examples/`
2. **Import validation models**: `from scripts.handoff_models import AgentHandoff`
3. **Document purpose**: Add docstring explaining what the example demonstrates
4. **Add to this README**: Update the "Available Examples" section

**Template**:
```python
"""
Example: [Brief description]

Demonstrates: [What IW pattern this shows]
"""

import instructor
from scripts.handoff_models import AgentHandoff
import os

def example_function():
    """Demonstrate [specific pattern]."""
    # Implementation
    pass

if __name__ == "__main__":
    # Run example
    example_function()
```

## Troubleshooting

**Error: "ANTHROPIC_API_KEY environment variable not set"**
- Solution: `export ANTHROPIC_API_KEY='your-key'`

**Error: "No module named 'instructor'"**
- Solution: `pip install instructor`

**Error: "ValidationError: Invalid agent name"**
- This is expected in validation examples
- Shows instructor catching errors before agent spawn

**Error: "Max retries reached"**
- LLM unable to generate valid handoff after retries
- Review prompt and validation requirements
- May need to simplify validation rules or improve prompt

## Performance Notes

**Token Usage**:
- Each validation attempt uses tokens for generation + validation
- max_retries=3 means maximum 4x token usage (1 initial + 3 retries)
- Recommended: Use max_retries=3 for production (balance cost/reliability)

**Retry Strategy**:
- Conservative (1 retry): Fast failure, low cost, development/debugging
- Standard (3 retries): Production recommended, handles most errors
- Aggressive (5 retries): Complex validations, high-value operations

## Contributing

To improve examples:

1. Test on clean environment (verify dependencies)
2. Include clear docstrings and comments
3. Handle errors gracefully
4. Add example to this README
5. Submit PR with examples tested

---

**Last Updated**: 2025-01-13
**Framework**: Instructor Workflow (IW)
**Maintained By**: DevOps Agent
