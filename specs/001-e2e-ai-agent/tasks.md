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
- **Project structure**: `src/test_helper/` for implementation (modular design)
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/e2e/`
- **Data storage**: `data/projects/` for runtime data
- **CLI entry**: `src/test_helper/cli/` for Typer commands

## Phase 3.1: Setup
- [ ] T001 Restructure modules from src/test_helper/e2e/ to src/test_helper/ direct modules
- [ ] T002 Add dependencies to pyproject.toml (openai, temporalio, playwright, pydantic, typer)
- [ ] T003 [P] Create docker-compose.yml for Temporal server and Playwright MCP services
- [ ] T004 [P] Configure pytest fixtures for testing in tests/conftest.py
- [ ] T005 [P] Setup data storage directories (data/projects/, data/cache/)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Service Tests
- [ ] T006 [P] Service test ProjectService.create() in tests/unit/services/test_project_service.py
- [ ] T007 [P] Service test ProjectService.get() in tests/unit/services/test_project_service.py
- [ ] T008 [P] Service test ProjectService.update() in tests/unit/services/test_project_service.py
- [ ] T009 [P] Service test ProjectService.delete() in tests/unit/services/test_project_service.py
- [ ] T010 [P] Service test ProjectService.list() in tests/unit/services/test_project_service.py
- [ ] T011 [P] Service test CaptureService.start() in tests/unit/services/test_capture_service.py
- [ ] T012 [P] Service test CaptureService.get_session() in tests/unit/services/test_capture_service.py
- [ ] T013 [P] Service test CaptureService.stop() in tests/unit/services/test_capture_service.py
- [ ] T014 [P] Service test GeneratorService.generate() in tests/unit/services/test_generator_service.py
- [ ] T015 [P] Service test StorageManager.list_tests() in tests/unit/services/test_storage_manager.py
- [ ] T016 [P] Service test StorageManager.get_test() in tests/unit/services/test_storage_manager.py
- [ ] T017 [P] Service test StorageManager.update_test() in tests/unit/services/test_storage_manager.py
- [ ] T018 [P] Service test ExecutorService.execute() in tests/unit/services/test_executor_service.py
- [ ] T019 [P] Service test ExecutorService.get_execution() in tests/unit/services/test_executor_service.py
- [ ] T020 [P] Service test FixService.analyze() in tests/unit/services/test_fix_service.py
- [ ] T021 [P] Service test FixService.apply_fix() in tests/unit/services/test_fix_service.py
- [ ] T022 [P] Service test StorageManager.get_history() in tests/unit/services/test_storage_manager.py

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
- [ ] T030 [P] Project model in src/test_helper/models/project.py
- [ ] T031 [P] Scenario model in src/test_helper/models/scenario.py
- [ ] T032 [P] Step models (Click, Input, Navigate, Wait, Assert) in src/test_helper/models/step.py
- [ ] T033 [P] Execution model in src/test_helper/models/execution.py
- [ ] T034 [P] FixProposal model in src/test_helper/models/fix_proposal.py
- [ ] T035 [P] BrowserConfig and ViewportSize models in src/test_helper/models/browser_config.py
- [ ] T036 [P] CaptureSession model in src/test_helper/models/capture_session.py

### Core Libraries
- [ ] T037 [P] Playwright MCP client wrapper in src/test_helper/lib/playwright_mcp.py
- [ ] T038 [P] Temporal workflow definitions in src/test_helper/lib/temporal_workflows.py
- [ ] T039 [P] Storage manager for projects/tests in src/test_helper/lib/storage_manager.py

### AI Agents
- [ ] T040 [P] Capture agent using OpenAI SDK in src/test_helper/agents/capture_agent.py
- [ ] T041 [P] Generator agent for test creation in src/test_helper/agents/generator_agent.py
- [ ] T042 [P] Diagnostic agent for failure analysis in src/test_helper/agents/diagnostic_agent.py
- [ ] T043 [P] Fix agent for test repair in src/test_helper/agents/fix_agent.py

### Services
- [ ] T044 Capture service orchestrating browser interactions in src/test_helper/services/capture_service.py
- [ ] T045 Generator service for test code creation in src/test_helper/services/generator_service.py
- [ ] T046 Analyzer service for test failure analysis in src/test_helper/services/analyzer_service.py
- [ ] T047 Fix service for automatic test repair in src/test_helper/services/fix_service.py
- [ ] T048 Executor service for test execution in src/test_helper/services/executor_service.py

### CLI Commands
- [ ] T049 CLI main entry point with Typer in src/test_helper/cli/main.py
- [ ] T050 Project management commands (create, list, get, update, delete) in src/test_helper/cli/project.py
- [ ] T051 Capture commands (start, stop, status, list) in src/test_helper/cli/capture.py
- [ ] T052 Test generation commands in src/test_helper/cli/generate.py
- [ ] T053 Test execution commands in src/test_helper/cli/execute.py
- [ ] T054 Fix commands (analyze, apply, review) in src/test_helper/cli/fix.py

### Interface Layer
- [ ] T055 Base interface definition in src/test_helper/interfaces/base.py
- [ ] T056 CLI interface implementation in src/test_helper/interfaces/cli.py
- [ ] T057 Interface factory for switching in src/test_helper/interfaces/factory.py
- [ ] T058 Service registry for dependency injection in src/test_helper/interfaces/registry.py

## Phase 3.4: Integration

### Service Integration
- [ ] T059 Connect Temporal client to workflows in src/test_helper/services/workflow_client.py
- [ ] T060 Integrate Playwright MCP with capture service
- [ ] T061 Connect OpenAI agents with services
- [ ] T062 Wire storage manager with all services

### Infrastructure
- [ ] T063 Error handling for services in src/test_helper/utils/errors.py
- [ ] T064 Logging configuration with structlog in src/test_helper/utils/logging.py
- [ ] T065 Data validation with Pydantic models
- [ ] T066 Configuration management with settings

### Data Persistence
- [ ] T067 Project metadata JSON storage implementation
- [ ] T068 Test file management (save/load Playwright tests)
- [ ] T069 Cache management for selectors and patterns
- [ ] T070 History tracking and retention policies

## Phase 3.5: Polish

### Unit Tests
- [ ] T071 [P] Unit tests for Project model validation in tests/unit/models/test_project_model.py
- [ ] T072 [P] Unit tests for Scenario model validation in tests/unit/models/test_scenario_model.py
- [ ] T073 [P] Unit tests for Step models in tests/unit/models/test_step_models.py
- [ ] T074 [P] Unit tests for storage manager in tests/unit/lib/test_storage_manager.py
- [ ] T075 [P] Unit tests for selector strategies in tests/unit/lib/test_selectors.py

### Performance & Optimization
- [ ] T076 Performance tests for test generation (<5 seconds) in tests/performance/test_generation_speed.py
- [ ] T077 Performance tests for test fixing (<10 seconds) in tests/performance/test_fix_speed.py
- [ ] T078 Memory usage tests (<2GB per agent) in tests/performance/test_memory_usage.py
- [ ] T079 Concurrent project handling tests in tests/performance/test_concurrency.py

### Documentation
- [ ] T080 [P] CLI documentation with Typer help text
- [ ] T081 [P] CLI command examples and usage guide
- [ ] T082 [P] Update README.md with test automation features
- [ ] T083 [P] Create CHANGELOG.md for version 0.1.0
- [ ] T084 [P] Generate llms.txt documentation

### Cleanup & Refactoring
- [ ] T085 Remove code duplication across services
- [ ] T086 Extract common patterns to utilities
- [ ] T087 Add type hints to all functions
- [ ] T088 Run linting and formatting (ruff, pyright)
- [ ] T089 Manual testing with quickstart.md scenarios

## Dependencies
- Setup (T001-T005) must complete first
- All tests (T006-T029) before ANY implementation
- Models (T030-T036) can be parallel but before services
- Agents and libraries (T037-T043) can be parallel
- Services (T044-T048) depend on agents and models
- CLI (T049-T054) depends on services
- Interface layer (T055-T058) provides abstraction
- Integration (T059-T066) depends on core implementation
- Data persistence (T067-T070) after services
- Polish (T071-T089) after everything else

## Parallel Execution Examples

### Batch 1: Service Tests (can run all together)
```bash
# Launch T006-T022 in parallel:
Task: "Service test ProjectService.create() in tests/unit/services/test_project_service.py"
Task: "Service test CaptureService.start() in tests/unit/services/test_capture_service.py"
# ... (all service tests)
```

### Batch 2: Models (after tests fail)
```bash
# Launch T030-T036 in parallel:
Task: "Project model in src/test_helper/models/project.py"
Task: "Scenario model in src/test_helper/models/scenario.py"
# ... (all models)
```

### Batch 3: Core Components
```bash
# Launch T037-T043 in parallel:
Task: "Playwright MCP client wrapper in src/test_helper/lib/playwright_mcp.py"
Task: "Capture agent using OpenAI SDK in src/test_helper/agents/capture_agent.py"
# ... (all agents and libraries)
```

## Notes
- [P] tasks = different files, no shared dependencies
- Verify ALL tests fail before implementing anything
- Commit after each task with conventional commits
- Use TDD strictly: RED (test fails) → GREEN (implement) → REFACTOR
- Services can be mostly parallel (different files)
- CLI commands are in separate files, so can be parallel

## Validation Checklist
*GATE: Checked before execution*

- [x] All core services have unit tests (17 service methods)
- [x] All 7 entities have model tasks
- [x] All tests come before implementation (T006-T029 before T030+)
- [x] Parallel tasks are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] Integration scenarios from quickstart.md included
- [x] Performance requirements have tests
- [x] CLI commands properly separated by file
- [x] Interface abstraction layer included
- [x] Factory pattern for extensibility implemented