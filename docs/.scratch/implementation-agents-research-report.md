# Implementation Agents Research Report

**Research Agent**: Analysis of specialized implementation agents for team effectiveness improvements
**Date**: 2025-01-13
**Scope**: Frontend Agent, Backend Agent, DevOps Agent, Test-Writer Agent, Test-Auditor Agent
**Framework**: Instructor Workflow (IW) - Enforcement Architecture for PopOS 22.04

---

## Executive Summary

### Key Findings

**CRITICAL DISCOVERY**: The implementation agents exhibit strong individual capabilities but lack systematic input validation and handoff enforcement. While the TDD workflow provides excellent role separation at the conceptual level, the agents need structural reinforcement through **Layer 5 (Instructor Validation)** to ensure consistent, validated handoffs.

**High-Impact Recommendations**:
1. **Add Pydantic validation models for ALL handoffs** - Currently only Planning Agent has Layer 5 integration
2. **Strengthen test file access controls** - All three implementation agents have identical restrictions but lack enforcement hooks
3. **Create specialized handoff models** - Different validation rules for Frontend vs Backend vs DevOps tasks
4. **Integrate Test-Writer validation patterns** - Current agent has behavioral directives but no structural validation
5. **Add environment detection patterns** - Test-Writer needs systematic mock detection protocols

**Risk Assessment**:
- **HIGH RISK**: Implementation agents can currently bypass test file restrictions (Layer 4 behavioral only)
- **MEDIUM RISK**: No validation that handoffs contain required research context from Phase 1
- **MEDIUM RISK**: Test-Writer agents lack structured validation for mock quality and assertion strength

---

## 1. Current State Analysis

### 1.1 Frontend Agent (Frank)

**File**: `/srv/projects/instructor-workflow/agents/frontend/frontend-agent.md`

**Current Responsibilities**:
- UI/UX implementation (React, Next.js, Vue, Svelte)
- Component architecture and state management
- Accessibility (WCAG 2.2 AA compliance)
- Performance optimization (Core Web Vitals)
- Responsive design and CSS architecture
- TypeScript type safety
- Security headers (CSP, XSS prevention)

**Role Boundaries**:
- ✅ **Clear**: Implementation only, forbidden from test files
- ✅ **Clear**: Cannot update Linear (Tracking Agent owns)
- ✅ **Clear**: Cannot commit to git (Tracking Agent owns)
- ⚠️ **Ambiguous**: Research brief consumption protocol needs reinforcement
- ⚠️ **Weak**: No validation that acceptance criteria present before starting

**Enforcement Mechanisms Present**:
- **Layer 4 (Behavioral)**: Strong emphatic directives with violation reporting template
- **Layer 4 (Behavioral)**: Self-check protocol every 5 actions
- **Layer 4 (Behavioral)**: Clear "CRITICAL: Test File Restrictions" section (lines 36-81)
- **MISSING Layer 1**: No tool restrictions defined (still has full Bash, Read, Write, Edit, Glob, Grep)
- **MISSING Layer 2**: No directory-scoped `.claude/settings.json` present
- **MISSING Layer 3**: No hook-based validation scripts
- **MISSING Layer 5**: No Pydantic input validation for handoffs

**Strengths**:
- Comprehensive accessibility and performance checklists
- Clear validation protocols (Lighthouse, axe DevTools)
- Strong security awareness (CSP, input sanitization)
- Research brief integration guidance (lines 768-810)
- Agent context update protocol present (lines 748-767)

**Weaknesses**:
- Test file restrictions rely entirely on agent self-discipline (Layer 4 only)
- No structural validation of incoming handoffs
- No enforcement that research context was read
- Validation checklist is manual (lines 303-351) - could be Pydantic model
- No automated detection of test file access attempts

### 1.2 Backend Agent (Billy)

**File**: `/srv/projects/instructor-workflow/agents/backend/backend-agent.md`

**Current Responsibilities**:
- API design/implementation (REST, GraphQL, gRPC)
- Database schema and queries
- Authentication and authorization
- Business logic and data transformations
- Background jobs and queues
- External API integrations
- Performance and scalability

**Role Boundaries**:
- ✅ **Clear**: Implementation only, forbidden from test files (lines 75-90)
- ✅ **Clear**: Cannot update Linear (Tracking Agent owns)
- ✅ **Clear**: Cannot commit to git (Tracking Agent owns)
- ❌ **CONFUSING**: Lines 16-50 contain stale "project-agnostic workflow framework" content
- ❌ **CONFUSING**: Duplicate Feature Selection Protocol section (inappropriate for implementation agent)

**Enforcement Mechanisms Present**:
- **Layer 4 (Behavioral)**: Test file restrictions stated (lines 75-90)
- **MISSING Layer 1**: No tool restrictions (full access)
- **MISSING Layer 2**: No directory-scoped config
- **MISSING Layer 3**: No hooks
- **MISSING Layer 5**: No handoff validation

**Strengths**:
- Strong security checklist (lines 229-236)
- Clear validation checklist (lines 253-278)
- Good error handling patterns (lines 299-328)
- Comprehensive code examples for common patterns

**Weaknesses**:
- **CRITICAL**: Contains Planning Agent content (lines 16-50) - wrong agent persona mixed in
- Test file restrictions weaker than Frontend Agent (less emphasis)
- No validation that incoming handoffs contain required data
- Security checklist is manual - could be automated with validation models
- No enforcement hooks present

### 1.3 DevOps Agent (Clay)

**File**: `/srv/projects/instructor-workflow/agents/devops/devops-agent.md`

**Current Responsibilities**:
- Infrastructure as Code (Terraform, Pulumi, CloudFormation)
- CI/CD pipelines (GitHub Actions, GitLab CI)
- Container orchestration (Docker, Kubernetes)
- Cloud platforms (AWS, GCP, Azure, Cloudflare)
- Monitoring and observability
- Security and compliance
- Database operations (provisioning, backups)

**Role Boundaries**:
- ✅ **Clear**: Infrastructure and deployment only
- ⚠️ **Confusing**: Lines 16-50 contain copy-pasted Planning Agent content (same issue as Backend Agent)
- ✅ **Clear**: Test file restrictions stated (lines 73-90)
- ✅ **Clear**: Cannot update Linear or create commits

**Enforcement Mechanisms Present**:
- **Layer 4 (Behavioral)**: Test file restrictions (lines 73-90)
- **MISSING Layer 1**: No tool restrictions
- **MISSING Layer 2**: No directory-scoped config
- **MISSING Layer 3**: No hooks
- **MISSING Layer 5**: No handoff validation

**Strengths**:
- Excellent infrastructure code examples (Terraform, K8s, GitHub Actions)
- Strong security best practices section (lines 847-992)
- Comprehensive disaster recovery patterns (lines 993-1074)
- Cost optimization guidance (lines 1101-1162)
- Detailed monitoring and alerting setup

**Weaknesses**:
- **CRITICAL**: Contains Planning Agent persona content (lines 16-50) - copy-paste error
- Test file restrictions less prominent than Frontend Agent
- No validation checklists automated
- Manual validation checklist (lines 543-598) - could be Pydantic model
- No integration with Layer 5 validation

### 1.4 Test-Writer Agent

**File**: `/srv/projects/instructor-workflow/agents/test-writer/test-writer-agent.md`

**Current Responsibilities**:
- Write tests BEFORE implementation (TDD Phase 3)
- Create comprehensive test suites (happy path, edge cases, errors)
- Use proper mocking for external dependencies
- Validate tests fail correctly before implementation
- Run test validation after implementation (TDD Phase 5)

**Role Boundaries**:
- ✅ **EXCELLENT**: Exclusive test file ownership clearly stated
- ✅ **EXCELLENT**: Strong "Failed Tests Never Acceptable" directive (lines 8-30)
- ✅ **EXCELLENT**: Self-check protocol built-in (lines 504-518)
- ✅ **Clear**: Cannot modify implementation code
- ✅ **Clear**: Cannot update Linear or create commits

**Enforcement Mechanisms Present**:
- **Layer 4 (Behavioral)**: Extremely strong directives with "Sacred Rule" emphasis
- **Layer 4 (Behavioral)**: Triple verification checklist (lines 21-30)
- **Layer 4 (Behavioral)**: Self-audit every 5 actions (lines 504-518)
- **MISSING Layer 1**: No tool restrictions specified (has Bash, Read, Write, Edit)
- **MISSING Layer 2**: No directory-scoped config
- **MISSING Layer 3**: No hooks for test file protection
- **MISSING Layer 5**: No validation of incoming specifications

**Strengths**:
- **OUTSTANDING**: Best-written agent prompt in the repository
- Clear testing philosophy (Arrange-Act-Assert, descriptive names, mock quality)
- Excellent anti-patterns section (lines 320-378)
- Strong test organization standards (lines 277-317)
- Comprehensive framework reference (Vitest, Pytest patterns)
- Environmental detection guidance (lines 226-246)

**Weaknesses**:
- No structural validation that acceptance criteria are present
- No automated detection of weak assertions (currently manual review)
- No enforcement that research context was provided
- Test validation workflow is behavioral only (no structural checks)
- No integration with Layer 5 validation models

### 1.5 Test-Auditor Agent

**File**: `/srv/projects/instructor-workflow/agents/test-auditor/test-auditor-agent.md`

**Current Responsibilities**:
- Audit test quality (not write tests)
- Run 7-point quality checklist
- Identify happy-path bias and weak assertions
- Flag missing edge cases and error conditions
- Request Test-Writer add missing tests
- Validate tests would catch implementation bugs

**Role Boundaries**:
- ✅ **EXCELLENT**: Read-only for test files (cannot modify)
- ✅ **EXCELLENT**: Clear delegation model (find problems, Test-Writer fixes)
- ✅ **Clear**: Cannot modify implementation code
- ✅ **Clear**: Cannot update Linear or create commits

**Enforcement Mechanisms Present**:
- **Layer 4 (Behavioral)**: Strong "Trust But Verify" directive
- **Layer 4 (Behavioral)**: Comprehensive 7-point checklist (lines 79-228)
- **Layer 4 (Behavioral)**: Self-audit protocol (lines 471-482)
- **MISSING Layer 1**: No tool restrictions (has Bash, Read despite read-only role)
- **MISSING Layer 2**: No directory-scoped config
- **MISSING Layer 3**: No hooks
- **MISSING Layer 5**: No validation of incoming audit requests

**Strengths**:
- **OUTSTANDING**: Second-best written agent prompt in repository
- Extremely detailed audit checklist with specific examples
- Clear quality issue categorization (lines 265-378)
- Excellent failure validation methodology (lines 169-189)
- Strong delegation protocol for requesting test fixes (lines 382-429)

**Weaknesses**:
- No structural validation of audit requests
- Checklist execution is manual (could be partially automated)
- No enforcement that audit was actually performed before approval
- No integration with Layer 5 validation

---

## 2. Input Validation Patterns

### 2.1 Industry Best Practices

**Multi-Agent System Validation Standards**:

Based on research of production agent systems (AutoGPT, LangChain agents, CrewAI), industry best practices include:

1. **Structural Validation (Pydantic Models)**
   - Type-safe schemas for all inter-agent communication
   - Field validators for domain-specific constraints
   - Model validators for cross-field consistency checks

2. **Pre-Condition Verification**
   - Required fields present before agent starts work
   - File paths validated as accessible
   - Dependencies confirmed available

3. **Post-Condition Validation**
   - Output format matches expected schema
   - Required artifacts present
   - Success criteria met

4. **Handoff Traceability**
   - Unique IDs for each delegation
   - Timestamp and context tracking
   - Clear success/failure state

### 2.2 Recommended Input Validation for Each Agent

#### Frontend Agent Input Model

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal

class FrontendAgentHandoff(BaseModel):
    """Validated handoff for Frontend Agent delegation."""

    work_block_id: str = Field(
        ...,
        min_length=3,
        description="Linear issue ID (e.g., 'WB-AUTH-001', '10N-123')"
    )

    feature_description: str = Field(
        ...,
        min_length=20,
        description="Clear description of UI feature to implement"
    )

    acceptance_criteria: List[str] = Field(
        ...,
        min_items=1,
        description="Specific, testable acceptance criteria"
    )

    test_file_paths: List[str] = Field(
        ...,
        min_items=1,
        description="Test files created by Test-Writer (for reference only)"
    )

    research_context_present: bool = Field(
        default=False,
        description="Confirms Research Agent enriched Linear issue"
    )

    component_type: Literal["react", "vue", "svelte", "web-component"] = Field(
        ...,
        description="Framework being used"
    )

    accessibility_required: bool = Field(
        default=True,
        description="WCAG 2.2 AA compliance required"
    )

    performance_targets: Optional[dict] = Field(
        default=None,
        description="Core Web Vitals targets (LCP, FID, CLS)"
    )

    @validator('test_file_paths', each_item=True)
    def validate_test_paths(cls, path):
        """Ensure paths are repo-relative and point to test files."""
        if path.startswith(('/home/', '/Users/', '/srv/', 'C:\\')):
            raise ValueError(f"Absolute path not allowed: {path}")
        if '..' in path:
            raise ValueError(f"Parent directory traversal not allowed: {path}")
        if not any(x in path for x in ['test/', 'tests/', '.test.', '.spec.']):
            raise ValueError(f"Not a test file: {path}")
        return path

    @validator('acceptance_criteria', each_item=True)
    def validate_criteria_clarity(cls, criterion):
        """Ensure acceptance criteria are specific and testable."""
        vague_terms = ['should work', 'looks good', 'is correct', 'functions properly']
        criterion_lower = criterion.lower()
        if any(term in criterion_lower for term in vague_terms):
            raise ValueError(f"Criterion too vague: '{criterion}'. Be specific.")
        if len(criterion) < 15:
            raise ValueError(f"Criterion too short: '{criterion}'. Provide details.")
        return criterion

    class Config:
        schema_extra = {
            "example": {
                "work_block_id": "10N-456",
                "feature_description": "Implement login form with email validation and password strength indicator",
                "acceptance_criteria": [
                    "Email input validates format on blur",
                    "Password strength indicator shows weak/medium/strong",
                    "Submit button disabled until both fields valid",
                    "Error messages display with ARIA live region"
                ],
                "test_file_paths": [
                    "tests/components/LoginForm.test.tsx",
                    "tests/integration/auth-flow.test.tsx"
                ],
                "research_context_present": True,
                "component_type": "react",
                "accessibility_required": True,
                "performance_targets": {
                    "LCP": "< 2.5s",
                    "FID": "< 100ms",
                    "CLS": "< 0.1"
                }
            }
        }
```

#### Backend Agent Input Model

```python
class BackendAgentHandoff(BaseModel):
    """Validated handoff for Backend Agent delegation."""

    work_block_id: str = Field(..., min_length=3)

    feature_description: str = Field(..., min_length=20)

    acceptance_criteria: List[str] = Field(..., min_items=1)

    test_file_paths: List[str] = Field(..., min_items=1)

    research_context_present: bool = Field(default=False)

    api_type: Literal["rest", "graphql", "grpc", "websocket"] = Field(...)

    database_operations: List[Literal["read", "write", "schema", "migration"]] = Field(
        default_factory=list,
        description="Database operations required"
    )

    external_integrations: List[str] = Field(
        default_factory=list,
        description="External APIs to integrate (e.g., Stripe, Twilio)"
    )

    security_requirements: List[Literal[
        "authentication",
        "authorization",
        "rate-limiting",
        "input-validation",
        "sql-injection-prevention"
    ]] = Field(
        default_factory=list,
        description="Security controls required"
    )

    performance_requirements: Optional[dict] = Field(
        default=None,
        description="Response time, throughput targets"
    )

    @validator('database_operations')
    def validate_migration_safety(cls, ops, values):
        """If schema changes required, ensure migration strategy specified."""
        if 'schema' in ops or 'migration' in ops:
            if 'description' not in values or 'rollback' not in values.get('feature_description', '').lower():
                raise ValueError(
                    "Database migrations must include rollback strategy in description"
                )
        return ops

    @validator('security_requirements')
    def validate_security_presence(cls, reqs, values):
        """Ensure auth endpoints have authentication requirement."""
        description = values.get('feature_description', '').lower()
        if 'auth' in description or 'login' in description or 'signup' in description:
            if 'authentication' not in reqs:
                raise ValueError(
                    "Authentication endpoints must include 'authentication' in security_requirements"
                )
        return reqs
```

#### DevOps Agent Input Model

```python
class DevOpsAgentHandoff(BaseModel):
    """Validated handoff for DevOps Agent delegation."""

    work_block_id: str = Field(..., min_length=3)

    feature_description: str = Field(..., min_length=20)

    acceptance_criteria: List[str] = Field(..., min_items=1)

    infrastructure_type: Literal[
        "iac",
        "ci-cd",
        "containerization",
        "orchestration",
        "monitoring",
        "security",
        "database-ops"
    ] = Field(...)

    cloud_provider: Optional[Literal["aws", "gcp", "azure", "cloudflare", "on-prem"]] = Field(
        default=None
    )

    iac_tool: Optional[Literal["terraform", "pulumi", "cloudformation", "cdk"]] = Field(
        default=None
    )

    environments: List[Literal["dev", "staging", "prod"]] = Field(
        default_factory=lambda: ["dev"],
        description="Target environments"
    )

    security_compliance: List[Literal["soc2", "hipaa", "gdpr", "pci-dss"]] = Field(
        default_factory=list,
        description="Compliance requirements"
    )

    disaster_recovery_required: bool = Field(
        default=False,
        description="Requires backup/restore strategy"
    )

    cost_constraints: Optional[dict] = Field(
        default=None,
        description="Budget limits and cost optimization requirements"
    )

    @validator('infrastructure_type')
    def validate_production_safety(cls, infra_type, values):
        """Ensure production deployments have proper safeguards."""
        envs = values.get('environments', [])
        if 'prod' in envs:
            criteria = values.get('acceptance_criteria', [])
            safety_terms = ['rollback', 'backup', 'monitoring', 'alert']
            has_safety = any(
                any(term in criterion.lower() for term in safety_terms)
                for criterion in criteria
            )
            if not has_safety:
                raise ValueError(
                    "Production deployments must include rollback/backup/monitoring in acceptance criteria"
                )
        return infra_type

    @validator('iac_tool')
    def validate_iac_tool_present(cls, tool, values):
        """Ensure IaC delegations specify tool."""
        if values.get('infrastructure_type') == 'iac' and not tool:
            raise ValueError("IaC infrastructure type requires iac_tool specification")
        return tool
```

#### Test-Writer Agent Input Model

```python
class TestWriterHandoff(BaseModel):
    """Validated handoff for Test-Writer Agent delegation."""

    work_block_id: str = Field(..., min_length=3)

    feature_description: str = Field(..., min_length=20)

    acceptance_criteria: List[str] = Field(..., min_items=1)

    research_context_present: bool = Field(
        default=False,
        description="Confirms Research Agent provided examples"
    )

    implementation_files: List[str] = Field(
        default_factory=list,
        description="Files that will be implemented (for test organization)"
    )

    test_categories: List[Literal[
        "unit",
        "integration",
        "e2e",
        "accessibility",
        "performance",
        "security"
    ]] = Field(
        ...,
        min_items=1,
        description="Types of tests required"
    )

    external_dependencies: List[str] = Field(
        default_factory=list,
        description="External services requiring mocks (APIs, databases, file systems)"
    )

    test_framework: Literal["vitest", "jest", "pytest", "playwright", "cypress"] = Field(
        ...,
        description="Testing framework to use"
    )

    coverage_target: int = Field(
        default=80,
        ge=70,
        le=100,
        description="Code coverage target percentage"
    )

    @validator('test_categories')
    def validate_accessibility_presence(cls, categories, values):
        """Ensure frontend work includes accessibility tests."""
        description = values.get('feature_description', '').lower()
        ui_terms = ['ui', 'component', 'form', 'button', 'page', 'frontend']
        is_ui_work = any(term in description for term in ui_terms)

        if is_ui_work and 'accessibility' not in categories:
            raise ValueError(
                "UI/frontend work must include 'accessibility' in test_categories"
            )
        return categories

    @validator('external_dependencies')
    def validate_mock_strategy(cls, deps, values):
        """Ensure external dependencies have mock strategy."""
        if deps:
            criteria = values.get('acceptance_criteria', [])
            has_mock_mention = any(
                'mock' in criterion.lower() or 'stub' in criterion.lower()
                for criterion in criteria
            )
            if not has_mock_mention:
                raise ValueError(
                    f"External dependencies present ({deps}) but no mock strategy in acceptance criteria"
                )
        return deps
```

#### Test-Auditor Agent Input Model

```python
class TestAuditorHandoff(BaseModel):
    """Validated handoff for Test-Auditor Agent delegation."""

    work_block_id: str = Field(..., min_length=3)

    test_file_paths: List[str] = Field(
        ...,
        min_items=1,
        description="Test files to audit"
    )

    acceptance_criteria: List[str] = Field(
        ...,
        min_items=1,
        description="Original acceptance criteria for comparison"
    )

    implementation_file_paths: List[str] = Field(
        ...,
        min_items=1,
        description="Implementation files being tested"
    )

    audit_focus: List[Literal[
        "coverage-completeness",
        "assertion-strength",
        "mock-quality",
        "test-isolation",
        "failure-validation",
        "naming-quality",
        "environment-handling"
    ]] = Field(
        default_factory=lambda: [
            "coverage-completeness",
            "assertion-strength",
            "mock-quality",
            "test-isolation",
            "failure-validation",
            "naming-quality",
            "environment-handling"
        ],
        description="Aspects to audit (default: all 7)"
    )

    risk_level: Literal["low", "medium", "high", "critical"] = Field(
        default="medium",
        description="Risk level determines audit thoroughness"
    )

    @validator('test_file_paths', each_item=True)
    def validate_test_file(cls, path):
        """Ensure paths point to actual test files."""
        if not any(x in path for x in ['test/', 'tests/', '.test.', '.spec.']):
            raise ValueError(f"Not a test file: {path}")
        return path

    @validator('audit_focus')
    def validate_critical_audits(cls, focus, values):
        """Ensure critical-risk audits include all 7 checks."""
        if values.get('risk_level') == 'critical' and len(focus) < 7:
            raise ValueError(
                "Critical risk level requires all 7 audit checks"
            )
        return focus
```

---

## 3. Team Effectiveness Analysis

### 3.1 Test-Writer vs Implementation Agents

**Current Separation**:
- ✅ **Conceptual**: Clear role boundaries in documentation
- ✅ **Workflow**: TDD phases enforce sequence (tests before implementation)
- ⚠️ **Enforcement**: Only Layer 4 (behavioral) prevents implementation agents from touching tests
- ❌ **Structural**: No automated detection of violations

**How to Strengthen**:

1. **Layer 1 (Tool Restrictions)**: Update agent YAML frontmatter
   ```yaml
   # Frontend/Backend/DevOps agents
   tools: Bash, Read, Glob, Grep, Write(src/**), Edit(src/**)
   # Explicitly exclude test file modifications
   ```

2. **Layer 3 (Hooks)**: Create test file protection hook for implementation agents
   ```python
   # agents/frontend/.claude/hooks/auto-deny.py
   def is_test_file_access(tool_name, file_path):
       test_indicators = ['test/', 'tests/', '.test.', '.spec.']
       return any(indicator in file_path for indicator in test_indicators)

   if is_test_file_access(tool_name, file_path):
       print("❌ VIOLATION: Frontend Agent cannot modify test files")
       print("Route request to Test-Writer Agent via Planning Agent")
       sys.exit(2)
   ```

3. **Layer 5 (Validation)**: Enforce test paths are reference-only
   ```python
   class FrontendAgentHandoff(BaseModel):
       test_file_paths: List[str] = Field(
           ...,
           description="Test files FOR REFERENCE ONLY - cannot modify"
       )

       @validator('test_file_paths')
       def validate_reference_only(cls, paths):
           # Document that these are read-only references
           return paths
   ```

### 3.2 Frontend/Backend/DevOps Coordination

**Current Coordination Gaps**:

1. **No shared infrastructure validation**
   - Frontend assumes API contracts
   - Backend assumes frontend requirements
   - DevOps provisions without validation from both

2. **No handoff for shared concerns**
   - API schemas not validated between Frontend↔Backend
   - Infrastructure requirements not confirmed with Backend before DevOps provision
   - Security headers coordinated via documentation, not validated handoffs

**Recommended Coordination Patterns**:

#### Shared Infrastructure Handoff Model

```python
class SharedInfrastructureHandoff(BaseModel):
    """Coordination between Frontend, Backend, and DevOps agents."""

    api_contract: dict = Field(
        ...,
        description="OpenAPI/GraphQL schema agreed between Frontend and Backend"
    )

    frontend_requirements: dict = Field(
        ...,
        description="CDN, caching, CORS, CSP requirements from Frontend"
    )

    backend_requirements: dict = Field(
        ...,
        description="Database, compute, storage requirements from Backend"
    )

    security_requirements: dict = Field(
        ...,
        description="Auth, secrets, compliance requirements for DevOps"
    )

    @validator('api_contract')
    def validate_contract_completeness(cls, contract):
        """Ensure API contract has required fields."""
        required = ['endpoints', 'authentication', 'error_responses']
        missing = [r for r in required if r not in contract]
        if missing:
            raise ValueError(f"API contract missing: {missing}")
        return contract
```

#### Frontend↔Backend API Contract Validation

```python
class APIContractHandoff(BaseModel):
    """Ensures Frontend and Backend agree on API shape."""

    contract_id: str = Field(..., description="Unique contract identifier")

    endpoints: List[dict] = Field(
        ...,
        description="API endpoints with method, path, request/response schemas"
    )

    frontend_agent_confirmed: bool = Field(
        default=False,
        description="Frontend Agent reviewed and approved contract"
    )

    backend_agent_confirmed: bool = Field(
        default=False,
        description="Backend Agent reviewed and approved contract"
    )

    @validator('endpoints', each_item=True)
    def validate_endpoint_completeness(cls, endpoint):
        """Ensure each endpoint fully specified."""
        required = ['method', 'path', 'request_schema', 'response_schema', 'error_codes']
        missing = [r for r in required if r not in endpoint]
        if missing:
            raise ValueError(f"Endpoint missing fields: {missing}")
        return endpoint

    class Config:
        schema_extra = {
            "example": {
                "contract_id": "AUTH-API-v1",
                "endpoints": [
                    {
                        "method": "POST",
                        "path": "/api/auth/login",
                        "request_schema": {"email": "string", "password": "string"},
                        "response_schema": {"token": "string", "user": "object"},
                        "error_codes": [400, 401, 429, 500]
                    }
                ],
                "frontend_agent_confirmed": True,
                "backend_agent_confirmed": True
            }
        }
```

### 3.3 Handoff Data Requirements

**Per Agent Type**:

| Agent | Required Input | Optional Input | Output |
|-------|----------------|----------------|--------|
| **Frontend** | work_block_id, feature_description, acceptance_criteria, test_file_paths, component_type | research_context, performance_targets | Implementation files, validation report |
| **Backend** | work_block_id, feature_description, acceptance_criteria, test_file_paths, api_type | database_operations, external_integrations, security_requirements | Implementation files, API documentation, validation report |
| **DevOps** | work_block_id, feature_description, acceptance_criteria, infrastructure_type | cloud_provider, iac_tool, environments, security_compliance | IaC files, CI/CD configs, deployment report |
| **Test-Writer** | work_block_id, feature_description, acceptance_criteria, test_categories, test_framework | research_context, implementation_files, external_dependencies | Test files, coverage report |
| **Test-Auditor** | work_block_id, test_file_paths, acceptance_criteria, implementation_file_paths | audit_focus, risk_level | Audit report (PASS/FAIL), fix recommendations |

### 3.4 Anti-Patterns Causing Cross-Agent Conflicts

**Identified Anti-Patterns**:

1. **Implementation Before Tests** (CRITICAL)
   - **Problem**: Action agents start coding before Test-Writer creates tests
   - **Impact**: Tests written to match implementation (not requirements)
   - **Solution**: Phase 3 (Test-Writer) MUST complete before Phase 4 (Implementation)
   - **Enforcement**: Planning Agent validates test files exist before spawning implementation agent

2. **Test File Modification by Implementation Agents** (CRITICAL)
   - **Problem**: Implementation agents "fix" failing tests instead of fixing implementation
   - **Impact**: False positives, gaming tests, quality degradation
   - **Solution**: Multi-layer enforcement (tool restrictions + hooks + validation)
   - **Enforcement**: Layer 1 (tools), Layer 3 (hooks), Layer 5 (validation)

3. **Missing Research Context** (HIGH)
   - **Problem**: Implementation agents use training data instead of current docs
   - **Impact**: Deprecated APIs, outdated patterns, security vulnerabilities
   - **Solution**: Validate research_context_present=True before implementation
   - **Enforcement**: Layer 5 validation rejects handoffs without research confirmation

4. **Vague Acceptance Criteria** (MEDIUM)
   - **Problem**: "Should work correctly" instead of specific, testable criteria
   - **Impact**: Agents guess requirements, incomplete implementations
   - **Solution**: Validate acceptance criteria specificity with Pydantic validators
   - **Enforcement**: Reject criteria containing vague terms ("work", "correct", "good")

5. **Absolute File Paths** (MEDIUM)
   - **Problem**: Handoffs contain `/home/user/project/file.ts` instead of `src/file.ts`
   - **Impact**: Breaks on different machines, security risk
   - **Solution**: Path validators reject absolute paths
   - **Enforcement**: Already present in Planning Agent's Layer 5 integration

6. **Coordination Without Validation** (MEDIUM)
   - **Problem**: Frontend assumes Backend API shape without confirmation
   - **Impact**: Integration failures, rework, delays
   - **Solution**: API contract handoff models validated by both agents
   - **Enforcement**: Require both frontend_agent_confirmed and backend_agent_confirmed=True

---

## 4. Enrichment Recommendations

### 4.1 What to ADD to Each Agent

#### Frontend Agent (Frank) - ADDITIONS

```markdown
## INPUT VALIDATION (Layer 5) - NEW SECTION

Before starting implementation, Planning Agent provides validated handoff via instructor:

\`\`\`python
from scripts.handoff_models import FrontendAgentHandoff

# Planning Agent generates this (automatic validation + retry)
handoff = client.chat.completions.create(
    response_model=FrontendAgentHandoff,
    messages=[{"role": "user", "content": task_description}],
    max_retries=3
)

# You receive validated, structured data:
# - work_block_id: Confirmed valid Linear issue ID
# - acceptance_criteria: Validated as specific and testable
# - test_file_paths: Confirmed as repo-relative test files
# - research_context_present: Confirmed Research Agent enriched issue
\`\`\`

**Pre-Start Checklist** (automatic via validation):
- ✅ Work block ID present and valid
- ✅ Acceptance criteria specific (not vague)
- ✅ Test files created by Test-Writer Agent
- ✅ Research context available in Linear issue
- ✅ Component type specified
- ✅ Accessibility requirements defined

**If handoff validation fails**, Planning Agent will automatically retry with corrections.

---

## TEST FILE ACCESS ENFORCEMENT - ENHANCED

**Layer 1 (Tool Restrictions)**: You have Write/Edit access to `src/**` only
**Layer 3 (Hooks)**: Auto-deny.py blocks test file access attempts
**Layer 4 (Behavioral)**: Self-discipline (this section)
**Layer 5 (Validation)**: test_file_paths marked as reference-only

If you attempt to modify test files:
1. Hook blocks operation with exit code 2
2. Clear error message: "Route to Test-Writer via Planning"
3. Planning Agent respawns Test-Writer to make changes

**NO EXCEPTIONS** - Test file modifications are architectural violations.

---

## RESEARCH CONTEXT VALIDATION - NEW SECTION

Before implementing, verify research context present:

1. **Read Linear issue** - Check for "## Research Context" section
2. **If missing** - Report to Planning Agent: "Research context not found, cannot proceed"
3. **If present** - Review:
   - Recommended approach with version numbers
   - Code examples with version-specific syntax
   - Reference documentation links
   - Implementation notes and gotchas

**Trust Research Agent over training data** - Your training data may be from 2023.

Research Agent provides 2025 sources via MCP tools (ref.tools, exa, perplexity).

---

## ACCESSIBILITY VALIDATION - AUTOMATED

**NEW**: Validation model ensures accessibility requirements specified

If `accessibility_required: true` in handoff (default for UI work):
- Run axe DevTools on every component
- Target: Lighthouse accessibility ≥ 90 (prefer 100)
- Zero tolerance for keyboard navigation failures
- WCAG 2.2 AA compliance mandatory

**Performance validation similarly automated** - performance_targets in handoff.

---
```

#### Backend Agent (Billy) - ADDITIONS

```markdown
## CLEANUP REQUIRED - REMOVE STALE CONTENT

**Lines 16-50**: DELETE - Contains Planning Agent persona (copy-paste error)

This content does not belong in Backend Agent:
- "You are updating the WORKFLOW FRAMEWORK, not user projects"
- "When user provides prompts referencing project-specific examples"
- Feature Selection Protocol section

**Action**: Remove lines 16-71 entirely (through duplicate Feature Selection Protocol)

---

## INPUT VALIDATION (Layer 5) - NEW SECTION

[Same pattern as Frontend Agent, using BackendAgentHandoff model]

Additional Backend-specific validations:
- `api_type` validated (rest/graphql/grpc/websocket)
- `security_requirements` enforced for auth endpoints
- `database_operations` validated for migration safety
- `external_integrations` documented for mock requirements

---

## TEST FILE ACCESS ENFORCEMENT - ENHANCED

[Same multi-layer enforcement as Frontend Agent]

---

## DATABASE MIGRATION SAFETY - NEW SECTION

**NEW**: Validation model enforces migration safety requirements

If `database_operations` includes 'schema' or 'migration':
- Handoff MUST include rollback strategy in description
- Validation automatically rejects migrations without rollback plan
- Planning Agent will prompt for rollback strategy if missing

**Zero tolerance for unsafe migrations** - Pydantic validator enforces this.

---

## API SECURITY VALIDATION - AUTOMATED

**NEW**: Security requirements automatically validated

If feature involves authentication/authorization:
- Validator ensures 'authentication' in security_requirements
- Forces explicit security consideration
- Prevents accidental insecure endpoints

Manual security checklist (lines 229-236) remains for implementation phase.

---
```

#### DevOps Agent (Clay) - ADDITIONS

```markdown
## CLEANUP REQUIRED - REMOVE STALE CONTENT

**Lines 16-50**: DELETE - Contains Planning Agent persona (copy-paste error)

[Same cleanup as Backend Agent]

---

## INPUT VALIDATION (Layer 5) - NEW SECTION

[Same pattern, using DevOpsAgentHandoff model]

Additional DevOps-specific validations:
- `infrastructure_type` validated (iac/ci-cd/containerization/etc.)
- `cloud_provider` specified if cloud infrastructure
- `iac_tool` required for IaC infrastructure type
- `production deployments` validated for safety requirements

---

## PRODUCTION DEPLOYMENT SAFETY - NEW SECTION

**NEW**: Validation model enforces production safety requirements

If `environments` includes 'prod':
- Acceptance criteria MUST mention rollback/backup/monitoring
- Validator automatically checks for safety terms
- Rejects production deployments without explicit safeguards

**Manual checklist remains** (lines 543-598) but initial validation catches missing requirements early.

---

## COST CONSTRAINTS VALIDATION - NEW SECTION

**NEW**: Cost awareness built into handoffs

If `cost_constraints` present in handoff:
- Budget limits documented
- Cost optimization strategies required
- Post-deployment cost verification mandatory

Helps prevent surprise cloud bills.

---
```

#### Test-Writer Agent - ADDITIONS

```markdown
## INPUT VALIDATION (Layer 5) - NEW SECTION

[Same pattern, using TestWriterHandoff model]

Additional Test-Writer-specific validations:
- `test_categories` validated (unit/integration/e2e/accessibility/etc.)
- `test_framework` specified (vitest/jest/pytest/playwright/cypress)
- `external_dependencies` documented for mock requirements
- `accessibility tests` required for UI work (automatic validator)

---

## MOCK STRATEGY ENFORCEMENT - NEW SECTION

**NEW**: Validation ensures mock strategy specified

If `external_dependencies` present (APIs, databases, file systems):
- Acceptance criteria MUST mention mock strategy
- Validator rejects handoffs without explicit mock guidance
- Forces Planning Agent to clarify mock requirements upfront

**Prevents common failure mode**: Writing tests that call real APIs.

---

## COVERAGE TARGET ENFORCEMENT - NEW SECTION

**NEW**: Coverage targets explicit in handoff

- Default: 80% coverage
- Range: 70-100% (validated by Pydantic)
- Critical features: 90%+ coverage required
- Displayed in test plan documentation

---

## ASSERTION STRENGTH VALIDATION - AUTOMATED DETECTION

**NEW**: Weak assertion detection (future enhancement)

Current: Manual review (your responsibility)
Future: Automated AST parsing detects:
- `toBeTruthy()` usage (weak)
- `toBeDefined()` usage (weak)
- `not.toThrow()` without behavior validation (weak)

For now: Follow self-check protocol (lines 504-518) to catch weak assertions.

---
```

#### Test-Auditor Agent - ADDITIONS

```markdown
## INPUT VALIDATION (Layer 5) - NEW SECTION

[Same pattern, using TestAuditorHandoff model]

Additional Test-Auditor-specific validations:
- `test_file_paths` validated as actual test files
- `audit_focus` validated (7 standard checks)
- `risk_level` determines audit thoroughness
- `critical risk` requires all 7 audit checks (validator enforces)

---

## RISK-BASED AUDIT AUTOMATION - NEW SECTION

**NEW**: Audit thoroughness scales with risk level

| Risk Level | Required Checks | Failure Tolerance | Re-Audit |
|------------|-----------------|-------------------|----------|
| **low** | 3 of 7 checks | Medium issues OK | No |
| **medium** | 5 of 7 checks | Critical issues only | Optional |
| **high** | All 7 checks | Medium issues flagged | Recommended |
| **critical** | All 7 checks | Zero tolerance | Mandatory |

Validator enforces: critical risk → all 7 checks required.

---

## AUTOMATED CHECKLIST ASSISTANCE - FUTURE

**Current**: Manual 7-point checklist (lines 79-228)
**Future**: Partial automation via AST parsing
  - Coverage completeness: pytest --cov analysis
  - Assertion strength: AST detection of weak patterns
  - Test isolation: Detect shared state between tests
  - Naming quality: Regex validation of test names

Manual audit remains gold standard, automation assists.

---
```

### 4.2 What to REMOVE

#### All Implementation Agents (Frontend, Backend, DevOps)

**REMOVE**:
1. Duplicate "Feature Selection Protocol" sections (inappropriate for implementation agents)
2. Stale "project-agnostic workflow framework" content (Backend/DevOps agents, lines 16-50)
3. References to deprecated technologies (currently none, but mechanism needed)
4. Vague "best practices" sections that don't provide concrete guidance

**Backend Agent specific removals**:
- Lines 16-71: Entire "project-agnostic workflow" section (Planning Agent content)

**DevOps Agent specific removals**:
- Lines 16-71: Entire "project-agnostic workflow" section (Planning Agent content)

#### Test-Writer Agent

**REMOVE**:
- None identified - agent is well-structured

**Future deprecation notices**:
- Add mechanism to flag deprecated test frameworks (e.g., if project moves from Jest to Vitest)

#### Test-Auditor Agent

**REMOVE**:
- None identified - agent is well-structured

### 4.3 What to MODIFY

#### All Implementation Agents

**MODIFY**:

1. **Tool restrictions (YAML frontmatter)**
   ```yaml
   # Current (too permissive):
   tools: Bash, Read, Write, Edit, Glob, Grep

   # Proposed (explicit boundaries):
   tools: Bash, Read, Glob, Grep, Write(src/**|docs/**), Edit(src/**|docs/**)
   # Explicitly exclude tests/, scripts/, agents/, .claude/
   ```

2. **Test file restriction sections**
   - Move from middle of document to TOP (line 36 for Frontend, line 75 for Backend/DevOps)
   - Add visual emphasis (more ⚠️ warnings)
   - Include hook enforcement explanation
   - Reference Layer 5 validation

3. **Research context consumption**
   - Make research brief review MANDATORY first step
   - Add validation that research was actually read (checklist or quiz-style)
   - Link to Research Agent documentation

4. **Validation checklists**
   - Convert manual checklists to references to Pydantic models
   - Note: "This validation performed automatically via Layer 5"
   - Keep checklists as implementation guidance, not pre-flight checks

#### Frontend Agent Specific

**MODIFY**:

1. **Lines 768-810 (Research Brief section)**
   - Elevate to required protocol, not optional guidance
   - Add validation step: "Confirm research context read"
   - Cross-reference to research_context_present field in handoff

2. **Lines 303-351 (Validation Checklist)**
   - Add note: "Pre-validated by Layer 5 - focus on implementation quality"
   - Reframe as implementation checklist, not handoff checklist

#### Backend Agent Specific

**MODIFY**:

1. **Lines 229-236 (Security Checklist)**
   - Add reference to security_requirements in handoff validation
   - Note: "Auth endpoints automatically flagged by Layer 5"
   - Keep checklist for implementation phase

2. **Lines 253-278 (Validation Checklist)**
   - Same as Frontend: Reframe as implementation-phase checklist

#### DevOps Agent Specific

**MODIFY**:

1. **Lines 543-598 (Validation Checklist)**
   - Add reference to handoff validation
   - Note: "Production deployments pre-validated by Layer 5"
   - Keep for implementation verification

2. **Lines 847-992 (Security Best Practices)**
   - Cross-reference to security_compliance field in handoff
   - Emphasize that compliance requirements specified upfront

#### Test-Writer Agent

**MODIFY**:

1. **Lines 21-30 (Self-Check Protocol)**
   - Add validation confirmation: "Verify handoff contained mock strategy"
   - Reference external_dependencies field in TestWriterHandoff

2. **Lines 504-518 (Self-Audit Checkpoint)**
   - Add validation check: "Did handoff specify test categories correctly?"
   - Catch edge cases where Planning Agent didn't use validation

#### Test-Auditor Agent

**MODIFY**:

1. **Lines 79-228 (Audit Checklist)**
   - Add risk-based filtering: "For low-risk audits, focus on checks 1, 2, 5"
   - Reference risk_level field in TestAuditorHandoff
   - Note which checks can be partially automated (future)

2. **Lines 382-429 (Requesting Fixes)**
   - Formalize Test-Writer delegation protocol
   - Include template for fix requests
   - Reference handoff validation for fix requests

---

## 5. Required .claude/ Enforcement Configs

### 5.1 Directory Structure

```
agents/
├── frontend/
│   ├── .claude/
│   │   ├── settings.json          # Layer 2: Directory-scoped config
│   │   └── hooks/
│   │       ├── auto-deny.py       # Layer 3: Hook-based enforcement
│   │       └── config.json        # Hook configuration
│   ├── frontend-agent.md          # Layer 4: Behavioral directives
│   └── CLAUDE.md                  # Agent-specific overrides
├── backend/
│   ├── .claude/
│   │   ├── settings.json
│   │   └── hooks/
│   │       ├── auto-deny.py
│   │       └── config.json
│   ├── backend-agent.md
│   └── CLAUDE.md
├── devops/
│   ├── .claude/
│   │   ├── settings.json
│   │   └── hooks/
│   │       ├── auto-deny.py
│   │       └── config.json
│   ├── devops-agent.md
│   └── CLAUDE.md
├── test-writer/
│   ├── .claude/
│   │   ├── settings.json
│   │   └── hooks/
│   │       ├── auto-deny.py
│   │       └── config.json
│   ├── test-writer-agent.md
│   └── CLAUDE.md
└── test-auditor/
    ├── .claude/
    │   ├── settings.json
    │   └── hooks/
    │       └── config.json
    ├── test-auditor-agent.md
    └── CLAUDE.md
```

### 5.2 Frontend Agent Configuration

**File**: `agents/frontend/.claude/settings.json`

```json
{
  "name": "frontend-agent",
  "description": "Frontend implementation specialist - UI/UX, accessibility, performance",
  "model": "sonnet",
  "tools": ["Bash", "Read", "Glob", "Grep", "Write", "Edit"],
  "allowed_write_patterns": [
    "src/**",
    "public/**",
    "docs/**",
    "*.md",
    "!tests/**",
    "!test/**",
    "!*.test.*",
    "!*.spec.*",
    "!scripts/**",
    "!agents/**",
    "!.claude/**"
  ],
  "hooks": {
    "PreToolUse": "hooks/auto-deny.py"
  },
  "validation": {
    "handoff_model": "FrontendAgentHandoff",
    "required_fields": [
      "work_block_id",
      "feature_description",
      "acceptance_criteria",
      "test_file_paths",
      "component_type"
    ]
  }
}
```

**File**: `agents/frontend/.claude/hooks/auto-deny.py`

```python
#!/usr/bin/env python3
"""
Frontend Agent Hook: Prevents test file modifications and enforces boundaries.

Layer 3 Enforcement for Frontend Agent.
"""

import sys
import json

def load_context():
    """Load hook context from stdin."""
    try:
        context = json.load(sys.stdin)
        return context
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON context", file=sys.stderr)
        sys.exit(1)

def is_test_file(file_path):
    """Check if file path is a test file."""
    test_indicators = [
        'test/',
        'tests/',
        '.test.',
        '.spec.',
        'cypress/',
        'playwright/',
        '__tests__/'
    ]
    return any(indicator in file_path for indicator in test_indicators)

def is_restricted_path(file_path):
    """Check if file path is in restricted directory."""
    restricted = [
        'scripts/',
        'agents/',
        '.claude/',
        'handoffs/'
    ]
    return any(restricted_dir in file_path for restricted_dir in restricted)

def main():
    context = load_context()

    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})

    # Extract file path from tool input
    file_path = tool_input.get('file_path', '')

    if not file_path:
        # No file path, allow operation
        sys.exit(0)

    # Check for test file access
    if tool_name in ['Write', 'Edit', 'NotebookEdit']:
        if is_test_file(file_path):
            print("❌ VIOLATION: Frontend Agent cannot modify test files")
            print(f"   File: {file_path}")
            print(f"   Tool: {tool_name}")
            print()
            print("✅ CORRECT ACTION:")
            print("   1. Report to Planning Agent: 'Test files need update'")
            print("   2. Planning Agent will spawn Test-Writer Agent")
            print("   3. Test-Writer Agent makes necessary changes")
            print()
            print("WHY: Test file ownership prevents gaming tests to pass bad code")
            sys.exit(2)

    # Check for restricted directory access
    if tool_name in ['Write', 'Edit', 'NotebookEdit']:
        if is_restricted_path(file_path):
            print("❌ VIOLATION: Frontend Agent cannot modify system files")
            print(f"   File: {file_path}")
            print(f"   Tool: {tool_name}")
            print()
            print("✅ CORRECT ACTION:")
            print("   Report to Planning Agent for proper delegation")
            sys.exit(2)

    # Allow operation
    sys.exit(0)

if __name__ == '__main__':
    main()
```

**File**: `agents/frontend/.claude/hooks/config.json`

```json
{
  "PreToolUse": {
    "script": "auto-deny.py",
    "executable": true,
    "description": "Prevents test file modifications and enforces Frontend Agent boundaries"
  }
}
```

### 5.3 Backend Agent Configuration

**File**: `agents/backend/.claude/settings.json`

```json
{
  "name": "backend-agent",
  "description": "Backend implementation specialist - APIs, databases, business logic",
  "model": "sonnet",
  "tools": ["Bash", "Read", "Glob", "Grep", "Write", "Edit"],
  "allowed_write_patterns": [
    "src/**",
    "lib/**",
    "api/**",
    "docs/**",
    "migrations/**",
    "*.md",
    "!tests/**",
    "!test/**",
    "!*.test.*",
    "!*.spec.*",
    "!scripts/**",
    "!agents/**",
    "!.claude/**"
  ],
  "hooks": {
    "PreToolUse": "hooks/auto-deny.py"
  },
  "validation": {
    "handoff_model": "BackendAgentHandoff",
    "required_fields": [
      "work_block_id",
      "feature_description",
      "acceptance_criteria",
      "test_file_paths",
      "api_type"
    ]
  }
}
```

**File**: `agents/backend/.claude/hooks/auto-deny.py`

```python
#!/usr/bin/env python3
"""
Backend Agent Hook: Prevents test file modifications and enforces boundaries.

Layer 3 Enforcement for Backend Agent.
"""

import sys
import json

def load_context():
    """Load hook context from stdin."""
    try:
        context = json.load(sys.stdin)
        return context
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON context", file=sys.stderr)
        sys.exit(1)

def is_test_file(file_path):
    """Check if file path is a test file."""
    test_indicators = [
        'test/',
        'tests/',
        '.test.',
        '.spec.',
        'pytest/',
        '__tests__/'
    ]
    return any(indicator in file_path for indicator in test_indicators)

def is_restricted_path(file_path):
    """Check if file path is in restricted directory."""
    restricted = [
        'scripts/',
        'agents/',
        '.claude/',
        'handoffs/',
        'frontend/',  # Backend shouldn't touch frontend code
        'public/'
    ]
    return any(restricted_dir in file_path for restricted_dir in restricted)

def main():
    context = load_context()

    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})

    # Extract file path from tool input
    file_path = tool_input.get('file_path', '')

    if not file_path:
        # No file path, allow operation
        sys.exit(0)

    # Check for test file access
    if tool_name in ['Write', 'Edit', 'NotebookEdit']:
        if is_test_file(file_path):
            print("❌ VIOLATION: Backend Agent cannot modify test files")
            print(f"   File: {file_path}")
            print(f"   Tool: {tool_name}")
            print()
            print("✅ CORRECT ACTION:")
            print("   1. Report to Planning Agent: 'Test files need update'")
            print("   2. Planning Agent will spawn Test-Writer Agent")
            print("   3. Test-Writer Agent makes necessary changes")
            print()
            print("WHY: Test file ownership prevents gaming tests to pass bad code")
            sys.exit(2)

    # Check for restricted directory access
    if tool_name in ['Write', 'Edit', 'NotebookEdit']:
        if is_restricted_path(file_path):
            print("❌ VIOLATION: Backend Agent cannot modify system or frontend files")
            print(f"   File: {file_path}")
            print(f"   Tool: {tool_name}")
            print()
            print("✅ CORRECT ACTION:")
            print("   Report to Planning Agent for proper delegation")
            sys.exit(2)

    # Allow operation
    sys.exit(0)

if __name__ == '__main__':
    main()
```

**File**: `agents/backend/.claude/hooks/config.json`

```json
{
  "PreToolUse": {
    "script": "auto-deny.py",
    "executable": true,
    "description": "Prevents test file modifications and enforces Backend Agent boundaries"
  }
}
```

### 5.4 DevOps Agent Configuration

**File**: `agents/devops/.claude/settings.json`

```json
{
  "name": "devops-agent",
  "description": "Infrastructure and deployment specialist - IaC, CI/CD, monitoring",
  "model": "sonnet",
  "tools": ["Bash", "Read", "Glob", "Grep", "Write", "Edit"],
  "allowed_write_patterns": [
    "terraform/**",
    "infra/**",
    "infrastructure/**",
    ".github/workflows/**",
    ".gitlab-ci.yml",
    "docker/**",
    "Dockerfile*",
    "k8s/**",
    "kubernetes/**",
    "docs/**",
    "*.md",
    "!tests/**",
    "!test/**",
    "!*.test.*",
    "!*.spec.*",
    "!src/**",
    "!lib/**",
    "!scripts/handoff_models.py",
    "!agents/**",
    "!.claude/**"
  ],
  "hooks": {
    "PreToolUse": "hooks/auto-deny.py"
  },
  "validation": {
    "handoff_model": "DevOpsAgentHandoff",
    "required_fields": [
      "work_block_id",
      "feature_description",
      "acceptance_criteria",
      "infrastructure_type"
    ]
  }
}
```

**File**: `agents/devops/.claude/hooks/auto-deny.py`

```python
#!/usr/bin/env python3
"""
DevOps Agent Hook: Prevents test file modifications and enforces boundaries.

Layer 3 Enforcement for DevOps Agent.
"""

import sys
import json

def load_context():
    """Load hook context from stdin."""
    try:
        context = json.load(sys.stdin)
        return context
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON context", file=sys.stderr)
        sys.exit(1)

def is_test_file(file_path):
    """Check if file path is a test file."""
    test_indicators = [
        'test/',
        'tests/',
        '.test.',
        '.spec.'
    ]
    return any(indicator in file_path for indicator in test_indicators)

def is_application_code(file_path):
    """Check if file path is application code (not infrastructure)."""
    app_code_indicators = [
        'src/',
        'lib/',
        'api/',
        'components/',
        'pages/',
        'services/'
    ]
    return any(indicator in file_path for indicator in app_code_indicators)

def is_restricted_path(file_path):
    """Check if file path is in restricted directory."""
    restricted = [
        'scripts/handoff_models.py',
        'agents/',
        '.claude/',
        'handoffs/'
    ]
    return any(restricted_path in file_path for restricted_path in restricted)

def main():
    context = load_context()

    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})

    # Extract file path from tool input
    file_path = tool_input.get('file_path', '')

    if not file_path:
        # No file path, allow operation
        sys.exit(0)

    # Check for test file access
    if tool_name in ['Write', 'Edit', 'NotebookEdit']:
        if is_test_file(file_path):
            print("❌ VIOLATION: DevOps Agent cannot modify test files")
            print(f"   File: {file_path}")
            print(f"   Tool: {tool_name}")
            print()
            print("NOTE: DevOps can CONFIGURE test runners in CI/CD")
            print("      but cannot modify test code itself")
            print()
            print("✅ CORRECT ACTION:")
            print("   1. Report to Planning Agent: 'Test files need update'")
            print("   2. Planning Agent will spawn Test-Writer Agent")
            sys.exit(2)

    # Check for application code access
    if tool_name in ['Write', 'Edit', 'NotebookEdit']:
        if is_application_code(file_path):
            print("❌ VIOLATION: DevOps Agent cannot modify application code")
            print(f"   File: {file_path}")
            print(f"   Tool: {tool_name}")
            print()
            print("✅ CORRECT ACTION:")
            print("   Route to Frontend or Backend Agent via Planning Agent")
            sys.exit(2)

    # Check for restricted directory access
    if tool_name in ['Write', 'Edit', 'NotebookEdit']:
        if is_restricted_path(file_path):
            print("❌ VIOLATION: DevOps Agent cannot modify system files")
            print(f"   File: {file_path}")
            print(f"   Tool: {tool_name}")
            print()
            print("✅ CORRECT ACTION:")
            print("   Report to Planning Agent for proper delegation")
            sys.exit(2)

    # Allow operation
    sys.exit(0)

if __name__ == '__main__':
    main()
```

**File**: `agents/devops/.claude/hooks/config.json`

```json
{
  "PreToolUse": {
    "script": "auto-deny.py",
    "executable": true,
    "description": "Prevents test file modifications, application code access, and enforces DevOps Agent boundaries"
  }
}
```

### 5.5 Test-Writer Agent Configuration

**File**: `agents/test-writer/.claude/settings.json`

```json
{
  "name": "test-writer-agent",
  "description": "Test creation and validation specialist - exclusive test file ownership",
  "model": "sonnet",
  "tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "NotebookEdit", "Task", "TodoWrite"],
  "allowed_write_patterns": [
    "tests/**",
    "test/**",
    "*.test.*",
    "*.spec.*",
    "cypress/**",
    "playwright/**",
    "__tests__/**",
    "vitest.config.*",
    "jest.config.*",
    "pytest.ini",
    "docs/.scratch/**",
    "!src/**",
    "!lib/**",
    "!api/**",
    "!agents/**",
    "!.claude/**"
  ],
  "hooks": {
    "PreToolUse": "hooks/auto-deny.py"
  },
  "validation": {
    "handoff_model": "TestWriterHandoff",
    "required_fields": [
      "work_block_id",
      "feature_description",
      "acceptance_criteria",
      "test_categories",
      "test_framework"
    ]
  }
}
```

**File**: `agents/test-writer/.claude/hooks/auto-deny.py`

```python
#!/usr/bin/env python3
"""
Test-Writer Agent Hook: Prevents implementation code modifications.

Layer 3 Enforcement for Test-Writer Agent.
"""

import sys
import json

def load_context():
    """Load hook context from stdin."""
    try:
        context = json.load(sys.stdin)
        return context
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON context", file=sys.stderr)
        sys.exit(1)

def is_implementation_code(file_path):
    """Check if file path is implementation code (not test)."""
    impl_indicators = [
        'src/',
        'lib/',
        'api/',
        'app/',
        'components/',
        'pages/',
        'services/',
        'utils/',
        'middleware/'
    ]
    # Exclude test directories even within these paths
    test_indicators = ['test/', 'tests/', '.test.', '.spec.', '__tests__/']

    is_impl = any(indicator in file_path for indicator in impl_indicators)
    is_test = any(indicator in file_path for indicator in test_indicators)

    return is_impl and not is_test

def is_restricted_path(file_path):
    """Check if file path is in restricted directory."""
    restricted = [
        'agents/',
        '.claude/',
        'handoffs/',
        'scripts/handoff_models.py',
        'terraform/',
        'infra/',
        'infrastructure/'
    ]
    return any(restricted_path in file_path for restricted_path in restricted)

def main():
    context = load_context()

    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})

    # Extract file path from tool input
    file_path = tool_input.get('file_path', '')

    if not file_path:
        # No file path, allow operation
        sys.exit(0)

    # Check for implementation code access
    if tool_name in ['Write', 'Edit', 'NotebookEdit']:
        if is_implementation_code(file_path):
            print("❌ VIOLATION: Test-Writer Agent cannot modify implementation code")
            print(f"   File: {file_path}")
            print(f"   Tool: {tool_name}")
            print()
            print("✅ CORRECT ACTION:")
            print("   1. If code needs fixing to pass tests:")
            print("      Report to Planning Agent: 'Implementation needs update'")
            print("   2. Planning Agent routes to appropriate implementation agent")
            print()
            print("WHY: Test file ownership is EXCLUSIVE - you own tests, they own code")
            sys.exit(2)

    # Check for restricted directory access
    if tool_name in ['Write', 'Edit', 'NotebookEdit']:
        if is_restricted_path(file_path):
            print("❌ VIOLATION: Test-Writer Agent cannot modify system files")
            print(f"   File: {file_path}")
            print(f"   Tool: {tool_name}")
            print()
            print("✅ CORRECT ACTION:")
            print("   Report to Planning Agent for proper delegation")
            sys.exit(2)

    # Allow operation (test files and docs)
    sys.exit(0)

if __name__ == '__main__':
    main()
```

**File**: `agents/test-writer/.claude/hooks/config.json`

```json
{
  "PreToolUse": {
    "script": "auto-deny.py",
    "executable": true,
    "description": "Prevents implementation code modifications and enforces Test-Writer Agent boundaries"
  }
}
```

### 5.6 Test-Auditor Agent Configuration

**File**: `agents/test-auditor/.claude/settings.json`

```json
{
  "name": "test-auditor-agent",
  "description": "Test quality auditor - read-only analysis of test files",
  "model": "sonnet",
  "tools": ["Bash", "Read", "Glob", "Grep", "Task", "TodoWrite"],
  "allowed_write_patterns": [
    "docs/.scratch/**",
    "!tests/**",
    "!test/**",
    "!src/**",
    "!lib/**",
    "!api/**",
    "!agents/**",
    "!.claude/**"
  ],
  "hooks": {
    "PreToolUse": "hooks/auto-deny.py"
  },
  "validation": {
    "handoff_model": "TestAuditorHandoff",
    "required_fields": [
      "work_block_id",
      "test_file_paths",
      "acceptance_criteria",
      "implementation_file_paths"
    ]
  }
}
```

**File**: `agents/test-auditor/.claude/hooks/auto-deny.py`

```python
#!/usr/bin/env python3
"""
Test-Auditor Agent Hook: Enforces read-only mode for test files.

Layer 3 Enforcement for Test-Auditor Agent.
"""

import sys
import json

def load_context():
    """Load hook context from stdin."""
    try:
        context = json.load(sys.stdin)
        return context
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON context", file=sys.stderr)
        sys.exit(1)

def is_code_file(file_path):
    """Check if file path is code (test or implementation)."""
    code_indicators = [
        'src/',
        'lib/',
        'api/',
        'tests/',
        'test/',
        '.test.',
        '.spec.',
        'components/',
        'services/'
    ]
    return any(indicator in file_path for indicator in code_indicators)

def is_restricted_path(file_path):
    """Check if file path is in restricted directory."""
    restricted = [
        'agents/',
        '.claude/',
        'handoffs/',
        'scripts/handoff_models.py'
    ]
    return any(restricted_path in file_path for restricted_path in restricted)

def main():
    context = load_context()

    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})

    # Extract file path from tool input
    file_path = tool_input.get('file_path', '')

    if not file_path:
        # No file path, allow operation
        sys.exit(0)

    # Check for ANY code file write attempts
    if tool_name in ['Write', 'Edit', 'NotebookEdit']:
        if is_code_file(file_path):
            print("❌ VIOLATION: Test-Auditor Agent is READ-ONLY for code files")
            print(f"   File: {file_path}")
            print(f"   Tool: {tool_name}")
            print()
            print("✅ CORRECT ACTION:")
            print("   1. If test files need fixes:")
            print("      Request Test-Writer Agent add missing tests")
            print("   2. If implementation needs fixes:")
            print("      Report to Planning Agent for implementation agent")
            print()
            print("WHY: Auditors analyze, writers modify. Role separation matters.")
            sys.exit(2)

    # Check for restricted directory access
    if tool_name in ['Write', 'Edit', 'NotebookEdit']:
        if is_restricted_path(file_path):
            print("❌ VIOLATION: Test-Auditor Agent cannot modify system files")
            print(f"   File: {file_path}")
            print(f"   Tool: {tool_name}")
            print()
            print("✅ CORRECT ACTION:")
            print("   Report to Planning Agent for proper delegation")
            sys.exit(2)

    # Allow operation (read operations and docs/.scratch writes)
    sys.exit(0)

if __name__ == '__main__':
    main()
```

**File**: `agents/test-auditor/.claude/hooks/config.json`

```json
{
  "PreToolUse": {
    "script": "auto-deny.py",
    "executable": true,
    "description": "Enforces read-only mode for code files and prevents system file modifications"
  }
}
```

---

## 6. TDD Workflow Integration

### 6.1 How Test-Writer/Test-Auditor Fit TDD Phases

**Phase 3: Test Creation (RED Phase)**

Test-Writer Agent responsibilities:
1. Receive validated handoff from Planning Agent (via Layer 5)
2. Read research context from Linear issue (code examples, version numbers)
3. Create test files covering:
   - Happy path (normal usage)
   - Edge cases (boundary conditions, empty inputs)
   - Error conditions (invalid inputs, missing data, failures)
4. Use proper mocking for external dependencies
5. Verify tests FAIL appropriately (no false positives)
6. Document test plan in `docs/.scratch/<issue>/test-plan.md`
7. Handoff to Planning Agent with test locations

**Phase 3.5: Test Audit (Quality Gate)**

Test-Auditor Agent responsibilities:
1. Receive validated handoff from Planning Agent
2. Read test files and run 7-point checklist:
   - Coverage completeness
   - Assertion strength
   - Mock quality
   - Test isolation
   - Failure validation
   - Naming quality
   - Environment handling
3. Audit result:
   - **PASS**: Approve for implementation → Phase 4
   - **FAIL**: Request Test-Writer add missing tests → Retry Phase 3
4. Handoff audit report to Planning Agent

**Phase 4: Implementation (GREEN Phase)**

Implementation Agents (Frontend/Backend/DevOps) responsibilities:
1. Receive validated handoff from Planning Agent
2. Read research context from Linear issue
3. Read test files to understand expected behavior
4. Implement ONLY enough code to pass tests
5. Run tests iteratively until all green
6. **FORBIDDEN** from modifying test files
7. Handoff to Planning Agent when tests pass

**Phase 5: Validation**

Test-Writer Agent responsibilities:
1. Receive validated handoff from Planning Agent
2. Run full test suite
3. Verify all tests PASS
4. Check for mesa-optimization (tests passing trivially)
5. Run security checks and validation commands
6. Validation result:
   - **PASS**: Implementation meets requirements → Phase 6
   - **FAIL**: Issues found → Back to Phase 4 (implementation retry)
7. Handoff validation report to Planning Agent

### 6.2 Role Separation Enforcement

**Conceptual Separation** (TDD Workflow Document):
- Phase 3: Test-Writer creates tests
- Phase 4: Implementation agents write code
- Phase 5: Test-Writer validates implementation
- Test-Auditor provides quality gate in Phase 3.5

**Behavioral Separation** (Layer 4 - Agent Prompts):
- Strong directives in each agent's .md file
- Self-check protocols
- Violation reporting templates
- Explicit "FORBIDDEN" sections

**Structural Separation** (Layer 5 - Validation):
- Pydantic models validate handoffs
- Field validators enforce constraints
- Model validators check cross-field consistency
- Automatic retry on validation failures

**Tool Separation** (Layer 1 - SubAgent Restrictions):
- YAML frontmatter defines allowed tools
- Implementation agents restricted from test files
- Test-Writer restricted from implementation files
- Test-Auditor read-only for code files

**Directory Separation** (Layer 2 - Scoped Configs):
- Each agent has own `.claude/settings.json`
- `allowed_write_patterns` enforce boundaries
- Launch from agent directory activates config

**Hook Separation** (Layer 3 - PreToolUse Hooks):
- Auto-deny.py scripts block violations
- Exit code 2 prevents operation
- Helpful error messages suggest correct delegation
- Validated working on PopOS 22.04

### 6.3 Integration Points

**Planning Agent → Test-Writer** (Phase 3):
```python
# Planning Agent generates validated handoff
handoff = client.chat.completions.create(
    response_model=TestWriterHandoff,
    messages=[{"role": "user", "content": delegation_prompt}],
    max_retries=3
)

# Spawn Test-Writer with validated data
spawn_agent(
    agent="test-writer",
    work_block=handoff.work_block_id,
    task=handoff.feature_description,
    criteria=handoff.acceptance_criteria,
    categories=handoff.test_categories,
    framework=handoff.test_framework,
    dependencies=handoff.external_dependencies
)
```

**Planning Agent → Test-Auditor** (Phase 3.5):
```python
# Planning Agent generates validated audit request
audit_request = client.chat.completions.create(
    response_model=TestAuditorHandoff,
    messages=[{"role": "user", "content": audit_prompt}],
    max_retries=3
)

# Spawn Test-Auditor with validated data
spawn_agent(
    agent="test-auditor",
    work_block=audit_request.work_block_id,
    test_files=audit_request.test_file_paths,
    impl_files=audit_request.implementation_file_paths,
    criteria=audit_request.acceptance_criteria,
    risk_level=audit_request.risk_level
)
```

**Planning Agent → Implementation Agent** (Phase 4):
```python
# Planning Agent generates validated implementation handoff
impl_handoff = client.chat.completions.create(
    response_model=FrontendAgentHandoff,  # or Backend/DevOps
    messages=[{"role": "user", "content": implementation_prompt}],
    max_retries=3
)

# Spawn Implementation Agent with validated data
spawn_agent(
    agent=impl_handoff.agent_name,
    work_block=impl_handoff.work_block_id,
    task=impl_handoff.feature_description,
    criteria=impl_handoff.acceptance_criteria,
    test_files=impl_handoff.test_file_paths,
    research_present=impl_handoff.research_context_present
)
```

---

## 7. Implementation Roadmap

### Priority 1: Critical (Week 1)

**1.1 Add Layer 5 Validation Models**
- File: `scripts/handoff_models.py`
- Add: `FrontendAgentHandoff`, `BackendAgentHandoff`, `DevOpsAgentHandoff`
- Add: `TestWriterHandoff`, `TestAuditorHandoff`
- Add: Field validators and model validators
- Test: Validate with example delegations
- **Impact**: Prevents invalid handoffs, enforces quality

**1.2 Create Layer 3 Hooks for All Agents**
- Create: `agents/{agent}/.claude/hooks/auto-deny.py` for each agent
- Test: Validate hooks block test file access for implementation agents
- Test: Validate hooks block implementation access for Test-Writer
- Test: Validate hooks enforce read-only for Test-Auditor
- **Impact**: Structural enforcement of role boundaries

**1.3 Clean Up Backend/DevOps Agent Prompts**
- Remove: Lines 16-71 from `backend-agent.md` and `devops-agent.md`
- Remove: Duplicate Feature Selection Protocol sections
- Test: Verify agents still function correctly
- **Impact**: Removes confusion from copy-paste errors

### Priority 2: High (Week 2)

**2.1 Add Layer 5 Sections to Agent Prompts**
- Add: Input Validation sections to all agent .md files
- Add: References to Pydantic models
- Add: Enhanced enforcement protocol sections
- Test: Verify agents understand validation workflow
- **Impact**: Behavioral reinforcement of structural validation

**2.2 Create Directory-Scoped Configs (Layer 2)**
- Create: `.claude/settings.json` for each agent
- Add: `allowed_write_patterns` restrictions
- Test: Validate configs work with hook enforcement
- **Impact**: Multiple layers of boundary enforcement

**2.3 Update agent-spawn-templates.md**
- Add: Layer 5 validation instructions for each spawn template
- Add: Pydantic model references
- Add: Example validated delegations
- Test: Verify Planning Agent can follow new templates
- **Impact**: Standardizes validated delegation patterns

### Priority 3: Medium (Week 3)

**3.1 Create API Contract Coordination Models**
- Add: `SharedInfrastructureHandoff` model
- Add: `APIContractHandoff` model
- Test: Validate Frontend↔Backend coordination
- **Impact**: Prevents integration failures

**3.2 Add Research Context Validation**
- Update: All handoff models with `research_context_present` field
- Add: Validator that confirms research was performed
- Test: Ensure implementation agents can't start without research
- **Impact**: Prevents use of outdated training data

**3.3 Document Enforcement Layers**
- Create: `docs/enforcement-architecture.md`
- Document: Each layer with examples
- Document: How layers interact
- Test: Verify documentation matches implementation
- **Impact**: Helps future developers understand system

### Priority 4: Low (Week 4)

**4.1 Add Automated Assertion Strength Detection**
- Create: AST parser for test files
- Detect: Weak assertions (`toBeTruthy`, `toBeDefined`)
- Integrate: With Test-Auditor workflow
- Test: Validate detection accuracy
- **Impact**: Partially automates test audit

**4.2 Create Validation Dashboard**
- Track: Handoff validation success/failure rates
- Track: Common validation errors
- Track: Agent boundary violations
- Display: Metrics for system health
- **Impact**: Visibility into enforcement effectiveness

**4.3 Add Cost Constraint Tracking**
- Extend: DevOps handoff model with cost validation
- Track: Infrastructure costs against constraints
- Alert: When nearing budget limits
- **Impact**: Prevents surprise cloud bills

---

## 8. Conclusion

### Summary of Findings

The implementation agents (Frontend, Backend, DevOps, Test-Writer, Test-Auditor) are **well-designed at the conceptual level** with clear role boundaries and strong behavioral directives. However, they lack **structural enforcement** through Layer 5 (Instructor Validation), making them vulnerable to role boundary violations and invalid handoffs.

### Key Recommendations

1. **Integrate Layer 5 validation** across all agents (currently only Planning Agent has it)
2. **Deploy Layer 3 hooks** to provide automatic denial of boundary violations
3. **Clean up stale content** from Backend and DevOps agent prompts
4. **Create coordination models** for Frontend↔Backend↔DevOps shared infrastructure
5. **Enforce research context** validation before implementation starts

### Expected Impact

After implementing these recommendations:
- **Zero role boundary violations** (hooks + validation prevent)
- **100% validated handoffs** (Pydantic models enforce quality)
- **Clear coordination** between agents (API contracts, infrastructure requirements)
- **Training data obsolescence eliminated** (research context validation)
- **Testable quality gates** (Test-Auditor with risk-based enforcement)

### Next Steps

1. Review this report with human stakeholders
2. Prioritize recommendations based on project constraints
3. Begin Week 1 implementation (Priority 1 items)
4. Iterate based on feedback and observed effectiveness

---

**Research Complete**
**Agent**: Research Agent
**Date**: 2025-01-13
**Confidence Level**: HIGH
**Sources**: Agent .md files, TDD workflow documentation, Instructor validation library, IW enforcement architecture
