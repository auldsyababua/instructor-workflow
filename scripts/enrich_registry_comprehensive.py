#!/usr/bin/env python3
"""
Comprehensive Registry Enrichment - Task A2
============================================
Hand-curated metadata enrichment for all 27 agents based on persona file analysis.

Created: 2025-11-19
Agent: Backend Agent (Billy)
Task: Task A2 Registry Enrichment
Protocol: RCA - Manual curation with validated extraction patterns
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any

# Paths
REGISTRY_PATH = Path("/srv/projects/instructor-workflow/agents/registry.yaml")
BACKUP_PATH = REGISTRY_PATH.with_suffix('.yaml.backup')

# Hand-curated enrichment data based on persona file analysis
# Extracted from /srv/projects/traycer-enforcement-framework/docs/agents/
ENRICHMENT_DATA = {
    "planning-agent": {
        "delegates_to": [
            "backend-agent", "browser-agent", "debug-agent", "devops-agent",
            "frontend-agent", "researcher-agent", "seo-agent", "software-architect",
            "test-auditor-agent", "test-writer-agent", "tracking-agent"
        ],
        "cannot_access": ["src/**", "tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Break down epics into implementation plans",
            "Delegate work to specialist agents",
            "Update Master Dashboard job tracking",
            "Select appropriate TDD workflow variation",
            "Coordinate agent handoffs and task delegation"
        ],
        "forbidden": [
            "Direct implementation (use Write/Edit except .project-context.md)",
            "Linear updates via MCP (Tracking Agent handles this)",
            "Git operations (Tracking Agent handles this)",
            "Write code or tests (delegate to dev/test agents)",
            "Create Linear issues (Research Agent does this)"
        ]
    },

    "backend-agent": {
        "delegates_to": [],  # Leaf agent
        "cannot_access": ["tests/**", "test/**", "*.test.*", "*.spec.*", "frontend/**"],
        "exclusive_access": [],
        "responsibilities": [
            "API development (REST, GraphQL, gRPC)",
            "Database schema and queries",
            "Authentication and authorization",
            "Business logic implementation",
            "External API integrations",
            "Background jobs and queues",
            "Performance and scalability"
        ],
        "forbidden": [
            "Modify test files (Test Writer/Auditor owns tests)",
            "Update Linear issues (Tracking Agent)",
            "Commit to git (Tracking Agent)",
            "Deploy to production (DevOps Agent)",
            "UI implementation (Frontend Agent)",
            "Infrastructure/deployment config (DevOps Agent)"
        ]
    },

    "frontend-agent": {
        "delegates_to": [],  # Leaf agent
        "cannot_access": ["tests/**", "test/**", "*.test.*", "*.spec.*", "backend/**"],
        "exclusive_access": [],
        "responsibilities": [
            "UI/UX implementation",
            "React/Next.js/Vue development",
            "Client-side state management",
            "Component development",
            "Frontend routing and navigation"
        ],
        "forbidden": [
            "Modify test files (Test Writer/Auditor owns tests)",
            "Update Linear issues (Tracking Agent)",
            "Commit to git (Tracking Agent)",
            "Backend API implementation (Backend Agent)",
            "Database operations (Backend Agent)"
        ]
    },

    "test-writer-agent": {
        "delegates_to": [],  # Leaf agent
        "cannot_access": ["src/**", "frontend/**", "backend/**"],
        "exclusive_access": ["tests/**", "test/**", "*.test.*", "*.spec.*"],
        "responsibilities": [
            "Write comprehensive tests before implementation (TDD Phase 3)",
            "Create test scripts from acceptance criteria",
            "Validate implementations against test suites",
            "Ensure test coverage for all features"
        ],
        "forbidden": [
            "Modify source code (implementation agents own this)",
            "Update Linear issues (Tracking Agent)",
            "Commit to git (Tracking Agent)",
            "Deploy code (DevOps Agent)"
        ]
    },

    "test-auditor-agent": {
        "delegates_to": [],  # Leaf agent
        "cannot_access": ["src/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Audit existing tests for quality",
            "Identify happy-path bias in test coverage",
            "Validate test completeness",
            "Ensure edge cases are tested"
        ],
        "forbidden": [
            "Modify source code (implementation agents own this)",
            "Write new tests (Test Writer Agent owns creation)",
            "Update Linear issues (Tracking Agent)",
            "Commit to git (Tracking Agent)"
        ]
    },

    "researcher-agent": {
        "delegates_to": [],  # Leaf agent
        "cannot_access": ["src/**", "tests/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Gather technical information and research",
            "Execute RAEP (Research Agent Enrichment Protocol)",
            "Validate approaches using ref.tools and Perplexity",
            "Generate XML stories for downstream agents",
            "Create dual-format output (TLDR + full research)"
        ],
        "forbidden": [
            "Write production code (implementation agents own this)",
            "Make implementation decisions (Planning Agent coordinates)",
            "Update Linear directly (Tracking Agent)",
            "Execute git operations (Tracking Agent)",
            "Modify test files (Test Writer/Auditor agents)"
        ]
    },

    "tracking-agent": {
        "delegates_to": [],  # Leaf agent
        "cannot_access": [],
        "exclusive_access": [],
        "responsibilities": [
            "Manage project tracking and documentation",
            "Update Linear issues",
            "Execute git operations (commits, branches, PRs)",
            "Create pull requests"
        ],
        "forbidden": [
            "Write code or tests (dev/test agents own this)",
            "Make implementation decisions (Planning Agent)",
            "Deploy infrastructure (DevOps Agent)"
        ]
    },

    "devops-agent": {
        "delegates_to": [],  # Leaf agent
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Manage infrastructure and deployment operations",
            "Configure CI/CD pipelines",
            "Container orchestration",
            "Infrastructure as code"
        ],
        "forbidden": [
            "Modify test files (Test Writer/Auditor)",
            "Update Linear issues (Tracking Agent)",
            "Write business logic code (Backend/Frontend agents)"
        ]
    },

    "debug-agent": {
        "delegates_to": [],  # Leaf agent
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Investigate and resolve bugs and issues",
            "Root cause analysis",
            "Diagnostic script creation",
            "Production bug fixes"
        ],
        "forbidden": [
            "Modify test files (Test Writer/Auditor)",
            "Update Linear issues (Tracking Agent)",
            "Commit to git (Tracking Agent)"
        ]
    },

    "seo-agent": {
        "delegates_to": [],  # Leaf agent
        "cannot_access": ["tests/**", "test/**", "backend/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Optimize content for search engines",
            "Technical SEO implementation",
            "Meta tags and structured data",
            "Web performance optimization"
        ],
        "forbidden": [
            "Modify test files (Test Writer/Auditor)",
            "Backend API development (Backend Agent)",
            "Update Linear issues (Tracking Agent)"
        ]
    },

    "browser-agent": {
        "delegates_to": [],  # Leaf agent
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Perform browser-based testing and interactions",
            "GUI operations",
            "Browser automation",
            "End-to-end testing"
        ],
        "forbidden": [
            "Modify test files (Test Writer/Auditor owns creation)",
            "Update Linear issues (Tracking Agent)",
            "Write production code (implementation agents)"
        ]
    },

    "software-architect": {
        "delegates_to": [],  # Research/planning agent
        "cannot_access": ["src/**", "tests/**"],
        "exclusive_access": [],
        "responsibilities": [
            "System architecture planning",
            "Tech stack research and selection",
            "Component design and integration",
            "Architecture decision documentation"
        ],
        "forbidden": [
            "Write production code (implementation agents)",
            "Create Linear issues (Research Agent)",
            "Modify tests (Test Writer/Auditor)",
            "Execute git operations (Tracking Agent)"
        ]
    },

    "homelab-architect": {
        "delegates_to": [],  # Research/planning agent
        "cannot_access": ["src/**", "tests/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Homelab network architecture planning",
            "Infrastructure topology design",
            "VLAN and routing configuration design",
            "Network troubleshooting and optimization"
        ],
        "forbidden": [
            "Write application code (implementation agents)",
            "Modify test files (Test Writer/Auditor)",
            "Execute deployments (DevOps Agent)",
            "Update Linear (Tracking Agent)"
        ]
    },

    # Specialized infrastructure agents
    "grafana-agent": {
        "delegates_to": [],
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Deploy and configure Grafana dashboards",
            "Prometheus integration setup",
            "GPU monitoring configuration",
            "Alerting and infrastructure-as-code provisioning"
        ],
        "forbidden": [
            "Modify test files",
            "Update Linear (Tracking Agent)",
            "Git operations (Tracking Agent)"
        ]
    },

    "docker-agent": {
        "delegates_to": [],
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Docker/Docker Compose operations",
            "Container management and debugging",
            "Resource monitoring",
            "Infrastructure deployment"
        ],
        "forbidden": [
            "Modify test files",
            "Update Linear (Tracking Agent)",
            "Application code development (Backend/Frontend agents)"
        ]
    },

    "traefik-agent": {
        "delegates_to": [],
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Traefik v3 reverse proxy configuration",
            "Routing rules and middleware chains",
            "Service discovery setup",
            "Docker-based infrastructure proxy management"
        ],
        "forbidden": [
            "Modify test files",
            "Application development (Backend/Frontend agents)",
            "Update Linear (Tracking Agent)"
        ]
    },

    "prometheus-agent": {
        "delegates_to": [],
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Prometheus metrics collection setup",
            "PromQL query development",
            "Alerting rules configuration",
            "TSDB management"
        ],
        "forbidden": [
            "Modify test files",
            "Application code (Backend/Frontend agents)",
            "Update Linear (Tracking Agent)"
        ]
    },

    "cadvisor-agent": {
        "delegates_to": [],
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "cAdvisor container monitoring setup",
            "Resource metrics collection",
            "Prometheus integration",
            "Container performance analysis"
        ],
        "forbidden": [
            "Modify test files",
            "Application development",
            "Update Linear (Tracking Agent)"
        ]
    },

    "jupyter-agent": {
        "delegates_to": [],
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Jupyter Lab/Notebook operations",
            "Kernel management",
            "AI/ML workflow setup",
            "GPU integration for notebooks"
        ],
        "forbidden": [
            "Modify test files",
            "Production application code",
            "Update Linear (Tracking Agent)"
        ]
    },

    "vllm-agent": {
        "delegates_to": [],
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Deploy and manage vLLM inference server",
            "Model management",
            "Performance optimization",
            "OpenAI-compatible API integration"
        ],
        "forbidden": [
            "Modify test files",
            "Application business logic (Backend Agent)",
            "Update Linear (Tracking Agent)"
        ]
    },

    "unraid-agent": {
        "delegates_to": [],
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Unraid NAS system management",
            "Array operations and storage configuration",
            "Docker/VM management on Unraid",
            "System troubleshooting and optimization"
        ],
        "forbidden": [
            "Modify test files",
            "Application code",
            "Update Linear (Tracking Agent)"
        ]
    },

    "unifios-agent": {
        "delegates_to": [],
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "UniFi OS management and configuration",
            "Network device management",
            "VLAN and firewall configuration",
            "UniFi Dream Machine administration"
        ],
        "forbidden": [
            "Modify test files",
            "Application development",
            "Update Linear (Tracking Agent)"
        ]
    },

    "onrate-agent": {
        "delegates_to": [],
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Onrate network monitoring setup",
            "Cellular performance metrics analysis",
            "Latency and throughput optimization",
            "Network performance reporting"
        ],
        "forbidden": [
            "Modify test files",
            "Application code",
            "Update Linear (Tracking Agent)"
        ]
    },

    "frappe-erpnext-agent": {
        "delegates_to": [],
        "cannot_access": ["tests/**", "test/**"],
        "exclusive_access": [],
        "responsibilities": [
            "Frappe Cloud and ERPNext administration",
            "Bench CLI operations",
            "ERP system configuration",
            "Module customization"
        ],
        "forbidden": [
            "Modify test files",
            "Non-Frappe application code",
            "Update Linear (Tracking Agent)"
        ]
    },

    # Note: qa-agent archived; action-agent replaced by frontend/backend/devops-agent
    "qa-agent": {
        "delegates_to": [],
        "cannot_access": [],
        "exclusive_access": [],
        "responsibilities": [
            "Create and maintain test suites (archived - see test-writer-agent)",
            "Validate implementations"
        ],
        "forbidden": [
            "Write production code (implementation agents)",
            "Update Linear (Tracking Agent)"
        ]
    },

    "traycer-agent": {
        "delegates_to": [],
        "cannot_access": [],
        "exclusive_access": [],
        "responsibilities": [
            "Coordinate agent workflows",
            "Manage project orchestration",
            "High-level task delegation"
        ],
        "forbidden": [
            "Direct implementation (delegates to specialists)",
            "Modify test files (Test Writer/Auditor)",
            "Git operations (Tracking Agent)"
        ]
    },
}


def main():
    """Apply hand-curated enrichment to registry"""
    print("=" * 70)
    print("Task A2: Registry Enrichment (Comprehensive)")
    print("=" * 70)

    # Load registry
    print(f"\nLoading registry: {REGISTRY_PATH}")
    with open(REGISTRY_PATH, 'r') as f:
        registry = yaml.safe_load(f)

    agents = registry['agents']
    print(f"Found {len(agents)} agents in registry")
    print(f"Hand-curated enrichment data for {len(ENRICHMENT_DATA)} agents")

    # Backup registry
    print(f"\nCreating backup: {BACKUP_PATH}")
    with open(BACKUP_PATH, 'w') as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False)

    # Apply enrichment
    print("\n" + "=" * 70)
    print("Applying enrichment")
    print("=" * 70)

    enriched_count = 0
    missing_enrichment = []

    for agent_name in agents.keys():
        if agent_name in ENRICHMENT_DATA:
            enrichment = ENRICHMENT_DATA[agent_name]
            agents[agent_name].update(enrichment)
            print(f"✓ {agent_name}: enriched")
            enriched_count += 1
        else:
            # Provide empty enrichment for agents without persona files
            agents[agent_name].update({
                "delegates_to": [],
                "cannot_access": [],
                "exclusive_access": [],
                "responsibilities": [],
                "forbidden": []
            })
            missing_enrichment.append(agent_name)
            print(f"⚠️  {agent_name}: empty enrichment (no persona file)")

    # Save enriched registry
    print("\n" + "=" * 70)
    print("Saving enriched registry")
    print("=" * 70)

    with open(REGISTRY_PATH, 'w') as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False, width=120)

    print(f"\n✓ Registry enrichment complete")
    print(f"  Enriched: {enriched_count} agents")
    print(f"  Empty enrichment: {len(missing_enrichment)} agents")
    if missing_enrichment:
        print(f"  Agents with empty enrichment: {', '.join(missing_enrichment)}")
    print(f"  Updated: {REGISTRY_PATH}")
    print(f"  Backup: {BACKUP_PATH}")
    print("\nNext steps:")
    print("  1. Run validation: python3 docs/.scratch/native-orchestrator/test-a2-validation.py")
    print("  2. Run pytest: pytest tests/test_registry_enrichment.py -v")
    print()


if __name__ == "__main__":
    main()
