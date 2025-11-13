"""
Test Suite for IW Agent Handoff Validation

Location: /srv/projects/instructor-workflow/scripts/test_handoff_validation.py

Run tests:
    pytest scripts/test_handoff_validation.py -v
    pytest scripts/test_handoff_validation.py -v --cov=scripts.handoff_models

Coverage:
    pytest scripts/test_handoff_validation.py --cov=scripts.handoff_models --cov-report=html
"""

import pytest
from pydantic import ValidationError
from scripts.handoff_models import AgentHandoff, validate_handoff, get_available_agents


# --- VALID HANDOFF TESTS ---

class TestValidHandoffs:
    """Test valid handoffs that should pass validation."""

    def test_valid_frontend_handoff(self):
        """Test valid frontend handoff with all required fields."""
        handoff_data = {
            "agent_name": "frontend",
            "task_description": (
                "Implement login form in src/components/Login.tsx with "
                "email validation, password field, and submit handler."
            ),
            "file_paths": [
                "src/components/Login.tsx",
                "src/hooks/useAuth.ts"
            ],
            "acceptance_criteria": [
                "[ ] Form validates email format",
                "[ ] Form submits to /api/auth/login",
                "[ ] Error messages display on failure"
            ],
            "context": "Integrate with auth API from LAW-123"
        }

        handoff = validate_handoff(handoff_data)

        assert handoff.agent_name == "frontend"
        assert len(handoff.file_paths) == 2
        assert len(handoff.acceptance_criteria) == 3
        assert handoff.context is not None

    def test_valid_backend_handoff(self):
        """Test valid backend handoff with deliverables."""
        handoff_data = {
            "agent_name": "backend",
            "task_description": (
                "Implement JWT authentication middleware in src/middleware/auth.py "
                "that validates Bearer tokens and returns 401 on invalid tokens."
            ),
            "file_paths": [
                "src/middleware/auth.py",
                "tests/test_auth.py"
            ],
            "acceptance_criteria": [
                "[ ] Middleware validates JWT signature",
                "[ ] Returns 401 on invalid token",
                "[ ] Unit tests cover all paths"
            ],
            "deliverables": [
                "auth.py middleware",
                "Unit tests"
            ]
        }

        handoff = validate_handoff(handoff_data)

        assert handoff.agent_name == "backend"
        assert len(handoff.deliverables) == 2

    def test_valid_research_handoff_no_files(self):
        """Test valid research handoff without file paths."""
        handoff_data = {
            "agent_name": "research",
            "task_description": (
                "Research authentication patterns for JWT implementation. "
                "Document findings in Linear issue with examples and recommendations."
            )
        }

        handoff = validate_handoff(handoff_data)

        assert handoff.agent_name == "research"
        assert handoff.file_paths == []

    def test_valid_devops_handoff(self):
        """Test valid devops handoff with infrastructure files."""
        handoff_data = {
            "agent_name": "devops",
            "task_description": (
                "Create GitHub Actions CI/CD pipeline in .github/workflows/deploy.yml "
                "that runs tests, builds Docker image, and deploys to production."
            ),
            "file_paths": [
                ".github/workflows/deploy.yml",
                "Dockerfile",
                "docker-compose.yml"
            ],
            "acceptance_criteria": [
                "[ ] Pipeline runs on push to main",
                "[ ] Tests execute before build",
                "[ ] Docker image built and pushed",
                "[ ] Deployment succeeds to prod"
            ]
        }

        handoff = validate_handoff(handoff_data)

        assert handoff.agent_name == "devops"
        assert len(handoff.file_paths) == 3

    def test_valid_test_writer_handoff(self):
        """Test valid test-writer handoff with acceptance criteria."""
        handoff_data = {
            "agent_name": "test-writer",
            "task_description": (
                "Write unit tests for JWT authentication middleware in "
                "tests/test_auth_middleware.py covering all success and failure paths."
            ),
            "file_paths": [
                "tests/test_auth_middleware.py"
            ],
            "acceptance_criteria": [
                "[ ] Valid tokens pass authentication",
                "[ ] Invalid tokens return 401",
                "[ ] Expired tokens return 403",
                "[ ] Missing tokens return 401"
            ]
        }

        handoff = validate_handoff(handoff_data)

        assert handoff.agent_name == "test-writer"
        assert len(handoff.acceptance_criteria) == 4


# --- INVALID AGENT NAME TESTS ---

class TestInvalidAgentNames:
    """Test invalid agent names trigger appropriate errors."""

    def test_invalid_agent_name(self):
        """Test invalid agent name triggers validation error."""
        handoff_data = {
            "agent_name": "invalid-agent",
            "task_description": "Do something with authentication code in multiple files",
            "file_paths": ["src/auth.py"]
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "Invalid agent name 'invalid-agent'" in error_msg
        assert "Available agents:" in error_msg

    def test_typo_in_agent_name(self):
        """Test typo in agent name triggers helpful error."""
        handoff_data = {
            "agent_name": "frontent",  # Typo: missing 't'
            "task_description": "Implement UI component in src/components/Button.tsx",
            "file_paths": ["src/components/Button.tsx"]
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "frontent" in error_msg
        assert "frontend" in error_msg.lower()

    def test_case_insensitive_agent_name(self):
        """Test agent name is case-insensitive."""
        handoff_data = {
            "agent_name": "FRONTEND",  # Uppercase
            "task_description": "Implement login form in src/components/Login.tsx",
            "file_paths": ["src/components/Login.tsx"],
            "acceptance_criteria": ["[ ] Form renders correctly"]
        }

        handoff = validate_handoff(handoff_data)

        assert handoff.agent_name == "frontend"  # Normalized to lowercase


# --- INVALID TASK DESCRIPTION TESTS ---

class TestInvalidTaskDescriptions:
    """Test invalid task descriptions trigger appropriate errors."""

    def test_task_description_too_short(self):
        """Test task description shorter than 20 chars fails."""
        handoff_data = {
            "agent_name": "frontend",
            "task_description": "Fix login",  # Only 10 chars
            "file_paths": ["src/components/Login.tsx"]
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "too_short" in error_msg.lower()

    def test_vague_task_description_fix_stuff(self):
        """Test vague 'fix stuff' description fails."""
        handoff_data = {
            "agent_name": "backend",
            "task_description": "Just fix stuff in the authentication code",
            "file_paths": ["src/auth.py"]
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "contains vague patterns" in error_msg.lower()
        assert "fix stuff" in error_msg.lower()
        assert "Describe what to fix and how" in error_msg

    def test_vague_task_description_do_something(self):
        """Test vague 'do something' description fails."""
        handoff_data = {
            "agent_name": "frontend",
            "task_description": "Do something with the login form component",
            "file_paths": ["src/components/Login.tsx"]
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "contains vague patterns" in error_msg.lower()
        assert "do something" in error_msg.lower()
        assert "Specify exactly what to do" in error_msg


# --- INVALID FILE PATH TESTS ---

class TestInvalidFilePaths:
    """Test invalid file paths trigger appropriate errors."""

    def test_absolute_path_linux_home(self):
        """Test absolute path with /home/ prefix fails."""
        handoff_data = {
            "agent_name": "frontend",
            "task_description": "Implement login form component with validation",
            "file_paths": ["/home/user/project/src/components/Login.tsx"]
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "hardcoded user or server directory" in error_msg.lower()
        assert "/home/user" in error_msg

    def test_absolute_path_windows_users(self):
        """Test absolute path with C:\\Users\\ prefix fails."""
        handoff_data = {
            "agent_name": "backend",
            "task_description": "Implement authentication middleware in backend",
            "file_paths": ["C:\\Users\\user\\project\\src\\auth.py"]
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "hardcoded user or server directory" in error_msg.lower()

    def test_absolute_path_srv(self):
        """Test absolute path with /srv/ prefix fails."""
        handoff_data = {
            "agent_name": "devops",
            "task_description": "Create deployment configuration for production",
            "file_paths": ["/srv/projects/app/deploy.yml"]
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "hardcoded user or server directory" in error_msg.lower()

    def test_parent_directory_traversal(self):
        """Test parent directory traversal (..) fails."""
        handoff_data = {
            "agent_name": "backend",
            "task_description": "Implement configuration loader for application",
            "file_paths": ["src/../../config/secrets.json"]
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "parent directory traversal" in error_msg.lower()
        assert ".." in error_msg

    def test_mixed_path_separators(self):
        """Test mixed path separators fails."""
        handoff_data = {
            "agent_name": "frontend",
            "task_description": "Implement button component with hover effects",
            "file_paths": ["src/components\\Button/index.tsx"]  # Mixed / and \\
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "mixes path separators" in error_msg.lower()


# --- INVALID ACCEPTANCE CRITERIA TESTS ---

class TestInvalidAcceptanceCriteria:
    """Test invalid acceptance criteria trigger appropriate errors."""

    def test_acceptance_criteria_too_short(self):
        """Test acceptance criterion shorter than 5 chars fails."""
        handoff_data = {
            "agent_name": "frontend",
            "task_description": "Implement login form with validation and error handling",
            "file_paths": ["src/components/Login.tsx"],
            "acceptance_criteria": ["OK"]  # Only 2 chars
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "too short" in error_msg.lower()
        assert "OK" in error_msg

    def test_vague_acceptance_criteria_works(self):
        """Test vague 'works' criterion fails."""
        handoff_data = {
            "agent_name": "backend",
            "task_description": "Implement JWT authentication middleware for API",
            "file_paths": ["src/middleware/auth.py"],
            "acceptance_criteria": ["works"]
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "too vague" in error_msg.lower()
        assert "works" in error_msg.lower()

    def test_vague_acceptance_criteria_done(self):
        """Test vague 'done' criterion fails."""
        handoff_data = {
            "agent_name": "frontend",
            "task_description": "Implement authentication form with validation",
            "file_paths": ["src/components/Login.tsx"],
            "acceptance_criteria": ["done"]
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "too short" in error_msg.lower()
        assert "done" in error_msg.lower()


# --- CROSS-FIELD VALIDATION TESTS ---

class TestCrossFieldValidation:
    """Test cross-field consistency validation."""

    def test_file_agent_requires_file_paths(self):
        """Test file-modifying agent without file_paths fails."""
        handoff_data = {
            "agent_name": "frontend",
            "task_description": "Implement login form with email and password fields",
            "file_paths": []  # ❌ Empty file paths for file agent
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "requires file_paths" in error_msg.lower()
        assert "frontend" in error_msg

    def test_implementation_task_requires_acceptance_criteria(self):
        """Test implementation task without acceptance criteria fails."""
        handoff_data = {
            "agent_name": "backend",
            "task_description": "Implement JWT authentication middleware in src/middleware/auth.py",
            "file_paths": ["src/middleware/auth.py"],
            "acceptance_criteria": []  # ❌ No criteria for implementation
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "require acceptance_criteria" in error_msg.lower()
        assert "implementation" in error_msg.lower()

    def test_test_writer_requires_acceptance_criteria(self):
        """Test test-writer agent without acceptance criteria fails."""
        handoff_data = {
            "agent_name": "test-writer",
            "task_description": "Write unit tests for authentication middleware",
            "file_paths": ["tests/test_auth.py"],
            "acceptance_criteria": []  # ❌ No criteria for test-writer
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "test-writer" in error_msg.lower()
        assert "requires acceptance_criteria" in error_msg.lower()

    def test_research_agent_cannot_have_file_paths(self):
        """Test research agent with file_paths fails."""
        handoff_data = {
            "agent_name": "research",
            "task_description": "Research authentication patterns for JWT implementation",
            "file_paths": ["docs/auth-patterns.md"]  # ❌ Research doesn't modify files
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "research agent" in error_msg.lower()
        assert "should not have file_paths" in error_msg.lower()

    def test_tracking_agent_cannot_have_file_paths(self):
        """Test tracking agent with file_paths fails."""
        handoff_data = {
            "agent_name": "tracking",
            "task_description": "Update Linear issue and create PR for authentication feature",
            "file_paths": ["src/auth.py"]  # ❌ Tracking doesn't modify source files
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data)

        error_msg = str(exc_info.value)
        assert "tracking agent" in error_msg.lower()
        assert "should not have file_paths" in error_msg.lower()


# --- UTILITY FUNCTIONS TESTS ---

class TestUtilityFunctions:
    """Test utility functions."""

    def test_get_available_agents(self):
        """Test get_available_agents returns correct agents."""
        agents = get_available_agents()

        assert isinstance(agents, dict)
        assert "frontend" in agents
        assert "backend" in agents
        assert "devops" in agents
        assert "research" in agents
        assert "tracking" in agents
        assert len(agents) > 5

    def test_get_available_agents_has_descriptions(self):
        """Test each agent has a description."""
        agents = get_available_agents()

        for name, desc in agents.items():
            assert isinstance(name, str)
            assert isinstance(desc, str)
            assert len(desc) > 10  # Description should be meaningful


# --- EDGE CASES TESTS ---

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_acceptance_criteria_allowed(self):
        """Test empty acceptance criteria is valid for non-implementation tasks."""
        handoff_data = {
            "agent_name": "research",
            "task_description": "Research authentication patterns for JWT implementation",
            "acceptance_criteria": []  # Empty is OK for research
        }

        handoff = validate_handoff(handoff_data)

        assert handoff.acceptance_criteria == []

    def test_optional_fields_can_be_none(self):
        """Test optional fields can be None."""
        handoff_data = {
            "agent_name": "research",
            "task_description": "Research authentication patterns for JWT implementation",
            "context": None,
            "blockers": None
        }

        handoff = validate_handoff(handoff_data)

        assert handoff.context is None
        assert handoff.blockers is None

    def test_task_description_exactly_20_chars(self):
        """Test task description with exactly 20 chars passes."""
        handoff_data = {
            "agent_name": "research",
            "task_description": "x" * 20,  # Exactly 20 chars
        }

        handoff = validate_handoff(handoff_data)

        assert len(handoff.task_description) == 20

    def test_whitespace_stripped_from_agent_name(self):
        """Test whitespace is stripped from agent name."""
        handoff_data = {
            "agent_name": "  frontend  ",  # Whitespace around name
            "task_description": "Implement button component with hover effects",
            "file_paths": ["src/components/Button.tsx"],
            "acceptance_criteria": ["[ ] Button renders correctly"]
        }

        handoff = validate_handoff(handoff_data)

        assert handoff.agent_name == "frontend"  # Stripped and normalized


# --- RETRY BEHAVIOR SIMULATION ---

class TestRetryBehavior:
    """Test retry behavior with multiple validation attempts."""

    def test_retry_with_corrected_agent_name(self):
        """Simulate retry with corrected agent name."""
        # First attempt: Invalid agent name
        invalid_data = {
            "agent_name": "the-frontend",
            "task_description": "Implement login form with validation",
            "file_paths": ["src/components/Login.tsx"]
        }

        with pytest.raises(ValidationError):
            validate_handoff(invalid_data)

        # Second attempt: Corrected agent name
        corrected_data = {
            "agent_name": "frontend",  # ✅ Corrected
            "task_description": "Implement login form with validation and error handling",
            "file_paths": ["src/components/Login.tsx"],
            "acceptance_criteria": ["[ ] Form validates email format"]
        }

        handoff = validate_handoff(corrected_data)

        assert handoff.agent_name == "frontend"

    def test_retry_with_more_specific_description(self):
        """Simulate retry with more specific task description."""
        # First attempt: Too vague
        vague_data = {
            "agent_name": "backend",
            "task_description": "fix the auth stuff",
            "file_paths": ["src/auth.py"]
        }

        with pytest.raises(ValidationError):
            validate_handoff(vague_data)

        # Second attempt: More specific
        specific_data = {
            "agent_name": "backend",
            "task_description": (
                "Fix JWT token validation in src/middleware/auth.py to "
                "return 401 when token signature is invalid"
            ),
            "file_paths": ["src/middleware/auth.py"],
            "acceptance_criteria": [
                "[ ] Invalid signatures return 401",
                "[ ] Valid signatures pass through"
            ]
        }

        handoff = validate_handoff(specific_data)

        assert handoff.agent_name == "backend"
        assert len(handoff.acceptance_criteria) == 2

    def test_retry_with_repo_relative_paths(self):
        """Simulate retry with corrected repo-relative paths."""
        # First attempt: Absolute paths
        absolute_paths_data = {
            "agent_name": "frontend",
            "task_description": "Implement login form with email validation",
            "file_paths": ["/home/user/project/src/components/Login.tsx"]
        }

        with pytest.raises(ValidationError):
            validate_handoff(absolute_paths_data)

        # Second attempt: Repo-relative paths
        relative_paths_data = {
            "agent_name": "frontend",
            "task_description": "Implement login form with email validation",
            "file_paths": ["src/components/Login.tsx"],  # ✅ Corrected
            "acceptance_criteria": ["[ ] Form validates email format"]
        }

        handoff = validate_handoff(relative_paths_data)

        assert handoff.file_paths == ["src/components/Login.tsx"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
