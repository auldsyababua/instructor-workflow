#!/usr/bin/env python3
"""
Instructor-based handoff validation for IW agents.
Layer 5 (Structural) - Validates handoff JSON structure with automatic retry.

Usage:
    python scripts/validate_handoff.py "Research current OpenTelemetry best practices for Lambda"

    Or for testing:
    python scripts/validate_handoff.py --test
"""
import instructor
import json
import sys
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import List, Literal
from datetime import datetime

# Initialize validated Anthropic client
try:
    client = instructor.from_provider(
        "anthropic/claude-3-haiku-20240307",
        mode=instructor.Mode.ANTHROPIC_TOOLS
    )
except Exception as e:
    print(f"Error initializing Instructor client: {e}")
    print("Ensure ANTHROPIC_API_KEY environment variable is set.")
    sys.exit(1)

class ResearchHandoff(BaseModel):
    """Validated handoff structure for Planning → Researcher."""
    target_agent: Literal["researcher-agent"] = "researcher-agent"
    task_description: str = Field(min_length=10, max_length=1000)
    research_question: str = Field(min_length=10, max_length=500)
    context_files: List[Path] = Field(default_factory=list)
    deliverable_path: Path = Field(default=Path("docs/.scratch/research-findings.md"))
    timebox_hours: int = Field(default=2, ge=1, le=8)
    priority: Literal["low", "medium", "high", "critical"] = "medium"

    @field_validator('context_files')
    @classmethod
    def validate_files_exist(cls, files: List[Path]) -> List[Path]:
        """Ensure all context files exist."""
        for f in files:
            if not f.exists():
                raise ValueError(f"Context file not found: {f}")
        return files

    @field_validator('deliverable_path')
    @classmethod
    def validate_deliverable_dir(cls, path: Path) -> Path:
        """Ensure deliverable directory exists or can be created."""
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

class ImplementationHandoff(BaseModel):
    """Validated handoff structure for Planning → Action (future)."""
    target_agent: Literal["action-agent"] = "action-agent"
    task_description: str = Field(min_length=10, max_length=1000)
    context_files: List[Path] = Field(default_factory=list)
    deliverable_path: Path
    acceptance_criteria: List[str] = Field(min_length=1)

    @field_validator('context_files')
    @classmethod
    def validate_files_exist(cls, files: List[Path]) -> List[Path]:
        for f in files:
            if not f.exists():
                raise ValueError(f"Context file not found: {f}")
        return files

def create_research_handoff(request: str) -> ResearchHandoff:
    """Generate validated research handoff with automatic retries."""
    return client.chat.completions.create(
        response_model=ResearchHandoff,
        messages=[
            {
                "role": "system",
                "content": "Generate validated agent handoffs for the IW (Instructor Workflow). "
                          "Planning Agent delegates research tasks to Researcher Agent via structured handoffs."
            },
            {
                "role": "user",
                "content": f"Create a research handoff for: {request}"
            }
        ],
        max_retries=3,
        max_tokens=1024
    )

def save_handoff(handoff: BaseModel, handoff_dir: Path = Path("handoffs")) -> Path:
    """Save validated handoff to file."""
    handoff_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    agent_name = handoff.target_agent.replace("-agent", "")
    filename = f"{agent_name}_{timestamp}.json"

    handoff_file = handoff_dir / filename
    handoff_file.write_text(handoff.model_dump_json(indent=2))

    return handoff_file

def test_validation():
    """Test handoff validation with known cases."""
    print("Testing handoff validation...")

    # Test 1: Valid research handoff
    print("\n1. Testing valid research handoff...")
    try:
        handoff = create_research_handoff(
            "Research current OpenTelemetry best practices for AWS Lambda observability"
        )
        print(f"✅ Valid handoff created: {handoff.research_question}")
        print(f"   Timebox: {handoff.timebox_hours} hours")
        print(f"   Priority: {handoff.priority}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test 2: Invalid research handoff (too short)
    print("\n2. Testing invalid handoff (too short description)...")
    try:
        handoff = create_research_handoff("Research it")
        print(f"❌ Should have failed validation: {handoff}")
    except Exception as e:
        print(f"✅ Correctly rejected: {e}")

    # Test 3: Handoff with context files
    print("\n3. Testing handoff with context files...")
    try:
        # Create a test context file
        test_file = Path("docs/.scratch/test-context.md")
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# Test Context\nSample context file")

        handoff = ResearchHandoff(
            task_description="Research Lambda observability with provided context",
            research_question="What are current best practices?",
            context_files=[test_file]
        )
        print(f"✅ Handoff with context files validated")
        print(f"   Context files: {[str(f) for f in handoff.context_files]}")

        # Cleanup
        test_file.unlink()
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test 4: Save and load handoff
    print("\n4. Testing handoff persistence...")
    try:
        handoff = create_research_handoff(
            "Research Instructor library integration patterns for multi-agent systems"
        )
        saved_path = save_handoff(handoff)
        print(f"✅ Handoff saved to: {saved_path}")

        # Verify it can be loaded
        loaded_data = json.loads(saved_path.read_text())
        print(f"✅ Handoff loaded successfully")
        print(f"   Task: {loaded_data['task_description'][:50]}...")
    except Exception as e:
        print(f"❌ Failed: {e}")

    print("\n✅ All tests completed")

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_handoff.py \"<research request>\"")
        print("       python scripts/validate_handoff.py --test")
        sys.exit(1)

    if sys.argv[1] == "--test":
        test_validation()
        sys.exit(0)

    request = " ".join(sys.argv[1:])

    try:
        print(f"Creating validated handoff for: {request}")
        handoff = create_research_handoff(request)

        saved_path = save_handoff(handoff)

        print(f"\n✅ Validated handoff created successfully!")
        print(f"\nTarget Agent: {handoff.target_agent}")
        print(f"Task: {handoff.task_description}")
        print(f"Research Question: {handoff.research_question}")
        print(f"Timebox: {handoff.timebox_hours} hours")
        print(f"Priority: {handoff.priority}")
        print(f"Deliverable: {handoff.deliverable_path}")
        print(f"\nHandoff saved to: {saved_path}")
        print(f"\nNext: Spawn researcher agent with:")
        print(f"  cd agents/researcher && claude --add-dir /srv/projects/instructor-workflow")

    except instructor.exceptions.InstructorRetryException as e:
        print(f"\n❌ Validation failed after {e.n_attempts} attempts:")
        print(f"   {e.last_exception}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error creating handoff: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
