"""
QA Metrics Unified Schema
Standardized schema for all QA tool outputs
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class QASeverity(str, Enum):
    """Severity levels for QA issues"""
    CRITICAL = "critical"
    HIGH = "high"
    ERROR = "error"
    MEDIUM = "medium"
    WARNING = "warning"
    LOW = "low"
    INFO = "info"


class QAIssueType(str, Enum):
    """Types of QA issues"""
    LINT = "lint"
    SECURITY = "security"
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"
    STYLE = "style"


class QAIssue(BaseModel):
    """Single QA issue from any tool"""
    file: str = Field(..., description="File path where issue found")
    line: int = Field(..., description="Line number")
    column: Optional[int] = Field(None, description="Column number (if available)")
    code: str = Field(..., description="Issue code/identifier")
    message: str = Field(..., description="Issue description")
    severity: QASeverity = Field(..., description="Issue severity")
    issue_type: QAIssueType = Field(..., description="Type of issue")
    tool: str = Field(..., description="Tool that found the issue (flake8/bandit/radon)")
    
    # Optional fields
    confidence: Optional[str] = Field(None, description="Confidence level (for security)")
    complexity: Optional[float] = Field(None, description="Complexity score (for radon)")
    more_info: Optional[str] = Field(None, description="Additional information URL")


class QAToolResult(BaseModel):
    """Result from a single QA tool execution"""
    tool: str = Field(..., description="Tool name (flake8/bandit/radon)")
    success: bool = Field(..., description="Whether tool ran successfully")
    file_path: str = Field(..., description="Path that was analyzed")
    issues_count: int = Field(0, description="Total issues found")
    issues: List[QAIssue] = Field(default_factory=list, description="List of issues")
    summary: str = Field("", description="Summary message")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    # Tool-specific metrics
    metrics: Dict = Field(default_factory=dict, description="Tool-specific metrics")


class ComplexityMetrics(BaseModel):
    """Complexity analysis metrics from radon"""
    average_complexity: float = Field(0.0, description="Average cyclomatic complexity")
    max_complexity: float = Field(0.0, description="Maximum complexity found")
    total_functions: int = Field(0, description="Total functions analyzed")
    high_complexity_count: int = Field(0, description="Functions with complexity > threshold")


class MaintainabilityMetrics(BaseModel):
    """Maintainability metrics from radon"""
    maintainability_index: float = Field(0.0, description="MI score (0-100)")
    grade: str = Field("F", description="MI grade (A-F)")


class SecurityMetrics(BaseModel):
    """Security metrics from bandit"""
    critical_count: int = Field(0, description="Critical severity issues")
    high_count: int = Field(0, description="High severity issues")
    medium_count: int = Field(0, description="Medium severity issues")
    low_count: int = Field(0, description="Low severity issues")


class LintMetrics(BaseModel):
    """Linting metrics from flake8"""
    error_count: int = Field(0, description="Error-level issues")
    warning_count: int = Field(0, description="Warning-level issues")
    info_count: int = Field(0, description="Info-level issues")


class AggregatedQAMetrics(BaseModel):
    """Aggregated metrics from all QA tools"""
    total_issues: int = Field(0, description="Total issues from all tools")
    critical_issues: int = Field(0, description="Critical/high severity issues")
    
    # Per-tool counts
    lint_issues: int = Field(0, description="Linting issues (flake8)")
    security_issues: int = Field(0, description="Security issues (bandit)")
    complexity_issues: int = Field(0, description="Complexity issues (radon)")
    
    # Detailed metrics
    complexity: Optional[ComplexityMetrics] = None
    maintainability: Optional[MaintainabilityMetrics] = None
    security: Optional[SecurityMetrics] = None
    lint: Optional[LintMetrics] = None
    
    # Overall scores
    quality_score: Optional[float] = Field(None, description="Overall quality score (0-100)")
    passes_quality_gate: bool = Field(False, description="Whether code passes quality gate")


class QAExecutionResult(BaseModel):
    """Complete result from QA analysis"""
    success: bool = Field(..., description="Whether analysis completed")
    file_path: str = Field(..., description="Path that was analyzed")
    timestamp: str = Field(..., description="Analysis timestamp")
    
    # Tool results
    flake8_result: Optional[QAToolResult] = None
    bandit_result: Optional[QAToolResult] = None
    radon_result: Optional[QAToolResult] = None
    
    # Aggregated metrics
    metrics: AggregatedQAMetrics = Field(default_factory=lambda: AggregatedQAMetrics())
    
    # All issues combined
    all_issues: List[QAIssue] = Field(default_factory=list)
    
    # Summary
    summary: str = Field("", description="Overall summary")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")


def normalize_flake8_issue(issue: Dict, file_path: str) -> QAIssue:
    """Convert flake8 issue to unified QAIssue"""
    return QAIssue(
        file=issue.get("file", file_path),
        line=issue.get("line", 0),
        column=issue.get("column"),
        code=issue.get("code", ""),
        message=issue.get("message", ""),
        severity=QASeverity(issue.get("severity", "info")),
        issue_type=QAIssueType.LINT,
        tool="flake8",
        confidence=None,
        complexity=None,
        more_info=None
    )


def normalize_bandit_issue(issue: Dict, file_path: str) -> QAIssue:
    """Convert bandit issue to unified QAIssue"""
    severity = issue.get("severity", "low").lower()
    
    # Map bandit severity to our schema
    severity_map = {
        "high": QASeverity.HIGH,
        "medium": QASeverity.MEDIUM,
        "low": QASeverity.LOW
    }
    
    return QAIssue(
        file=issue.get("file", file_path),
        line=issue.get("line", 0),
        column=None,
        code=issue.get("code", ""),
        message=issue.get("message", ""),
        severity=severity_map.get(severity, QASeverity.LOW),
        issue_type=QAIssueType.SECURITY,
        tool="bandit",
        confidence=issue.get("confidence"),
        complexity=None,
        more_info=issue.get("more_info")
    )


def normalize_radon_issue(func: Dict, threshold: int, file_path: str) -> Optional[QAIssue]:
    """Convert radon complexity to QAIssue if over threshold"""
    complexity = func.get("complexity", 0)
    
    if complexity > threshold:
        # Determine severity based on complexity
        if complexity > 20:
            severity = QASeverity.HIGH
        elif complexity > 10:
            severity = QASeverity.MEDIUM
        else:
            severity = QASeverity.LOW
        
        return QAIssue(
            file=func.get("file", file_path),
            line=func.get("line", 0),
            column=None,
            code="C901",  # Standard complexity warning code
            message=f"Function '{func.get('name', 'unknown')}' is too complex (complexity: {complexity})",
            severity=severity,
            issue_type=QAIssueType.COMPLEXITY,
            tool="radon",
            confidence=None,
            complexity=float(complexity),
            more_info=None
        )
    
    return None
