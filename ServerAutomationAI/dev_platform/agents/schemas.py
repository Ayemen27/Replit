"""
Pydantic Schemas for Agent Data Validation
"""

from typing import List, Dict, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class TaskComplexity(str, Enum):
    """Task complexity level"""
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class Task(BaseModel):
    """Schema for a single task in the plan"""
    id: int = Field(..., ge=1, description="Task ID (must be >= 1)")
    title: str = Field(..., min_length=1, description="Task title")
    description: str = Field(..., min_length=1, description="Task description")
    dependencies: List[int] = Field(default_factory=list, description="List of task IDs this task depends on")
    estimated_hours: Optional[float] = Field(None, ge=0, description="Estimated hours to complete")
    complexity: Optional[TaskComplexity] = Field(TaskComplexity.MODERATE, description="Task complexity level")
    agent_type: Optional[str] = Field(None, description="Agent responsible for this task (planner, executor, qa)")
    language: Optional[str] = Field(None, description="Programming language for this task (python, javascript, etc.)")
    context: Optional[Dict] = Field(default_factory=dict, description="Additional context for task execution")
    
    @field_validator('dependencies')
    @classmethod
    def validate_dependencies(cls, v, info):
        """Ensure dependencies don't reference self"""
        task_id = info.data.get('id')
        if task_id and task_id in v:
            raise ValueError(f"Task cannot depend on itself (ID: {task_id})")
        return v


class ProjectStructure(BaseModel):
    """Schema for project file structure"""
    files: List[Union[str, Dict]] = Field(default_factory=list, description="List of files to create (strings or dicts with 'path' and 'content')")
    folders: List[str] = Field(default_factory=list, description="List of folders to create")


class Plan(BaseModel):
    """Schema for a complete project plan"""
    understanding: str = Field(..., min_length=10, description="Summary of user's request")
    project_type: str = Field(..., description="Type of project (web, api, cli, etc)")
    technologies: List[str] = Field(default_factory=list, description="Technologies to use")
    tasks: List[Task] = Field(..., description="List of tasks to execute")
    structure: ProjectStructure = Field(default_factory=ProjectStructure, description="Project structure")
    next_steps: List[str] = Field(default_factory=list, description="Immediate next actions")
    
    @field_validator('tasks')
    @classmethod
    def validate_task_order(cls, v):
        """Validate task IDs are sequential and dependencies are valid"""
        if not v:
            raise ValueError("Plan must have at least one task")
        
        # Check for duplicate IDs
        task_ids = [task.id for task in v]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("Duplicate task IDs found")
        
        # Check dependencies reference existing tasks
        for task in v:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    raise ValueError(f"Task {task.id} depends on non-existent task {dep_id}")
        
        return v
    
    @field_validator('project_type')
    @classmethod
    def validate_project_type(cls, v):
        """Normalize project type"""
        valid_types = ['web', 'api', 'cli', 'script', 'data', 'mobile', 'desktop', 'other']
        if v.lower() not in valid_types:
            return 'other'
        return v.lower()


class ResourceEstimate(BaseModel):
    """Schema for resource estimation"""
    total_estimated_hours: float = Field(..., ge=0, description="Total estimated hours for all tasks")
    estimated_completion_days: float = Field(..., ge=0, description="Estimated days to completion (assuming 8h/day)")
    complexity_breakdown: Dict[str, int] = Field(
        default_factory=dict, 
        description="Count of tasks by complexity level"
    )
    total_tasks: int = Field(..., ge=1, description="Total number of tasks")
    critical_path_hours: Optional[float] = Field(None, ge=0, description="Hours for critical path (longest dependency chain)")
    recommended_team_size: int = Field(1, ge=1, le=10, description="Recommended number of developers")


class ProjectPlan(BaseModel):
    """Enhanced schema for complete project planning (extends Plan)"""
    understanding: str = Field(..., min_length=10, description="Summary of user's request")
    project_name: str = Field(..., min_length=1, description="Name of the project")
    project_type: str = Field(..., description="Type of project (web, api, cli, etc)")
    description: str = Field(..., min_length=10, description="Detailed project description")
    technologies: List[str] = Field(default_factory=list, description="Technologies to use")
    tasks: List[Task] = Field(..., description="List of tasks to execute")
    structure: ProjectStructure = Field(default_factory=ProjectStructure, description="Project structure")
    resource_estimate: Optional[ResourceEstimate] = Field(None, description="Resource estimation")
    risks: List[str] = Field(default_factory=list, description="Potential risks and challenges")
    assumptions: List[str] = Field(default_factory=list, description="Project assumptions")
    success_criteria: List[str] = Field(default_factory=list, description="Criteria for project success")
    next_steps: List[str] = Field(default_factory=list, description="Immediate next actions")
    
    @field_validator('tasks')
    @classmethod
    def validate_task_order(cls, v):
        """Validate task IDs are sequential and dependencies are valid"""
        if not v:
            raise ValueError("Plan must have at least one task")
        
        # Check for duplicate IDs
        task_ids = [task.id for task in v]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("Duplicate task IDs found")
        
        # Check dependencies reference existing tasks
        for task in v:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    raise ValueError(f"Task {task.id} depends on non-existent task {dep_id}")
        
        return v
    
    @field_validator('project_type')
    @classmethod
    def validate_project_type(cls, v):
        """Normalize project type"""
        valid_types = ['web', 'api', 'cli', 'script', 'data', 'mobile', 'desktop', 'other']
        if v.lower() not in valid_types:
            return 'other'
        return v.lower()


class CodeExecutionRequest(BaseModel):
    """Schema for code execution request"""
    action: str = Field(..., description="Action: execute_python, execute_bash, file_operation, install_package")
    code: Optional[str] = Field(None, description="Python code to execute (for execute_python)")
    command: Optional[str] = Field(None, description="Bash command to execute (for execute_bash)")
    timeout: Optional[int] = Field(None, ge=1, le=600, description="Timeout in seconds (1-600)")
    cwd: Optional[str] = Field(None, description="Working directory for bash commands")
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        """Validate action type"""
        valid_actions = ['execute_python', 'execute_bash', 'file_operation', 'install_package']
        if v not in valid_actions:
            raise ValueError(f"Invalid action. Must be one of: {', '.join(valid_actions)}")
        return v


class FileOperationRequest(BaseModel):
    """Schema for file operation request"""
    action: str = Field("file_operation", description="Must be 'file_operation'")
    operation: str = Field(..., description="Operation: read, write, list, delete")
    path: Optional[str] = Field(None, description="File/directory path")
    content: Optional[str] = Field(None, description="Content to write (for write operation)")
    create_dirs: bool = Field(True, description="Create parent directories if needed")
    recursive: bool = Field(False, description="Recursive listing (for list operation)")
    pattern: Optional[str] = Field(None, description="File pattern filter (for list operation)")
    
    @field_validator('operation')
    @classmethod
    def validate_operation(cls, v):
        """Validate file operation type"""
        valid_ops = ['read', 'write', 'list', 'delete']
        if v not in valid_ops:
            raise ValueError(f"Invalid operation. Must be one of: {', '.join(valid_ops)}")
        return v


class PackageInstallRequest(BaseModel):
    """Schema for package installation request"""
    action: str = Field("install_package", description="Must be 'install_package'")
    language: str = Field(..., description="Language: python, node, npm, pip")
    packages: List[str] = Field(..., min_length=1, description="List of packages to install")
    save: bool = Field(True, description="Save to requirements.txt/package.json")
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        """Normalize language name"""
        language_map = {
            'py': 'python',
            'pip': 'python',
            'js': 'node',
            'javascript': 'node',
            'npm': 'node'
        }
        normalized = language_map.get(v.lower(), v.lower())
        if normalized not in ['python', 'node']:
            raise ValueError(f"Unsupported language: {v}. Supported: python, node")
        return normalized


class ExecutionResult(BaseModel):
    """Schema for execution result"""
    success: bool = Field(..., description="Whether execution succeeded")
    output: Optional[str] = Field(None, description="Standard output")
    error: Optional[str] = Field(None, description="Error message if any")
    returncode: Optional[int] = Field(None, description="Return code (for bash)")
    timestamp: Optional[str] = Field(None, description="Execution timestamp")


# ========== QA/Test Agent Schemas ==========


class TestStatus(str, Enum):
    """Test execution status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    RUNNING = "running"


class SeverityLevel(str, Enum):
    """Bug/Issue severity level"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class TestResult(BaseModel):
    """Schema for individual test result"""
    test_name: str = Field(..., description="Name of the test")
    status: TestStatus = Field(..., description="Test status")
    duration: Optional[float] = Field(None, description="Test duration in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    traceback: Optional[str] = Field(None, description="Full traceback if failed")
    file_path: Optional[str] = Field(None, description="Test file path")
    line_number: Optional[int] = Field(None, description="Line number in test file")


class QualityGate(BaseModel):
    """Schema for quality gate check"""
    name: str = Field(..., description="Gate name (e.g., 'coverage', 'lint')")
    passed: bool = Field(..., description="Whether gate passed")
    threshold: Optional[float] = Field(None, description="Required threshold")
    actual_value: Optional[float] = Field(None, description="Actual measured value")
    message: Optional[str] = Field(None, description="Gate status message")


class DefectRecord(BaseModel):
    """Schema for bug/defect record"""
    id: str = Field(..., description="Unique defect ID")
    severity: SeverityLevel = Field(..., description="Defect severity")
    title: str = Field(..., min_length=1, description="Short title")
    description: str = Field(..., description="Detailed description")
    file_path: Optional[str] = Field(default=None, description="File where defect was found")
    line_number: Optional[int] = Field(default=None, description="Line number")
    suggested_fix: Optional[str] = Field(default=None, description="AI-suggested fix")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")


class RunTestsRequest(BaseModel):
    """Schema for running tests"""
    action: str = Field("run_tests", description="Must be 'run_tests'")
    test_type: str = Field("all", description="Type: all, unit, integration, specific")
    test_path: Optional[str] = Field(None, description="Specific test file or directory")
    test_pattern: Optional[str] = Field(None, description="Test name pattern (e.g., 'test_*')")
    coverage: bool = Field(True, description="Generate coverage report")
    verbose: bool = Field(False, description="Verbose output")
    
    @field_validator('test_type')
    @classmethod
    def validate_test_type(cls, v):
        """Validate test type"""
        valid_types = ['all', 'unit', 'integration', 'specific']
        if v not in valid_types:
            raise ValueError(f"Invalid test_type. Must be one of: {', '.join(valid_types)}")
        return v


class RunTestsResponse(BaseModel):
    """Schema for test run results"""
    success: bool = Field(..., description="Whether test run completed")
    total_tests: int = Field(0, description="Total number of tests")
    passed: int = Field(0, description="Number of passed tests")
    failed: int = Field(0, description="Number of failed tests")
    skipped: int = Field(0, description="Number of skipped tests")
    errors: int = Field(0, description="Number of errors")
    duration: float = Field(0.0, description="Total duration in seconds")
    coverage: Optional[float] = Field(None, description="Code coverage percentage")
    test_results: List[TestResult] = Field(default_factory=list, description="Individual test results")
    summary: Optional[str] = Field(None, description="Summary message")


class AnalyzeQualityRequest(BaseModel):
    """Schema for code quality analysis"""
    action: str = Field("analyze_quality", description="Must be 'analyze_quality'")
    file_path: Optional[str] = Field(None, description="Specific file to analyze (None = all)")
    check_types: List[str] = Field(default_factory=lambda: ["lint", "complexity", "coverage"], 
                                    description="Types of checks: lint, complexity, coverage, security")
    thresholds: Optional[Dict[str, float]] = Field(None, description="Quality thresholds")


class AnalyzeQualityResponse(BaseModel):
    """Schema for quality analysis results"""
    success: bool = Field(..., description="Whether analysis completed")
    quality_gates: List[QualityGate] = Field(default_factory=list, description="Quality gate results")
    overall_passed: bool = Field(..., description="Whether all gates passed")
    lint_issues: int = Field(0, description="Number of lint issues")
    complexity_score: Optional[float] = Field(None, description="Code complexity score")
    coverage: Optional[float] = Field(None, description="Code coverage percentage")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")


class ReportBugRequest(BaseModel):
    """Schema for bug reporting"""
    action: str = Field("report_bug", description="Must be 'report_bug'")
    test_results: Optional[List[TestResult]] = Field(None, description="Test results to analyze")
    auto_triage: bool = Field(True, description="Auto-assign severity")
    suggest_fixes: bool = Field(True, description="Generate fix suggestions")


class ReportBugResponse(BaseModel):
    """Schema for bug report"""
    success: bool = Field(..., description="Whether report was generated")
    defects: List[DefectRecord] = Field(default_factory=list, description="Found defects")
    critical_count: int = Field(0, description="Number of critical bugs")
    high_count: int = Field(0, description="Number of high priority bugs")
    total_count: int = Field(0, description="Total defects found")
    summary: Optional[str] = Field(None, description="Report summary")


class GenerateTestsRequest(BaseModel):
    """Schema for test generation"""
    action: str = Field("generate_tests", description="Must be 'generate_tests'")
    file_path: str = Field(..., description="File to generate tests for")
    test_type: str = Field("unit", description="Type: unit, integration, e2e")
    framework: str = Field("pytest", description="Test framework: pytest, unittest, etc")
    coverage_target: Optional[float] = Field(None, ge=0, le=100, description="Target coverage %")


class GenerateTestsResponse(BaseModel):
    """Schema for generated tests"""
    success: bool = Field(..., description="Whether tests were generated")
    test_file_path: Optional[str] = Field(None, description="Path to generated test file")
    test_code: Optional[str] = Field(None, description="Generated test code")
    tests_count: int = Field(0, description="Number of tests generated")
    estimated_coverage: Optional[float] = Field(None, description="Estimated coverage increase")


# ========== QA Tools Integration Schemas ==========


class QAToolType(str, Enum):
    """QA tool types"""
    FLAKE8 = "flake8"
    BANDIT = "bandit"
    RADON = "radon"
    PYTEST = "pytest"
    CUSTOM = "custom"


class QAToolExecutionRequest(BaseModel):
    """Schema for QA tool execution request"""
    tool: QAToolType = Field(..., description="Tool to execute")
    file_path: str = Field(..., description="Path to analyze")
    options: Dict = Field(default_factory=dict, description="Tool-specific options")
    timeout: Optional[int] = Field(None, description="Execution timeout in seconds")


class QAToolExecutionResult(BaseModel):
    """Schema for QA tool execution result"""
    tool: QAToolType = Field(..., description="Tool that was executed")
    success: bool = Field(..., description="Whether execution succeeded")
    file_path: str = Field(..., description="Path that was analyzed")
    issues_count: int = Field(0, description="Number of issues found")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    summary: str = Field("", description="Summary message")
    error: Optional[str] = Field(None, description="Error message if failed")
    raw_output: Optional[Dict] = Field(None, description="Raw tool output")


class QAIssueCategory(str, Enum):
    """QA issue categories"""
    LINT = "lint"
    SECURITY = "security"
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"
    STYLE = "style"
    BUG = "bug"


class QAIssueDetail(BaseModel):
    """Schema for detailed QA issue"""
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")
    column: Optional[int] = Field(None, description="Column number")
    code: str = Field(..., description="Issue code")
    message: str = Field(..., description="Issue message")
    severity: SeverityLevel = Field(..., description="Issue severity")
    category: QAIssueCategory = Field(..., description="Issue category")
    tool: QAToolType = Field(..., description="Tool that found the issue")
    confidence: Optional[str] = Field(None, description="Confidence level (for security)")
    complexity: Optional[float] = Field(None, description="Complexity value (for radon)")
    more_info: Optional[str] = Field(None, description="Additional information URL")


class AggregatedQAReport(BaseModel):
    """Schema for aggregated QA report from all tools"""
    success: bool = Field(..., description="Whether analysis completed")
    file_path: str = Field(..., description="Analyzed path")
    timestamp: str = Field(..., description="Analysis timestamp")
    
    # Tool results
    flake8_executed: bool = Field(False, description="Whether flake8 ran")
    bandit_executed: bool = Field(False, description="Whether bandit ran")
    radon_executed: bool = Field(False, description="Whether radon ran")
    
    # Issue counts
    total_issues: int = Field(0, description="Total issues from all tools")
    critical_issues: int = Field(0, description="Critical severity issues")
    lint_issues: int = Field(0, description="Linting issues")
    security_issues: int = Field(0, description="Security issues")
    complexity_issues: int = Field(0, description="Complexity issues")
    
    # Detailed issues
    all_issues: List[QAIssueDetail] = Field(default_factory=list, description="All issues found")
    
    # Metrics
    average_complexity: Optional[float] = Field(None, description="Average code complexity")
    max_complexity: Optional[float] = Field(None, description="Maximum complexity found")
    maintainability_index: Optional[float] = Field(None, description="Maintainability index (0-100)")
    maintainability_grade: Optional[str] = Field(None, description="Maintainability grade (A-F)")
    
    # Quality gates
    passes_quality_gate: bool = Field(False, description="Whether code passes quality gate")
    quality_score: Optional[float] = Field(None, description="Overall quality score (0-100)")
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    summary: str = Field("", description="Overall summary")


class AsyncQAAnalysisRequest(BaseModel):
    """Schema for async QA analysis request"""
    file_path: str = Field(..., description="Path to analyze")
    tools: List[QAToolType] = Field(default_factory=lambda: [QAToolType.FLAKE8, QAToolType.BANDIT, QAToolType.RADON], 
                                     description="Tools to run")
    options: Dict = Field(default_factory=dict, description="Tool options")
    sequential: bool = Field(True, description="Run tools sequentially (for RAM management)")
    max_memory_mb: Optional[int] = Field(None, description="Max memory per tool (MB)")


class RAMUsageMetrics(BaseModel):
    """Schema for RAM usage metrics"""
    current_mb: float = Field(..., description="Current RAM usage in MB")
    peak_mb: float = Field(..., description="Peak RAM usage in MB")
    limit_mb: Optional[float] = Field(None, description="Configured limit in MB")
    within_limit: bool = Field(True, description="Whether within configured limit")
    timestamp: str = Field(..., description="Measurement timestamp")


# ========== Ops Coordinator Agent Schemas ==========


class WorkflowType(str, Enum):
    """Workflow type enumeration"""
    DELIVERY_PIPELINE = "delivery_pipeline"
    REGRESSION = "regression"
    MAINTENANCE = "maintenance"
    CUSTOM = "custom"


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentCommand(BaseModel):
    """Schema for agent command"""
    agent_id: str = Field(..., description="Target agent ID (planner, code_executor, qa_test)")
    action: str = Field(..., description="Action to execute")
    parameters: Dict = Field(default_factory=dict, description="Action parameters")
    timeout: Optional[int] = Field(None, ge=1, description="Command timeout in seconds")


class AgentResult(BaseModel):
    """Schema for agent execution result"""
    agent_id: str = Field(..., description="Agent that executed the command")
    success: bool = Field(..., description="Whether command succeeded")
    result: Optional[Dict] = Field(None, description="Result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    duration: Optional[float] = Field(None, description="Execution duration in seconds")
    timestamp: Optional[str] = Field(None, description="Completion timestamp")


class ProjectProgressSnapshot(BaseModel):
    """Schema for project progress snapshot"""
    project_id: str = Field(..., description="Unique project ID")
    workflow_id: str = Field(..., description="Current workflow ID")
    workflow_type: WorkflowType = Field(..., description="Workflow type")
    status: WorkflowStatus = Field(..., description="Current status")
    tasks_total: int = Field(0, description="Total number of tasks")
    tasks_completed: int = Field(0, description="Completed tasks")
    tasks_failed: int = Field(0, description="Failed tasks")
    start_time: Optional[str] = Field(None, description="Workflow start time")
    current_agent: Optional[str] = Field(None, description="Currently executing agent")
    metrics: Dict = Field(default_factory=dict, description="Additional metrics")


class StartWorkflowRequest(BaseModel):
    """Schema for starting a workflow"""
    action: str = Field("start_workflow", description="Must be 'start_workflow'")
    workflow_type: WorkflowType = Field(..., description="Type of workflow to start")
    project_name: Optional[str] = Field(None, description="Project name")
    user_request: Optional[str] = Field(None, description="User request (for delivery_pipeline)")
    parameters: Dict = Field(default_factory=dict, description="Workflow-specific parameters")
    auto_execute: bool = Field(True, description="Auto-execute tasks without user confirmation")


class StartWorkflowResponse(BaseModel):
    """Schema for workflow start response"""
    success: bool = Field(..., description="Whether workflow started successfully")
    workflow_id: str = Field(..., description="Unique workflow ID")
    workflow_type: WorkflowType = Field(..., description="Workflow type")
    status: WorkflowStatus = Field(..., description="Initial status")
    message: Optional[str] = Field(None, description="Status message")
    next_steps: List[str] = Field(default_factory=list, description="Next steps to execute")


class WorkflowStatusUpdate(BaseModel):
    """Schema for workflow status update"""
    workflow_id: str = Field(..., description="Workflow ID")
    status: WorkflowStatus = Field(..., description="Current status")
    progress_percent: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = Field(None, description="Current step description")
    agent_results: List[AgentResult] = Field(default_factory=list, description="Recent agent results")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    timestamp: Optional[str] = Field(None, description="Update timestamp")


class UserInteractionRequest(BaseModel):
    """Schema for user interaction request"""
    interaction_type: str = Field(..., description="Type: prompt, confirm, choice, input")
    message: str = Field(..., description="Message to show user")
    options: Optional[List[str]] = Field(None, description="Options for choice interaction")
    default_value: Optional[str] = Field(None, description="Default value")
    timeout: Optional[int] = Field(None, description="Timeout in seconds")


class UserInteractionResponse(BaseModel):
    """Schema for user interaction response"""
    success: bool = Field(..., description="Whether user responded")
    interaction_type: str = Field(..., description="Type of interaction")
    user_input: Optional[str] = Field(None, description="User's input")
    selected_option: Optional[str] = Field(None, description="Selected option (for choice)")
    timed_out: bool = Field(False, description="Whether interaction timed out")


class AlertNotification(BaseModel):
    """Schema for alert notification"""
    alert_type: str = Field(..., description="Type: info, warning, error, critical")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    source: Optional[str] = Field(None, description="Source agent/workflow")
    severity: SeverityLevel = Field(SeverityLevel.INFO, description="Severity level")
    timestamp: Optional[str] = Field(None, description="Alert timestamp")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")


# ============================================================
# Code Executor Schemas (Phase 3.2)
# ============================================================

class CodeLanguage(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    HTML = "html"
    CSS = "css"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"


class CodeArtifact(BaseModel):
    """Schema for generated code artifact"""
    language: CodeLanguage = Field(..., description="Programming language of the code")
    file_path: str = Field(..., min_length=1, description="Relative file path (e.g., 'src/main.py')")
    content: str = Field(..., description="The generated code content")
    description: Optional[str] = Field(None, description="Description of what this code does")
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies/imports")
    task_id: Optional[int] = Field(None, description="Task ID this artifact is for")
    is_entry_point: bool = Field(False, description="Whether this is the main entry point")
    
    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v):
        """Ensure file path is relative and safe"""
        import os
        if os.path.isabs(v):
            raise ValueError("File path must be relative, not absolute")
        if '..' in v:
            raise ValueError("File path cannot contain '..'")
        return v


class FileTemplate(BaseModel):
    """Schema for code file template"""
    template_name: str = Field(..., description="Name of the template (e.g., 'python_flask_api')")
    language: CodeLanguage = Field(..., description="Primary language")
    file_path: str = Field(..., description="Default file path")
    template_content: str = Field(..., description="Template with placeholders like {{project_name}}")
    variables: List[str] = Field(default_factory=list, description="List of template variables")
    description: str = Field(..., description="Template description")


class DependencyConfig(BaseModel):
    """Schema for project dependencies configuration"""
    language: str = Field(..., description="Language ecosystem (python, node, etc)")
    packages: List[str] = Field(default_factory=list, description="List of packages to install")
    dev_packages: List[str] = Field(default_factory=list, description="Development packages")
    config_file: str = Field(..., description="Config file name (requirements.txt, package.json)")
    install_command: str = Field(..., description="Command to install (pip install -r, npm install)")
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        """Validate language ecosystem"""
        valid_langs = ['python', 'node', 'javascript', 'ruby', 'go', 'rust']
        if v.lower() not in valid_langs:
            raise ValueError(f"Language must be one of: {', '.join(valid_langs)}")
        return v.lower()


class CodeGenerationRequest(BaseModel):
    """Schema for code generation request"""
    task: Task = Field(..., description="Task to generate code for")
    project_context: Dict = Field(default_factory=dict, description="Project context (type, technologies, etc)")
    template_name: Optional[str] = Field(None, description="Template to use (optional)")
    additional_requirements: List[str] = Field(default_factory=list, description="Additional requirements")
    target_directory: str = Field(".", description="Target directory for generated files")
    
    @field_validator('target_directory')
    @classmethod
    def validate_target_directory(cls, v):
        """Ensure target directory is safe"""
        import os
        if os.path.isabs(v):
            raise ValueError("Target directory must be relative")
        if '..' in v:
            raise ValueError("Target directory cannot contain '..'")
        return v


class CodeGenerationResult(BaseModel):
    """Schema for code generation result"""
    success: bool = Field(..., description="Whether generation succeeded")
    artifacts: List[CodeArtifact] = Field(default_factory=list, description="Generated code artifacts")
    dependencies: Optional[DependencyConfig] = Field(None, description="Dependencies configuration")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    files_created: List[str] = Field(default_factory=list, description="List of created file paths")
    execution_time_seconds: float = Field(0.0, ge=0, description="Time taken to generate")
    
    @field_validator('artifacts')
    @classmethod
    def validate_artifacts(cls, v):
        """Ensure at least one artifact on success"""
        # Note: We can't access 'success' here in validator, so just validate structure
        return v


class ProjectScaffold(BaseModel):
    """Schema for complete project scaffolding"""
    project_name: str = Field(..., min_length=1, description="Name of the project")
    project_type: str = Field(..., description="Type (web, api, cli, etc)")
    structure: ProjectStructure = Field(..., description="Files and folders to create")
    artifacts: List[CodeArtifact] = Field(default_factory=list, description="All code artifacts")
    dependencies: List[DependencyConfig] = Field(default_factory=list, description="All dependencies")
    readme_content: str = Field("", description="README.md content")
    setup_instructions: List[str] = Field(default_factory=list, description="Setup steps for user")
    
    @field_validator('project_name')
    @classmethod
    def validate_project_name(cls, v):
        """Validate project name is safe for filesystem"""
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Project name must contain only letters, numbers, underscores, and hyphens")
        return v


# ============================================================
# Error Handling & Recovery Schemas (Phase 3.2)
# ============================================================

class ErrorSeverity(str, Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ExecutionError(BaseModel):
    """Schema for code execution error"""
    error_type: str = Field(..., description="Type of error (syntax, runtime, import, etc)")
    message: str = Field(..., description="Error message")
    source_file: Optional[str] = Field(None, description="File where error occurred")
    line_number: Optional[int] = Field(None, ge=1, description="Line number of error")
    column_number: Optional[int] = Field(None, ge=1, description="Column number of error")
    stack_trace: Optional[str] = Field(None, description="Full stack trace")
    severity: ErrorSeverity = Field(ErrorSeverity.ERROR, description="Error severity")
    fix_suggestion: Optional[str] = Field(None, description="AI-suggested fix")
    is_fixable: bool = Field(False, description="Whether error can be auto-fixed")
    
    @field_validator('error_type')
    @classmethod
    def validate_error_type(cls, v):
        """Validate error type"""
        valid_types = ['syntax', 'runtime', 'import', 'type', 'logic', 'dependency', 'configuration']
        if v.lower() not in valid_types:
            return v  # Allow custom types but log warning
        return v.lower()


class CodeFixRequest(BaseModel):
    """Schema for requesting code fix"""
    artifact: CodeArtifact = Field(..., description="Original code artifact with error")
    errors: List[ExecutionError] = Field(..., min_length=1, description="List of errors to fix")
    context: Dict = Field(default_factory=dict, description="Additional context for fixing")
    max_attempts: int = Field(3, ge=1, le=5, description="Maximum fix attempts")
    preserve_functionality: bool = Field(True, description="Preserve existing functionality")


class CodeFixResult(BaseModel):
    """Schema for code fix result"""
    success: bool = Field(..., description="Whether fix succeeded")
    fixed_artifact: Optional[CodeArtifact] = Field(None, description="Fixed code artifact")
    errors_fixed: List[ExecutionError] = Field(default_factory=list, description="Errors that were fixed")
    errors_remaining: List[ExecutionError] = Field(default_factory=list, description="Errors still present")
    fix_description: str = Field("", description="Description of fixes applied")
    attempts_used: int = Field(1, ge=1, description="Number of fix attempts used")
