"""
Planner Agent
Plans and decomposes user requests into actionable tasks
"""

from typing import Dict, List, Optional
import json
import logging
from pydantic import ValidationError

from .base_agent import BaseAgent
from .schemas import (
    Plan,
    Task,
    TaskComplexity,
    ProjectStructure,
    ResourceEstimate,
    ProjectPlan
)

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """
    Planner Agent
    
    Responsibilities:
    - Understand user requests
    - Decompose into actionable tasks
    - Create execution plans
    - Provide project structure recommendations
    """
    
    def __init__(self):
        super().__init__(
            agent_id="planner",
            name="Planner Agent",
            description="Plans and decomposes user requests into tasks",
            permission_level="basic"
        )
        
        # Maximum number of recovery attempts
        self.max_recovery_attempts = 2
        
        self.system_prompt = """You are a Planner Agent in an AI development platform.
Your job is to:
1. Understand user requests for software projects
2. Decompose them into clear, actionable tasks
3. Suggest project structure and technologies
4. Create step-by-step execution plans

CRITICAL: You MUST respond with VALID JSON only. No extra text before or after.

Required JSON format:
{
  "understanding": "Clear summary of what user wants (min 10 characters)",
  "project_type": "Type of project: web, api, cli, script, data, mobile, desktop, or other",
  "technologies": ["list", "of", "technologies"],
  "tasks": [
    {"id": 1, "title": "Task title", "description": "Detailed description", "dependencies": []},
    {"id": 2, "title": "Second task", "description": "Details", "dependencies": [1]}
  ],
  "structure": {
    "files": ["file/paths/to/create.ext"],
    "folders": ["folder/paths/to/create"]
  },
  "next_steps": ["Immediate action 1", "Immediate action 2"]
}

VALIDATION RULES:
- understanding: minimum 10 characters
- project_type: must be one of: web, api, cli, script, data, mobile, desktop, other
- tasks: minimum 1 task required
- Each task MUST have: id (number >= 1), title (not empty), description (not empty), dependencies (array of task IDs)
- Task dependencies must reference existing task IDs
- Task IDs must be unique
- structure: files and folders are optional arrays of strings

Respond with ONLY the JSON object. No markdown code blocks, no explanations."""
    
    def execute(self, request: Dict) -> Dict:
        """
        Execute planning
        
        Args:
            request: Dict with 'user_request' (str)
        
        Returns:
            Dict with 'success', 'plan', and optional 'error'
        """
        try:
            user_request = request.get("user_request", "")
            
            if not user_request:
                return {
                    "success": False,
                    "error": "No user request provided"
                }
            
            logger.info(f"Planning for: {user_request[:100]}...")
            
            # Create task
            task_id = self.create_task(
                task_description=f"Plan: {user_request[:50]}",
                metadata={"request": user_request}
            )
            
            # Update task status
            self.update_task(task_id, "in_progress")
            
            # Ask model for plan
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_request}
            ]
            
            model_response = self.ask_model(
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent planning
                use_cache=True
            )
            
            if not model_response.get("content"):
                self.update_task(task_id, "failed", "Model returned empty response")
                return {
                    "success": False,
                    "error": "Model returned empty response"
                }
            
            # Parse and validate plan with recovery attempts
            validated_plan, parsing_errors = self._parse_and_validate_with_recovery(
                model_response["content"],
                user_request,
                attempt=0
            )
            
            if not validated_plan:
                # All parsing attempts failed
                logger.error(f"Failed to generate valid plan after {self.max_recovery_attempts + 1} attempts")
                logger.error(f"Parsing errors: {parsing_errors}")
                
                self.update_task(task_id, "failed", f"Failed to parse plan: {parsing_errors[-1] if parsing_errors else 'Unknown error'}")
                
                return {
                    "success": False,
                    "error": f"Failed to generate valid plan: {parsing_errors[-1] if parsing_errors else 'Unknown error'}",
                    "parsing_errors": parsing_errors,
                    "raw_response": model_response["content"]
                }
            
            # Enrich plan with resource estimates and project structure
            project_plan = self._build_project_plan(validated_plan)
            
            # Update task
            self.update_task(
                task_id,
                "completed",
                result=json.dumps(project_plan, indent=2)
            )
            
            return {
                "success": True,
                "plan": project_plan,
                "task_id": task_id,
                "model": model_response.get("model"),
                "tokens_used": model_response.get("tokens_used", 0)
            }
        
        except Exception as e:
            logger.error(f"Planning error: {e}")
            if self.current_task:
                self.update_task(self.current_task, "failed", str(e))
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_and_validate_with_recovery(
        self,
        content: str,
        user_request: str,
        attempt: int = 0
    ) -> tuple[Optional[Dict], List[str]]:
        """
        Parse and validate plan with recovery attempts
        
        Returns:
            Tuple of (validated_plan_dict, list_of_errors)
        """
        errors = []
        
        try:
            # Parse JSON
            plan_dict = self._parse_plan(content)
            
            # Validate with Pydantic
            plan = Plan(**plan_dict)
            
            # Convert back to dict for compatibility
            validated_dict = plan.model_dump()
            
            logger.info(f"✓ Plan validated successfully (attempt {attempt + 1})")
            logger.debug(f"Plan details: {validated_dict.get('understanding', '')}")
            logger.debug(f"Tasks count: {len(validated_dict.get('tasks', []))}")
            
            return validated_dict, errors
        
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing error: {str(e)}"
            errors.append(error_msg)
            logger.warning(f"✗ {error_msg} (attempt {attempt + 1})")
            logger.debug(f"Content that failed: {content[:200]}...")
        
        except ValidationError as e:
            error_msg = f"Schema validation error: {str(e)}"
            errors.append(error_msg)
            logger.warning(f"✗ {error_msg} (attempt {attempt + 1})")
            logger.debug(f"Validation errors: {e.errors()}")
        
        except Exception as e:
            error_msg = f"Unexpected parsing error: {str(e)}"
            errors.append(error_msg)
            logger.error(f"✗ {error_msg} (attempt {attempt + 1})")
        
        # If we haven't exhausted recovery attempts, try again with repair prompt
        if attempt < self.max_recovery_attempts:
            logger.info(f"Attempting recovery (attempt {attempt + 2}/{self.max_recovery_attempts + 1})...")
            
            recovery_content = self._attempt_recovery(
                content,
                user_request,
                errors[-1],
                attempt
            )
            
            if recovery_content:
                # Recursive retry with recovered content
                recovered_plan, recovery_errors = self._parse_and_validate_with_recovery(
                    recovery_content,
                    user_request,
                    attempt + 1
                )
                
                errors.extend(recovery_errors)
                return recovered_plan, errors
        
        # All attempts failed - try fallback to text extraction
        logger.warning("All recovery attempts failed, using fallback text extraction")
        fallback_plan = self._fallback_text_extraction(content, user_request)
        
        return fallback_plan, errors
    
    def _build_project_plan(self, validated_plan: Dict) -> Dict:
        """
        Build enriched ProjectPlan from validated Plan
        
        Args:
            validated_plan: Dictionary from Plan validation
        
        Returns:
            Dictionary representing ProjectPlan with resource estimates
        """
        from dev_platform.agents.schemas import Task, TaskComplexity
        
        try:
            # Convert task dicts to Task objects for estimation
            tasks = []
            for task_dict in validated_plan.get('tasks', []):
                # Enrich task with estimation metadata
                task = Task(
                    id=task_dict['id'],
                    title=task_dict['title'],
                    description=task_dict['description'],
                    dependencies=task_dict.get('dependencies', []),
                    estimated_hours=self._estimate_task_hours(task_dict),
                    complexity=self._infer_task_complexity(task_dict),
                    agent_type=self._assign_agent_type(task_dict)
                )
                tasks.append(task)
            
            # Generate resource estimate
            resource_estimate = self.estimate_resources(tasks)
            
            # Generate project structure
            project_type = validated_plan.get('project_type', 'other')
            technologies = validated_plan.get('technologies', [])
            project_structure = self.generate_project_structure(project_type, technologies)
            
            # Build ProjectPlan dictionary
            project_plan = {
                **validated_plan,  # Include all original fields
                'tasks': [task.model_dump() for task in tasks],  # Enriched tasks
                'resource_estimate': resource_estimate.model_dump(),
                'structure': project_structure.model_dump()
            }
            
            logger.info(f"✓ ProjectPlan enriched: {resource_estimate.total_tasks} tasks, "
                       f"{resource_estimate.total_estimated_hours:.1f}h estimated, "
                       f"{len(project_structure.files)} files, {len(project_structure.folders)} folders")
            
            return project_plan
        
        except Exception as e:
            logger.warning(f"Failed to enrich ProjectPlan: {e}, returning basic plan")
            return validated_plan
    
    def _estimate_task_hours(self, task_dict: Dict) -> float:
        """Estimate hours for a single task based on description complexity"""
        description = task_dict.get('description', '')
        title = task_dict.get('title', '')
        
        # Simple heuristic: longer descriptions = more complex tasks
        text_length = len(description) + len(title)
        
        if text_length < 50:
            return 1.0
        elif text_length < 150:
            return 2.0
        elif text_length < 300:
            return 4.0
        else:
            return 8.0
    
    def _infer_task_complexity(self, task_dict: Dict) -> 'TaskComplexity':
        """Infer task complexity from title and description"""
        from dev_platform.agents.schemas import TaskComplexity
        
        text = (task_dict.get('title', '') + ' ' + task_dict.get('description', '')).lower()
        
        # Keywords indicating complexity
        complex_keywords = ['integrate', 'refactor', 'architecture', 'security', 'optimize', 'performance']
        moderate_keywords = ['implement', 'create', 'build', 'develop', 'test']
        simple_keywords = ['setup', 'install', 'configure', 'add', 'update']
        
        if any(kw in text for kw in complex_keywords):
            return TaskComplexity.COMPLEX
        elif any(kw in text for kw in moderate_keywords):
            return TaskComplexity.MODERATE
        elif any(kw in text for kw in simple_keywords):
            return TaskComplexity.SIMPLE
        else:
            return TaskComplexity.MODERATE
    
    def _assign_agent_type(self, task_dict: Dict) -> str:
        """Assign agent type based on task nature"""
        text = (task_dict.get('title', '') + ' ' + task_dict.get('description', '')).lower()
        
        if any(kw in text for kw in ['test', 'qa', 'verify', 'validate']):
            return 'qa'
        elif any(kw in text for kw in ['plan', 'design', 'architect']):
            return 'planner'
        else:
            return 'executor'
    
    # === ASYNC API METHODS (Phase 3.1 Roadmap Compliance) ===
    
    async def analyze_user_request(self, request: str) -> Dict:
        """
        تحليل طلب المستخدم وإنشاء خطة مشروع كاملة (Phase 3.1 API)
        
        Args:
            request: طلب المستخدم
        
        Returns:
            ProjectPlan dictionary محسّن مع تقديرات الموارد وهيكل المشروع
        """
        import asyncio
        
        # Run synchronous execute() in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.execute,
            {"user_request": request}
        )
        
        # Return the ProjectPlan if successful
        if result.get('success'):
            return result.get('plan', {})
        else:
            raise ValueError(f"Failed to analyze request: {result.get('error')}")
    
    async def create_task_breakdown(self, project_plan: Dict) -> List[Dict]:
        """
        استخراج وإرجاع قائمة المهام المفصلة من ProjectPlan (Phase 3.1 API)
        
        Args:
            project_plan: ProjectPlan dictionary (من analyze_user_request)
        
        Returns:
            قائمة المهام المفصلة مع البيانات الوصفية (estimated_hours, complexity, agent_type)
        """
        tasks = project_plan.get('tasks', [])
        
        if not tasks:
            logger.warning("No tasks found in project plan")
            return []
        
        logger.info(f"Extracted {len(tasks)} tasks from project plan")
        return tasks
    
    async def estimate_resources_async(self, tasks: List[Task]) -> ResourceEstimate:
        """
        تقدير الموارد المطلوبة async (Phase 3.1 API)
        
        Args:
            tasks: قائمة كائنات Task
        
        Returns:
            ResourceEstimate مع التقديرات الكاملة
        """
        import asyncio
        
        # Run synchronous estimate_resources in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.estimate_resources,
            tasks
        )
    
    async def generate_project_structure_async(self, project_type: str, technologies: List[str]) -> ProjectStructure:
        """
        توليد هيكل الملفات والمجلدات async (Phase 3.1 API)
        
        Args:
            project_type: نوع المشروع (web, api, cli, etc.)
            technologies: قائمة التقنيات المستخدمة
        
        Returns:
            ProjectStructure مع قوائم الملفات والمجلدات
        """
        import asyncio
        
        # Run synchronous generate_project_structure in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.generate_project_structure,
            project_type,
            technologies
        )
    
    # === END ASYNC API METHODS ===
    
    def _attempt_recovery(
        self,
        failed_content: str,
        user_request: str,
        error_message: str,
        attempt: int
    ) -> Optional[str]:
        """
        Attempt to recover from parsing failure with a repair prompt
        
        Returns recovered content or None
        """
        recovery_prompt = f"""The previous response had an error: {error_message}

Original user request: {user_request}

Previous (invalid) response:
{failed_content[:500]}...

Please provide a CORRECTED response that follows ALL validation rules:
1. Valid JSON format (no markdown code blocks)
2. All required fields present
3. understanding: minimum 10 characters
4. project_type: one of [web, api, cli, script, data, mobile, desktop, other]
5. tasks: at least 1 task with id, title, description, dependencies
6. All task IDs must be unique and dependencies must reference existing tasks

Respond with ONLY the corrected JSON object:"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "assistant", "content": failed_content[:1000]},  # Show what failed
            {"role": "user", "content": recovery_prompt}
        ]
        
        try:
            response = self.ask_model(
                messages=messages,
                temperature=0.2,  # Lower temperature for more deterministic correction
                use_cache=False  # Don't cache recovery attempts
            )
            
            recovered_content = response.get("content", "")
            if recovered_content:
                logger.info("✓ Recovery prompt generated new response")
                return recovered_content
        
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
        
        return None
    
    def _parse_plan(self, content: str) -> Dict:
        """Parse JSON plan from model response"""
        # Try to extract JSON from markdown code blocks
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            content = content[json_start:json_end].strip()
        elif "```" in content:
            json_start = content.find("```") + 3
            json_end = content.find("```", json_start)
            content = content[json_start:json_end].strip()
        
        # Parse JSON
        plan = json.loads(content)
        
        return plan
    
    def _fallback_text_extraction(self, text: str, user_request: str) -> Optional[Dict]:
        """
        Fallback: Extract a basic plan from plain text when all parsing fails
        
        Returns a minimal valid plan structure
        """
        logger.info("Using fallback text extraction for plan generation")
        
        tasks = self._extract_tasks_from_text(text)
        
        # Create minimal valid plan
        fallback_plan = {
            "understanding": f"Project planning based on: {user_request[:100]}",
            "project_type": "other",
            "technologies": [],
            "tasks": tasks if tasks else [
                {
                    "id": 1,
                    "title": "Execute project",
                    "description": text[:200] if text else user_request,
                    "dependencies": []
                }
            ],
            "structure": {
                "files": [],
                "folders": []
            },
            "next_steps": ["Review and refine the plan", "Begin implementation"]
        }
        
        logger.warning(f"Fallback plan generated with {len(fallback_plan['tasks'])} tasks")
        
        return fallback_plan
    
    def _extract_tasks_from_text(self, text: str) -> List[Dict]:
        """Extract tasks from plain text response"""
        tasks = []
        lines = text.split("\n")
        
        task_id = 1
        for line in lines:
            line = line.strip()
            
            # Look for numbered lists
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                # Clean up line
                task_title = line.lstrip("0123456789.-* ").strip()
                
                if task_title:
                    tasks.append({
                        "id": task_id,
                        "title": task_title,
                        "description": task_title,
                        "dependencies": []
                    })
                    task_id += 1
        
        return tasks
    
    def analyze_request(self, user_request: str) -> Dict:
        """
        Quick analysis of user request without full planning
        
        Args:
            user_request: User's request
        
        Returns:
            Dict with request classification
        """
        messages = [
            {
                "role": "system",
                "content": "Classify this request in one word: web, api, cli, script, data, or other"
            },
            {"role": "user", "content": user_request}
        ]
        
        response = self.ask_model(messages, temperature=0.1, use_cache=True)
        project_type = response.get("content", "other").strip().lower()
        
        return {
            "project_type": project_type,
            "complexity": "simple" if len(user_request.split()) < 20 else "complex"
        }
    
    # ========== Extended Planning Methods (Phase 3) ==========
    
    def estimate_resources(self, tasks: List[Task]) -> ResourceEstimate:
        """
        تقدير الموارد المطلوبة بناءً على المهام
        
        Args:
            tasks: قائمة المهام
        
        Returns:
            تقدير الموارد
        """
        # Calculate total hours
        total_hours = sum(task.estimated_hours or 2.0 for task in tasks)
        
        # Complexity breakdown
        complexity_breakdown = {}
        for task in tasks:
            complexity = task.complexity.value if task.complexity else 'moderate'
            complexity_breakdown[complexity] = complexity_breakdown.get(complexity, 0) + 1
        
        # Calculate critical path (simplified - just longest dependency chain)
        critical_path = self._calculate_critical_path(tasks)
        
        # Estimate completion days (8h/day)
        completion_days = total_hours / 8.0
        
        # Recommend team size based on complexity
        complex_count = complexity_breakdown.get('complex', 0) + complexity_breakdown.get('very_complex', 0)
        team_size = min(1 + (complex_count // 3), 5)
        
        return ResourceEstimate(
            total_estimated_hours=total_hours,
            estimated_completion_days=completion_days,
            complexity_breakdown=complexity_breakdown,
            total_tasks=len(tasks),
            critical_path_hours=critical_path,
            recommended_team_size=team_size
        )
    
    def _calculate_critical_path(self, tasks: List[Task]) -> float:
        """Calculate critical path (longest dependency chain) in hours"""
        task_map = {task.id: task for task in tasks}
        
        def get_path_hours(task_id: int, visited: set) -> float:
            if task_id in visited:
                return 0
            
            task = task_map.get(task_id)
            if not task:
                return 0
            
            visited.add(task_id)
            task_hours = task.estimated_hours or 2.0
            
            if not task.dependencies:
                return task_hours
            
            # Get max of dependency paths
            dep_hours = max(
                (get_path_hours(dep_id, visited.copy()) for dep_id in task.dependencies),
                default=0
            )
            
            return task_hours + dep_hours
        
        # Find max path across all tasks
        return max(
            (get_path_hours(task.id, set()) for task in tasks),
            default=0
        )
    
    def generate_project_structure(self, project_type: str, technologies: List[str]) -> ProjectStructure:
        """
        توليد هيكل الملفات والمجلدات بناءً على نوع المشروع
        
        Args:
            project_type: نوع المشروع
            technologies: التقنيات المستخدمة
        
        Returns:
            هيكل المشروع
        """
        # Base files for all projects
        files = ['README.md']
        folders = []
        
        # Project type specific structure
        if project_type == 'web':
            files.extend(['index.html', 'styles.css', 'script.js'])
            folders.extend(['assets', 'css', 'js'])
        
        elif project_type == 'api':
            files.extend(['main.py', 'requirements.txt', '.env.example'])
            folders.extend(['api', 'models', 'tests'])
        
        elif project_type == 'cli':
            files.extend(['main.py', 'requirements.txt'])
            folders.extend(['src', 'tests'])
        
        elif project_type == 'script':
            files.extend(['script.py', 'requirements.txt', 'config.yaml'])
            folders.extend(['utils', 'logs'])
        
        elif project_type == 'data':
            files.extend(['analysis.py', 'requirements.txt', 'notebook.ipynb', '.env.example'])
            folders.extend(['data', 'notebooks', 'models', 'visualizations'])
        
        elif project_type == 'mobile':
            files.extend(['App.js', 'package.json', 'app.json', '.env.example'])
            folders.extend(['src', 'assets', 'components', 'screens', 'navigation'])
        
        elif project_type == 'desktop':
            files.extend(['main.py', 'requirements.txt', 'config.ini'])
            folders.extend(['src', 'resources', 'ui', 'assets'])
        
        else:
            # Default structure for 'other' or unrecognized types
            files.extend(['main.py' if 'python' in str(technologies).lower() else 'main.js'])
            folders.extend(['src', 'tests'])
        
        # Technology-specific additions
        if 'python' in [t.lower() for t in technologies]:
            if 'requirements.txt' not in files:
                files.append('requirements.txt')
            if 'tests' not in folders:
                folders.append('tests')
        
        if any(t.lower() in ['javascript', 'nodejs', 'react', 'vue'] for t in technologies):
            if 'package.json' not in files:
                files.append('package.json')
            if 'node_modules' not in folders:
                folders.append('node_modules')
        
        if 'react' in [t.lower() for t in technologies]:
            files.extend(['vite.config.js', 'index.html'])
            folders.extend(['src', 'public', 'src/components'])
        
        return ProjectStructure(
            files=list(set(files)),
            folders=list(set(folders))
        )


# Global instance
_planner_agent = None

def get_planner_agent() -> PlannerAgent:
    """Get global planner agent instance"""
    global _planner_agent
    if _planner_agent is None:
        _planner_agent = PlannerAgent()
    return _planner_agent
