#!/usr/bin/env python3
"""
Rate Limiter - Token bucket algorithm for agent spawning DoS prevention

Location: /srv/projects/instructor-workflow/scripts/rate_limiter.py

Implements per-capability rate limiting to prevent:
- Spawn DoS attacks (malicious prompt spawning excessive agents)
- Resource exhaustion (too many concurrent agents)
- Accidental runaway spawning (buggy code loops)

Configuration via environment variables:
- IW_MAX_SPAWNS_PER_MIN: Max spawns per minute per capability (default: 10)
- IW_MAX_CONCURRENT: Max concurrent agents per type (default: 5)

Usage:
    limiter = RateLimiter()

    # Check if spawn allowed
    limiter.check_spawn_allowed('backend')  # Raises RateLimitError if exceeded

    # Record successful spawn
    limiter.record_spawn('backend')

    # Record agent completion (frees concurrent slot)
    limiter.record_completion('backend')
"""

import os
import time
from collections import defaultdict
from typing import Dict, List, Tuple


class RateLimitError(Exception):
    """
    Raised when rate limit exceeded for agent spawning.

    Attributes:
        agent_type: Agent capability that hit rate limit
        current_rate: Current spawn rate (spawns per minute)
        limit: Configured rate limit
        message: Human-readable error message
    """
    def __init__(self, agent_type: str, current_rate: int, limit: int, message: str):
        self.agent_type = agent_type
        self.current_rate = current_rate
        self.limit = limit
        self.message = message
        super().__init__(message)


class RateLimiter:
    """
    Token bucket rate limiter for agent spawning.

    Enforces two types of limits:
    1. Spawn rate limit: Max spawns per minute per capability (DoS prevention)
    2. Concurrent limit: Max active agents per type (resource management)

    Each agent type has separate buckets to prevent one capability
    from starving others (e.g., frontend spawns don't block backend spawns).

    Thread-safety: NOT thread-safe. Use locks if spawning from multiple threads.
    """

    def __init__(self):
        """
        Initialize rate limiter with configuration from environment.

        Environment variables:
            IW_MAX_SPAWNS_PER_MIN: Max spawns per minute per capability (default: 10)
            IW_MAX_CONCURRENT: Max concurrent agents per type (default: 5)
        """
        # Spawn history: agent_type -> [(timestamp, count), ...]
        # Each tuple represents a spawn event with its timestamp
        self.spawn_history: Dict[str, List[Tuple[float, int]]] = defaultdict(list)

        # Concurrent agent tracking: agent_type -> count
        # Incremented on spawn, decremented on completion
        self.concurrent_agents: Dict[str, int] = defaultdict(int)

        # Load limits from environment (with defaults)
        self.max_spawns_per_minute = int(os.getenv('IW_MAX_SPAWNS_PER_MIN', '10'))
        self.max_concurrent_per_type = int(os.getenv('IW_MAX_CONCURRENT', '5'))

        # Validation window (60 seconds)
        self.window_seconds = 60

    def check_spawn_allowed(self, agent_type: str) -> bool:
        """
        Check if spawn is allowed under rate limits.

        Validates both spawn rate (10/min) and concurrent limits (5 concurrent).
        Raises RateLimitError if either limit exceeded.

        Args:
            agent_type: Agent capability to check (e.g., 'backend', 'frontend')

        Returns:
            True if spawn allowed

        Raises:
            RateLimitError: If rate limit or concurrent limit exceeded

        Example:
            >>> limiter = RateLimiter()
            >>> limiter.check_spawn_allowed('backend')  # Returns True if under limit
            >>> # After 10 spawns in last minute:
            >>> limiter.check_spawn_allowed('backend')  # Raises RateLimitError
        """
        now = time.time()

        # Clean up stale spawn history (older than 60 seconds)
        self.spawn_history[agent_type] = [
            (ts, count) for ts, count in self.spawn_history[agent_type]
            if now - ts < self.window_seconds
        ]

        # Count spawns in last minute (sum of counts in history)
        spawns_last_minute = sum(
            count for ts, count in self.spawn_history[agent_type]
        )

        # Check spawn rate limit
        if spawns_last_minute >= self.max_spawns_per_minute:
            raise RateLimitError(
                agent_type=agent_type,
                current_rate=spawns_last_minute,
                limit=self.max_spawns_per_minute,
                message=(
                    f"Spawn rate limit exceeded for {agent_type}: "
                    f"{spawns_last_minute}/{self.max_spawns_per_minute} spawns/minute\n\n"
                    f"Security: DoS prevention - too many agents spawned too quickly.\n\n"
                    f"Wait 60 seconds or increase IW_MAX_SPAWNS_PER_MIN environment variable.\n"
                    f"Current setting: IW_MAX_SPAWNS_PER_MIN={self.max_spawns_per_minute}"
                )
            )

        # Check concurrent limit
        current_concurrent = self.concurrent_agents[agent_type]
        if current_concurrent >= self.max_concurrent_per_type:
            raise RateLimitError(
                agent_type=agent_type,
                current_rate=current_concurrent,
                limit=self.max_concurrent_per_type,
                message=(
                    f"Concurrent limit exceeded for {agent_type}: "
                    f"{current_concurrent}/{self.max_concurrent_per_type} active agents\n\n"
                    f"Resource management: Too many {agent_type} agents running simultaneously.\n\n"
                    f"Wait for agents to complete or increase IW_MAX_CONCURRENT environment variable.\n"
                    f"Current setting: IW_MAX_CONCURRENT={self.max_concurrent_per_type}"
                )
            )

        return True

    def record_spawn(self, agent_type: str) -> None:
        """
        Record successful spawn for rate tracking.

        Call this AFTER spawning agent to track spawn history
        and increment concurrent count.

        Args:
            agent_type: Agent capability that was spawned

        Example:
            >>> limiter = RateLimiter()
            >>> limiter.check_spawn_allowed('backend')  # Check first
            >>> # ... spawn agent ...
            >>> limiter.record_spawn('backend')  # Record after successful spawn
        """
        now = time.time()

        # Add to spawn history (timestamp, count=1)
        self.spawn_history[agent_type].append((now, 1))

        # Increment concurrent count
        self.concurrent_agents[agent_type] += 1

    def record_completion(self, agent_type: str) -> None:
        """
        Record agent completion to free concurrent slot.

        Call this when agent finishes execution (success or failure)
        to decrement concurrent count and free up capacity.

        Args:
            agent_type: Agent capability that completed

        Example:
            >>> limiter = RateLimiter()
            >>> # ... agent completes ...
            >>> limiter.record_completion('backend')  # Free concurrent slot
        """
        # Decrement concurrent count (never go below 0)
        self.concurrent_agents[agent_type] = max(
            0, self.concurrent_agents[agent_type] - 1
        )

    def get_stats(self, agent_type: str) -> Dict[str, int]:
        """
        Get current rate limit statistics for agent type.

        Useful for monitoring and dashboard visualization.

        Args:
            agent_type: Agent capability to get stats for

        Returns:
            Dictionary with current spawn rate and concurrent count

        Example:
            >>> limiter = RateLimiter()
            >>> stats = limiter.get_stats('backend')
            >>> print(stats)
            {
                'spawns_last_minute': 7,
                'spawns_limit': 10,
                'concurrent_agents': 3,
                'concurrent_limit': 5,
                'spawn_capacity_remaining': 3,
                'concurrent_capacity_remaining': 2
            }
        """
        now = time.time()

        # Clean up stale history
        self.spawn_history[agent_type] = [
            (ts, count) for ts, count in self.spawn_history[agent_type]
            if now - ts < self.window_seconds
        ]

        # Calculate current rates
        spawns_last_minute = sum(
            count for ts, count in self.spawn_history[agent_type]
        )
        concurrent = self.concurrent_agents[agent_type]

        return {
            'spawns_last_minute': spawns_last_minute,
            'spawns_limit': self.max_spawns_per_minute,
            'concurrent_agents': concurrent,
            'concurrent_limit': self.max_concurrent_per_type,
            'spawn_capacity_remaining': max(0, self.max_spawns_per_minute - spawns_last_minute),
            'concurrent_capacity_remaining': max(0, self.max_concurrent_per_type - concurrent)
        }

    def reset(self) -> None:
        """
        Reset all rate limiting state.

        Useful for testing or emergency overrides.
        WARNING: Only use in development or emergency situations.
        """
        self.spawn_history.clear()
        self.concurrent_agents.clear()


# Example usage and testing
if __name__ == "__main__":
    print("=== Rate Limiter Examples ===\n")

    # Example 1: Normal operation
    print("Example 1: Normal Operation")
    print("-" * 50)
    limiter = RateLimiter()

    # Spawn 5 backend agents (under limit)
    for i in range(5):
        try:
            limiter.check_spawn_allowed('backend')
            limiter.record_spawn('backend')
            print(f"✅ Backend agent {i+1} spawned")
        except RateLimitError as e:
            print(f"❌ Spawn blocked: {e.message}")

    stats = limiter.get_stats('backend')
    print(f"\nStats: {stats['spawns_last_minute']}/{stats['spawns_limit']} spawns, "
          f"{stats['concurrent_agents']}/{stats['concurrent_limit']} concurrent")
    print()

    # Example 2: Concurrent limit exceeded
    print("Example 2: Concurrent Limit Exceeded")
    print("-" * 50)
    limiter2 = RateLimiter()

    # Spawn max concurrent agents (5)
    for i in range(5):
        limiter2.check_spawn_allowed('frontend')
        limiter2.record_spawn('frontend')

    # Try to spawn 6th (should fail)
    try:
        limiter2.check_spawn_allowed('frontend')
        print("✅ Spawn allowed (unexpected!)")
    except RateLimitError as e:
        print(f"❌ Expected concurrent limit hit:")
        print(f"   {e.message[:150]}...")
    print()

    # Example 3: Rate limit exceeded
    print("Example 3: Rate Limit Exceeded")
    print("-" * 50)
    limiter3 = RateLimiter()

    # Spawn 10 agents rapidly (hit limit)
    for i in range(10):
        limiter3.check_spawn_allowed('devops')
        limiter3.record_spawn('devops')
        # Immediately complete to free concurrent slot
        limiter3.record_completion('devops')

    # Try 11th spawn (should fail rate limit)
    try:
        limiter3.check_spawn_allowed('devops')
        print("✅ Spawn allowed (unexpected!)")
    except RateLimitError as e:
        print(f"❌ Expected rate limit hit:")
        print(f"   {e.message[:150]}...")
    print()

    # Example 4: Per-capability isolation
    print("Example 4: Per-Capability Isolation")
    print("-" * 50)
    limiter4 = RateLimiter()

    # Spawn 10 backend agents (hit limit)
    for i in range(10):
        limiter4.check_spawn_allowed('backend')
        limiter4.record_spawn('backend')
        limiter4.record_completion('backend')  # Free concurrent

    # Frontend should still work (separate bucket)
    try:
        limiter4.check_spawn_allowed('frontend')
        limiter4.record_spawn('frontend')
        print("✅ Frontend spawn succeeded (backend limit doesn't affect frontend)")
    except RateLimitError as e:
        print(f"❌ Unexpected failure: {e.message}")

    backend_stats = limiter4.get_stats('backend')
    frontend_stats = limiter4.get_stats('frontend')
    print(f"\nBackend: {backend_stats['spawns_last_minute']}/{backend_stats['spawns_limit']} spawns")
    print(f"Frontend: {frontend_stats['spawns_last_minute']}/{frontend_stats['spawns_limit']} spawns")
    print("\n✅ Per-capability isolation working correctly")
