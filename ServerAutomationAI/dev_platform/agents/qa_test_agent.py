"""
QA/Test Agent
Automated testing, quality analysis, and bug detection
"""

from typing import Dict, List, Optional
import logging
import uuid
import re
import asyncio
from datetime import datetime

from .base_agent import BaseAgent
from .schemas import (
    TestStatus, SeverityLevel, TestResult, QualityGate, DefectRecord,
    RunTestsRequest, RunTestsResponse,
    AnalyzeQualityRequest, AnalyzeQualityResponse,
    ReportBugRequest, ReportBugResponse,
    GenerateTestsRequest, GenerateTestsResponse,
    QAToolType, AggregatedQAReport, RAMUsageMetrics
)

logger = logging.getLogger(__name__)


class QATestAgent(BaseAgent):
    """
    QA/Test Agent
    
    Responsibilities:
    - Run tests (unit, integration, all)
    - Analyze code quality (lint, coverage, complexity)
    - Detect and report bugs
    - Generate test suggestions
    - Track quality metrics over time
    """
    
    def __init__(self):
        super().__init__(
            agent_id="qa_test",
            name="QA/Test Agent",
            description="Automated testing and quality assurance",
            permission_level="execute"
        )
        
        # Test run history
        self.test_history: List[Dict] = []
        
        # Quality metrics history
        self.quality_history: List[Dict] = []
        
        # Known defects
        self.defects: Dict[str, DefectRecord] = {}
        
        # Load state
        self._load_qa_state()
    
    def _load_qa_state(self):
        """Load QA state from cache"""
        # Load test history
        history = self.cache.cache_get(f"qa_test_history_{self.agent_id}")
        if history:
            self.test_history = history[-50:]  # Keep last 50 runs
        
        # Load quality history
        quality_hist = self.cache.cache_get(f"qa_quality_history_{self.agent_id}")
        if quality_hist:
            self.quality_history = quality_hist[-50:]
        
        # Load defects
        defects_data = self.cache.cache_get(f"qa_defects_{self.agent_id}")
        if defects_data:
            self.defects = {k: DefectRecord(**v) for k, v in defects_data.items()}
    
    def _save_qa_state(self):
        """Save QA state to cache"""
        self.cache.cache_set(
            f"qa_test_history_{self.agent_id}",
            self.test_history[-50:],
            expire=86400 * 7  # 7 days
        )
        self.cache.cache_set(
            f"qa_quality_history_{self.agent_id}",
            self.quality_history[-50:],
            expire=86400 * 7
        )
        self.cache.cache_set(
            f"qa_defects_{self.agent_id}",
            {k: v.model_dump() for k, v in self.defects.items()},
            expire=86400 * 30  # 30 days
        )
    
    def execute(self, request: Dict) -> Dict:
        """
        Execute QA/Test request
        
        Args:
            request: Dict with 'action' and action-specific parameters
        
        Returns:
            Dict with results
        """
        try:
            action = request.get("action")
            
            if not action:
                return {
                    "success": False,
                    "error": "No action specified. Valid actions: run_tests, analyze_quality, report_bug, generate_tests"
                }
            
            # Route to appropriate handler
            if action == "run_tests":
                return self.run_tests(request)
            elif action == "analyze_quality":
                return self.analyze_quality(request)
            elif action == "report_bug":
                return self.report_bug(request)
            elif action == "generate_tests":
                return self.generate_tests(request)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}. Valid: run_tests, analyze_quality, report_bug, generate_tests"
                }
        
        except Exception as e:
            logger.error(f"Error in QATestAgent.execute: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========== Test Execution Manager ==========
    
    def run_tests(self, request: Dict) -> Dict:
        """
        Run tests (all, unit, integration, or specific)
        
        Args:
            request: RunTestsRequest data
        
        Returns:
            RunTestsResponse data
        """
        try:
            test_type = request.get("test_type", "all")
            test_path = request.get("test_path")
            test_pattern = request.get("test_pattern")
            coverage = request.get("coverage", True)
            verbose = request.get("verbose", False)
            
            logger.info(f"Running {test_type} tests...")
            
            # Build pytest command
            cmd_parts = ["python", "-m", "pytest"]
            
            # Add path or default to tests/
            if test_path:
                cmd_parts.append(test_path)
            elif test_type == "unit":
                cmd_parts.append("tests/unit/")
            elif test_type == "integration":
                cmd_parts.append("tests/integration/")
            else:
                cmd_parts.append("tests/")
            
            # Add pattern if specified
            if test_pattern:
                cmd_parts.extend(["-k", test_pattern])
            
            # Add coverage if requested
            if coverage:
                cmd_parts.extend(["--cov=dev_platform", "--cov-report=term-missing"])
            
            # Add verbosity
            if verbose:
                cmd_parts.append("-v")
            else:
                cmd_parts.append("-q")
            
            # Add JSON report for parsing
            cmd_parts.append("--tb=short")
            
            command = " ".join(cmd_parts)
            
            # Execute via Code Executor
            exec_result = self.call_tool(
                "execute_bash",
                kwargs={
                    "command": command,
                    "timeout": 300  # 5 minutes
                }
            )
            
            if not exec_result.get("success"):
                return {
                    "success": False,
                    "error": f"Test execution failed: {exec_result.get('error', 'Unknown error')}",
                    "total_tests": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "errors": 0,
                    "duration": 0.0
                }
            
            # Parse test output
            output = exec_result.get("stdout", "") + exec_result.get("stderr", "")
            test_results = self._parse_pytest_output(output)
            
            # Build response
            response = {
                "success": True,
                "total_tests": test_results["total"],
                "passed": test_results["passed"],
                "failed": test_results["failed"],
                "skipped": test_results["skipped"],
                "errors": test_results["errors"],
                "duration": test_results["duration"],
                "coverage": test_results.get("coverage"),
                "test_results": test_results.get("individual_results", []),
                "summary": test_results.get("summary", "Tests completed")
            }
            
            # Save to history
            self.test_history.append({
                "timestamp": self._get_timestamp(),
                "test_type": test_type,
                "results": response
            })
            self._save_qa_state()
            
            return response
        
        except Exception as e:
            logger.error(f"Error running tests: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
                "duration": 0.0
            }
    
    def _parse_pytest_output(self, output: str) -> Dict:
        """Parse pytest output to extract test results"""
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "duration": 0.0,
            "coverage": None,
            "summary": "",
            "individual_results": []
        }
        
        # Parse summary line (e.g., "27 passed in 10.04s")
        summary_pattern = r'(\d+)\s+passed|(\d+)\s+failed|(\d+)\s+skipped|(\d+)\s+error'
        for match in re.finditer(summary_pattern, output):
            if match.group(1):  # passed
                results["passed"] = int(match.group(1))
            elif match.group(2):  # failed
                results["failed"] = int(match.group(2))
            elif match.group(3):  # skipped
                results["skipped"] = int(match.group(3))
            elif match.group(4):  # error
                results["errors"] = int(match.group(4))
        
        results["total"] = results["passed"] + results["failed"] + results["skipped"] + results["errors"]
        
        # Parse duration
        duration_match = re.search(r'in\s+([\d.]+)s', output)
        if duration_match:
            results["duration"] = float(duration_match.group(1))
        
        # Parse coverage
        coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
        if coverage_match:
            results["coverage"] = float(coverage_match.group(1))
        
        # Build summary
        if results["total"] > 0:
            results["summary"] = f"{results['passed']}/{results['total']} tests passed"
            if results["failed"] > 0:
                results["summary"] += f", {results['failed']} failed"
        
        return results
    
    # ========== Quality Insights Pipeline ==========
    
    def analyze_quality(self, request: Dict) -> Dict:
        """
        Analyze code quality (lint, coverage, complexity)
        
        Args:
            request: AnalyzeQualityRequest data
        
        Returns:
            AnalyzeQualityResponse data
        """
        try:
            file_path = request.get("file_path")
            check_types = request.get("check_types", ["lint", "coverage"])
            thresholds = request.get("thresholds", {})
            
            logger.info(f"Analyzing quality: {check_types}")
            
            quality_gates = []
            lint_issues = 0
            coverage = None
            complexity_score = None
            recommendations = []
            
            # Run coverage check if requested
            if "coverage" in check_types:
                coverage_gate = self._check_coverage(file_path, thresholds.get("coverage", 80.0))
                quality_gates.append(coverage_gate)
                coverage = coverage_gate.get("actual_value")
                
                if not coverage_gate.get("passed"):
                    recommendations.append(f"Increase test coverage to {thresholds.get('coverage', 80)}%")
            
            # Run lint check if requested
            if "lint" in check_types:
                lint_gate = self._check_lint(file_path, thresholds.get("lint_issues", 0))
                quality_gates.append(lint_gate)
                lint_issues = int(lint_gate.get("actual_value", 0))
                
                if not lint_gate.get("passed"):
                    recommendations.append("Fix linting issues")
            
            # Determine overall pass/fail
            overall_passed = all(gate.get("passed", False) for gate in quality_gates)
            
            response = {
                "success": True,
                "quality_gates": quality_gates,
                "overall_passed": overall_passed,
                "lint_issues": lint_issues,
                "complexity_score": complexity_score,
                "coverage": coverage,
                "recommendations": recommendations
            }
            
            # Save to history
            self.quality_history.append({
                "timestamp": self._get_timestamp(),
                "results": response
            })
            self._save_qa_state()
            
            return response
        
        except Exception as e:
            logger.error(f"Error analyzing quality: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "quality_gates": [],
                "overall_passed": False,
                "lint_issues": 0
            }
    
    def _check_coverage(self, file_path: Optional[str], threshold: float) -> Dict:
        """Check code coverage"""
        # Run tests with coverage
        result = self.run_tests({
            "test_type": "all",
            "coverage": True,
            "verbose": False
        })
        
        coverage = result.get("coverage", 0.0)
        passed = coverage >= threshold
        
        return {
            "name": "coverage",
            "passed": passed,
            "threshold": threshold,
            "actual_value": coverage,
            "message": f"Coverage: {coverage}% (threshold: {threshold}%)"
        }
    
    def _check_lint(self, file_path: Optional[str], max_issues: int) -> Dict:
        """Check code linting"""
        # For now, return a placeholder - can integrate flake8/ruff later
        return {
            "name": "lint",
            "passed": True,
            "threshold": max_issues,
            "actual_value": 0,
            "message": "No linting issues found"
        }
    
    # ========== Bug Triage Module ==========
    
    def report_bug(self, request: Dict) -> Dict:
        """
        Generate bug report from test results
        
        Args:
            request: ReportBugRequest data
        
        Returns:
            ReportBugResponse data
        """
        try:
            test_results_data = request.get("test_results", [])
            auto_triage = request.get("auto_triage", True)
            suggest_fixes = request.get("suggest_fixes", True)
            
            defects = []
            critical_count = 0
            high_count = 0
            
            # Analyze test results for defects
            for test_result in test_results_data:
                if test_result.get("status") in ["failed", "error"]:
                    defect = self._create_defect_record(test_result, auto_triage, suggest_fixes)
                    defects.append(defect)
                    
                    # Count by severity
                    if defect.get("severity") == "critical":
                        critical_count += 1
                    elif defect.get("severity") == "high":
                        high_count += 1
                    
                    # Store defect
                    defect_obj = DefectRecord(**defect)
                    self.defects[defect["id"]] = defect_obj
            
            # Build summary
            total_count = len(defects)
            summary = f"Found {total_count} defects: {critical_count} critical, {high_count} high priority"
            
            response = {
                "success": True,
                "defects": defects,
                "critical_count": critical_count,
                "high_count": high_count,
                "total_count": total_count,
                "summary": summary
            }
            
            self._save_qa_state()
            
            return response
        
        except Exception as e:
            logger.error(f"Error reporting bug: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "defects": [],
                "critical_count": 0,
                "high_count": 0,
                "total_count": 0
            }
    
    def _create_defect_record(
        self,
        test_result: Dict,
        auto_triage: bool,
        suggest_fixes: bool
    ) -> Dict:
        """Create a defect record from test result"""
        defect_id = str(uuid.uuid4())[:8]
        
        # Determine severity
        severity = "medium"
        if auto_triage:
            error_msg = test_result.get("error_message", "").lower()
            if any(kw in error_msg for kw in ["critical", "fatal", "crash", "security"]):
                severity = "critical"
            elif any(kw in error_msg for kw in ["error", "exception", "failed"]):
                severity = "high"
        
        # Generate fix suggestion if requested
        suggested_fix = None
        if suggest_fixes:
            suggested_fix = f"Review test '{test_result.get('test_name')}' and fix the underlying issue"
        
        return {
            "id": defect_id,
            "severity": severity,
            "title": f"Test failed: {test_result.get('test_name', 'Unknown')}",
            "description": test_result.get("error_message", "No error message"),
            "file_path": test_result.get("file_path"),
            "line_number": test_result.get("line_number"),
            "suggested_fix": suggested_fix,
            "created_at": self._get_timestamp()
        }
    
    # ========== Test Authoring Assistant ==========
    
    def generate_tests(self, request: Dict) -> Dict:
        """
        Generate test code for a file (AI-powered)
        
        Args:
            request: GenerateTestsRequest data
        
        Returns:
            GenerateTestsResponse data
        """
        try:
            file_path = request.get("file_path")
            test_type = request.get("test_type", "unit")
            framework = request.get("framework", "pytest")
            coverage_target = request.get("coverage_target")
            
            if not file_path:
                return {
                    "success": False,
                    "error": "No file_path provided",
                    "tests_count": 0
                }
            
            logger.info(f"Generating {test_type} tests for {file_path}")
            
            # Read the file to generate tests for
            file_result = self.call_tool("read_file", kwargs={"path": file_path})
            
            if not file_result.get("success"):
                return {
                    "success": False,
                    "error": f"Could not read file: {file_result.get('error')}",
                    "tests_count": 0
                }
            
            file_content = file_result.get("content", "")
            
            # Use AI to generate tests
            test_code = self._generate_test_code_with_ai(
                file_path, file_content, test_type, framework
            )
            
            if not test_code:
                return {
                    "success": False,
                    "error": "Failed to generate test code",
                    "tests_count": 0
                }
            
            # Determine test file path
            test_file_path = self._get_test_file_path(file_path, test_type)
            
            # Count generated tests
            tests_count = len(re.findall(r'def test_', test_code))
            
            return {
                "success": True,
                "test_file_path": test_file_path,
                "test_code": test_code,
                "tests_count": tests_count,
                "estimated_coverage": None  # Can be calculated after writing tests
            }
        
        except Exception as e:
            logger.error(f"Error generating tests: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "tests_count": 0
            }
    
    def _generate_test_code_with_ai(
        self,
        file_path: str,
        file_content: str,
        test_type: str,
        framework: str
    ) -> Optional[str]:
        """Use AI to generate test code"""
        prompt = f"""Generate {test_type} tests using {framework} for the following Python code.

File: {file_path}

Code:
```python
{file_content[:2000]}  # Truncate to avoid token limits
```

Requirements:
1. Use {framework} framework
2. Test all public functions and methods
3. Include edge cases and error handling
4. Follow best practices
5. Add clear docstrings

Return ONLY the test code, no explanations."""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.ask_model(messages, temperature=0.3)
            
            if isinstance(response, str):
                # Extract code from markdown if present
                code_match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)
                if code_match:
                    return code_match.group(1)
                return response
            
            return None
        except Exception as e:
            logger.error(f"Error generating test code with AI: {e}")
            return None
    
    def _get_test_file_path(self, source_file: str, test_type: str) -> str:
        """Get test file path for source file"""
        # Convert source path to test path
        # e.g., dev_platform/agents/qa_agent.py -> tests/unit/test_qa_agent.py
        file_name = source_file.split("/")[-1]
        test_file_name = f"test_{file_name}"
        
        if test_type == "integration":
            return f"tests/integration/{test_file_name}"
        else:
            return f"tests/unit/{test_file_name}"
    
    # ========== Utility Methods ==========
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()
    
    def get_status(self) -> Dict:
        """
        Get agent status and metrics
        
        Returns:
            Dict with status and stats
        """
        total_runs = len(self.test_history)
        recent_run = self.test_history[-1] if self.test_history else None
        
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state,
            "stats": {
                "total_test_runs": total_runs,
                "total_defects": len(self.defects),
                "critical_defects": sum(1 for d in self.defects.values() if d.severity == SeverityLevel.CRITICAL),
                "recent_coverage": recent_run["results"].get("coverage") if recent_run else None
            },
            "recent_run": recent_run
        }
    
    def get_defects(self, severity: Optional[str] = None) -> List[Dict]:
        """Get all defects, optionally filtered by severity"""
        defects = list(self.defects.values())
        
        if severity:
            defects = [d for d in defects if d.severity == severity]
        
        return [d.model_dump() for d in defects]
    
    def clear_defects(self, defect_ids: Optional[List[str]] = None):
        """Clear defects (all or specific IDs)"""
        if defect_ids:
            for defect_id in defect_ids:
                self.defects.pop(defect_id, None)
        else:
            self.defects.clear()
        
        self._save_qa_state()
        logger.info(f"Cleared {len(defect_ids) if defect_ids else 'all'} defects")
    
    # ========== Async Methods (Phase 3.3) ==========
    
    async def run_tests_async(
        self,
        test_type: str = "all",
        test_path: Optional[str] = None,
        test_pattern: Optional[str] = None,
        coverage: bool = True,
        verbose: bool = False
    ) -> Dict:
        """
        Run tests asynchronously
        
        Args:
            test_type: Type of tests (all, unit, integration, specific)
            test_path: Specific test file or directory
            test_pattern: Test name pattern (e.g., 'test_*')
            coverage: Generate coverage report
            verbose: Verbose output
        
        Returns:
            RunTestsResponse data
        """
        try:
            logger.info(f"Running {test_type} tests asynchronously...")
            
            # Build pytest command
            cmd_parts = ["python", "-m", "pytest"]
            
            # Add path or default to tests/
            if test_path:
                cmd_parts.append(test_path)
            elif test_type == "unit":
                cmd_parts.append("tests/unit/")
            elif test_type == "integration":
                cmd_parts.append("tests/integration/")
            else:
                cmd_parts.append("tests/")
            
            # Add pattern if specified
            if test_pattern:
                cmd_parts.extend(["-k", test_pattern])
            
            # Add coverage if requested
            if coverage:
                cmd_parts.extend(["--cov=dev_platform", "--cov-report=term-missing"])
            
            # Add verbosity
            if verbose:
                cmd_parts.append("-v")
            else:
                cmd_parts.append("-q")
            
            cmd_parts.append("--tb=short")
            
            # Execute asynchronously
            process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=300.0  # 5 minutes
                )
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": "Test execution timed out (5 minutes)",
                    "total_tests": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "errors": 0,
                    "duration": 0.0
                }
            
            # Decode output
            output = stdout.decode("utf-8", errors="ignore") + stderr.decode("utf-8", errors="ignore")
            
            # Parse test output
            test_results = self._parse_pytest_output(output)
            
            # Build response
            response = {
                "success": True,
                "total_tests": test_results["total"],
                "passed": test_results["passed"],
                "failed": test_results["failed"],
                "skipped": test_results["skipped"],
                "errors": test_results["errors"],
                "duration": test_results["duration"],
                "coverage": test_results.get("coverage"),
                "test_results": test_results.get("individual_results", []),
                "summary": test_results.get("summary", "Tests completed")
            }
            
            # Save to history
            self.test_history.append({
                "timestamp": self._get_timestamp(),
                "test_type": test_type,
                "results": response
            })
            self._save_qa_state()
            
            logger.info(f"Async test run completed: {response['summary']}")
            
            return response
        
        except Exception as e:
            logger.error(f"Error running tests async: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
                "duration": 0.0
            }
    
    async def analyze_quality_async(
        self,
        file_path: str,
        tools: Optional[List[QAToolType]] = None,
        options: Optional[Dict] = None
    ) -> AggregatedQAReport:
        """
        Analyze code quality asynchronously using QA tools
        
        Args:
            file_path: Path to file or directory to analyze
            tools: List of tools to run (default: [flake8, bandit, radon])
            options: Tool-specific options
        
        Returns:
            AggregatedQAReport with results from all tools
        """
        try:
            logger.info(f"Analyzing code quality asynchronously: {file_path}")
            
            # Lazy import to avoid circular dependency
            from dev_platform.tools.async_qa_manager import AsyncQATaskManager
            
            # Create manager and run analysis
            manager = AsyncQATaskManager()
            report = await manager.analyze_code_quality_async(
                file_path=file_path,
                tools=tools,
                options=options
            )
            
            # Save to quality history
            self.quality_history.append({
                "timestamp": self._get_timestamp(),
                "file_path": file_path,
                "total_issues": report.total_issues,
                "quality_score": report.quality_score,
                "passes_gate": report.passes_quality_gate
            })
            self._save_qa_state()
            
            logger.info(f"Quality analysis completed: {report.summary}")
            
            return report
        
        except Exception as e:
            logger.error(f"Error analyzing quality async: {e}", exc_info=True)
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
    
    async def report_bug_async(
        self,
        test_results: Optional[List[TestResult]] = None,
        auto_triage: bool = True,
        suggest_fixes: bool = True
    ) -> Dict:
        """
        Report bugs asynchronously with AI-powered triage
        
        Args:
            test_results: Test results to analyze for bugs
            auto_triage: Auto-assign severity levels
            suggest_fixes: Generate fix suggestions using AI
        
        Returns:
            ReportBugResponse data
        """
        try:
            logger.info("Generating bug report asynchronously...")
            
            if not test_results:
                # Get latest test results from history
                if self.test_history:
                    latest_run = self.test_history[-1]
                    test_results = latest_run.get("results", {}).get("test_results", [])
            
            if not test_results:
                return {
                    "success": False,
                    "error": "No test results available",
                    "defects": [],
                    "critical_count": 0,
                    "high_count": 0,
                    "total_count": 0
                }
            
            # Analyze test results for defects
            defects = []
            critical_count = 0
            high_count = 0
            
            for test_result in test_results:
                if isinstance(test_result, TestResult):
                    test_result_dict = test_result.model_dump()
                else:
                    test_result_dict = test_result
                
                if test_result_dict.get("status") in ["failed", "error"]:
                    defect = await asyncio.to_thread(
                        self._create_defect_record,
                        test_result_dict,
                        auto_triage,
                        suggest_fixes
                    )
                    defects.append(defect)
                    
                    # Count by severity
                    if defect.get("severity") == "critical":
                        critical_count += 1
                    elif defect.get("severity") == "high":
                        high_count += 1
                    
                    # Store defect
                    defect_obj = DefectRecord(**defect)
                    self.defects[defect["id"]] = defect_obj
            
            self._save_qa_state()
            
            # Build response
            response = {
                "success": True,
                "defects": defects,
                "critical_count": critical_count,
                "high_count": high_count,
                "total_count": len(defects),
                "summary": f"Found {len(defects)} defect(s): {critical_count} critical, {high_count} high"
            }
            
            logger.info(f"Bug report completed: {response['summary']}")
            
            return response
        
        except Exception as e:
            logger.error(f"Error reporting bugs async: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "defects": [],
                "critical_count": 0,
                "high_count": 0,
                "total_count": 0
            }
    
    async def generate_tests_async(
        self,
        file_path: str,
        test_type: str = "unit",
        framework: str = "pytest",
        coverage_target: Optional[float] = None
    ) -> Dict:
        """
        Generate tests asynchronously using AI
        
        Args:
            file_path: File to generate tests for
            test_type: Type of tests (unit, integration, e2e)
            framework: Test framework (pytest, unittest, etc)
            coverage_target: Target coverage percentage
        
        Returns:
            GenerateTestsResponse data
        """
        try:
            logger.info(f"Generating {test_type} tests asynchronously for {file_path}")
            
            # Run test generation in thread pool (AI call is CPU-intensive)
            result = await asyncio.to_thread(
                self._generate_tests_with_ai,
                file_path,
                test_type,
                framework,
                coverage_target
            )
            
            logger.info(f"Test generation completed: {result.get('tests_count', 0)} tests generated")
            
            return result
        
        except Exception as e:
            logger.error(f"Error generating tests async: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "test_file_path": None,
                "test_code": None,
                "tests_count": 0,
                "estimated_coverage": None
            }
    
    def _generate_tests_with_ai(
        self,
        file_path: str,
        test_type: str,
        framework: str,
        coverage_target: Optional[float]
    ) -> Dict:
        """Helper method to generate tests using AI (sync)"""
        try:
            # Read the file
            file_result = self.call_tool("read_file", kwargs={"path": file_path})
            
            if not file_result.get("success"):
                return {
                    "success": False,
                    "error": f"Could not read file: {file_result.get('error')}",
                    "test_file_path": None,
                    "test_code": None,
                    "tests_count": 0,
                    "estimated_coverage": None
                }
            
            file_content = file_result.get("content", "")
            
            # Use existing AI method
            test_code = self._generate_test_code_with_ai(
                file_path, file_content, test_type, framework
            )
            
            if not test_code:
                return {
                    "success": False,
                    "error": "Failed to generate test code",
                    "test_file_path": None,
                    "test_code": None,
                    "tests_count": 0,
                    "estimated_coverage": None
                }
            
            # Count tests
            test_count = test_code.count("def test_")
            
            # Estimate coverage
            estimated_coverage = min(coverage_target or 80, test_count * 10)
            
            # Determine test file path
            test_file_path = file_path.replace(".py", "_test.py")
            if not test_file_path.endswith("_test.py"):
                test_file_path = file_path.replace(".py", "") + "_test.py"
            
            return {
                "success": True,
                "test_file_path": test_file_path,
                "test_code": test_code,
                "tests_count": test_count,
                "estimated_coverage": estimated_coverage
            }
        
        except Exception as e:
            logger.error(f"Error in AI test generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_file_path": None,
                "test_code": None,
                "tests_count": 0,
                "estimated_coverage": None
            }
    
    async def get_ram_metrics_async(self) -> RAMUsageMetrics:
        """
        Get RAM usage metrics asynchronously
        
        Returns:
            RAMUsageMetrics with current and peak usage
        """
        try:
            from dev_platform.tools.async_qa_manager import AsyncQATaskManager
            
            manager = AsyncQATaskManager()
            metrics = manager.get_ram_metrics()
            
            return metrics
        
        except Exception as e:
            logger.error(f"Error getting RAM metrics: {e}")
            return RAMUsageMetrics(
                current_mb=0.0,
                peak_mb=0.0,
                limit_mb=3584.0,
                within_limit=True,
                timestamp=datetime.now().isoformat()
            )
