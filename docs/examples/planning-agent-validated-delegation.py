"""
Planning Agent Validated Delegation Example

Demonstrates how Planning Agent uses instructor validation (Layer 5)
to generate quality-assured handoffs to specialist agents.

Location: /srv/projects/instructor-workflow/docs/examples/planning-agent-validated-delegation.py
"""

import instructor
from anthropic import Anthropic
from scripts.handoff_models import AgentHandoff, get_available_agents
import os


class PlanningAgentExample:
    """
    Planning Agent with Layer 5 validation integration.

    Shows how Planning Agent delegates to specialists using
    instructor-validated handoffs with automatic retry.
    """

    def __init__(self):
        """Initialize Planning Agent with instructor client."""
        # Layer 5: Initialize instructor client for validated handoff generation
        self.client = instructor.from_provider(
            "anthropic/claude-3-5-sonnet",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.available_agents = get_available_agents()

    def delegate_implementation(self, user_request: str) -> AgentHandoff:
        """
        Delegate implementation task to specialist agent.

        Uses instructor validation to ensure:
        - Valid agent selection
        - Clear task description
        - Repo-relative file paths
        - Testable acceptance criteria

        Args:
            user_request: User's feature request

        Returns:
            AgentHandoff: Validated handoff ready for agent spawning

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
2. Provide clear, specific task description (20+ chars, no vague terms)
3. Specify repo-relative file paths (no /home/, /Users/, /srv/)
4. Define testable acceptance criteria
5. Add context if needed (related issues, dependencies, constraints)

Agent selection guide:
- UI/frontend work → frontend
- API/backend/database → backend
- Infrastructure/CI/CD → devops
- Root cause analysis → debug
- Technical SEO → seo
- Test creation → test-writer
- Test quality audit → test-auditor
- Information gathering → research
- Git/Linear operations → tracking
"""

        # Generate validated handoff with automatic retry
        print("🔍 Generating validated handoff...")
        handoff = self.client.chat.completions.create(
            response_model=AgentHandoff,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_request}
            ],
            max_retries=3  # Automatic retry on validation failure
        )

        print("✅ Handoff validated successfully")
        return handoff

    def spawn_agent(self, handoff: AgentHandoff):
        """
        Spawn specialist agent with validated handoff.

        In production, this would:
        1. Create tmux session for agent
        2. Pass validated handoff data
        3. Monitor agent completion

        Args:
            handoff: Validated handoff from Planning Agent
        """
        print(f"\n🚀 Spawning {handoff.agent_name} agent")
        print(f"📝 Task: {handoff.task_description}")
        print(f"📁 Files: {', '.join(handoff.file_paths) if handoff.file_paths else 'N/A'}")
        print(f"✓ Criteria: {len(handoff.acceptance_criteria)} criteria")

        if handoff.context:
            print(f"📌 Context: {handoff.context}")

        # In production: spawn via tmux
        # Example: tmux new-session -d -s iw-{agent_name} "cd agents/{agent_name} && claude"


def example_frontend_delegation():
    """
    Example 1: Frontend authentication UI delegation
    """
    print("=" * 70)
    print("Example 1: Frontend Authentication UI")
    print("=" * 70)

    planner = PlanningAgentExample()

    user_request = """
    Implement JWT authentication UI for the React app.
    Users should be able to login with email/password.
    Store JWT token in localStorage after successful login.
    Protect dashboard routes from unauthenticated access.
    Display appropriate error messages on login failure.
    """

    try:
        handoff = planner.delegate_implementation(user_request)
        planner.spawn_agent(handoff)
        print("\n✅ Delegation successful\n")
    except Exception as e:
        print(f"\n❌ Delegation failed: {e}\n")


def example_backend_api_delegation():
    """
    Example 2: Backend API endpoint delegation
    """
    print("=" * 70)
    print("Example 2: Backend API Authentication")
    print("=" * 70)

    planner = PlanningAgentExample()

    user_request = """
    Create REST API endpoints for user authentication:
    - POST /api/auth/login - validate credentials, issue JWT
    - POST /api/auth/refresh - refresh expired token
    - POST /api/auth/logout - invalidate token

    Use bcrypt for password hashing.
    Use RS256 for JWT signing.
    Return appropriate HTTP status codes.
    """

    try:
        handoff = planner.delegate_implementation(user_request)
        planner.spawn_agent(handoff)
        print("\n✅ Delegation successful\n")
    except Exception as e:
        print(f"\n❌ Delegation failed: {e}\n")


def example_devops_delegation():
    """
    Example 3: DevOps infrastructure delegation
    """
    print("=" * 70)
    print("Example 3: DevOps CI/CD Pipeline")
    print("=" * 70)

    planner = PlanningAgentExample()

    user_request = """
    Set up GitHub Actions CI/CD pipeline:
    - Run linter on all PRs
    - Run test suite on all PRs
    - Deploy to staging on merge to main
    - Deploy to production on release tags
    - Send Slack notification on deployment failures
    """

    try:
        handoff = planner.delegate_implementation(user_request)
        planner.spawn_agent(handoff)
        print("\n✅ Delegation successful\n")
    except Exception as e:
        print(f"\n❌ Delegation failed: {e}\n")


def example_validation_failure():
    """
    Example 4: Demonstrate validation catching errors

    This would fail validation but instructor automatically retries
    with corrections based on validation error messages.
    """
    print("=" * 70)
    print("Example 4: Validation Auto-Correction (Simulated)")
    print("=" * 70)

    print("❌ Initial handoff (would fail validation):")
    print("  - agent_name: 'invalid-agent' (not in valid agents list)")
    print("  - task_description: 'fix stuff' (too vague)")
    print("  - file_paths: ['/home/user/project/src/main.py'] (absolute path)")
    print()
    print("🔄 Instructor automatically retries with corrections:")
    print("  - agent_name: 'backend' (valid agent)")
    print("  - task_description: 'Fix authentication token validation...' (specific)")
    print("  - file_paths: ['src/middleware/auth.py'] (repo-relative)")
    print()
    print("✅ Validation succeeds after auto-correction")
    print()


if __name__ == "__main__":
    """
    Run examples demonstrating Planning Agent validated delegation.

    Requirements:
    - ANTHROPIC_API_KEY environment variable set
    - instructor library installed (pip install instructor)

    Usage:
        python docs/examples/planning-agent-validated-delegation.py
    """

    print("\n" + "=" * 70)
    print("Planning Agent Validated Delegation Examples")
    print("Layer 5 Integration: Instructor Validation")
    print("=" * 70 + "\n")

    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    # Run examples
    example_frontend_delegation()
    example_backend_api_delegation()
    example_devops_delegation()
    example_validation_failure()

    print("=" * 70)
    print("Examples Complete")
    print("=" * 70)
    print()
    print("📚 For more details, see:")
    print("  - docs/instructor-validation-usage.md")
    print("  - docs/shared-ref-docs/agent-spawn-templates.md")
    print("  - scripts/handoff_models.py")
    print()
