"""
Async QA Task Manager
Orchestrates QA tools sequentially with RAM limits
"""

import asyncio
import logging
import psutil
import time
from typing import Dict, List, Optional
from datetime import datetime

from .flake8_wrapper import Flake8Wrapper
from .bandit_wrapper import BanditWrapper
from .radon_wrapper import RadonWrapper
from .qa_tools_config import QAToolsConfig
from dev_platform.agents.schemas import (
    QAToolType, QAIssueDetail, QAIssueCategory, SeverityLevel,
    AggregatedQAReport, RAMUsageMetrics
)

logger = logging.getLogger(__name__)


class AsyncQATaskManager:
    """
    Async manager for orchestrating QA tools sequentially
    
    Features:
    - Sequential execution to control RAM usage
    - Memory monitoring and limits
    - Result aggregation
    - Error handling and recovery
    """
    
    def __init__(self, config: Optional[QAToolsConfig] = None):
        """
        Initialize AsyncQATaskManager
        
        Args:
            config: QA tools configuration (uses defaults if None)
        """
        self.config = config or QAToolsConfig()
        
        # Initialize wrappers
        self.flake8 = Flake8Wrapper(config=self.config.get_flake8_config())
        self.bandit = BanditWrapper(config=self.config.get_bandit_config())
        self.radon = RadonWrapper(config=self.config.get_radon_config())
        
        # RAM tracking
        self.ram_limits = self.config.get_ram_limits()
        self.peak_memory_mb = 0.0
        self.initial_memory_mb = 0.0
        
        # Execution stats
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0
    
    async def analyze_code_quality_async(
        self,
        file_path: str,
        tools: Optional[List[QAToolType]] = None,
        options: Optional[Dict] = None
    ) -> AggregatedQAReport:
        """
        Analyze code quality using multiple QA tools sequentially
        
        Args:
            file_path: Path to file or directory to analyze
            tools: List of tools to run (default: all)
            options: Tool-specific options
        
        Returns:
            AggregatedQAReport with results from all tools
        """
        try:
            start_time = time.time()
            timestamp = datetime.now().isoformat()
            
            # Track initial memory
            self.initial_memory_mb = self._get_current_memory_mb()
            self.peak_memory_mb = self.initial_memory_mb
            
            # Default to all tools
            if tools is None:
                tools = [QAToolType.FLAKE8, QAToolType.BANDIT, QAToolType.RADON]
            
            options = options or {}
            
            logger.info(f"Starting QA analysis on {file_path} with tools: {tools}")
            
            # Initialize report
            report = AggregatedQAReport(
                success=True,
                file_path=file_path,
                timestamp=timestamp,
                flake8_executed=False,
                bandit_executed=False,
                radon_executed=False,
                total_issues=0,
                critical_issues=0,
                lint_issues=0,
                security_issues=0,
                complexity_issues=0,
                average_complexity=None,
                max_complexity=None,
                maintainability_index=None,
                maintainability_grade=None,
                passes_quality_gate=False,
                quality_score=None,
                summary=""
            )
            
            all_issues: List[QAIssueDetail] = []
            
            # Run tools sequentially
            if QAToolType.FLAKE8 in tools:
                logger.info("Running flake8...")
                flake8_result = await self._run_flake8(file_path, options)
                report.flake8_executed = True
                
                if flake8_result["success"]:
                    issues = self._convert_flake8_issues(flake8_result, file_path)
                    all_issues.extend(issues)
                    report.lint_issues = len(issues)
                
                await self._check_memory_limit()
            
            if QAToolType.BANDIT in tools:
                logger.info("Running bandit...")
                bandit_result = await self._run_bandit(file_path, options)
                report.bandit_executed = True
                
                if bandit_result["success"]:
                    issues = self._convert_bandit_issues(bandit_result, file_path)
                    all_issues.extend(issues)
                    report.security_issues = len(issues)
                
                await self._check_memory_limit()
            
            if QAToolType.RADON in tools:
                logger.info("Running radon...")
                radon_result = await self._run_radon(file_path, options)
                report.radon_executed = True
                
                if radon_result["success"]:
                    # Extract metrics
                    report.average_complexity = radon_result.get("average_complexity", 0)
                    report.max_complexity = radon_result.get("max_complexity", 0)
                    report.maintainability_index = radon_result.get("maintainability_index")
                    report.maintainability_grade = radon_result.get("maintainability_grade")
                    
                    # Convert complexity issues
                    issues = self._convert_radon_issues(radon_result, file_path)
                    all_issues.extend(issues)
                    report.complexity_issues = len(issues)
                
                await self._check_memory_limit()
            
            # Aggregate results
            report.all_issues = all_issues
            report.total_issues = len(all_issues)
            report.critical_issues = len([i for i in all_issues if i.severity == SeverityLevel.CRITICAL or i.severity == SeverityLevel.HIGH])
            
            # Calculate quality score
            report.quality_score = self._calculate_quality_score(report)
            
            # Determine if passes quality gate
            report.passes_quality_gate = self._evaluate_quality_gate(report)
            
            # Generate recommendations
            report.recommendations = self._generate_recommendations(report)
            
            # Generate summary
            execution_time = time.time() - start_time
            report.summary = self._generate_summary(report, execution_time)
            
            # Update stats
            self.total_runs += 1
            self.successful_runs += 1
            
            logger.info(f"QA analysis completed in {execution_time:.2f}s - {report.total_issues} issues found")
            
            return report
        
        except Exception as e:
            logger.error(f"Error during QA analysis: {e}", exc_info=True)
            self.total_runs += 1
            self.failed_runs += 1
            
            return AggregatedQAReport(
                success=False,
                file_path=file_path,
                timestamp=datetime.now().isoformat(),
                flake8_executed=False,
                bandit_executed=False,
                radon_executed=False,
                total_issues=0,
                critical_issues=0,
                lint_issues=0,
                security_issues=0,
                complexity_issues=0,
                average_complexity=None,
                max_complexity=None,
                maintainability_index=None,
                maintainability_grade=None,
                passes_quality_gate=False,
                quality_score=None,
                summary=f"Analysis failed: {str(e)}"
            )
    
    async def _run_flake8(self, file_path: str, options: Dict) -> Dict:
        """Run flake8 linting"""
        try:
            result = await self.flake8.run_async(file_path, options.get("flake8", {}))
            return result
        except Exception as e:
            logger.error(f"Flake8 execution failed: {e}")
            return {"success": False, "error": str(e), "issues": []}
    
    async def _run_bandit(self, file_path: str, options: Dict) -> Dict:
        """Run bandit security scan"""
        try:
            result = await self.bandit.run_async(file_path, options.get("bandit", {}))
            return result
        except Exception as e:
            logger.error(f"Bandit execution failed: {e}")
            return {"success": False, "error": str(e), "issues": []}
    
    async def _run_radon(self, file_path: str, options: Dict) -> Dict:
        """Run radon complexity analysis"""
        try:
            # Run both complexity and maintainability
            complexity_result = await self.radon.analyze_complexity_async(file_path, options.get("radon", {}))
            maintainability_result = await self.radon.analyze_maintainability_async(file_path, options.get("radon", {}))
            
            # Merge results
            result = complexity_result.copy()
            if maintainability_result.get("success"):
                result["maintainability_index"] = maintainability_result.get("maintainability_index", 0)
                result["maintainability_grade"] = maintainability_result.get("grade", "F")
            
            return result
        except Exception as e:
            logger.error(f"Radon execution failed: {e}")
            return {"success": False, "error": str(e), "functions": []}
    
    def _convert_flake8_issues(self, result: Dict, file_path: str) -> List[QAIssueDetail]:
        """Convert flake8 issues to QAIssueDetail"""
        issues = []
        
        for issue in result.get("issues", []):
            # Map severity
            severity_map = {
                "error": SeverityLevel.HIGH,
                "warning": SeverityLevel.MEDIUM,
                "info": SeverityLevel.LOW
            }
            
            severity = severity_map.get(issue.get("severity", "info"), SeverityLevel.LOW)
            
            issues.append(QAIssueDetail(
                file=issue.get("file", file_path),
                line=issue.get("line", 0),
                column=issue.get("column"),
                code=issue.get("code", ""),
                message=issue.get("message", ""),
                severity=severity,
                category=QAIssueCategory.LINT,
                tool=QAToolType.FLAKE8,
                confidence=None,
                complexity=None,
                more_info=None
            ))
        
        return issues
    
    def _convert_bandit_issues(self, result: Dict, file_path: str) -> List[QAIssueDetail]:
        """Convert bandit issues to QAIssueDetail"""
        issues = []
        
        for issue in result.get("issues", []):
            # Map severity
            severity_str = issue.get("severity", "low").upper()
            severity = SeverityLevel(severity_str) if severity_str in [s.value.upper() for s in SeverityLevel] else SeverityLevel.LOW
            
            issues.append(QAIssueDetail(
                file=issue.get("file", file_path),
                line=issue.get("line", 0),
                column=None,
                code=issue.get("code", ""),
                message=issue.get("message", ""),
                severity=severity,
                category=QAIssueCategory.SECURITY,
                tool=QAToolType.BANDIT,
                confidence=issue.get("confidence"),
                complexity=None,
                more_info=issue.get("more_info")
            ))
        
        return issues
    
    def _convert_radon_issues(self, result: Dict, file_path: str) -> List[QAIssueDetail]:
        """Convert radon complexity issues to QAIssueDetail"""
        issues = []
        threshold = self.config.get_radon_config().get("max_complexity", 10)
        
        for func in result.get("functions", []):
            complexity = func.get("complexity", 0)
            
            if complexity > threshold:
                # Determine severity
                if complexity > 20:
                    severity = SeverityLevel.HIGH
                elif complexity > 10:
                    severity = SeverityLevel.MEDIUM
                else:
                    severity = SeverityLevel.LOW
                
                issues.append(QAIssueDetail(
                    file=func.get("file", file_path),
                    line=func.get("line", 0),
                    column=None,
                    code="C901",
                    message=f"Function '{func.get('name', 'unknown')}' is too complex (complexity: {complexity})",
                    severity=severity,
                    category=QAIssueCategory.COMPLEXITY,
                    tool=QAToolType.RADON,
                    confidence=None,
                    complexity=float(complexity),
                    more_info=None
                ))
        
        return issues
    
    def _calculate_quality_score(self, report: AggregatedQAReport) -> float:
        """Calculate overall quality score (0-100)"""
        score = 100.0
        
        # Deduct points for issues
        score -= report.critical_issues * 10
        score -= report.lint_issues * 0.5
        score -= report.security_issues * 5
        score -= report.complexity_issues * 2
        
        # Adjust for maintainability
        if report.maintainability_index is not None:
            mi_bonus = (report.maintainability_index - 50) * 0.1
            score += mi_bonus
        
        # Clamp to 0-100
        return max(0.0, min(100.0, score))
    
    def _evaluate_quality_gate(self, report: AggregatedQAReport) -> bool:
        """Evaluate if code passes quality gate"""
        # Fail if critical issues
        if report.critical_issues > 0:
            return False
        
        # Fail if too many total issues
        if report.total_issues > 50:
            return False
        
        # Fail if quality score too low
        if report.quality_score is not None and report.quality_score < 60:
            return False
        
        # Fail if maintainability too low
        if report.maintainability_index is not None and report.maintainability_index < 20:
            return False
        
        return True
    
    def _generate_recommendations(self, report: AggregatedQAReport) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if report.critical_issues > 0:
            recommendations.append(f"🚨 Fix {report.critical_issues} critical issue(s) immediately")
        
        if report.security_issues > 0:
            recommendations.append(f"🔒 Address {report.security_issues} security issue(s)")
        
        if report.complexity_issues > 0:
            recommendations.append(f"📊 Refactor {report.complexity_issues} complex function(s)")
        
        if report.lint_issues > 10:
            recommendations.append(f"🧹 Clean up {report.lint_issues} linting issue(s)")
        
        if report.maintainability_grade and report.maintainability_grade in ["D", "F"]:
            recommendations.append(f"⚠️ Improve maintainability (current grade: {report.maintainability_grade})")
        
        if not recommendations:
            recommendations.append("✅ Code quality looks good!")
        
        return recommendations
    
    def _generate_summary(self, report: AggregatedQAReport, execution_time: float) -> str:
        """Generate overall summary"""
        gate_status = "✅ PASSED" if report.passes_quality_gate else "❌ FAILED"
        
        tools_run = []
        if report.flake8_executed:
            tools_run.append("flake8")
        if report.bandit_executed:
            tools_run.append("bandit")
        if report.radon_executed:
            tools_run.append("radon")
        
        summary = f"QA Analysis {gate_status} | {report.total_issues} issues | "
        summary += f"Quality score: {report.quality_score:.1f}/100 | "
        summary += f"Tools: {', '.join(tools_run)} | "
        summary += f"Time: {execution_time:.2f}s"
        
        return summary
    
    def _get_current_memory_mb(self) -> float:
        """Get current process memory usage in MB"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / (1024 * 1024)  # Convert to MB
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return 0.0
    
    async def _check_memory_limit(self) -> None:
        """Check and update peak memory, warn if limit exceeded"""
        current_mb = self._get_current_memory_mb()
        self.peak_memory_mb = max(self.peak_memory_mb, current_mb)
        
        limit_mb = self.ram_limits.get("total_limit_mb", 3584)
        
        if current_mb > limit_mb:
            logger.warning(f"⚠️ Memory usage ({current_mb:.1f} MB) exceeds limit ({limit_mb} MB)")
        
        # Small delay to allow garbage collection
        await asyncio.sleep(0.1)
    
    def get_ram_metrics(self) -> RAMUsageMetrics:
        """Get RAM usage metrics"""
        current_mb = self._get_current_memory_mb()
        limit_mb = self.ram_limits.get("total_limit_mb", 3584)
        
        return RAMUsageMetrics(
            current_mb=current_mb,
            peak_mb=self.peak_memory_mb,
            limit_mb=limit_mb,
            within_limit=self.peak_memory_mb <= limit_mb,
            timestamp=datetime.now().isoformat()
        )
    
    def get_stats(self) -> Dict:
        """Get manager statistics"""
        return {
            "total_runs": self.total_runs,
            "successful_runs": self.successful_runs,
            "failed_runs": self.failed_runs,
            "success_rate": (self.successful_runs / self.total_runs * 100) if self.total_runs > 0 else 0,
            "peak_memory_mb": self.peak_memory_mb,
            "flake8_stats": self.flake8.get_stats(),
            "bandit_stats": self.bandit.get_stats(),
            "radon_stats": self.radon.get_stats()
        }


# Convenience function
async def analyze_code_quality(
    file_path: str,
    tools: Optional[List[QAToolType]] = None,
    config: Optional[QAToolsConfig] = None,
    options: Optional[Dict] = None
) -> AggregatedQAReport:
    """
    Convenience function to analyze code quality
    
    Args:
        file_path: Path to analyze
        tools: Tools to run (default: all)
        config: QA tools configuration
        options: Tool-specific options
    
    Returns:
        AggregatedQAReport with results
    """
    manager = AsyncQATaskManager(config=config)
    return await manager.analyze_code_quality_async(file_path, tools=tools, options=options)
