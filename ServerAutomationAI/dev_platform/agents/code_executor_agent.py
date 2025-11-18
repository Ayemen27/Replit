"""
Code Executor Agent
Executes code, manages files, installs packages, generates code using AI
"""

from typing import Dict, List, Optional, Any
import logging
import asyncio
from pathlib import Path

from .base_agent import BaseAgent
from .schemas import (
    CodeArtifact, CodeGenerationRequest, CodeGenerationResult,
    ProjectStructure, DependencyConfig, ExecutionError, CodeFixRequest, CodeFixResult
)

logger = logging.getLogger(__name__)


class CodeExecutorAgent(BaseAgent):
    """
    Code Executor Agent
    
    Responsibilities:
    - Execute Python and Bash code
    - Read/Write/Delete files
    - Install and manage packages
    - Track execution history
    - Provide execution context
    """
    
    def __init__(self):
        super().__init__(
            agent_id="code_executor",
            name="Code Executor Agent",
            description="Executes code and manages files/packages",
            permission_level="execute"
        )
        
        # Execution history
        self.execution_history: List[Dict] = []
        
        # Code generation components
        self._code_generator = None
        self._dependency_manager = None
        
        # WorkflowStorage for artifact persistence
        from ..core.workflow_storage import WorkflowStorage
        self._storage = WorkflowStorage()
        
        # Load history from cache
        self._load_history()
    
    def _ensure_tools_loaded(self):
        """Lazy load code generation tools"""
        if not self._code_generator:
            from ..tools.code_generator import CodeGenerator
            # BaseAgent uses self.model as the ModelRouter instance
            self._code_generator = CodeGenerator(model_router=self.model)
        
        if not self._dependency_manager:
            from ..tools.dependency_manager import DependencyManager
            self._dependency_manager = DependencyManager()
    
    def _load_history(self):
        """Load execution history from cache"""
        history = self.cache.cache_get(f"executor_history_{self.agent_id}")
        if history:
            self.execution_history = history[-100:]  # Keep last 100
    
    def _save_history(self):
        """Save execution history to cache"""
        self.cache.cache_set(
            f"executor_history_{self.agent_id}",
            self.execution_history[-100:],
            expire=86400
        )
    
    def _add_to_history(self, entry: Dict):
        """Add entry to execution history"""
        self.execution_history.append(entry)
        self._save_history()
    
    def execute(self, request: Dict) -> Dict:
        """
        Execute code executor request
        
        Args:
            request: Dict with:
                - action: "execute_python", "execute_bash", "file_operation", "install_package"
                - Additional action-specific parameters
        
        Returns:
            Dict with 'success', 'result', and optional 'error'
        """
        try:
            action = request.get("action")
            
            if not action:
                return {
                    "success": False,
                    "error": "No action specified. Valid actions: execute_python, execute_bash, file_operation, install_package"
                }
            
            # Route to appropriate handler
            if action == "execute_python":
                return self.execute_python_code(request)
            elif action == "execute_bash":
                return self.execute_bash_command(request)
            elif action == "file_operation":
                return self.file_operation(request)
            elif action == "install_package":
                return self.install_package(request)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
        
        except Exception as e:
            logger.error(f"Error in CodeExecutorAgent.execute: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_python_code(self, request: Dict) -> Dict:
        """
        Execute Python code
        
        Args:
            request: Dict with 'code' and optional 'timeout'
        
        Returns:
            Execution result
        """
        code = request.get("code")
        timeout = request.get("timeout")
        
        if not code:
            return {"success": False, "error": "No code provided"}
        
        logger.info(f"Executing Python code ({len(code)} chars)")
        
        # Call execute_python tool
        result = self.call_tool(
            "execute_python",
            kwargs={"code": code, "timeout": timeout}
        )
        
        # Add to history
        self._add_to_history({
            "action": "execute_python",
            "code_length": len(code),
            "success": result.get("success"),
            "timestamp": self._get_timestamp()
        })
        
        return result
    
    def execute_bash_command(self, request: Dict) -> Dict:
        """
        Execute bash command
        
        Args:
            request: Dict with 'command', optional 'timeout', 'cwd'
        
        Returns:
            Execution result
        """
        command = request.get("command")
        timeout = request.get("timeout")
        cwd = request.get("cwd")
        
        if not command:
            return {"success": False, "error": "No command provided"}
        
        logger.info(f"Executing bash: {command[:100]}")
        
        # Call execute_bash tool
        result = self.call_tool(
            "execute_bash",
            kwargs={
                "command": command,
                "timeout": timeout,
                "cwd": cwd
            }
        )
        
        # Add to history
        self._add_to_history({
            "action": "execute_bash",
            "command": command[:100],
            "success": result.get("success"),
            "timestamp": self._get_timestamp()
        })
        
        return result
    
    def file_operation(self, request: Dict) -> Dict:
        """
        Perform file operation
        
        Args:
            request: Dict with:
                - operation: "read", "write", "list", "delete"
                - path: File/directory path
                - Additional operation-specific params
        
        Returns:
            Operation result
        """
        operation = request.get("operation")
        path = request.get("path")
        
        if not operation:
            return {"success": False, "error": "No operation specified"}
        
        if not path and operation != "list":
            return {"success": False, "error": "No path provided"}
        
        logger.info(f"File operation: {operation} on {path}")
        
        # Route to appropriate file tool
        if operation == "read":
            result = self.call_tool("read_file", kwargs={"path": path})
        
        elif operation == "write":
            content = request.get("content", "")
            create_dirs = request.get("create_dirs", True)
            result = self.call_tool(
                "write_file",
                kwargs={
                    "path": path,
                    "content": content,
                    "create_dirs": create_dirs
                }
            )
        
        elif operation == "list":
            directory = path or "."
            recursive = request.get("recursive", False)
            pattern = request.get("pattern")
            result = self.call_tool(
                "list_files",
                kwargs={
                    "directory": directory,
                    "recursive": recursive,
                    "pattern": pattern
                }
            )
        
        elif operation == "delete":
            result = self.call_tool("delete_file", kwargs={"path": path})
        
        else:
            return {
                "success": False,
                "error": f"Unknown file operation: {operation}"
            }
        
        # Add to history
        self._add_to_history({
            "action": f"file_{operation}",
            "path": path,
            "success": result.get("success"),
            "timestamp": self._get_timestamp()
        })
        
        return result
    
    def install_package(self, request: Dict) -> Dict:
        """
        Install package(s)
        
        Args:
            request: Dict with:
                - language: "python", "node", etc
                - packages: List of package names
                - save: Save to requirements/package.json
        
        Returns:
            Installation result
        """
        language = request.get("language")
        packages = request.get("packages", [])
        save = request.get("save", True)
        
        if not language:
            return {"success": False, "error": "No language specified"}
        
        if not packages:
            return {"success": False, "error": "No packages specified"}
        
        logger.info(f"Installing {len(packages)} {language} packages")
        
        # Call install_package tool
        result = self.call_tool(
            "install_package",
            kwargs={
                "language": language,
                "packages": packages,
                "save": save
            }
        )
        
        # Add to history
        self._add_to_history({
            "action": "install_package",
            "language": language,
            "packages": packages,
            "success": result.get("success"),
            "timestamp": self._get_timestamp()
        })
        
        return result
    
    def get_execution_history(self, limit: int = 20) -> List[Dict]:
        """
        Get recent execution history
        
        Args:
            limit: Number of recent entries
        
        Returns:
            List of execution history entries
        """
        return self.execution_history[-limit:]
    
    def clear_history(self):
        """Clear execution history"""
        self.execution_history = []
        self._save_history()
        logger.info("Execution history cleared")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    # ============================================================
    # Async Code Generation APIs (Phase 3.2)
    # ============================================================
    
    async def generate_code(
        self,
        request: CodeGenerationRequest
    ) -> CodeGenerationResult:
        """
        Generate code using AI based on task
        
        Args:
            request: CodeGenerationRequest with task and context
        
        Returns:
            CodeGenerationResult with generated artifacts
        """
        # Ensure tools are loaded BEFORE any operation
        self._ensure_tools_loaded()
        
        try:
            task = request.task
            context = request.project_context
            language = getattr(task, 'language', None) or "python"
            
            logger.info(f"Generating code for task: {task.title}")
            
            # Validate request
            if not task.title and not task.description:
                return CodeGenerationResult(
                    success=False,
                    errors=["Task must have either title or description"],
                    dependencies=None,
                    execution_time_seconds=0.0
                )
            
            # Generate code using AI
            if self._code_generator is None:
                raise RuntimeError("Code generator not initialized")
            
            result = await self._code_generator.generate_code(
                task_description=task.description or task.title,
                language=language,
                context=context,
                file_path=None
            )
            
            if not result.get("success"):
                return CodeGenerationResult(
                    success=False,
                    errors=[result.get("error", "Code generation failed")],
                    dependencies=None,
                    execution_time_seconds=0.0
                )
            
            # Create CodeArtifact
            from dev_platform.agents.schemas import CodeLanguage
            
            # Validate and convert language to CodeLanguage enum
            try:
                lang_enum = CodeLanguage(language)
            except ValueError:
                logger.warning(f"Unsupported language '{language}', falling back to Python")
                return CodeGenerationResult(
                    success=False,
                    errors=[f"Unsupported language: {language}. Supported: {', '.join([e.value for e in CodeLanguage])}"],
                    dependencies=None,
                    execution_time_seconds=0.0
                )
            
            artifact = CodeArtifact(
                language=lang_enum,
                file_path=result.get("file_path", "main.py"),
                content=result.get("code", ""),
                description=result.get("description", ""),
                dependencies=result.get("dependencies", []),
                task_id=task.id,
                is_entry_point=True
            )
            
            # Extract dependencies if any
            deps_config = None
            if result.get("dependencies") and self._dependency_manager:
                dep_result = self._dependency_manager.generate_dependency_file(
                    language=language,
                    dependencies=result["dependencies"],
                    project_name=context.get("project_name", "project")
                )
                
                if dep_result.get("success"):
                    deps_config = DependencyConfig(
                        language=language,
                        packages=result["dependencies"],
                        dev_packages=[],
                        config_file=dep_result["file_path"],
                        install_command=dep_result["install_command"]
                    )
            
            result_obj = CodeGenerationResult(
                success=True,
                artifacts=[artifact],
                dependencies=deps_config,
                files_created=[artifact.file_path],
                execution_time_seconds=0.0
            )
            
            # Persist artifact to WorkflowStorage
            await self._persist_artifact(
                artifact=artifact,
                task_id=task.id,
                operation="generate_code"
            )
            
            return result_obj
        
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return CodeGenerationResult(
                success=False,
                errors=[str(e)],
                dependencies=None,
                execution_time_seconds=0.0
            )
    
    async def create_file_structure(
        self,
        structure: ProjectStructure,
        base_path: str = ".",
        overwrite: bool = False,
        backup: bool = True
    ) -> Dict:
        """
        Create project file structure from ProjectStructure with conflict handling
        
        Args:
            structure: ProjectStructure with folders and files
            base_path: Base directory path
            overwrite: Whether to overwrite existing files
            backup: Whether to backup existing files before overwriting
        
        Returns:
            Dict with 'success', 'files_created', 'folders_created', 'conflicts', 'backups'
        """
        from pathlib import Path
        import shutil
        from datetime import datetime
        
        # Initialize tracking lists before try block
        files_created = []
        folders_created = []
        conflicts = []
        backups = []
        
        try:
            base = Path(base_path)
            rollback_needed = False
            
            logger.info(f"Creating file structure at {base_path} (overwrite={overwrite}, backup={backup})")
            
            # Track created items for rollback
            created_items = []
            
            try:
                # Create folders
                for folder in structure.folders:
                    folder_path = base / folder
                    if not folder_path.exists():
                        folder_path.mkdir(parents=True, exist_ok=True)
                        folders_created.append(str(folder_path))
                        created_items.append(('folder', folder_path))
                        logger.debug(f"Created folder: {folder_path}")
                    else:
                        logger.debug(f"Folder already exists: {folder_path}")
                
                # Create files
                for file_info in structure.files:
                    if isinstance(file_info, dict):
                        path_str: str = file_info.get("path", "")  # type: ignore
                        file_path = base / path_str
                        content = file_info.get("content", "")
                    else:
                        # Handle string paths
                        file_path = base / str(file_info)
                        content = ""
                    
                    # Ensure parent directory exists
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Check for conflicts
                    if file_path.exists():
                        conflicts.append(str(file_path))
                        
                        if not overwrite:
                            logger.warning(f"File already exists (skipping): {file_path}")
                            continue
                        
                        # Backup existing file
                        if backup:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            backup_path = file_path.parent / f"{file_path.name}.backup_{timestamp}"
                            shutil.copy2(file_path, backup_path)
                            backups.append(str(backup_path))
                            logger.debug(f"Backed up to: {backup_path}")
                    
                    # Write file
                    file_path.write_text(content, encoding='utf-8')
                    files_created.append(str(file_path))
                    created_items.append(('file', file_path))
                    logger.debug(f"Created file: {file_path}")
                
                result = {
                    "success": True,
                    "files_created": files_created,
                    "folders_created": folders_created,
                    "total_items": len(files_created) + len(folders_created),
                    "conflicts": conflicts,
                    "backups": backups,
                    "conflicts_count": len(conflicts)
                }
                
                # Persist metadata to WorkflowStorage
                await self._persist_operation_metadata(
                    operation="create_file_structure",
                    result=result,
                    parameters={"base_path": str(base_path), "overwrite": overwrite, "backup": backup}
                )
                
                return result
            
            except Exception as inner_e:
                rollback_needed = True
                raise inner_e
            
            finally:
                # Rollback on error if needed
                if rollback_needed:
                    logger.warning(f"Rolling back due to error - restoring {len(backups)} backups and removing {len(created_items)} created items")
                    
                    restoration_success = True
                    restored_files = []
                    
                    # First, restore backed up files with verification
                    for backup_path_str in backups:
                        try:
                            backup_path = Path(backup_path_str)
                            if backup_path.exists():
                                # Extract original path from backup (remove .backup_timestamp)
                                original_path = Path(str(backup_path).split('.backup_')[0])
                                
                                # Restore with verification
                                shutil.copy2(backup_path, original_path)
                                
                                # Verify restoration
                                if original_path.exists():
                                    restored_files.append(str(original_path))
                                    logger.debug(f"Restored backup: {backup_path} -> {original_path}")
                                else:
                                    logger.error(f"Backup restoration failed (file missing): {original_path}")
                                    restoration_success = False
                        except Exception as restore_error:
                            logger.error(f"Backup restoration error for {backup_path_str}: {restore_error}")
                            restoration_success = False
                    
                    # Only remove newly created items if ALL backups were restored successfully
                    if restoration_success or len(backups) == 0:
                        for item_type, item_path in reversed(created_items):
                            try:
                                if item_type == 'file' and item_path.exists():
                                    # Don't delete if it was restored from backup
                                    if str(item_path) not in restored_files:
                                        item_path.unlink()
                                        logger.debug(f"Rolled back file: {item_path}")
                                elif item_type == 'folder' and item_path.exists() and not list(item_path.iterdir()):
                                    item_path.rmdir()
                                    logger.debug(f"Rolled back empty folder: {item_path}")
                            except Exception as rollback_error:
                                logger.error(f"Rollback error for {item_path}: {rollback_error}")
                    else:
                        logger.error("Rollback incomplete - backup restoration failed, skipping deletion to preserve project state")
        
        except Exception as e:
            logger.error(f"Error creating file structure: {e}")
            return {
                "success": False,
                "error": str(e),
                "files_created": [],
                "folders_created": [],
                "conflicts": conflicts,
                "backups": backups
            }
    
    async def install_dependencies(
        self,
        dependencies: DependencyConfig,
        base_path: str = ".",
        auto_install: bool = False
    ) -> Dict:
        """
        Install dependencies and create config files
        
        NOTE: auto_install is disabled for security until sandbox implementation
        
        Args:
            dependencies: DependencyConfig with packages and install command
            base_path: Base directory path
            auto_install: Whether to automatically install packages (DISABLED - returns config only)
        
        Returns:
            Dict with installation result
        """
        # Ensure tools are loaded BEFORE any operation
        self._ensure_tools_loaded()
        
        try:
            from pathlib import Path
            
            if self._dependency_manager is None:
                raise RuntimeError("Dependency manager not initialized")
            
            base = Path(base_path)
            logger.info(f"Installing {dependencies.language} dependencies (auto_install={auto_install})")
            
            # Generate dependency file
            dep_result = self._dependency_manager.generate_dependency_file(
                language=dependencies.language,
                dependencies=dependencies.packages,
                dev_dependencies=dependencies.dev_packages
            )
            
            if not dep_result.get("success"):
                return {
                    "success": False,
                    "error": dep_result.get("error", "Failed to generate dependency file")
                }
            
            # Write dependency file
            config_file_path = base / dep_result["file_path"]
            config_file_path.parent.mkdir(parents=True, exist_ok=True)
            config_file_path.write_text(dep_result["content"], encoding='utf-8')
            
            logger.info(f"Created {dep_result['file_path']}")
            
            # Disable auto_install until sandbox implementation (Phase 3.2 security requirement)
            if auto_install:
                logger.warning("auto_install is disabled for security - dependencies configured but not installed")
                logger.info(f"To install manually, run: {dep_result['install_command']}")
            
            result = {
                "success": True,
                "config_file": str(config_file_path),
                "packages_count": len(dependencies.packages),
                "install_command": dep_result["install_command"],
                "installed": False,  # Always False until sandbox implementation
                "install_output": None,
                "message": f"Dependencies configured in {dep_result['file_path']}. Manual installation required."
            }
            
            # Persist metadata to WorkflowStorage
            await self._persist_operation_metadata(
                operation="install_dependencies",
                result=result,
                parameters={"language": dependencies.language, "packages": dependencies.packages}
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Error installing dependencies: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def apply_code_fixes(
        self,
        fix_request: CodeFixRequest
    ) -> CodeFixResult:
        """
        Apply AI-powered fixes to code with errors
        
        Args:
            fix_request: CodeFixRequest with artifact and errors
        
        Returns:
            CodeFixResult with fixed code
        """
        try:
            self._ensure_tools_loaded()
            
            artifact = fix_request.artifact
            errors = fix_request.errors
            max_attempts = fix_request.max_attempts
            
            logger.info(f"Applying fixes to {artifact.file_path} ({len(errors)} errors)")
            
            # Build fix prompt
            error_descriptions = "\n".join([
                f"- {err.error_type}: {err.message} (line {err.line_number or 'unknown'})"
                for err in errors
            ])
            
            fix_prompt = f"""Fix the following errors in this {artifact.language} code:

Original Code:
```{artifact.language}
{artifact.content}
```

Errors to fix:
{error_descriptions}

Instructions:
1. Fix all errors listed above
2. Preserve existing functionality
3. Follow best practices for {artifact.language}
4. Return ONLY the fixed code, no explanations

Fixed code:"""
            
            # Try to fix using AI (with retry logic)
            attempts = 0
            fixed_code = None
            
            if self._code_generator is None:
                raise RuntimeError("Code generator not initialized")
            
            while attempts < max_attempts and not fixed_code:
                attempts += 1
                
                result = await self._code_generator._call_model_async(fix_prompt)
                
                if result.get("success"):
                    fixed_code = self._code_generator._extract_code_from_response(
                        result["content"],
                        artifact.language
                    )
                else:
                    logger.warning(f"Fix attempt {attempts} failed")
            
            if not fixed_code:
                return CodeFixResult(
                    success=False,
                    fixed_artifact=artifact,
                    errors_remaining=errors,
                    fix_description="Failed to generate fix after all attempts",
                    attempts_used=attempts
                )
            
            # Create fixed artifact
            fixed_artifact = CodeArtifact(
                language=artifact.language,
                file_path=artifact.file_path,
                content=fixed_code,
                description=artifact.description,
                dependencies=artifact.dependencies,
                task_id=artifact.task_id,
                is_entry_point=artifact.is_entry_point
            )
            
            return CodeFixResult(
                success=True,
                fixed_artifact=fixed_artifact,
                errors_fixed=errors,
                errors_remaining=[],
                fix_description=f"Applied {len(errors)} fixes successfully",
                attempts_used=attempts
            )
        
        except Exception as e:
            logger.error(f"Error applying code fixes: {e}")
            return CodeFixResult(
                success=False,
                fixed_artifact=fix_request.artifact,
                errors_remaining=fix_request.errors,
                fix_description=f"Error: {str(e)}",
                attempts_used=1
            )
    
    async def _persist_artifact(
        self,
        artifact: "CodeArtifact",
        task_id: Optional[int] = None,
        operation: str = "unknown"
    ) -> str:
        """
        Persist generated artifact to WorkflowStorage
        
        Args:
            artifact: CodeArtifact to persist
            task_id: Task ID (optional)
            operation: Operation type (generate_code, apply_fix, etc.)
        
        Returns:
            workflow_id of persisted artifact
        """
        try:
            from datetime import datetime
            import uuid
            
            # Initialize storage if needed
            await self._storage.initialize_schema()
            
            # Create unique workflow entry for artifact (UUID to avoid collisions)
            workflow_id = f"artifact_{uuid.uuid4().hex[:8]}_{artifact.language.value}"
            
            workflow_data = {
                "workflow_id": workflow_id,
                "workflow_type": "code_generation",
                "status": "completed",
                "project_name": "code_executor",
                "user_request": f"{operation} for task {task_id}",
                "parameters": {
                    "task_id": task_id,
                    "language": artifact.language.value,
                    "file_path": artifact.file_path,
                    "operation": operation
                },
                "result": {
                    "artifact": {
                        "language": artifact.language.value,
                        "file_path": artifact.file_path,
                        "content": artifact.content,
                        "description": artifact.description,
                        "dependencies": artifact.dependencies,
                        "task_id": artifact.task_id,
                        "is_entry_point": artifact.is_entry_point
                    }
                },
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "current_step": 1,
                "total_steps": 1,
                "progress_percent": 100.0
            }
            
            await self._storage.save_workflow(workflow_data)
            logger.info(f"✓ Persisted artifact to WorkflowStorage: {workflow_id}")
            return workflow_id
        
        except Exception as e:
            logger.error(f"Failed to persist artifact: {e}")
            # Don't fail the operation if persistence fails
            return ""
    
    async def retrieve_artifact(self, workflow_id: str) -> Optional[Dict]:
        """
        Retrieve persisted artifact from WorkflowStorage
        
        Args:
            workflow_id: Workflow ID to retrieve
        
        Returns:
            Artifact dict or None
        """
        try:
            workflow = await self._storage.get_workflow(workflow_id)
            if workflow and workflow.get("result"):
                return workflow["result"].get("artifact")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve artifact: {e}")
            return None
    
    async def _persist_operation_metadata(
        self,
        operation: str,
        result: Dict,
        parameters: Optional[Dict] = None
    ) -> str:
        """
        Persist operation metadata to WorkflowStorage
        
        Args:
            operation: Operation name
            result: Operation result
            parameters: Operation parameters
        
        Returns:
            workflow_id of persisted metadata
        """
        try:
            from datetime import datetime
            import uuid
            
            # Initialize storage if needed
            await self._storage.initialize_schema()
            
            # Create unique workflow entry
            workflow_id = f"op_{uuid.uuid4().hex[:12]}_{operation}"
            
            workflow_data = {
                "workflow_id": workflow_id,
                "workflow_type": "code_execution",
                "status": "completed" if result.get("success") else "failed",
                "project_name": "code_executor",
                "user_request": f"{operation} operation",
                "parameters": parameters or {},
                "result": result,
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "current_step": 1,
                "total_steps": 1,
                "progress_percent": 100.0
            }
            
            await self._storage.save_workflow(workflow_data)
            logger.debug(f"✓ Persisted {operation} metadata: {workflow_id}")
            return workflow_id
        
        except Exception as e:
            logger.error(f"Failed to persist {operation} metadata: {e}")
            return ""
    
    def get_status(self) -> Dict:
        """
        Get current status
        
        Returns:
            Dict with agent status and stats
        """
        total_executions = len(self.execution_history)
        successful = sum(1 for e in self.execution_history if e.get("success"))
        failed = total_executions - successful
        
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state,
            "permission_level": self.permission_level,
            "stats": {
                "total_executions": total_executions,
                "successful": successful,
                "failed": failed,
                "success_rate": f"{(successful/total_executions*100):.1f}%" if total_executions > 0 else "N/A"
            },
            "recent_history": self.get_execution_history(5)
        }
