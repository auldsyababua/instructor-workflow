# Instructor Validation Usage Guide

**Layer 5**: Pydantic-based handoff validation with automatic retry

**Location**: `/srv/projects/instructor-workflow/scripts/handoff_models.py`

**Purpose**: Validate Planning Agent handoffs to specialist agents with automatic LLM self-correction on validation failures.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [How to Use in Planning Agent](#how-to-use-in-planning-agent)
3. [Example Integration Code](#example-integration-code)
4. [Common Validation Errors and Fixes](#common-validation-errors-and-fixes)
5. [Retry Strategy Recommendations](#retry-strategy-recommendations)
6. [Testing Validation](#testing-validation)

---

## Quick Start

### Installation

```bash
# Install dependencies
pip install instructor>=1.0.0 anthropic>=0.21.0

# Or use requirements.txt
pip install -r requirements.txt
```

### Basic Usage

```python
from scripts.handoff_models import validate_handoff

# Validate handoff data
handoff = validate_handoff({
    "agent_name": "frontend",
    "task_description": "Implement login form in src/components/Login.tsx",
    "file_paths": ["src/components/Login.tsx"],
    "acceptance_criteria": [
        "[ ] Form validates email format",
        "[ ] Form submits to /api/auth/login"
    ]
})

print(f"✅ Validated handoff to {handoff.agent_name} agent")
```

---

## How to Use in Planning Agent

### Pattern 1: Automatic Validation with Instructor (Recommended)

**Use Case**: Planning Agent generates handoffs via Claude API with automatic validation

```python
import instructor
from anthropic import Anthropic
from scripts.handoff_models import AgentHandoff
import os

# Initialize instructor client with Claude
client = instructor.from_provider(
    "anthropic/claude-3-5-sonnet",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Generate handoff with automatic validation
handoff = client.chat.completions.create(
    response_model=AgentHandoff,  # Pydantic model for validation
    messages=[
        {
            "role": "system",
            "content": (
                "You are Planning Agent for IW (Instructor Workflow). "
                "Generate handoff for specialist agent to complete user request."
            )
        },
        {
            "role": "user",
            "content": (
                "User requested: Implement JWT authentication in React. "
                "Create handoff for appropriate specialist agent."
            )
        }
    ],
    max_retries=3  # Retry up to 3 times on validation failure
)

# handoff is validated AgentHandoff instance
print(f"✅ Validated handoff to {handoff.agent_name} agent")
print(f"Task: {handoff.task_description}")
print(f"Files: {handoff.file_paths}")
print(f"Criteria: {handoff.acceptance_criteria}")
```

**How It Works**:
1. Claude generates handoff JSON
2. Instructor validates against AgentHandoff model
3. If validation fails → error message sent back to Claude
4. Claude regenerates handoff with corrections
5. Repeat until success or max_retries reached

**Advantages**:
- ✅ Automatic retry with LLM self-correction
- ✅ No manual error handling required
- ✅ Validation errors teach LLM proper format
- ✅ Best for production Planning Agent workflow

---

### Pattern 2: Manual Validation (Direct Validation)

**Use Case**: Planning Agent validates handoff JSON manually (no API call)

```python
from scripts.handoff_models import validate_handoff
from pydantic import ValidationError

# Handoff data from Planning Agent
handoff_data = {
    "agent_name": "frontend",
    "task_description": "Implement login form in src/components/Login.tsx",
    "file_paths": ["src/components/Login.tsx"],
    "acceptance_criteria": [
        "[ ] Form validates email format",
        "[ ] Form submits to /api/auth/login"
    ]
}

try:
    handoff = validate_handoff(handoff_data)
    print("✅ Handoff validated successfully")
    # Proceed to spawn agent with validated handoff
except ValidationError as e:
    print("❌ Validation failed:")
    for error in e.errors():
        field = error['loc'][0]
        message = error['msg']
        print(f"  - {field}: {message}")
    # Report validation errors to Planning Agent for correction
```

**Manual Retry Loop**:

```python
from scripts.handoff_models import validate_handoff
from pydantic import ValidationError

max_retries = 3
retry_count = 0

while retry_count < max_retries:
    try:
        handoff = validate_handoff(handoff_data)
        print("✅ Validation successful")
        break
    except ValidationError as e:
        retry_count += 1
        print(f"❌ Validation failed (attempt {retry_count}/{max_retries}):")

        # Extract error messages for correction
        error_messages = []
        for error in e.errors():
            field = error['loc'][0]
            message = error['msg']
            error_messages.append(f"{field}: {message}")
            print(f"  - {message}")

        if retry_count < max_retries:
            print("Retrying with corrections...")
            # Planning Agent regenerates handoff based on error messages
            # Update handoff_data with corrections
        else:
            print("❌ Max retries reached. Manual intervention required.")
            # Escalate to user or log for debugging
```

**Advantages**:
- ✅ Fine-grained control over retry logic
- ✅ Can log validation errors for debugging
- ✅ Useful for testing validation rules
- ✅ No API calls during validation

---

## Example Integration Code

### Complete Planning Agent Workflow

```python
"""
Planning Agent with Instructor Validation
"""

import instructor
from anthropic import Anthropic
from scripts.handoff_models import AgentHandoff, get_available_agents
import os


class PlanningAgent:
    """Planning Agent with validated handoff generation."""

    def __init__(self):
        """Initialize Planning Agent with instructor client."""
        self.client = instructor.from_provider(
            "anthropic/claude-3-5-sonnet",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.available_agents = get_available_agents()

    def delegate_to_specialist(self, user_request: str) -> AgentHandoff:
        """
        Delegate user request to appropriate specialist agent.

        Args:
            user_request: User's feature request or task

        Returns:
            AgentHandoff: Validated handoff to specialist agent

        Raises:
            ValidationError: If handoff cannot be validated after max retries
        """
        # Build system prompt with available agents
        agents_list = '\n'.join(
            f"- {name}: {desc}"
            for name, desc in self.available_agents.items()
        )

        system_prompt = f"""You are Planning Agent for IW (Instructor Workflow).

Your job: Analyze user request and create validated handoff for specialist agent.

Available agents:
{agents_list}

Handoff requirements:
1. Choose appropriate agent based on task type
2. Provide clear, specific task description (20+ chars)
3. Specify repo-relative file paths (no /home/, /Users/, /srv/)
4. Define testable acceptance criteria
5. Add context if needed (related issues, dependencies)

Choose agent wisely:
- UI work → frontend
- API/database → backend
- Infrastructure/CI/CD → devops
- Testing → test-writer or test-auditor
- Research → research
- Git/Linear → tracking
"""

        # Generate validated handoff
        handoff = self.client.chat.completions.create(
            response_model=AgentHandoff,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_request}
            ],
            max_retries=3
        )

        return handoff

    def spawn_agent(self, handoff: AgentHandoff):
        """
        Spawn specialist agent with validated handoff.

        Args:
            handoff: Validated handoff from Planning Agent
        """
        print(f"🚀 Spawning {handoff.agent_name} agent")
        print(f"Task: {handoff.task_description}")
        print(f"Files: {', '.join(handoff.file_paths)}")
        print(f"Criteria: {len(handoff.acceptance_criteria)} criteria")

        # Spawn agent via tmux or direct terminal
        # Implementation depends on IW spawning strategy


# --- USAGE EXAMPLE ---

if __name__ == "__main__":
    planner = PlanningAgent()

    # Example user request
    user_request = """
    Implement JWT authentication for the React app.
    Users should be able to login with email/password.
    Store JWT token in localStorage.
    Protect dashboard routes.
    """

    try:
        handoff = planner.delegate_to_specialist(user_request)
        print("✅ Handoff validated successfully")
        planner.spawn_agent(handoff)
    except Exception as e:
        print(f"❌ Failed to create handoff: {e}")
```

---

## Common Validation Errors and Fixes

### Error 1: Invalid Agent Name

**Error Message**:
```
Invalid agent name 'the-frontend'. Available agents:
  - action: General implementation
  - frontend: React/Vue/Next.js UI implementation
  - backend: API development, database operations
  ...
```

**Cause**: Agent name not in valid agents list

**Fix**:
```python
# ❌ WRONG
handoff_data = {
    "agent_name": "the-frontend",  # Invalid name
    ...
}

# ✅ RIGHT
handoff_data = {
    "agent_name": "frontend",  # Valid name from list
    ...
}
```

---

### Error 2: Task Description Too Short or Vague

**Error Message**:
```
Task description too short (10 chars). Provide detailed description (minimum 20 characters).

Good description includes:
  - WHAT: Specific action to take
  - WHERE: Files or locations to modify
  - HOW: Verification method or acceptance criteria
```

**Cause**: Description less than 20 chars or contains vague terms

**Fix**:
```python
# ❌ WRONG
handoff_data = {
    "task_description": "Fix login",  # Too short (10 chars)
    ...
}

# ❌ WRONG
handoff_data = {
    "task_description": "Fix stuff in the auth code",  # Vague term "stuff"
    ...
}

# ✅ RIGHT
handoff_data = {
    "task_description": (
        "Fix JWT token validation in src/middleware/auth.ts "
        "to return 401 when token signature is invalid"
    ),
    ...
}
```

---

### Error 3: Absolute File Paths

**Error Message**:
```
Path '/home/user/project/src/main.py' contains hardcoded user directory.

Use repo-relative paths instead:
  ❌ '/home/user/project/src/main.py'
  ✅ 'src/main.py'
```

**Cause**: File paths start with /home/, /Users/, C:\Users\, or /srv/

**Fix**:
```python
# ❌ WRONG
handoff_data = {
    "file_paths": [
        "/home/user/project/src/components/Login.tsx",
        "C:\\Users\\user\\project\\src\\auth.py"
    ],
    ...
}

# ✅ RIGHT
handoff_data = {
    "file_paths": [
        "src/components/Login.tsx",
        "src/middleware/auth.py"
    ],
    ...
}
```

---

### Error 4: Parent Directory Traversal

**Error Message**:
```
Path 'src/../../config/secrets.json' contains parent directory traversal (..).

Use direct repo-relative paths only:
  ❌ '../../../etc/passwd'
  ✅ 'config/secrets.json'

Security: Parent traversal blocked to prevent path injection.
```

**Cause**: File paths contain .. (security risk)

**Fix**:
```python
# ❌ WRONG
handoff_data = {
    "file_paths": [
        "src/../../config/secrets.json",  # Path traversal
        "../../../etc/passwd"  # Security risk
    ],
    ...
}

# ✅ RIGHT
handoff_data = {
    "file_paths": [
        "config/secrets.json",  # Direct path
        "src/middleware/auth.py"
    ],
    ...
}
```

---

### Error 5: File Agent Missing File Paths

**Error Message**:
```
Agent 'frontend' requires file_paths.

Specify which files this agent should work with:
  Example for frontend: ['src/components/Auth.tsx', 'src/hooks/useAuth.ts']
```

**Cause**: File-modifying agent (frontend, backend, devops) has empty file_paths

**Fix**:
```python
# ❌ WRONG
handoff_data = {
    "agent_name": "frontend",
    "task_description": "Implement login form",
    "file_paths": [],  # Missing file paths
    ...
}

# ✅ RIGHT
handoff_data = {
    "agent_name": "frontend",
    "task_description": "Implement login form in src/components/Login.tsx",
    "file_paths": ["src/components/Login.tsx"],  # Specify files
    ...
}
```

---

### Error 6: Implementation Task Missing Acceptance Criteria

**Error Message**:
```
Implementation tasks require acceptance_criteria.

Define how to verify task completion:
  ❌ Task description only
  ✅ Task description + acceptance criteria
```

**Cause**: Task contains "implement", "create", "build" but no acceptance_criteria

**Fix**:
```python
# ❌ WRONG
handoff_data = {
    "agent_name": "backend",
    "task_description": "Implement JWT authentication middleware",
    "file_paths": ["src/middleware/auth.py"],
    "acceptance_criteria": [],  # Missing criteria
}

# ✅ RIGHT
handoff_data = {
    "agent_name": "backend",
    "task_description": "Implement JWT authentication middleware",
    "file_paths": ["src/middleware/auth.py"],
    "acceptance_criteria": [
        "[ ] Middleware validates JWT signature",
        "[ ] Returns 401 on invalid token",
        "[ ] Unit tests cover all paths"
    ],
}
```

---

### Error 7: Research Agent with File Paths

**Error Message**:
```
research agent should NOT have file_paths.

Research agent gathers information and creates Linear issues.
It does not modify files.

Remove file_paths field or choose different agent:
  - To modify docs → 'action' agent
  - To investigate only → 'research' (no file_paths)
```

**Cause**: Research agent has file_paths (research doesn't modify files)

**Fix**:
```python
# ❌ WRONG
handoff_data = {
    "agent_name": "research",
    "task_description": "Research auth patterns and update docs",
    "file_paths": ["docs/auth-patterns.md"],  # Research doesn't modify
}

# ✅ RIGHT (Option 1: Remove file paths)
handoff_data = {
    "agent_name": "research",
    "task_description": "Research auth patterns for JWT implementation",
    # No file_paths - research creates Linear issue with findings
}

# ✅ RIGHT (Option 2: Use action agent for file modification)
handoff_data = {
    "agent_name": "action",
    "task_description": "Update auth patterns docs based on research (LAW-123)",
    "file_paths": ["docs/auth-patterns.md"],
    "acceptance_criteria": ["[ ] Docs updated with JWT patterns"]
}
```

---

## Retry Strategy Recommendations

### Conservative (1 Retry)

**Use Case**: Development, debugging, cost-sensitive

```python
handoff = client.chat.completions.create(
    response_model=AgentHandoff,
    messages=[...],
    max_retries=1  # Fail fast, report to user
)
```

**Pros**:
- ✅ Low cost (max 2x token usage)
- ✅ Fast failure for debugging
- ✅ Forces prompt engineering improvements

**Cons**:
- ❌ May fail on minor LLM mistakes
- ❌ Less forgiving for complex validations

---

### Standard (3 Retries) - RECOMMENDED

**Use Case**: Production Planning Agent

```python
handoff = client.chat.completions.create(
    response_model=AgentHandoff,
    messages=[...],
    max_retries=3  # Balance between correction and cost
)
```

**Pros**:
- ✅ Handles most validation errors with self-correction
- ✅ Reasonable cost (max 4x token usage)
- ✅ Good balance for production use

**Cons**:
- ❌ Still fails on persistent validation issues
- ❌ Higher cost than conservative approach

---

### Aggressive (5 Retries)

**Use Case**: Complex validations, high-value operations

```python
handoff = client.chat.completions.create(
    response_model=AgentHandoff,
    messages=[...],
    max_retries=5  # Use for complex validations
)
```

**Pros**:
- ✅ Maximum chance of successful validation
- ✅ Handles complex cross-field validations

**Cons**:
- ❌ High cost (max 6x token usage)
- ❌ Slower due to multiple retries
- ❌ May mask prompt engineering issues

---

### When to Escalate to User

**Escalation Triggers**:
1. Max retries reached without success
2. Same validation error repeats across retries
3. LLM generates nonsensical corrections

**Escalation Strategy**:

```python
try:
    handoff = client.chat.completions.create(
        response_model=AgentHandoff,
        messages=[...],
        max_retries=3
    )
except Exception as e:
    # Log validation errors
    print(f"❌ Validation failed after {max_retries} retries")
    print(f"Last error: {e}")

    # Notify user with helpful message
    user_message = f"""
    Failed to create valid handoff after {max_retries} attempts.

    Last validation error:
    {e}

    Please review your request and try again with:
    - More specific task description
    - Clear file paths
    - Testable acceptance criteria
    """

    print(user_message)
    # Or send to user via UI/chat
```

---

## Testing Validation

### Run Test Suite

```bash
# Run all tests
pytest scripts/test_handoff_validation.py -v

# Run with coverage
pytest scripts/test_handoff_validation.py -v --cov=scripts.handoff_models

# Generate HTML coverage report
pytest scripts/test_handoff_validation.py --cov=scripts.handoff_models --cov-report=html
```

### Test Categories

**Valid Handoffs**:
- Frontend handoff with all fields
- Backend handoff with deliverables
- Research handoff without file paths
- DevOps handoff with infrastructure files
- Test-writer handoff with acceptance criteria

**Invalid Agent Names**:
- Invalid agent name
- Typo in agent name
- Case sensitivity

**Invalid Task Descriptions**:
- Too short (< 20 chars)
- Vague terms ("fix stuff", "do something")

**Invalid File Paths**:
- Absolute paths (/home/, /Users/, C:\Users\)
- Parent directory traversal (..)
- Mixed path separators

**Invalid Acceptance Criteria**:
- Too short (< 5 chars)
- Vague terms ("works", "done", "fixed")

**Cross-Field Validation**:
- File agent missing file_paths
- Implementation task missing acceptance_criteria
- Research agent with file_paths
- Tracking agent with file_paths

**Retry Behavior**:
- Retry with corrected agent name
- Retry with more specific description
- Retry with repo-relative paths

### Manual Testing

```python
# Test valid handoff
from scripts.handoff_models import validate_handoff

handoff = validate_handoff({
    "agent_name": "frontend",
    "task_description": "Implement login form with validation",
    "file_paths": ["src/components/Login.tsx"],
    "acceptance_criteria": ["[ ] Form validates email"]
})

print(f"✅ Agent: {handoff.agent_name}")
```

```python
# Test invalid handoff
from scripts.handoff_models import validate_handoff
from pydantic import ValidationError

try:
    validate_handoff({
        "agent_name": "invalid-agent",
        "task_description": "fix stuff",
        "file_paths": ["/home/user/project/src/main.py"]
    })
except ValidationError as e:
    print("❌ Expected validation errors:")
    for error in e.errors():
        print(f"  - {error['loc'][0]}: {error['msg'][:100]}...")
```

---

## Summary

**Layer 5 (Instructor Validation)** provides:

1. ✅ **Automatic Validation**: Pydantic models validate handoff structure
2. ✅ **Automatic Retry**: LLM self-corrects based on validation errors
3. ✅ **Instructive Errors**: Error messages teach Planning Agent proper format
4. ✅ **Security Checks**: Blocks absolute paths, parent traversal, hardcoded dirs
5. ✅ **Cross-Field Consistency**: Validates relationships between fields
6. ✅ **Comprehensive Testing**: 40+ test cases covering all validation rules

**Best Practices**:
- Use **Pattern 1** (Automatic Validation) for production Planning Agent
- Configure **max_retries=3** for standard validation
- Monitor retry counts and escalate persistent failures to user
- Run test suite regularly to catch validation regressions
- Update validators when adding new agents or validation rules

**Next Steps**:
1. Integrate validation into Planning Agent workflow
2. Test with real user requests
3. Monitor validation failures and improve error messages
4. Add new validators as needed for domain-specific rules

---

**Documentation Version**: 1.0
**Last Updated**: 2025-11-13
**Framework**: Instructor Workflow (IW)
