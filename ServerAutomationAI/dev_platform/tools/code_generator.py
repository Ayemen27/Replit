"""
Code Generation Tool
Generates code using AI models based on tasks and requirements
"""

import logging
from typing import Dict, List, Optional
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class CodeGenerator:
    """
    AI-powered code generation tool
    
    Features:
    - Generate code from task descriptions
    - Multi-language support (Python, JavaScript, HTML, CSS)
    - Template-based generation
    - Context-aware code generation
    - Best practices enforcement
    """
    
    def __init__(self, model_router=None):
        """
        Initialize code generator
        
        Args:
            model_router: ModelRouter instance for AI calls
        """
        self.model_router = model_router
        self.generation_history: List[Dict] = []
        
        # Language-specific templates and settings
        self.language_configs = {
            "python": {
                "extension": ".py",
                "comment_style": "#",
                "template_imports": [
                    "from typing import Dict, List, Optional, Any",
                    "import logging"
                ],
                "best_practices": [
                    "Use type hints",
                    "Add docstrings",
                    "Follow PEP 8",
                    "Handle errors properly"
                ]
            },
            "javascript": {
                "extension": ".js",
                "comment_style": "//",
                "template_imports": [],
                "best_practices": [
                    "Use const/let instead of var",
                    "Add JSDoc comments",
                    "Handle promises properly",
                    "Use async/await"
                ]
            },
            "html": {
                "extension": ".html",
                "comment_style": "<!--",
                "template_structure": "<!DOCTYPE html>",
                "best_practices": [
                    "Use semantic HTML5",
                    "Add accessibility attributes",
                    "Proper indentation"
                ]
            },
            "css": {
                "extension": ".css",
                "comment_style": "/*",
                "best_practices": [
                    "Use modern CSS features",
                    "Mobile-first approach",
                    "Proper naming conventions"
                ]
            }
        }
    
    async def generate_code(
        self,
        task_description: str,
        language: str,
        context: Optional[Dict] = None,
        file_path: Optional[str] = None
    ) -> Dict:
        """
        Generate code using AI based on task description
        
        Args:
            task_description: Description of what code should do
            language: Programming language (python, javascript, html, css)
            context: Additional context (project_type, technologies, etc.)
            file_path: Suggested file path
        
        Returns:
            Dict with 'success', 'code', 'file_path', 'dependencies', 'description'
        """
        try:
            if not self.model_router:
                return {
                    "success": False,
                    "error": "Model router not initialized"
                }
            
            language = language.lower()
            if language not in self.language_configs:
                return {
                    "success": False,
                    "error": f"Unsupported language: {language}. Supported: {', '.join(self.language_configs.keys())}"
                }
            
            # Build generation prompt
            prompt = self._build_generation_prompt(
                task_description,
                language,
                context or {}
            )
            
            logger.info(f"Generating {language} code for: {task_description[:100]}")
            
            # Call AI model
            result = await self._call_model_async(prompt)
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": result.get("error", "Code generation failed")
                }
            
            # Extract and validate code
            generated_code = result.get("content", "")
            code = self._extract_code_from_response(generated_code, language)
            
            # Generate file path if not provided
            if not file_path:
                file_path = self._suggest_file_path(task_description, language)
            
            # Extract dependencies
            dependencies = self._extract_dependencies(code, language)
            
            # Add to history
            self.generation_history.append({
                "task": task_description[:100],
                "language": language,
                "file_path": file_path,
                "success": True
            })
            
            return {
                "success": True,
                "code": code,
                "file_path": file_path,
                "language": language,
                "dependencies": dependencies,
                "description": task_description,
                "best_practices_applied": self.language_configs[language]["best_practices"]
            }
        
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_generation_prompt(
        self,
        task_description: str,
        language: str,
        context: Dict
    ) -> str:
        """Build AI prompt for code generation"""
        
        config = self.language_configs[language]
        best_practices = "\n".join(f"- {bp}" for bp in config["best_practices"])
        
        project_type = context.get("project_type", "general")
        technologies = context.get("technologies", [])
        
        prompt = f"""Generate {language.upper()} code for the following task:

Task Description: {task_description}

Project Type: {project_type}
Technologies: {', '.join(technologies) if technologies else 'None specified'}

Requirements:
{best_practices}

Instructions:
1. Generate clean, production-ready code
2. Include proper error handling
3. Add comments explaining complex logic
4. Follow best practices for {language}
5. Make the code modular and maintainable
6. Return ONLY the code, no explanations

Generate the code now:"""
        
        return prompt
    
    async def _call_model_async(self, prompt: str) -> Dict:
        """Call AI model asynchronously"""
        try:
            if not self.model_router:
                return {"success": False, "error": "Model router not initialized"}
            
            # Use model router's async method
            if hasattr(self.model_router, 'chat_async'):
                result = await self.model_router.chat_async(  # type: ignore
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
            else:
                # Fallback to sync if async not available
                result = self.model_router.chat(  # type: ignore
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
            
            return {
                "success": True,
                "content": result.get("content", ""),
                "tokens_used": result.get("tokens_used", 0)
            }
        
        except Exception as e:
            logger.error(f"Model call failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_code_from_response(self, response: str, language: str) -> str:
        """Extract code from AI response (remove markdown, explanations)"""
        
        # Remove markdown code blocks
        if "```" in response:
            parts = response.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Code block content
                    # Remove language identifier
                    lines = part.strip().split('\n')
                    if lines and lines[0].strip().lower() in ['python', 'javascript', 'js', 'html', 'css', language]:
                        lines = lines[1:]
                    return '\n'.join(lines).strip()
        
        # Return as-is if no markdown
        return response.strip()
    
    def _suggest_file_path(self, task_description: str, language: str) -> str:
        """Suggest a file path based on task description"""
        
        config = self.language_configs[language]
        extension = config["extension"]
        
        # Generate filename from task
        words = task_description.lower().split()[:3]
        filename = '_'.join(w for w in words if w.isalnum())
        
        # Default paths per language
        if language == "python":
            return f"src/{filename}{extension}"
        elif language in ["javascript", "typescript"]:
            return f"src/{filename}{extension}"
        elif language == "html":
            return f"public/{filename}{extension}"
        elif language == "css":
            return f"public/css/{filename}{extension}"
        
        return f"{filename}{extension}"
    
    def _extract_dependencies(self, code: str, language: str) -> List[str]:
        """Extract dependencies from code"""
        
        dependencies = []
        
        if language == "python":
            # Extract imports
            for line in code.split('\n'):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    # Extract package name
                    if 'import ' in line:
                        parts = line.split('import ')
                        if len(parts) > 1:
                            pkg = parts[1].split()[0].split('.')[0]
                            if pkg not in ['typing', 'os', 'sys', 'json', 'logging']:
                                dependencies.append(pkg)
        
        elif language == "javascript":
            # Extract require/import statements
            for line in code.split('\n'):
                line = line.strip()
                if 'require(' in line or 'from ' in line:
                    # Extract package name
                    if "'" in line:
                        parts = line.split("'")
                        if len(parts) > 1:
                            pkg = parts[1]
                            if not pkg.startswith('.'):
                                dependencies.append(pkg)
        
        return list(set(dependencies))
    
    async def generate_multiple_files(
        self,
        tasks: List[Dict],
        context: Dict
    ) -> Dict:
        """
        Generate multiple code files from multiple tasks
        
        Args:
            tasks: List of task dictionaries with 'description', 'language', 'file_path'
            context: Project context
        
        Returns:
            Dict with 'success', 'artifacts', 'failed_tasks'
        """
        artifacts = []
        failed_tasks = []
        
        for task in tasks:
            result = await self.generate_code(
                task_description=task.get("description", ""),
                language=task.get("language", "python"),
                context=context,
                file_path=task.get("file_path")
            )
            
            if result.get("success"):
                artifacts.append(result)
            else:
                failed_tasks.append({
                    "task": task,
                    "error": result.get("error")
                })
        
        return {
            "success": len(failed_tasks) == 0,
            "artifacts": artifacts,
            "failed_tasks": failed_tasks,
            "total_generated": len(artifacts),
            "total_failed": len(failed_tasks)
        }
    
    def get_generation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent generation history"""
        return self.generation_history[-limit:]
    
    def clear_history(self):
        """Clear generation history"""
        self.generation_history = []


# Helper function for direct usage
async def generate_code_from_task(
    task: Dict,
    model_router,
    context: Optional[Dict] = None
) -> Dict:
    """
    Convenience function to generate code from a task
    
    Args:
        task: Task dictionary with 'description', 'title', etc.
        model_router: ModelRouter instance
        context: Additional context
    
    Returns:
        Generation result dictionary
    """
    generator = CodeGenerator(model_router=model_router)
    
    # Extract info from task
    description = task.get("description", task.get("title", ""))
    language = task.get("language", "python")
    
    return await generator.generate_code(
        task_description=description,
        language=language,
        context=context
    )
