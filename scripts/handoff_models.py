"""
IW Agent Handoff Validation Models

Location: /srv/projects/instructor-workflow/scripts/handoff_models.py

Usage:
    from scripts.handoff_models import AgentHandoff, validate_handoff

    # Via instructor client
    client = instructor.from_provider("anthropic/claude-3-5-sonnet")
    handoff = client.chat.completions.create(
        response_model=AgentHandoff,
        messages=[...],
        max_retries=3
    )

    # Direct validation
    handoff = validate_handoff({
        "agent_name": "action",
        "task_description": "Implement auth middleware",
        ...
    })
"""

# CRITICAL: Force CPU usage BEFORE any imports that load PyTorch
# This must be the first code executed (before pydantic, llm_guard, etc.)
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Hide CUDA devices, force CPU

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from pathlib import Path
import re
import logging
import hashlib

# LLM Guard for semantic prompt injection detection
from llm_guard.input_scanners import PromptInjection


# Module-level constant for available agents (single source of truth)
_AVAILABLE_AGENTS = {
    'action': 'General implementation (deprecated, prefer specialized agents)',
    'frontend': 'React/Vue/Next.js UI implementation',
    'backend': 'API development, database operations',
    'devops': 'Infrastructure, deployment, CI/CD',
    'debug': 'Root cause analysis, troubleshooting',
    'seo': 'Technical SEO, meta tags, structured data',
    'qa': 'Testing and validation (deprecated, use test-writer/test-auditor)',
    'test-writer': 'Write tests before implementation (TDD)',
    'test-auditor': 'Audit test quality, catch happy-path bias',
    'research': 'Information gathering, Linear issue creation',
    'tracking': 'Linear updates, git operations, PR creation',
    'browser': 'GUI operations, browser automation'
}

# Initialize LLM Guard prompt injection scanner (module-level for reuse)
# Threshold 0.7 = block if confidence > 70% that input is malicious
# Lower threshold = more sensitive (catches more attacks, may increase false positives)
# Higher threshold = less sensitive (fewer false positives, may miss sophisticated attacks)
_INJECTION_SCANNER = PromptInjection(threshold=0.7, use_onnx=False)


class AgentHandoff(BaseModel):
    """
    Agent handoff validation model for IW (Instructor Workflow).

    Validates Planning Agent delegations to specialist agents with:
    - Agent name validation (from available agents list)
    - Task description quality checks
    - File path validation (repo-relative, no hardcoded paths)
    - Acceptance criteria requirements
    - Cross-field consistency validation
    """

    agent_name: str = Field(
        description=(
            "Target agent name. Available agents: "
            "action (general implementation), "
            "frontend (React/Vue UI), "
            "backend (API/database), "
            "devops (infrastructure/CI/CD), "
            "debug (troubleshooting), "
            "seo (technical SEO), "
            "qa (testing/validation), "
            "research (information gathering), "
            "tracking (Linear/git operations), "
            "browser (GUI automation)"
        )
    )

    task_description: str = Field(
        min_length=20,
        description=(
            "Clear, specific task description. Include: "
            "WHAT to do, WHERE to do it, HOW to verify. "
            "Example: 'Implement JWT auth middleware in src/middleware/auth.ts, "
            "add unit tests, ensure 401 on invalid token.'"
        )
    )

    acceptance_criteria: list[str] = Field(
        default=[],
        description=(
            "List of acceptance criteria for task completion. "
            "Each criterion should be testable/verifiable. "
            "Example: '[ ] Middleware validates JWT tokens', "
            "'[ ] Returns 401 on invalid token', "
            "'[ ] Unit tests cover all auth flows'"
        )
    )

    context: Optional[str] = Field(
        default=None,
        description=(
            "Additional context for agent (optional). "
            "Include: related issues, dependencies, constraints, "
            "research findings, or special considerations."
        )
    )

    file_paths: list[str] = Field(
        default=[],
        description=(
            "Repo-relative file paths agent should work with. "
            "Examples: 'src/main.py', 'tests/test_api.py'. "
            "DO NOT use absolute paths (/home/, /Users/, /srv/, C:\\Users\\)."
        )
    )

    blockers: Optional[str] = Field(
        default=None,
        description=(
            "Known blockers or dependencies (optional). "
            "Example: 'Waiting on API keys', 'Blocked by LAW-123'"
        )
    )

    deliverables: list[str] = Field(
        default=[],
        description=(
            "Expected deliverables from agent (optional). "
            "Example: 'auth.ts middleware', 'unit tests', 'API documentation'"
        )
    )

    # --- FIELD VALIDATORS ---

    @field_validator('agent_name')
    @classmethod
    def validate_agent_name(cls, v: str) -> str:
        """
        Validate agent name against available agents list.

        Ensures agent name is from the valid set of specialist agents.
        Provides detailed error message with available agents if invalid.

        Args:
            v: Agent name to validate

        Returns:
            str: Validated and normalized agent name (lowercase)

        Raises:
            ValueError: If agent name not in valid agents list
        """
        v_lower = v.lower().strip()
        if v_lower not in _AVAILABLE_AGENTS:
            available = '\n'.join(f"  - {name}: {desc}" for name, desc in _AVAILABLE_AGENTS.items())
            raise ValueError(
                f"Invalid agent name '{v}'. Available agents:\n{available}\n\n"
                "Choose agent based on task type:\n"
                "  - UI work → 'frontend'\n"
                "  - API/database → 'backend'\n"
                "  - Testing → 'test-writer' or 'test-auditor'\n"
                "  - Research → 'research'\n"
                "  - Git/Linear → 'tracking'"
            )

        return v_lower

    @field_validator('task_description')
    @classmethod
    def validate_task_description(cls, v: str) -> str:
        """
        Validate task description is clear and specific.

        Checks for:
        - Minimum length (20 characters)
        - Vague terms that indicate unclear requirements
        - Provides guidance on writing clear task descriptions

        Args:
            v: Task description to validate

        Returns:
            str: Validated task description

        Raises:
            ValueError: If description too short or contains vague terms
        """
        if len(v) < 20:
            raise ValueError(
                f"Task description too short ({len(v)} chars). "
                "Provide detailed description (minimum 20 characters).\n\n"
                "Good description includes:\n"
                "  - WHAT: Specific action to take\n"
                "  - WHERE: Files or locations to modify\n"
                "  - HOW: Verification method or acceptance criteria\n\n"
                "Example: 'Implement JWT authentication middleware in src/middleware/auth.ts, "
                "add unit tests in tests/auth.test.ts, ensure 401 response on invalid token.'"
            )

        # Check for vague descriptions
        vague_patterns = [
            ('do something', 'Specify exactly what to do'),
            ('fix stuff', 'Describe what to fix and how'),
            ('update things', 'List specific files and changes'),
            ('make it work', 'Define working criteria'),
            ('handle it', 'Describe handling approach'),
            ('deal with', 'Specify action to take')
        ]

        v_lower = v.lower()
        found_vague = []
        for pattern, suggestion in vague_patterns:
            if pattern in v_lower:
                found_vague.append((pattern, suggestion))

        if found_vague:
            vague_list = '\n'.join(f"  - '{pattern}': {suggestion}" for pattern, suggestion in found_vague)
            raise ValueError(
                f"Task description contains vague patterns:\n{vague_list}\n\n"
                "Be specific:\n"
                "  ❌ 'Fix the auth stuff'\n"
                "  ✅ 'Fix JWT token validation in src/middleware/auth.ts "
                "to return 401 when token signature is invalid'"
            )

        # Check for prompt injection using LLM Guard (semantic detection)
        # NOTE: This replaces regex-based detection with ML model that understands context.
        # ML model can distinguish "Implement bash runner" (legitimate) from
        # "Execute bash command" (attack) based on semantic meaning, not just keywords.
        #
        # Defense-in-depth: This is Layer 2 validation. Primary injection defense should
        # be at Planning Agent input sanitization layer (Layer 1, before reaching Pydantic).

        try:
            # Scan task description for prompt injection
            # Returns: (sanitized_output, is_valid, risk_score)
            # - sanitized_output: Cleaned text (we don't use this)
            # - is_valid: False if risk_score > threshold (0.7)
            # - risk_score: 0.0-1.0 confidence that input is malicious
            _sanitized_output, is_valid, risk_score = _INJECTION_SCANNER.scan(
                prompt=v  # Scan the task description
            )

            if not is_valid:
                raise ValueError(
                    f"Potential prompt injection detected (OWASP LLM01).\n\n"
                    f"Risk score: {risk_score:.3f} (threshold: 0.7)\n"
                    f"Confidence: {risk_score * 100:.1f}% likely malicious\n\n"
                    "Security: Task description blocked to prevent context injection.\n\n"
                    "This ML model detected semantic patterns indicating:\n"
                    "  - Attempts to override agent instructions\n"
                    "  - Role manipulation attacks\n"
                    "  - Command injection patterns\n"
                    "  - Encoding-based obfuscation\n\n"
                    "If this is legitimate:\n"
                    "  1. Rephrase task description more clearly\n"
                    "  2. Avoid language that resembles attack patterns\n"
                    "  3. For CLI tools, describe WHAT to build, not HOW to execute\n"
                    "     Example: 'Design CLI command parser' instead of 'Execute bash commands'\n"
                    "  4. Contact security team if risk score seems incorrect"
                )
        except Exception as e:
            # SECURITY TRADE-OFF: Fail-open strategy
            #
            # We intentionally allow validation to proceed if LLM Guard scanner fails.
            # This prioritizes availability over security in edge cases (model load failures,
            # CUDA errors, out-of-memory, etc.).
            #
            # RISK: Malicious input can bypass injection detection during scanner outages.
            #
            # MITIGATION:
            # 1. Monitor scanner failure rate (logs/metrics below)
            # 2. Alert on sustained scanner failures (>1% failure rate)
            # 3. Consider fail-closed (raise exception) in production after proving reliability
            # 4. Audit logs retain task descriptions for post-incident analysis
            #
            # This decision favors uninterrupted agent operations while accepting temporary
            # security degradation. Review this trade-off based on your threat model.

            # If LLM Guard fails (model not loaded, etc.), fall back to basic validation
            # Don't block legitimate traffic due to scanner failures
            if "prompt injection" in str(e).lower():
                # Re-raise validation errors from our own ValueError above
                raise

            # Log scanner failure for monitoring/alerting
            logger = logging.getLogger(__name__)
            logger.warning(
                "LLM Guard injection scanner failed - validation proceeding without check",
                extra={
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'task_description_hash': hashlib.sha256(v.encode()).hexdigest(),
                    'fail_open': True,
                    'security_layer': 'injection_detection'
                }
            )

            # Log scanner failure but don't block (fail-open for availability)
            import warnings
            warnings.warn(
                f"LLM Guard scanner failed: {e}. Skipping injection check.",
                stacklevel=2  # Point to caller, not this line
            )

        return v

    @field_validator('file_paths')
    @classmethod
    def validate_file_paths(cls, v: list[str]) -> list[str]:
        """
        Validate file paths are repo-relative and secure.

        Checks for:
        - Absolute paths with hardcoded user or server directories
        - Parent directory traversal (..)
        - Mixed path separators

        Args:
            v: List of file paths to validate

        Returns:
            list[str]: Validated file paths

        Raises:
            ValueError: If any path is absolute, contains traversal, or has mixed separators
        """
        for path in v:
            # Reject absolute paths with hardcoded user or server directories
            forbidden_prefixes = ['/home/', '/Users/', 'C:\\Users\\', 'C:/Users/', '/srv/']
            for prefix in forbidden_prefixes:
                if path.startswith(prefix):
                    raise ValueError(
                        f"Path '{path}' contains hardcoded user or server directory.\n\n"
                        "Use repo-relative paths instead:\n"
                        "  ❌ '/home/user/project/src/main.py'\n"
                        "  ✅ 'src/main.py'\n\n"
                        "  ❌ 'C:\\Users\\user\\project\\tests\\test.py'\n"
                        "  ✅ 'tests/test.py'\n\n"
                        "Agent will resolve paths relative to project root."
                    )

            # Reject parent directory traversal (security)
            if '..' in path:
                raise ValueError(
                    f"Path '{path}' contains parent directory traversal (..).\n\n"
                    "Use direct repo-relative paths only:\n"
                    "  ❌ '../../../etc/passwd'\n"
                    "  ❌ 'src/../../config/secrets.json'\n"
                    "  ✅ 'src/main.py'\n"
                    "  ✅ 'config/app.json'\n\n"
                    "Security: Parent traversal blocked to prevent path injection."
                )

            # Check for common path separators (accept both)
            if '\\' in path and '/' in path:
                raise ValueError(
                    f"Path '{path}' mixes path separators.\n\n"
                    "Use consistent separators:\n"
                    "  ✅ 'src/components/Button.tsx' (forward slashes)\n"
                    "  ✅ 'src\\components\\Button.tsx' (backslashes)\n"
                    "  ❌ 'src/components\\Button.tsx' (mixed)\n\n"
                    "Prefer forward slashes (/) for cross-platform compatibility."
                )

        return v

    @field_validator('acceptance_criteria')
    @classmethod
    def validate_acceptance_criteria(cls, v: list[str]) -> list[str]:
        """
        Validate acceptance criteria are testable.

        Checks for:
        - Minimum length (5 characters per criterion)
        - Vague criteria that aren't testable

        Args:
            v: List of acceptance criteria to validate

        Returns:
            list[str]: Validated acceptance criteria

        Raises:
            ValueError: If criteria too short or vague
        """
        if not v:
            return v  # Optional field, empty list is valid

        for criterion in v:
            if len(criterion.strip()) < 5:
                raise ValueError(
                    f"Acceptance criterion too short: '{criterion}'\n\n"
                    "Each criterion should be specific and testable:\n"
                    "  ❌ 'Works'\n"
                    "  ❌ 'Fixed'\n"
                    "  ✅ '[ ] Middleware validates JWT signature'\n"
                    "  ✅ '[ ] Returns 401 on expired token'\n"
                    "  ✅ '[ ] Unit tests achieve 90% code coverage'"
                )

            # Check for vague criteria
            vague_terms = ['works', 'done', 'fixed', 'complete', 'good']
            if criterion.lower().strip() in vague_terms:
                raise ValueError(
                    f"Acceptance criterion too vague: '{criterion}'\n\n"
                    "Make criteria testable and specific:\n"
                    "  ❌ 'Auth works'\n"
                    "  ✅ 'Auth middleware returns 200 for valid tokens'\n\n"
                    "  ❌ 'Tests pass'\n"
                    "  ✅ 'All unit tests pass with >90% coverage'"
                )

        return v

    # --- MODEL VALIDATORS ---

    @model_validator(mode='after')
    def validate_capability_constraints(self):
        """
        Enforce agent capability boundaries (privilege escalation prevention).

        CRITICAL: This validator runs AFTER field validation completes (mode='after').
        Field validators run first, then model validators enforce cross-field constraints.

        Validates that spawning agent has permission to spawn target agent.
        Prevents attacks where compromised/malicious agent attempts to
        spawn higher-privileged agents.

        Capability matrix (spawner → allowed targets):
        - planning: ['*'] (universal capability - can spawn any agent)
        - qa: ['test-writer', 'test-auditor'] (only test-related agents)
        - test-writer: [] (no spawning capability)
        - test-auditor: [] (no spawning capability)
        - frontend: ['frontend', 'test-writer'] (can spawn self + tests)
        - backend: ['backend', 'test-writer', 'devops'] (can spawn self + tests + infra)
        - devops: ['devops', 'test-writer'] (can spawn self + tests)
        - research: [] (no spawning capability - information gathering only)
        - tracking: [] (no spawning capability - git/linear operations only)
        - browser: [] (no spawning capability - GUI automation only)

        Environment: Set IW_SPAWNING_AGENT to indicate which agent is delegating.

        Returns:
            Self: Validated model instance

        Raises:
            ValueError: If spawning agent lacks capability to spawn target agent
        """
        spawning_agent = os.getenv('IW_SPAWNING_AGENT')
        target_agent = self.agent_name

        # Capability matrix (spawner → allowed targets)
        # NOTE: This matrix is security-critical. Changes require security review.
        capability_matrix = {
            # Planning Agent: Universal capability (trusted coordinator)
            'planning': ['*'],

            # QA Agent: Can spawn test-related agents only
            'qa': ['test-writer', 'test-auditor'],

            # Implementation agents: Can spawn self + tests + related infra
            'frontend': ['frontend', 'test-writer'],
            'backend': ['backend', 'test-writer', 'devops'],
            'devops': ['devops', 'test-writer'],
            'debug': ['debug', 'test-writer'],
            'seo': ['seo', 'test-writer'],

            # Test agents: No spawning capability (leaf nodes)
            'test-writer': [],
            'test-auditor': [],

            # Research/tracking/browser: No spawning capability (specialized ops)
            'research': [],
            'tracking': [],
            'browser': [],

            # Deprecated agents (maintain for backward compatibility)
            'action': ['action', 'test-writer'],
        }

        # Get allowed targets for spawning agent
        allowed_targets = capability_matrix.get(spawning_agent, [])

        # Check if target is allowed
        # '*' = universal capability (planning agent)
        if '*' not in allowed_targets and target_agent not in allowed_targets:
            # Format allowed list for error message
            if not allowed_targets:
                allowed_str = "none (no spawning capability)"
            else:
                allowed_str = ', '.join(f"'{a}'" for a in allowed_targets)

            raise ValueError(
                f"Capability violation: '{spawning_agent}' cannot spawn '{target_agent}'.\n\n"
                f"Allowed targets for '{spawning_agent}': {allowed_str}\n\n"
                "Security: Prevents privilege escalation via agent spawning.\n\n"
                "This error indicates:\n"
                "  1. Wrong agent is attempting delegation (should be Planning Agent)\n"
                "  2. IW_SPAWNING_AGENT environment variable incorrectly set\n"
                "  3. Attack attempt (malicious agent trying to spawn privileged agent)\n\n"
                "If this is legitimate:\n"
                "  - Delegate through Planning Agent instead\n"
                "  - Update capability_matrix in handoff_models.py if new workflow requires it\n"
                "  - Contact security team for capability matrix changes"
            )

        # TODO(future): Add spawn graph depth limits
        # Prevent spawn chains (A spawns B spawns C spawns D...) from exceeding
        # depth limit (e.g., max 3 levels deep). This prevents:
        # - Infinite spawn loops (A → B → C → A)
        # - Resource exhaustion via deep spawn trees
        # - Attack vectors using spawn chain obfuscation
        # Implementation: Track spawn ancestry via IW_SPAWN_DEPTH env var,
        # reject if depth > IW_MAX_SPAWN_DEPTH (default: 3)

        return self

    @model_validator(mode='after')
    def validate_consistency(self):
        """
        Validate cross-field consistency.

        Checks:
        - Research/tracking agents don't have file_paths (SPECIFIC RULES FIRST)
        - Test-writer agent has acceptance_criteria (SPECIFIC RULES FIRST)
        - File-modifying agents have file_paths specified (GENERAL RULES SECOND)
        - Implementation tasks have acceptance_criteria (GENERAL RULES SECOND)

        Returns:
            Self: Validated model instance

        Raises:
            ValueError: If cross-field validation fails
        """

        # SPECIFIC RULES FIRST (agent-specific constraints)
        # These must be checked before general rules to avoid masking errors

        # Research agent should NOT have file paths (doesn't modify files)
        if self.agent_name == 'research' and self.file_paths:
            raise ValueError(
                "research agent should NOT have file_paths.\n\n"
                "Research agent gathers information and creates Linear issues.\n"
                "It does not modify files.\n\n"
                "Remove file_paths field or choose different agent:\n"
                "  - To modify docs → 'action' agent\n"
                "  - To update code → 'frontend', 'backend', or 'devops'\n"
                "  - To investigate only → 'research' (no file_paths)"
            )

        # Tracking agent should NOT have file paths (git ops only)
        if self.agent_name == 'tracking' and self.file_paths:
            raise ValueError(
                "tracking agent should NOT have file_paths.\n\n"
                "Tracking agent handles:\n"
                "  - Linear issue updates\n"
                "  - Git operations (commit, push, PR)\n"
                "  - Documentation archiving\n\n"
                "It does not modify source files.\n\n"
                "Remove file_paths or choose different agent:\n"
                "  - To modify files → 'action', 'frontend', 'backend', etc.\n"
                "  - To handle git/Linear → 'tracking' (no file_paths)"
            )

        # Test-writer agent should have acceptance criteria (defines test cases)
        if self.agent_name == 'test-writer' and not self.acceptance_criteria:
            raise ValueError(
                "test-writer agent requires acceptance_criteria.\n\n"
                "Acceptance criteria define what tests should verify:\n"
                "  [ ] Valid tokens pass authentication\n"
                "  [ ] Invalid tokens return 401\n"
                "  [ ] Expired tokens return 403\n"
                "  [ ] Missing tokens return 401\n\n"
                "Test-writer uses these to write test cases."
            )

        # GENERAL RULES SECOND (role-based constraints)
        # These are checked after specific rules to ensure proper error reporting

        # File-modifying agents should have file paths
        file_agents = ['action', 'frontend', 'backend', 'devops', 'debug', 'seo']
        if self.agent_name in file_agents:
            if not self.file_paths:
                raise ValueError(
                    f"Agent '{self.agent_name}' requires file_paths.\n\n"
                    f"Specify which files this agent should work with:\n"
                    "  Example for frontend: ['src/components/Auth.tsx', 'src/hooks/useAuth.ts']\n"
                    "  Example for backend: ['src/api/auth.py', 'src/models/user.py']\n"
                    "  Example for tests: ['tests/test_auth.py']\n\n"
                    "If agent doesn't know which files yet, use pattern: ['src/**/*.py']"
                )

        # Implementation tasks should have acceptance criteria
        # Use word boundary regex to avoid false positives (e.g., "implementation" contains "implement")
        impl_keywords = ['implement', 'create', 'build', 'develop', 'add', 'write']
        desc_lower = self.task_description.lower()
        has_impl = any(re.search(r'\b' + re.escape(kw) + r'\b', desc_lower) for kw in impl_keywords)

        if has_impl and not self.acceptance_criteria:
            raise ValueError(
                "Implementation tasks require acceptance_criteria.\n\n"
                "Define how to verify task completion:\n"
                "  ❌ Task description only\n"
                "  ✅ Task description + acceptance criteria\n\n"
                "Example acceptance criteria:\n"
                "  [ ] Middleware validates JWT signature\n"
                "  [ ] Returns 401 on invalid token\n"
                "  [ ] Returns 403 on expired token\n"
                "  [ ] Unit tests cover all auth flows\n"
                "  [ ] Integration tests verify end-to-end auth"
            )

        return self


# --- VALIDATION FUNCTIONS ---

def validate_handoff(data: dict, spawning_agent: str) -> AgentHandoff:
    """
    Validate handoff data and return AgentHandoff model.

    Args:
        data: Dictionary with handoff fields
        spawning_agent: Agent making the delegation (for capability validation)

    Returns:
        AgentHandoff: Validated handoff model

    Raises:
        ValidationError: If validation fails with detailed error messages

    Example:
        >>> handoff = validate_handoff({
        ...     "agent_name": "frontend",
        ...     "task_description": "Implement login form in src/components/Login.tsx",
        ...     "file_paths": ["src/components/Login.tsx"],
        ...     "acceptance_criteria": [
        ...         "[ ] Form validates email format",
        ...         "[ ] Form submits to /api/auth/login",
        ...         "[ ] Error messages display on failure"
        ...     ]
        ... }, spawning_agent='planning')
    """
    # Set spawning agent in environment for validator to access
    # NOTE: NOT thread-safe for concurrent validations from multiple threads.
    # os.environ is process-global state - concurrent validations can race.
    # For multi-threaded use, implement thread-local storage or pass via context.
    os.environ['IW_SPAWNING_AGENT'] = spawning_agent
    try:
        return AgentHandoff(**data)
    finally:
        # Clean up to prevent leakage to other validations
        os.environ.pop('IW_SPAWNING_AGENT', None)


def get_available_agents() -> dict[str, str]:
    """
    Get dictionary of available agent names and descriptions.

    Returns:
        dict: Agent name → description mapping

    Example:
        >>> agents = get_available_agents()
        >>> print(agents['frontend'])
        'React/Vue/Next.js UI implementation'
    """
    return _AVAILABLE_AGENTS.copy()


# --- EXAMPLE USAGE ---

if __name__ == "__main__":
    print("=== IW Agent Handoff Validation Examples ===\n")

    # Example 1: Valid handoff
    print("Example 1: Valid Frontend Handoff")
    print("-" * 50)
    valid_handoff = {
        "agent_name": "frontend",
        "task_description": (
            "Implement JWT authentication form in src/components/Login.tsx. "
            "Form should validate email format, submit to /api/auth/login, "
            "and display error messages on failure."
        ),
        "file_paths": [
            "src/components/Login.tsx",
            "src/hooks/useAuth.ts",
            "tests/Login.test.tsx"
        ],
        "acceptance_criteria": [
            "[ ] Form validates email format client-side",
            "[ ] Form submits credentials to /api/auth/login",
            "[ ] Error messages display for invalid credentials",
            "[ ] Success redirects to dashboard",
            "[ ] Unit tests cover all form interactions"
        ],
        "context": "Integrate with existing auth API from backend team (LAW-123)"
    }

    try:
        handoff = validate_handoff(valid_handoff, spawning_agent='planning')
        print("✅ Valid handoff:")
        print(f"  Agent: {handoff.agent_name}")
        print(f"  Task: {handoff.task_description[:50]}...")
        print(f"  Files: {len(handoff.file_paths)} files")
        print(f"  Criteria: {len(handoff.acceptance_criteria)} criteria")
        print()
    except Exception as e:
        print(f"❌ Validation failed: {e}\n")

    # Example 2: Invalid handoff (multiple errors)
    print("Example 2: Invalid Handoff (Multiple Errors)")
    print("-" * 50)
    invalid_handoff = {
        "agent_name": "invalid-agent",  # ❌ Not in valid agents list
        "task_description": "fix stuff",  # ❌ Too vague and too short
        "file_paths": ["/home/user/project/src/main.py"],  # ❌ Absolute path
    }

    try:
        validate_handoff(invalid_handoff, spawning_agent='planning')
        print("✅ Validation passed (unexpected!)")
    except Exception as e:
        print("❌ Expected validation failure:")
        print(f"  Error: {str(e)[:200]}...")
        print()

    # Example 3: Valid backend handoff
    print("Example 3: Valid Backend Handoff")
    print("-" * 50)
    backend_handoff = {
        "agent_name": "backend",
        "task_description": (
            "Implement JWT authentication middleware in src/middleware/auth.py "
            "that validates Bearer tokens, verifies signatures using RS256, "
            "checks expiration, and returns appropriate HTTP status codes."
        ),
        "file_paths": [
            "src/middleware/auth.py",
            "src/utils/jwt.py",
            "tests/test_auth_middleware.py"
        ],
        "acceptance_criteria": [
            "[ ] Middleware extracts Bearer token from Authorization header",
            "[ ] Middleware validates token signature using public key",
            "[ ] Returns 401 for invalid token",
            "[ ] Returns 403 for expired token",
            "[ ] Unit tests cover all success and failure paths"
        ],
        "context": "Use PyJWT library (version 2.8.0+). Public key in config/jwt_public_key.pem.",
        "deliverables": [
            "auth.py middleware module",
            "jwt.py utility functions",
            "Unit tests with 90%+ coverage"
        ]
    }

    try:
        handoff = validate_handoff(backend_handoff, spawning_agent='planning')
        print("✅ Valid handoff:")
        print(f"  Agent: {handoff.agent_name}")
        print(f"  Task: {handoff.task_description[:60]}...")
        print(f"  Files: {len(handoff.file_paths)} files")
        print(f"  Criteria: {len(handoff.acceptance_criteria)} criteria")
        print(f"  Deliverables: {len(handoff.deliverables)} deliverables")
        print()
    except Exception as e:
        print(f"❌ Validation failed: {e}\n")

    # Example 4: Invalid research handoff (wrong agent for file modification)
    print("Example 4: Invalid Research Handoff (File Modification)")
    print("-" * 50)
    invalid_research = {
        "agent_name": "research",
        "task_description": "Research authentication patterns and update docs/auth-patterns.md",
        "file_paths": ["docs/auth-patterns.md"]  # ❌ Research agent shouldn't modify files
    }

    try:
        validate_handoff(invalid_research, spawning_agent='planning')
        print("✅ Validation passed (unexpected!)")
    except Exception as e:
        print("❌ Expected validation failure:")
        print(f"  Error: {str(e)[:200]}...")
        print()

    print("=== Available Agents ===")
    print("-" * 50)
    agents = get_available_agents()
    for name, desc in agents.items():
        print(f"  {name:15} → {desc}")
