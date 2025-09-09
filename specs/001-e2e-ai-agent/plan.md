# Implementation Plan: E2E Test Automation AI Agent

**Branch**: `001-e2e-ai-agent` | **Date**: 2025-09-09 | **Spec**: [/specs/001-e2e-ai-agent/spec.md]
**Input**: Feature specification from `/specs/001-e2e-ai-agent/spec.md`

## Execution Flow (/plan command scope)

```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:

-   Phase 2: /tasks command creates tasks.md
-   Phase 3-4: Implementation execution (manual or via tools)

## Summary

E2E Test Automation AI Agent system that automatically generates and maintains Playwright tests for web applications. The system captures user interactions, generates test code, and automatically fixes failing tests when applications change, using OpenAI Agents SDK for AI orchestration and Temporal for workflow management.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: OpenAI Agents SDK, Temporal Python SDK, Playwright MCP, Playwright, Pydantic
**Storage**: Local JSON files for cache, file system for test projects
**Testing**: pytest, Playwright test runner
**Target Platform**: Linux/MacOS/Windows with Docker support
**Project Type**: single - Python library with CLI interface
**Performance Goals**: Test generation < 5 seconds, test fix < 10 seconds, parallel test execution
**Constraints**: Memory < 2GB per agent, support 100+ test files per project
**Scale/Scope**: Support multiple concurrent test projects, 100 test files retention, 30 days history

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Simplicity**:

-   Projects: 1 (single Python library)
-   Using framework directly? Yes (Playwright, Temporal, OpenAI SDK directly)
-   Single data model? Yes (Pydantic models for all entities)
-   Avoiding patterns? Yes (no unnecessary abstractions)

**Architecture**:

-   EVERY feature as library? Yes (core test generation library)
-   Libraries listed:
    -   `test_helper.e2e`: E2E test automation sub-module (integrated)
    -   `test_helper.e2e.capture`: Browser interaction capture
    -   `test_helper.e2e.analyzer`: Test failure analysis
    -   `test_helper.e2e.storage`: Project and test management
-   CLI per library:
    -   `test-helper e2e --help/--version/--format` (E2E subcommand)
    -   `test-helper e2e capture --help`
    -   `test-helper e2e analyze --help`
    -   `test-helper e2e generate --help`
-   Library docs: llms.txt format planned? Yes

**Testing (NON-NEGOTIABLE)**:

-   RED-GREEN-Refactor cycle enforced? Yes
-   Git commits show tests before implementation? Yes
-   Order: Contract→Integration→E2E→Unit strictly followed? Yes
-   Real dependencies used? Yes (real browser, real Temporal server)
-   Integration tests for: new libraries, contract changes, shared schemas? Yes
-   FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:

-   Structured logging included? Yes
-   Frontend logs → backend? N/A (no frontend)
-   Error context sufficient? Yes

**Versioning**:

-   Version number assigned? 0.1.0
-   BUILD increments on every change? Yes
-   Breaking changes handled? Yes (versioned API contracts)

## Project Structure

### Documentation (this feature)

```
specs/001-e2e-ai-agent/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

```
# Current project structure (test-helper-agent)
src/
├── test_helper/           # Extended with E2E test automation features
│   ├── __init__.py
│   ├── e2e/              # E2E test automation sub-module
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── project.py      # E2E project model
│   │   │   ├── scenario.py     # Test scenario model
│   │   │   ├── execution.py    # Test execution model
│   │   │   └── fix_proposal.py # Fix proposal model
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── capture_service.py
│   │   │   ├── generator_service.py
│   │   │   ├── analyzer_service.py
│   │   │   └── fix_service.py
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   └── commands.py
│   │   ├── lib/
│   │   │   ├── __init__.py
│   │   │   ├── playwright_mcp.py
│   │   │   ├── temporal_workflows.py
│   │   │   └── storage_manager.py
│   │   └── agents/
│   │       ├── __init__.py
│   │       ├── capture_agent.py
│   │       ├── generator_agent.py
│   │       ├── diagnostic_agent.py
│   │       └── fix_agent.py
│   ├── interfaces/       # Existing code
│   ├── models/           # Existing code
│   ├── utils/            # Existing code

tests/
├── contract/
├── integration/
├── unit/
├── api/
└── e2e/

data/
├── projects/
│   └── {project_id}/
│       ├── metadata.json
│       ├── tests/
│       ├── cache/
│       └── history/
```

**Structure Decision**: Integrate E2E automation features into existing test_helper module - Python library with CLI interface

## Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:

    - OpenAI Agents SDK best practices and patterns
    - Temporal workflow design for test automation
    - Playwright MCP integration approach
    - Local storage structure for test projects
    - Pydantic model design for test entities

2. **Generate and dispatch research agents**:

    ```
    Task: "Research OpenAI Agents SDK for test automation workflows"
    Task: "Find best practices for Temporal in Python for long-running test operations"
    Task: "Research Playwright MCP for browser automation integration"
    Task: "Design JSON schema for test project storage"
    Task: "Research Pydantic patterns for test data validation"
    ```

3. **Consolidate findings** in `research.md` using format:
    - Decision: [what was chosen]
    - Rationale: [why chosen]
    - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts

_Prerequisites: research.md complete_

1. **Extract entities from feature spec** → `data-model.md`:

    - Project (id, name, url, metadata) - E2E test project
    - Scenario (steps, assertions, selectors) - Test scenario
    - Step (action, selector, value) - Individual test step
    - Execution (status, duration, artifacts) - Test execution record
    - FixProposal (changes, confidence, rationale)
    - BrowserSession (config, state)

2. **Generate API contracts** from functional requirements:

    - POST /api/v1/projects - Create test project
    - POST /api/v1/projects/{id}/capture - Start capture session
    - POST /api/v1/projects/{id}/generate - Generate tests
    - POST /api/v1/projects/{id}/execute - Run tests
    - POST /api/v1/projects/{id}/fix - Fix failing tests
    - GET /api/v1/projects/{id}/tests - List tests
    - GET /api/v1/projects/{id}/history - Get test history

3. **Generate contract tests** from contracts:

    - One test file per endpoint in tests/contract/
    - Assert request/response schemas
    - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:

    - Capture and generate test from user interactions
    - Fix failing test after UI change
    - Handle flaky test optimization
    - Manage multiple test scenarios

5. **Update agent file incrementally** (O(1) operation):
    - Update CLAUDE.md with E2E test automation context
    - Add new technologies: OpenAI Agents SDK, Temporal, Playwright MCP
    - Update recent changes section

**Output**: data-model.md, /contracts/\*, failing tests, quickstart.md, CLAUDE.md

## Phase 2: Task Planning Approach

_This section describes what the /tasks command will do - DO NOT execute during /plan_

**Task Generation Strategy**:

-   Load `/templates/tasks-template.md` as base
-   Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
-   Each contract → contract test task [P]
-   Each entity → model creation task [P]
-   Each user story → integration test task
-   Implementation tasks to make tests pass

**Ordering Strategy**:

-   TDD order: Tests before implementation
-   Dependency order: Models before services before UI
-   Mark [P] for parallel execution (independent files)

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation

_These phases are beyond the scope of the /plan command_

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking

_No violations - design follows constitution principles_

## Progress Tracking

_This checklist is updated during execution flow_

**Phase Status**:

-   [x] Phase 0: Research complete (/plan command)
-   [x] Phase 1: Design complete (/plan command)
-   [x] Phase 2: Task planning complete (/plan command - describe approach only)
-   [ ] Phase 3: Tasks generated (/tasks command)
-   [ ] Phase 4: Implementation complete
-   [ ] Phase 5: Validation passed

**Gate Status**:

-   [x] Initial Constitution Check: PASS
-   [x] Post-Design Constitution Check: PASS
-   [x] All NEEDS CLARIFICATION resolved
-   [x] Complexity deviations documented

---

_Based on Constitution v2.1.1 - See `/memory/constitution.md`_
