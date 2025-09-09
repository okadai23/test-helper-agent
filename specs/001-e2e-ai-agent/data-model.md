# Data Model: E2E Test Automation AI Agent

**Version**: 1.0.0  
**Date**: 2025-09-09  
**Status**: Final

## Overview
This document defines the data models for the E2E Test Automation AI Agent system. All models use Pydantic v2 for validation and serialization.

## Core Entities

### Project
Represents a test automation project for a specific web application.

```python
class Project(BaseModel):
    """E2E test automation project configuration and metadata."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    url: HttpUrl = Field(..., description="Target application URL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: Literal["active", "archived", "paused"] = "active"
    metadata: dict[str, Any] = Field(default_factory=dict)
    browser_config: BrowserConfig
    test_count: int = Field(default=0, ge=0)
    last_execution: Optional[datetime] = None
    retention_days: int = Field(default=30, ge=1, le=365)
    max_test_files: int = Field(default=100, ge=1, le=1000)
```

### BrowserConfig
Browser configuration for test execution.

```python
class BrowserConfig(BaseModel):
    """Browser configuration settings."""
    
    browser: Literal["chromium", "firefox", "webkit"] = "chromium"
    headless: bool = True
    viewport: ViewportSize = Field(default_factory=lambda: ViewportSize())
    locale: str = "en-US"
    timezone: str = "UTC"
    user_agent: Optional[str] = None
    device_scale_factor: float = Field(default=1.0, gt=0, le=3)
    is_mobile: bool = False
    has_touch: bool = False
    color_scheme: Literal["light", "dark", "no-preference"] = "light"

class ViewportSize(BaseModel):
    """Browser viewport dimensions."""
    width: int = Field(default=1280, ge=320, le=3840)
    height: int = Field(default=720, ge=240, le=2160)
```

### Scenario
Complete test scenario with steps and assertions.

```python
class Scenario(BaseModel):
    """E2E test scenario definition with steps and metadata."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1, ge=1)
    tags: list[str] = Field(default_factory=list)
    steps: list[Step]
    assertions: list[Assertion] = Field(default_factory=list)
    timeout: int = Field(default=30000, ge=1000, le=300000)  # milliseconds
    retry_count: int = Field(default=3, ge=0, le=10)
    status: Literal["draft", "active", "deprecated"] = "active"
    
    @field_validator('steps')
    def validate_steps(cls, v):
        if len(v) == 0:
            raise ValueError("Test scenario must have at least one step")
        return v
```

### Step
Individual test action within a scenario (using discriminated union).

```python
# Base class for all test steps
class BaseStep(BaseModel):
    """Base class for E2E test steps."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    description: Optional[str] = None
    wait_before: float = Field(default=0, ge=0, le=30)  # seconds
    screenshot: bool = False
    
# Specific step types
class ClickStep(BaseStep):
    """Click action on an element."""
    type: Literal["click"] = "click"
    selector: str
    button: Literal["left", "right", "middle"] = "left"
    click_count: int = Field(default=1, ge=1, le=3)
    modifier_keys: list[Literal["Alt", "Control", "Meta", "Shift"]] = []

class InputStep(BaseStep):
    """Text input action."""
    type: Literal["input"] = "input"
    selector: str
    value: str
    clear_first: bool = True
    press_enter: bool = False

class NavigateStep(BaseStep):
    """Navigation action."""
    type: Literal["navigate"] = "navigate"
    url: str
    wait_until: Literal["load", "domcontentloaded", "networkidle"] = "load"

class WaitStep(BaseStep):
    """Wait for element or condition."""
    type: Literal["wait"] = "wait"
    selector: Optional[str] = None
    condition: Literal["visible", "hidden", "attached", "detached", "enabled"] = "visible"
    timeout: int = Field(default=5000, ge=100, le=60000)

class AssertStep(BaseStep):
    """Assertion step."""
    type: Literal["assert"] = "assert"
    assertion: Assertion

# Discriminated union
Step = Annotated[
    Union[ClickStep, InputStep, NavigateStep, WaitStep, AssertStep],
    Field(discriminator='type')
]
```

### Assertion
Test assertion definition.

```python
class Assertion(BaseModel):
    """E2E test assertion configuration."""
    
    type: Literal["text", "attribute", "visibility", "count", "url", "title"]
    selector: Optional[str] = None  # Not needed for url/title assertions
    expected: Union[str, int, bool]
    operator: Literal["equals", "contains", "matches", "greater_than", "less_than"] = "equals"
    case_sensitive: bool = True
    
    @model_validator(mode='after')
    def validate_assertion(self):
        if self.type in ["text", "attribute", "visibility", "count"] and not self.selector:
            raise ValueError(f"Selector required for {self.type} assertion")
        return self
```

### Execution
Record of a test execution.

```python
class Execution(BaseModel):
    """E2E test execution record with results."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    scenario_id: str
    project_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    status: Literal["running", "passed", "failed", "error", "timeout", "skipped"]
    error_message: Optional[str] = None
    error_stack: Optional[str] = None
    failed_step_id: Optional[str] = None
    screenshots: list[str] = Field(default_factory=list)  # File paths
    video_path: Optional[str] = None
    logs: list[LogEntry] = Field(default_factory=list)
    retry_attempt: int = Field(default=1, ge=1)
    browser_info: dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def calculate_duration(self):
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_ms = int(delta.total_seconds() * 1000)
        return self

class LogEntry(BaseModel):
    """Execution log entry."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: Literal["debug", "info", "warning", "error"]
    message: str
    context: dict[str, Any] = Field(default_factory=dict)
```

### FixProposal
Proposed fix for a failing test.

```python
class FixProposal(BaseModel):
    """Proposed fix for a failing test."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    execution_id: str
    scenario_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(..., ge=0, le=1)
    fix_type: Literal["selector", "wait", "assertion", "step_order", "retry_logic"]
    description: str
    rationale: str
    changes: list[ProposedChange]
    estimated_impact: Literal["low", "medium", "high"]
    auto_applicable: bool = False
    
    @field_validator('confidence')
    def validate_confidence(cls, v):
        return round(v, 2)

class ProposedChange(BaseModel):
    """Individual change within a fix proposal."""
    
    step_id: str
    change_type: Literal["replace", "insert", "delete", "modify"]
    field: str  # Which field to change
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    position: Optional[int] = None  # For insert operations
```

### CaptureSession
Browser interaction capture session.

```python
class CaptureSession(BaseModel):
    """Browser interaction capture session."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    status: Literal["active", "completed", "failed", "cancelled"] = "active"
    browser_session_id: str
    captured_interactions: list[CapturedInteraction] = Field(default_factory=list)
    dom_snapshots: list[DOMSnapshot] = Field(default_factory=list)
    
class CapturedInteraction(BaseModel):
    """Single captured user interaction."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: Literal["click", "input", "navigate", "scroll", "keypress"]
    target_selector: str
    alternative_selectors: list[str] = Field(default_factory=list)
    value: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class DOMSnapshot(BaseModel):
    """DOM state snapshot at a point in time."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    url: str
    title: str
    element_count: int
    interactive_elements: list[dict[str, Any]]
    has_forms: bool = False
    has_frames: bool = False
```

## Storage Schemas

### ProjectMetadata
Project metadata stored in `metadata.json`.

```python
class ProjectMetadata(BaseModel):
    """Project metadata for storage."""
    
    project: Project
    statistics: ProjectStatistics
    last_sync: datetime = Field(default_factory=datetime.utcnow)

class ProjectStatistics(BaseModel):
    """Project usage statistics."""
    
    total_scenarios: int = 0
    total_executions: int = 0
    success_rate: float = 0.0
    average_duration_ms: int = 0
    last_7_days_executions: int = 0
    storage_size_mb: float = 0.0
```

### Cache
Cached test data for performance.

```python
class Cache(BaseModel):
    """Cached E2E test data."""
    
    selectors: dict[str, SelectorStrategy]
    dom_patterns: list[DOMPattern]
    common_waits: dict[str, int]
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SelectorStrategy(BaseModel):
    """Element selector strategy."""
    
    primary: str
    alternatives: list[str]
    reliability_score: float = Field(ge=0, le=1)
    last_verified: datetime

class DOMPattern(BaseModel):
    """Recognized DOM pattern."""
    
    pattern_type: str
    selector_template: str
    occurrences: int
    confidence: float
```

## Validation Rules

### Business Rules
1. Project names must be unique within the system
2. Test scenarios must have at least one step
3. Fix proposals with confidence < 0.5 should not be auto-applicable
4. Retention period cannot exceed 365 days
5. Maximum 1000 test files per project

### Data Integrity
1. All IDs use UUID v4 format
2. Timestamps in UTC timezone
3. File paths must be relative to project directory
4. URLs must be valid HTTP/HTTPS
5. Selector strings must be valid CSS or XPath

## Serialization

### JSON Schema Generation
```python
# Generate OpenAPI schemas for all models
for model in [Project, Scenario, Execution, FixProposal]:
    schema = model.model_json_schema()
    # Save to contracts directory
```

### Storage Format
- All models serialize to JSON with ISO 8601 timestamps
- Binary data (screenshots) stored as file paths
- Large text fields (logs, stack traces) can be stored separately

## Migration Strategy
- Version field in all stored documents
- Backward compatibility for 2 major versions
- Migration scripts in `scripts/migrations/`

## Performance Considerations
- Index on: project_id, scenario_id, created_at
- Pagination for list operations (max 100 items)
- Lazy loading for execution logs and screenshots
- Cache selector strategies per project

---
*End of Data Model Specification*