#!/usr/bin/env python3
"""
AgentSpawner - Direct tmux-based multi-agent orchestration

Spawns Claude Code agents in isolated tmux sessions without TUI dependencies.
Based on proven patterns from mkXultra/claude_code_setup and agent-farm projects.
"""

import subprocess
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class AgentType(Enum):
    TRACKING = "tracking"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DEVOPS = "devops"
    QA = "qa"
    RESEARCH = "research"


@dataclass
class AgentSession:
    agent_type: AgentType
    session_name: str
    worktree_path: Path
    started: float


class AgentSpawner:
    """Manages agent lifecycle via direct tmux spawning"""

    def __init__(self, project_root: str = "/srv/projects/instructor-workflow"):
        self.project_root = Path(project_root)
        self.worktrees_dir = Path("/srv/projects/instructor-workflow-worktrees")
        self.worktrees_dir.mkdir(exist_ok=True)
        self.active_sessions = {}

    def spawn_agent(
        self,
        agent_type: str,
        task_id: int,
        prompt: str,
        agent_prompt_path: Optional[str] = None
    ) -> str:
        """
        Spawn agent in isolated tmux session with git worktree

        Args:
            agent_type: Type of agent (tracking, frontend, etc.)
            task_id: Unique task identifier
            prompt: Task instructions
            agent_prompt_path: Path to agent persona file (optional)

        Returns:
            session_name: tmux session identifier
        """
        # Validate agent type
        agent_enum = AgentType(agent_type)

        # Create session name
        session_name = f"{agent_type}-{task_id}"

        # Create git worktree for isolation
        worktree_path = self.worktrees_dir / session_name
        if worktree_path.exists():
            # Clean up old worktree
            subprocess.run(["git", "worktree", "remove", "-f", str(worktree_path)],
                         cwd=self.project_root, capture_output=True)

        subprocess.run([
            "git", "worktree", "add",
            str(worktree_path),
            "HEAD"
        ], cwd=self.project_root, capture_output=True)

        # Build Claude Code command
        # Note: Using prompt argument causes the session to exit after completion.
        # For persistent sessions, we keep the shell alive with a follow-up prompt.
        # Escape prompt for bash safety
        safe_prompt = prompt.replace('"', '\\"')

        if agent_prompt_path:
            # With agent persona
            claude_cmd = (
                f'cd {worktree_path} && '
                f'claude --dangerously-skip-permissions '
                f'--append-system-prompt "$(cat {agent_prompt_path})" '
                f'"{safe_prompt}"; '
                f'exec bash'  # Keep shell alive after Claude exits
            )
        else:
            # Standalone prompt
            claude_cmd = (
                f'cd {worktree_path} && '
                f'claude --dangerously-skip-permissions '
                f'"{safe_prompt}"; '
                f'exec bash'  # Keep shell alive after Claude exits
            )

        # Spawn tmux session
        subprocess.run([
            "tmux", "new-session", "-d",
            "-s", session_name,
            "bash", "-c", claude_cmd
        ], capture_output=True)

        # Track session
        session_info = AgentSession(
            agent_type=agent_enum,
            session_name=session_name,
            worktree_path=worktree_path,
            started=time.time()
        )
        self.active_sessions[session_name] = session_info

        return session_name

    def is_running(self, session_name: str) -> bool:
        """Check if tmux session still exists"""
        result = subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            capture_output=True
        )
        return result.returncode == 0

    def get_output(self, session_name: str) -> str:
        """Capture pane content from agent session"""
        if not self.is_running(session_name):
            return ""

        result = subprocess.run(
            ["tmux", "capture-pane", "-t", session_name, "-p"],
            capture_output=True,
            text=True
        )
        return result.stdout

    def cleanup(self, session_name: str):
        """Kill session and remove worktree"""
        # Kill tmux session
        subprocess.run(["tmux", "kill-session", "-t", session_name],
                     capture_output=True)

        # Remove worktree
        if session_name in self.active_sessions:
            worktree = self.active_sessions[session_name].worktree_path
            subprocess.run(["git", "worktree", "remove", "-f", str(worktree)],
                         cwd=self.project_root, capture_output=True)
            del self.active_sessions[session_name]
