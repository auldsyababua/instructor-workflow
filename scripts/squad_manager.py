#!/usr/bin/env python3
"""
SquadManager - Programmatic interface for claude-squad agent spawning

This class provides Python integration with claude-squad's tmux-based
multi-agent orchestration system. It enables:

- Spawning specialized agents (tracking, dev, orchestration)
- Monitoring agent execution status
- Waiting for parallel agent completion
- Cleanup and session management

Usage:
    manager = SquadManager()

    # Spawn tracking agent
    tracking_session = manager.spawn_agent(
        agent_type="tracking",
        task_id=123,
        prompt="Update Linear issues based on recent commits"
    )

    # Wait for completion
    manager.wait_for_agents([tracking_session], timeout=600)

    # Cleanup
    manager.cleanup()
"""

import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class AgentType(Enum):
    """Supported agent types with their tool permissions"""
    TRACKING = "tracking"
    DEV = "dev"
    ORCHESTRATION = "orchestration"
    PLANNING = "planning"
    QA = "qa"
    RESEARCH = "research"


class AgentStatus(Enum):
    """Agent execution states"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class AgentInfo:
    """Information about a spawned agent"""
    agent_type: AgentType
    task_id: int
    session_id: str
    prompt: str
    status: AgentStatus
    started: float
    log_file: Optional[Path] = None
    result: Optional[str] = None


class SquadManager:
    """Manages claude-squad agent lifecycle for IW deployment"""

    def __init__(self, squad_session: str = "claude-squad", logs_dir: str = "logs"):
        """
        Initialize SquadManager

        Args:
            squad_session: Name of the tmux session running claude-squad TUI
            logs_dir: Directory to store agent execution logs
        """
        self.squad_session = squad_session
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        self.active_agents: Dict[str, AgentInfo] = {}

    def spawn_agent(
        self,
        agent_type: str,
        task_id: int,
        prompt: str,
        wait_for_ready: float = 1.0
    ) -> str:
        """
        Spawn a specialized agent via claude-squad

        Args:
            agent_type: Type of agent to spawn (tracking, dev, orchestration, etc.)
            task_id: Unique task identifier
            prompt: Task instructions for the agent
            wait_for_ready: Seconds to wait after spawning before returning

        Returns:
            session_id: Unique identifier for this agent session

        Raises:
            ValueError: If agent_type is not recognized
            RuntimeError: If squad session doesn't exist
        """
        # Validate agent type
        try:
            agent_enum = AgentType(agent_type)
        except ValueError:
            raise ValueError(
                f"Unknown agent type: {agent_type}. "
                f"Valid types: {[t.value for t in AgentType]}"
            )

        # Check if squad session exists
        result = subprocess.run(
            ["tmux", "list-sessions"],
            capture_output=True,
            text=True
        )
        if self.squad_session not in result.stdout:
            raise RuntimeError(
                f"Squad session '{self.squad_session}' not found. "
                f"Launch with: cs"
            )

        # Create session ID
        session_id = f"{agent_type}-{task_id}"

        # Create log file
        log_file = self.logs_dir / f"{session_id}.log"

        # Send 'N' keystroke to create new session
        subprocess.run([
            "tmux", "send-keys", "-t", self.squad_session,
            "N", "Enter"
        ])

        time.sleep(0.5)

        # Send prompt (escape single quotes)
        escaped_prompt = prompt.replace("'", "'\\''")
        subprocess.run([
            "tmux", "send-keys", "-t", self.squad_session,
            escaped_prompt, "Enter"
        ])

        # Track agent
        agent_info = AgentInfo(
            agent_type=agent_enum,
            task_id=task_id,
            session_id=session_id,
            prompt=prompt,
            status=AgentStatus.RUNNING,
            started=time.time(),
            log_file=log_file
        )
        self.active_agents[session_id] = agent_info

        # Wait for agent to initialize
        time.sleep(wait_for_ready)

        return session_id

    def check_completion(self, session_id: str) -> bool:
        """
        Check if agent has completed execution

        Args:
            session_id: Agent session identifier

        Returns:
            True if agent completed, False if still running
        """
        agent_info = self.active_agents.get(session_id)
        if not agent_info:
            return False

        # Already marked as completed
        if agent_info.status in [AgentStatus.COMPLETED, AgentStatus.FAILED]:
            return True

        # Check log file for completion markers
        if agent_info.log_file and agent_info.log_file.exists():
            content = agent_info.log_file.read_text()

            # Look for completion indicators
            completion_markers = [
                "Task completed",
                "Done",
                "✓ Complete",
                "Session ended",
                "All tasks complete"
            ]

            for marker in completion_markers:
                if marker in content:
                    agent_info.status = AgentStatus.COMPLETED
                    agent_info.result = content
                    return True

        # Check if tmux session still exists
        result = subprocess.run(
            ["tmux", "list-sessions"],
            capture_output=True,
            text=True
        )

        # If agent's tmux session is gone, mark as completed
        agent_session_pattern = f"agent-{session_id}"
        if agent_session_pattern not in result.stdout:
            agent_info.status = AgentStatus.COMPLETED
            if agent_info.log_file and agent_info.log_file.exists():
                agent_info.result = agent_info.log_file.read_text()
            return True

        return False

    def wait_for_agents(
        self,
        session_ids: List[str],
        timeout: int = 300,
        poll_interval: int = 2
    ) -> bool:
        """
        Wait for multiple agents to complete

        Args:
            session_ids: List of agent session identifiers to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: How often to check completion status

        Returns:
            True if all agents completed, False if timeout occurred
        """
        start = time.time()

        while time.time() - start < timeout:
            completed = [
                sid for sid in session_ids
                if self.check_completion(sid)
            ]

            # All agents completed
            if len(completed) == len(session_ids):
                return True

            # Show progress
            elapsed = int(time.time() - start)
            print(
                f"[{elapsed}s] Waiting for agents: "
                f"{len(completed)}/{len(session_ids)} complete"
            )

            time.sleep(poll_interval)

        # Timeout occurred - mark remaining as timeout
        for sid in session_ids:
            agent_info = self.active_agents.get(sid)
            if agent_info and agent_info.status == AgentStatus.RUNNING:
                agent_info.status = AgentStatus.TIMEOUT

        return False

    def get_agent_result(self, session_id: str) -> Optional[str]:
        """
        Get the result/output from a completed agent

        Args:
            session_id: Agent session identifier

        Returns:
            Agent output if available, None otherwise
        """
        agent_info = self.active_agents.get(session_id)
        if not agent_info:
            return None

        # If we have cached result, return it
        if agent_info.result:
            return agent_info.result

        # Try to read from log file
        if agent_info.log_file and agent_info.log_file.exists():
            result = agent_info.log_file.read_text()
            agent_info.result = result
            return result

        return None

    def list_active_agents(self) -> List[str]:
        """
        Get list of currently active agent session IDs

        Returns:
            List of session IDs for agents still running
        """
        return [
            sid for sid, info in self.active_agents.items()
            if info.status == AgentStatus.RUNNING
        ]

    def cleanup(self):
        """Kill all squad sessions and cleanup resources"""
        # Send 'q' to quit squad TUI
        subprocess.run([
            "tmux", "send-keys", "-t", self.squad_session,
            "q", "Enter"
        ])

        time.sleep(0.5)

        # Confirm quit
        subprocess.run([
            "tmux", "send-keys", "-t", self.squad_session,
            "y", "Enter"
        ])

        # Clear tracking
        self.active_agents.clear()

    def get_stats(self) -> Dict:
        """
        Get statistics about agent execution

        Returns:
            Dictionary with execution statistics
        """
        stats = {
            "total_agents": len(self.active_agents),
            "running": sum(
                1 for info in self.active_agents.values()
                if info.status == AgentStatus.RUNNING
            ),
            "completed": sum(
                1 for info in self.active_agents.values()
                if info.status == AgentStatus.COMPLETED
            ),
            "failed": sum(
                1 for info in self.active_agents.values()
                if info.status == AgentStatus.FAILED
            ),
            "timeout": sum(
                1 for info in self.active_agents.values()
                if info.status == AgentStatus.TIMEOUT
            ),
            "by_type": {}
        }

        # Count by agent type
        for info in self.active_agents.values():
            agent_type = info.agent_type.value
            if agent_type not in stats["by_type"]:
                stats["by_type"][agent_type] = 0
            stats["by_type"][agent_type] += 1

        return stats


# Example usage
if __name__ == "__main__":
    # Create manager
    manager = SquadManager()

    # Spawn tracking agent
    print("Spawning tracking agent...")
    tracking_session = manager.spawn_agent(
        agent_type="tracking",
        task_id=1,
        prompt="List all Python files in src/ and count total lines of code"
    )

    print(f"Agent spawned: {tracking_session}")

    # Wait for completion
    print("Waiting for agent to complete...")
    success = manager.wait_for_agents([tracking_session], timeout=120)

    if success:
        print("✓ Agent completed successfully")
        result = manager.get_agent_result(tracking_session)
        if result:
            print(f"\nAgent output:\n{result}")
    else:
        print("✗ Agent timed out")

    # Show stats
    stats = manager.get_stats()
    print(f"\nExecution stats: {json.dumps(stats, indent=2)}")

    # Cleanup
    print("\nCleaning up...")
    manager.cleanup()
    print("Done")
