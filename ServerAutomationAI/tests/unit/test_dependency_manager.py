"""
Unit Tests for Dependency Manager
Tests dependency extraction, analysis, and config generation
"""

import pytest
import json

from dev_platform.tools.dependency_manager import DependencyManager, create_dependency_config


class TestDependencyManager:
    """Test suite for DependencyManager"""
    
    @pytest.fixture
    def manager(self):
        """Create DependencyManager instance"""
        return DependencyManager()
    
    def test_init(self, manager):
        """Test initialization"""
        assert manager.analyzed_dependencies == {}
        assert "python" in manager.language_configs
        assert "javascript" in manager.language_configs
    
    def test_language_configs(self, manager):
        """Test language configurations"""
        # Python
        py_config = manager.language_configs["python"]
        assert py_config["config_file"] == "requirements.txt"
        assert py_config["package_manager"] == "pip"
        
        # JavaScript
        js_config = manager.language_configs["javascript"]
        assert js_config["config_file"] == "package.json"
        assert js_config["package_manager"] == "npm"
    
    def test_extract_dependencies_python(self, manager):
        """Test Python dependency extraction"""
        code = """
import requests
from flask import Flask, jsonify
import json
import os
from sqlalchemy import create_engine
"""
        result = manager.extract_dependencies_from_code(code, "python")
        
        assert result["success"] is True
        assert "requests" in result["dependencies"]
        assert "flask" in result["dependencies"]
        assert "sqlalchemy" in result["dependencies"]
        assert "json" in result["standard_imports"]
        assert "os" in result["standard_imports"]
    
    def test_extract_dependencies_javascript(self, manager):
        """Test JavaScript dependency extraction"""
        code = """
const express = require('express');
import React from 'react';
const fs = require('fs');
import axios from 'axios';
"""
        result = manager.extract_dependencies_from_code(code, "javascript")
        
        assert result["success"] is True
        assert "express" in result["dependencies"]
        assert "react" in result["dependencies"]
        assert "axios" in result["dependencies"]
        assert "fs" in result["standard_imports"]
    
    def test_extract_dependencies_unsupported_language(self, manager):
        """Test unsupported language"""
        result = manager.extract_dependencies_from_code("code", "ruby")
        assert result["success"] is False
    
    def test_generate_requirements_txt(self, manager):
        """Test requirements.txt generation"""
        deps = ["flask", "requests", "pytest"]
        content = manager._generate_requirements_txt(deps)
        
        assert "flask" in content
        assert "requests" in content
        assert "pytest" in content
        assert content.endswith('\n')
    
    def test_generate_requirements_txt_with_versions(self, manager):
        """Test requirements.txt with version hints"""
        deps = ["flask", "fastapi", "custom-package"]
        content = manager._generate_requirements_txt(deps)
        
        assert "flask>=" in content  # Has version hint
        assert "fastapi>=" in content  # Has version hint
        assert "custom-package\n" in content  # No version hint
    
    def test_generate_package_json(self, manager):
        """Test package.json generation"""
        content = manager._generate_package_json(
            name="test-project",
            version="1.0.0",
            dependencies=["express", "react"],
            dev_dependencies=["jest", "eslint"]
        )
        
        pkg = json.loads(content)
        assert pkg["name"] == "test-project"
        assert pkg["version"] == "1.0.0"
        assert "express" in pkg["dependencies"]
        assert "react" in pkg["dependencies"]
        assert "jest" in pkg["devDependencies"]
        assert "eslint" in pkg["devDependencies"]
    
    def test_generate_dependency_file_python(self, manager):
        """Test Python dependency file generation"""
        result = manager.generate_dependency_file(
            language="python",
            dependencies=["flask", "requests"],
            project_name="test-app"
        )
        
        assert result["success"] is True
        assert result["file_path"] == "requirements.txt"
        assert "flask" in result["content"]
        assert "requests" in result["content"]
        assert result["dependencies_count"] == 2
    
    def test_generate_dependency_file_javascript(self, manager):
        """Test JavaScript dependency file generation"""
        result = manager.generate_dependency_file(
            language="javascript",
            dependencies=["express", "axios"],
            dev_dependencies=["jest"],
            project_name="my-app",
            version="2.0.0"
        )
        
        assert result["success"] is True
        assert result["file_path"] == "package.json"
        pkg = json.loads(result["content"])
        assert pkg["name"] == "my-app"
        assert pkg["version"] == "2.0.0"
        assert "express" in pkg["dependencies"]
        assert "jest" in pkg["devDependencies"]
    
    def test_analyze_dependencies_from_files(self, manager):
        """Test dependency analysis across multiple files"""
        artifacts = [
            {
                "file_path": "main.py",
                "content": "import flask\nimport requests"
            },
            {
                "file_path": "utils.py",
                "content": "import requests\nimport sqlalchemy"
            }
        ]
        
        result = manager.analyze_dependencies_from_files(artifacts, "python")
        
        assert result["success"] is True
        assert "flask" in result["all_dependencies"]
        assert "requests" in result["all_dependencies"]
        assert "sqlalchemy" in result["all_dependencies"]
        assert result["total_dependencies"] == 3
        assert result["files_analyzed"] == 2
    
    def test_suggest_dev_dependencies_python_web(self, manager):
        """Test Python web project dev dependencies"""
        deps = manager.suggest_dev_dependencies("python", "web")
        assert "pytest" in deps
        assert "black" in deps
    
    def test_suggest_dev_dependencies_javascript_api(self, manager):
        """Test JavaScript API project dev dependencies"""
        deps = manager.suggest_dev_dependencies("javascript", "api")
        assert "jest" in deps
        assert "eslint" in deps
        assert "nodemon" in deps
    
    def test_suggest_dev_dependencies_unsupported(self, manager):
        """Test unsupported language returns empty list"""
        deps = manager.suggest_dev_dependencies("rust", "cli")
        assert deps == []
    
    def test_resolve_conflicts_python(self, manager):
        """Test conflict detection"""
        result = manager.resolve_conflicts(["asyncio", "twisted"], "python")
        
        assert result["success"] is True
        # Should detect conflict between asyncio and twisted
    
    def test_get_install_instructions_python(self, manager):
        """Test Python install instructions"""
        result = manager.get_install_instructions("python", use_virtual_env=True)
        
        assert result["success"] is True
        assert "venv" in result["steps"][0]
        assert "pip install" in result["steps"][-1]
        assert result["config_file"] == "requirements.txt"
    
    def test_get_install_instructions_javascript(self, manager):
        """Test JavaScript install instructions"""
        result = manager.get_install_instructions("javascript", use_virtual_env=False)
        
        assert result["success"] is True
        assert "npm install" in result["steps"][0]
        assert result["config_file"] == "package.json"
    
    def test_get_install_instructions_unsupported(self, manager):
        """Test unsupported language"""
        result = manager.get_install_instructions("golang")
        assert result["success"] is False


def test_create_dependency_config_helper():
    """Test helper function"""
    result = create_dependency_config(
        language="python",
        packages=["flask", "requests"],
        project_name="test"
    )
    
    assert result["success"] is True
    assert "flask" in result["content"]
