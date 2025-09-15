# Test Helper Agent - Implementation Plan

## Overview
This document outlines the implementation plan for enhancing the Test Helper Agent application with TypeScript/Playwright test generation, syntax fixing, and improved CLI functionality.

## Requirements

### 1. Test Syntax Fix Agent
- Create a new agent that can automatically fix syntax errors in generated Playwright TypeScript test files
- Implement iterative fixing until all syntax errors are resolved
- Integrate with Node.js tooling for linting and validation

### 2. Node.js/TypeScript Infrastructure
- Set up project-wide Node.js module management
- Install TypeScript and Playwright linting tools
- Create npm scripts for linting and building TypeScript files
- Integrate Node.js tooling with Python agents

### 3. Package Installation & CLI
- Make the project installable as a package via `uv pip install -e .[dev,agents]`
- Create `test-helper` command entry point
- Add `--dot-env` parameter for environment file configuration
- Integrate all agent commands into main CLI interface

### 4. File Organization
- Organize mock test data for reuse
- Clean up temporary test files
- Establish proper directory structure for generated tests

### 5. Environment Configuration
- Implement flexible .env file loading
- Support optional path specification
- Default to current directory .env if not specified

## Implementation Tasks

### Phase 1: Node.js/TypeScript Setup
1. [ ] Create package.json with TypeScript and Playwright dependencies
2. [ ] Install ESLint, Prettier, and TypeScript compiler
3. [ ] Configure tsconfig.json for Playwright tests
4. [ ] Create npm scripts for linting and fixing
5. [ ] Set up .eslintrc.json with Playwright rules

### Phase 2: Test Syntax Fix Agent
6. [ ] Create `SyntaxFixAgent` class in `src/test_helper/agents/`
7. [ ] Implement TypeScript syntax error detection using `tsc`
8. [ ] Implement ESLint error detection and auto-fixing
9. [ ] Create iterative fixing mechanism
10. [ ] Add unit tests for SyntaxFixAgent
11. [ ] Create service wrapper in `src/test_helper/services/`

### Phase 3: Package Configuration
12. [ ] Update pyproject.toml with proper entry points
13. [ ] Add `test-helper` console script
14. [ ] Configure package dependencies properly
15. [ ] Test package installation with `uv pip install -e .[dev,agents]`

### Phase 4: Environment Configuration
16. [ ] Enhance `settings.py` to accept custom .env paths
17. [ ] Add `--dot-env` parameter to CLI commands
18. [ ] Implement fallback to current directory .env
19. [ ] Update all CLI commands to use new settings

### Phase 5: CLI Integration
20. [ ] Create unified CLI interface in `src/test_helper/interfaces/cli.py`
21. [ ] Add `generate`, `capture`, `diagnose`, `fix` commands
22. [ ] Add `syntax-check` command for TypeScript validation
23. [ ] Implement proper error handling and user feedback

### Phase 6: File Organization
24. [ ] Create `data/mock_sessions/` for reusable test sessions
25. [ ] Move example sessions to organized directories
26. [ ] Clean up temporary test files
27. [ ] Update .gitignore appropriately

### Phase 7: Integration Testing
28. [ ] Test complete workflow in mock mode
29. [ ] Test complete workflow in SDK mode with real OpenAI API
30. [ ] Verify syntax fixing works for common errors
31. [ ] Document usage in README.md

## Directory Structure

```
test-helper-agent/
├── src/
│   └── test_helper/
│       ├── agents/
│       │   ├── syntax_fix_agent.py  # NEW
│       │   └── ...
│       ├── services/
│       │   ├── syntax_fix_service.py  # NEW
│       │   └── ...
│       ├── interfaces/
│       │   └── cli.py  # ENHANCED
│       └── utils/
│           └── settings.py  # ENHANCED
├── tests/
│   └── unit/
│       └── agents/
│           └── test_syntax_fix_agent.py  # NEW
├── data/
│   ├── mock_sessions/  # NEW
│   │   ├── landing_page.json
│   │   └── comprehensive_test.json
│   └── generated_tests/  # NEW
├── node_modules/  # NEW (git-ignored)
├── package.json  # NEW
├── package-lock.json  # NEW
├── tsconfig.json  # NEW
├── .eslintrc.json  # NEW
├── .prettierrc.json  # NEW
└── pyproject.toml  # ENHANCED

```

## Success Criteria

1. ✅ `test-helper` command works after package installation
2. ✅ Generated TypeScript tests have no syntax errors
3. ✅ Syntax errors are automatically fixed
4. ✅ Environment configuration is flexible with `--dot-env`
5. ✅ Both mock and SDK modes work correctly
6. ✅ All tests pass (unit, API, E2E)
7. ✅ Documentation is complete and accurate

## Estimated Timeline

- Phase 1-2: Core functionality (2 hours)
- Phase 3-4: Configuration (1 hour)
- Phase 5-6: Integration (1 hour)
- Phase 7: Testing & Documentation (1 hour)

Total: ~5 hours of implementation