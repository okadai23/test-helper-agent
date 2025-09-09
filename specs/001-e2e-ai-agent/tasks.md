# Tasks: E2E Test Automation AI Agent

**Input**: Design documents from `/specs/001-e2e-ai-agent/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Project structure**: `src/test_helper/e2e/` for implementation
- **Tests**: `tests/contract/`, `tests/integration/`, `tests/unit/`, `tests/e2e/`
- **Data storage**: `data/projects/` for runtime data

## Phase 3.1: Setup
- [ ] T001 Create E2E submodule structure in src/test_helper/e2e/ with __init__.py files
- [ ] T002 Add E2E dependencies to pyproject.toml (openai, temporalio, playwright, pydantic)
- [ ] T003 [P] Create docker-compose.yml for Temporal server and Playwright MCP services
- [ ] T004 [P] Configure pytest fixtures for E2E testing in tests/conftest.py
- [ ] T005 [P] Setup data storage directories (data/projects/, data/cache/)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests
- [ ] T006 [P] Contract test POST /api/v1/projects in tests/contract/test_projects_post.py
- [ ] T007 [P] Contract test GET /api/v1/projects/{id} in tests/contract/test_projects_get.py
- [ ] T008 [P] Contract test PATCH /api/v1/projects/{id} in tests/contract/test_projects_patch.py
- [ ] T009 [P] Contract test DELETE /api/v1/projects/{id} in tests/contract/test_projects_delete.py
- [ ] T010 [P] Contract test GET /api/v1/projects in tests/contract/test_projects_list.py
- [ ] T011 [P] Contract test POST /api/v1/projects/{id}/capture in tests/contract/test_capture_start.py
- [ ] T012 [P] Contract test GET /api/v1/projects/{id}/capture/{session_id} in tests/contract/test_capture_get.py
- [ ] T013 [P] Contract test POST /api/v1/projects/{id}/capture/{session_id} in tests/contract/test_capture_stop.py
- [ ] T014 [P] Contract test POST /api/v1/projects/{id}/generate in tests/contract/test_generate_tests.py
- [ ] T015 [P] Contract test GET /api/v1/projects/{id}/tests in tests/contract/test_tests_list.py
- [ ] T016 [P] Contract test GET /api/v1/projects/{id}/tests/{test_id} in tests/contract/test_tests_get.py
- [ ] T017 [P] Contract test PATCH /api/v1/projects/{id}/tests/{test_id} in tests/contract/test_tests_patch.py
- [ ] T018 [P] Contract test POST /api/v1/projects/{id}/execute in tests/contract/test_execute_tests.py
- [ ] T019 [P] Contract test GET /api/v1/projects/{id}/executions/{execution_id} in tests/contract/test_executions_get.py
- [ ] T020 [P] Contract test POST /api/v1/projects/{id}/fix in tests/contract/test_fix_tests.py
- [ ] T021 [P] Contract test POST /api/v1/projects/{id}/fix/{proposal_id}/apply in tests/contract/test_fix_apply.py
- [ ] T022 [P] Contract test GET /api/v1/projects/{id}/history in tests/contract/test_history_get.py

### Integration Tests
- [ ] T023 [P] Integration test: Create project and capture session flow in tests/integration/test_project_capture_flow.py
- [ ] T024 [P] Integration test: Generate tests from captured interactions in tests/integration/test_generate_from_capture.py
- [ ] T025 [P] Integration test: Execute generated tests in tests/integration/test_execute_generated_tests.py
- [ ] T026 [P] Integration test: Fix failing tests automatically in tests/integration/test_auto_fix_tests.py
- [ ] T027 [P] Integration test: E-commerce scenario workflow in tests/integration/test_ecommerce_scenario.py

### E2E Tests
- [ ] T028 [P] E2E test: Complete user journey from project creation to test execution in tests/e2e/test_complete_journey.py
- [ ] T029 [P] E2E test: Test failure and auto-fix workflow in tests/e2e/test_failure_fix_workflow.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Models (Pydantic)
- [ ] T030 [P] Project model in src/test_helper/e2e/models/project.py
- [ ] T031 [P] Scenario model in src/test_helper/e2e/models/scenario.py
- [ ] T032 [P] Step models (Click, Input, Navigate, Wait, Assert) in src/test_helper/e2e/models/step.py
- [ ] T033 [P] Execution model in src/test_helper/e2e/models/execution.py
- [ ] T034 [P] FixProposal model in src/test_helper/e2e/models/fix_proposal.py
- [ ] T035 [P] BrowserConfig and ViewportSize models in src/test_helper/e2e/models/browser_config.py
- [ ] T036 [P] CaptureSession model in src/test_helper/e2e/models/capture_session.py

### Core Libraries
- [ ] T037 [P] Playwright MCP client wrapper in src/test_helper/e2e/lib/playwright_mcp.py
- [ ] T038 [P] Temporal workflow definitions in src/test_helper/e2e/lib/temporal_workflows.py
- [ ] T039 [P] Storage manager for projects/tests in src/test_helper/e2e/lib/storage_manager.py

### AI Agents
- [ ] T040 [P] Capture agent using OpenAI SDK in src/test_helper/e2e/agents/capture_agent.py
- [ ] T041 [P] Generator agent for test creation in src/test_helper/e2e/agents/generator_agent.py
- [ ] T042 [P] Diagnostic agent for failure analysis in src/test_helper/e2e/agents/diagnostic_agent.py
- [ ] T043 [P] Fix agent for test repair in src/test_helper/e2e/agents/fix_agent.py

### Services
- [ ] T044 Capture service orchestrating browser interactions in src/test_helper/e2e/services/capture_service.py
- [ ] T045 Generator service for test code creation in src/test_helper/e2e/services/generator_service.py
- [ ] T046 Analyzer service for test failure analysis in src/test_helper/e2e/services/analyzer_service.py
- [ ] T047 Fix service for automatic test repair in src/test_helper/e2e/services/fix_service.py

### CLI Commands
- [ ] T048 CLI main entry point with Click/Typer in src/test_helper/e2e/cli/commands.py
- [ ] T049 Project management commands (create, list, get, update, delete) in src/test_helper/e2e/cli/commands.py
- [ ] T050 Capture commands (start, stop, status, list) in src/test_helper/e2e/cli/commands.py
- [ ] T051 Test generation commands in src/test_helper/e2e/cli/commands.py
- [ ] T052 Test execution commands in src/test_helper/e2e/cli/commands.py
- [ ] T053 Fix commands (analyze, apply, review) in src/test_helper/e2e/cli/commands.py

### API Endpoints (FastAPI)
- [ ] T054 Project endpoints router in src/test_helper/e2e/api/projects.py
- [ ] T055 Capture endpoints router in src/test_helper/e2e/api/capture.py
- [ ] T056 Test management endpoints router in src/test_helper/e2e/api/tests.py
- [ ] T057 Execution endpoints router in src/test_helper/e2e/api/executions.py
- [ ] T058 Fix endpoints router in src/test_helper/e2e/api/fixes.py
- [ ] T059 Main FastAPI app with routers in src/test_helper/e2e/api/app.py

## Phase 3.4: Integration

### Service Integration
- [ ] T060 Connect Temporal client to workflows in src/test_helper/e2e/services/workflow_client.py
- [ ] T061 Integrate Playwright MCP with capture service
- [ ] T062 Connect OpenAI agents with services
- [ ] T063 Wire storage manager with all services

### Middleware & Infrastructure
- [ ] T064 Error handling middleware for API in src/test_helper/e2e/api/middleware.py
- [ ] T065 Logging configuration with structlog in src/test_helper/e2e/lib/logging.py
- [ ] T066 Request/response validation with Pydantic
- [ ] T067 CORS and security headers configuration

### Data Persistence
- [ ] T068 Project metadata JSON storage implementation
- [ ] T069 Test file management (save/load Playwright tests)
- [ ] T070 Cache management for selectors and patterns
- [ ] T071 History tracking and retention policies

## Phase 3.5: Polish

### Unit Tests
- [ ] T072 [P] Unit tests for Project model validation in tests/unit/test_project_model.py
- [ ] T073 [P] Unit tests for Scenario model validation in tests/unit/test_scenario_model.py
- [ ] T074 [P] Unit tests for Step models in tests/unit/test_step_models.py
- [ ] T075 [P] Unit tests for storage manager in tests/unit/test_storage_manager.py
- [ ] T076 [P] Unit tests for selector strategies in tests/unit/test_selectors.py

### Performance & Optimization
- [ ] T077 Performance tests for test generation (<5 seconds) in tests/performance/test_generation_speed.py
- [ ] T078 Performance tests for test fixing (<10 seconds) in tests/performance/test_fix_speed.py
- [ ] T079 Memory usage tests (<2GB per agent) in tests/performance/test_memory_usage.py
- [ ] T080 Concurrent project handling tests in tests/performance/test_concurrency.py

### Documentation
- [ ] T081 [P] API documentation with OpenAPI/Swagger
- [ ] T082 [P] CLI help text and examples
- [ ] T083 [P] Update README.md with E2E features
- [ ] T084 [P] Create CHANGELOG.md for version 0.1.0
- [ ] T085 [P] Generate llms.txt documentation

### Cleanup & Refactoring
- [ ] T086 Remove code duplication across services
- [ ] T087 Extract common patterns to utilities
- [ ] T088 Add type hints to all functions
- [ ] T089 Run linting and formatting (ruff, pyright)
- [ ] T090 Manual testing with quickstart.md scenarios

## Dependencies
- Setup (T001-T005) must complete first
- All tests (T006-T029) before ANY implementation
- Models (T030-T036) can be parallel but before services
- Agents and libraries (T037-T043) can be parallel
- Services (T044-T047) depend on agents and models
- CLI (T048-T053) depends on services
- API (T054-T059) depends on services
- Integration (T060-T071) depends on core implementation
- Polish (T072-T090) after everything else

## Parallel Execution Examples

### Batch 1: Contract Tests (can run all together)
```bash
# Launch T006-T022 in parallel:
Task: "Contract test POST /api/v1/projects in tests/contract/test_projects_post.py"
Task: "Contract test GET /api/v1/projects/{id} in tests/contract/test_projects_get.py"
# ... (all contract tests)
```

### Batch 2: Models (after tests fail)
```bash
# Launch T030-T036 in parallel:
Task: "Project model in src/test_helper/e2e/models/project.py"
Task: "Scenario model in src/test_helper/e2e/models/scenario.py"
# ... (all models)
```

### Batch 3: Core Components
```bash
# Launch T037-T043 in parallel:
Task: "Playwright MCP client wrapper in src/test_helper/e2e/lib/playwright_mcp.py"
Task: "Capture agent using OpenAI SDK in src/test_helper/e2e/agents/capture_agent.py"
# ... (all agents and libraries)
```

## Notes
- [P] tasks = different files, no shared dependencies
- Verify ALL tests fail before implementing anything
- Commit after each task with conventional commits
- Use TDD strictly: RED (test fails) → GREEN (implement) → REFACTOR
- Services and API cannot be parallel due to shared dependencies
- CLI commands are in same file, so sequential (T048-T053)

## Validation Checklist
*GATE: Checked before execution*

- [x] All 17 API operations have contract tests
- [x] All 7 entities have model tasks
- [x] All tests come before implementation (T006-T029 before T030-T059)
- [x] Parallel tasks are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] Integration scenarios from quickstart.md included
- [x] Performance requirements have tests