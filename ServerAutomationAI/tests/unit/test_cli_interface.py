"""
Tests for CLI/TUI Interface
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from textual.pilot import Pilot
from rich.text import Text

from dev_platform.cli_interface import (
    DeveloperCLI,
    MainMenuScreen,
    WorkflowScreen,
    StatusScreen,
    HistoryScreen,
    run_simple_cli
)
from dev_platform.agents.schemas import WorkflowType, WorkflowStatus
from dev_platform.agents.ops_coordinator_agent import OpsCoordinatorAgent


def get_widget_text(widget) -> str:
    """Extract plain text from Textual widget"""
    try:
        # Try to render the widget
        rendered = widget.render()
        
        # If it's a Rich Text object, convert to plain string
        if isinstance(rendered, Text):
            return str(rendered.plain)
        
        # Otherwise, return string representation
        return str(rendered)
    except Exception:
        # Fallback to string representation
        return str(widget)


class TestDeveloperCLI:
    """Test DeveloperCLI app"""
    
    @pytest.mark.asyncio
    async def test_app_initializes(self):
        """Test that the app initializes properly"""
        app = DeveloperCLI()
        assert app is not None
        assert hasattr(app, 'coordinator')
        assert isinstance(app.coordinator, OpsCoordinatorAgent)
    
    @pytest.mark.asyncio
    async def test_app_mounts_main_menu(self):
        """Test that app shows main menu on mount"""
        app = DeveloperCLI()
        async with app.run_test() as pilot:
            await pilot.pause()
            assert len(app.screen_stack) > 0
    
    @pytest.mark.asyncio
    async def test_app_title_set(self):
        """Test that app title is set correctly"""
        app = DeveloperCLI()
        async with app.run_test() as pilot:
            await pilot.pause()
            assert app.title == "لوحة تحكم بالذكاء الاصطناعي"
            assert app.sub_title == "المرحلة 2أ: واجهة المطور"


class TestMainMenuScreen:
    """Test MainMenuScreen"""
    
    @pytest.mark.asyncio
    async def test_main_menu_renders(self):
        """Test that main menu renders properly"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            await pilot.pause()
            
            app_title = app.screen.query_one("#app-title")
            assert app_title is not None
            assert "لوحة تحكم" in get_widget_text(app_title)
    
    @pytest.mark.asyncio
    async def test_main_menu_bindings(self):
        """Test main menu key bindings"""
        app = DeveloperCLI()
        screen = MainMenuScreen(app.coordinator)
        
        bindings = [b.key for b in screen.BINDINGS]
        assert "q" in bindings
        assert "1" in bindings
        assert "2" in bindings
        assert "3" in bindings
        assert "4" in bindings
        assert "s" in bindings
        assert "h" in bindings
    
    @pytest.mark.asyncio
    async def test_delivery_action_pushes_workflow_screen(self):
        """Test that delivery action pushes workflow screen"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            await pilot.pause()
            
            screen = app.screen
            initial_stack_size = len(app.screen_stack)
            
            screen.action_delivery()
            await pilot.pause()
            
            assert len(app.screen_stack) > initial_stack_size
    
    @pytest.mark.asyncio
    async def test_status_action_pushes_status_screen(self):
        """Test that status action pushes status screen"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            await pilot.pause()
            
            screen = app.screen
            initial_stack_size = len(app.screen_stack)
            
            screen.action_status()
            await pilot.pause()
            
            assert len(app.screen_stack) > initial_stack_size
    
    @pytest.mark.asyncio
    async def test_history_action_pushes_history_screen(self):
        """Test that history action pushes history screen"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            await pilot.pause()
            
            screen = app.screen
            initial_stack_size = len(app.screen_stack)
            
            screen.action_history()
            await pilot.pause()
            
            assert len(app.screen_stack) > initial_stack_size


class TestWorkflowScreen:
    """Test WorkflowScreen"""
    
    @pytest.mark.asyncio
    async def test_workflow_screen_initializes(self):
        """Test workflow screen initialization"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        screen = WorkflowScreen(WorkflowType.DELIVERY_PIPELINE, coordinator)
        
        assert screen.workflow_type == WorkflowType.DELIVERY_PIPELINE
        assert screen.coordinator is coordinator
        assert screen.workflow_id is None
    
    @pytest.mark.asyncio
    async def test_workflow_screen_description(self):
        """Test workflow descriptions"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        
        delivery = WorkflowScreen(WorkflowType.DELIVERY_PIPELINE, coordinator)
        assert "التخطيط" in delivery._get_workflow_description()
        assert "التنفيذ" in delivery._get_workflow_description()
        
        regression = WorkflowScreen(WorkflowType.REGRESSION, coordinator)
        assert "الانحدار" in regression._get_workflow_description()
        
        maintenance = WorkflowScreen(WorkflowType.MAINTENANCE, coordinator)
        assert "الصيانة" in maintenance._get_workflow_description().lower() or "فحوصات" in maintenance._get_workflow_description()
        
        custom = WorkflowScreen(WorkflowType.CUSTOM, coordinator)
        assert "مخصص" in custom._get_workflow_description()
    
    @pytest.mark.asyncio
    async def test_workflow_screen_renders(self):
        """Test workflow screen renders properly"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            app.push_screen(WorkflowScreen(WorkflowType.DELIVERY_PIPELINE, coordinator))
            await pilot.pause()
            
            title = app.screen.query_one("#workflow-title")
            assert title is not None
            assert "delivery_pipeline" in get_widget_text(title).lower()
    
    @pytest.mark.asyncio
    async def test_start_workflow_button_exists(self):
        """Test that start workflow button exists"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            app.push_screen(WorkflowScreen(WorkflowType.DELIVERY_PIPELINE, coordinator))
            await pilot.pause()
            
            button = app.screen.query_one("#start-workflow")
            assert button is not None
    
    @pytest.mark.asyncio
    async def test_workflow_screen_back_action(self):
        """Test back action pops screen"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            initial_stack_size = len(app.screen_stack)
            app.push_screen(WorkflowScreen(WorkflowType.DELIVERY_PIPELINE, coordinator))
            await pilot.pause()
            
            assert len(app.screen_stack) > initial_stack_size
            
            current_screen = app.screen
            current_screen.action_back()
            await pilot.pause()
            
            assert len(app.screen_stack) == initial_stack_size


class TestStatusScreen:
    """Test StatusScreen"""
    
    @pytest.mark.asyncio
    async def test_status_screen_initializes(self):
        """Test status screen initialization"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        screen = StatusScreen(coordinator)
        
        assert screen.coordinator is coordinator
    
    @pytest.mark.asyncio
    async def test_status_screen_renders(self):
        """Test status screen renders"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            app.push_screen(StatusScreen(coordinator))
            await pilot.pause()
            
            title = app.screen.query_one("#status-title")
            assert title is not None
            assert "حالة" in get_widget_text(title)
    
    @pytest.mark.asyncio
    async def test_status_display_no_workflows(self):
        """Test status display with no active workflows"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        screen = StatusScreen(coordinator)
        
        status = screen._get_status_display()
        assert "لا يوجد سير عمل نشط" in status
    
    @pytest.mark.asyncio
    async def test_status_refresh_button_exists(self):
        """Test refresh button exists"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            app.push_screen(StatusScreen(coordinator))
            await pilot.pause()
            
            button = app.screen.query_one("#refresh-btn")
            assert button is not None
    
    @pytest.mark.asyncio
    async def test_status_screen_back_action(self):
        """Test back action pops screen"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            initial_stack_size = len(app.screen_stack)
            app.push_screen(StatusScreen(coordinator))
            await pilot.pause()
            
            assert len(app.screen_stack) > initial_stack_size
            
            current_screen = app.screen
            current_screen.action_back()
            await pilot.pause()
            
            assert len(app.screen_stack) == initial_stack_size


class TestHistoryScreen:
    """Test HistoryScreen"""
    
    @pytest.mark.asyncio
    async def test_history_screen_initializes(self):
        """Test history screen initialization"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        screen = HistoryScreen(coordinator)
        
        assert screen.coordinator is coordinator
    
    @pytest.mark.asyncio
    async def test_history_screen_renders(self):
        """Test history screen renders"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            app.push_screen(HistoryScreen(coordinator))
            await pilot.pause()
            
            title = app.screen.query_one("#history-title")
            assert title is not None
            assert "سجل" in get_widget_text(title)
    
    @pytest.mark.asyncio
    async def test_history_display_no_history(self):
        """Test history display with no history"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        screen = HistoryScreen(coordinator)
        
        history = screen._get_history_display()
        assert "لا يوجد سجل سير عمل" in history
    
    @pytest.mark.asyncio
    async def test_history_screen_back_action(self):
        """Test back action pops screen"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            initial_stack_size = len(app.screen_stack)
            app.push_screen(HistoryScreen(coordinator))
            await pilot.pause()
            
            assert len(app.screen_stack) > initial_stack_size
            
            current_screen = app.screen
            current_screen.action_back()
            await pilot.pause()
            
            assert len(app.screen_stack) == initial_stack_size


class TestSimpleCLI:
    """Test simple CLI (Rich-based)"""
    
    @patch('dev_platform.cli_interface.Console')
    def test_run_simple_cli_executes(self, mock_console):
        """Test that simple CLI runs without errors"""
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance
        
        run_simple_cli()
        
        assert mock_console_instance.print.called
        call_args = [str(call) for call in mock_console_instance.print.call_args_list]
        
        found_workflows = any("سير العمل المتاحة" in str(call) for call in call_args)
        assert found_workflows
    
    @patch('dev_platform.cli_interface.Console')
    def test_simple_cli_shows_coordinator_status(self, mock_console):
        """Test simple CLI shows coordinator status"""
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance
        
        run_simple_cli()
        
        assert mock_console_instance.print.called
        call_args = [str(call) for call in mock_console_instance.print.call_args_list]
        
        found_active = any("سير العمل النشط" in str(call) for call in call_args)
        found_history = any("السجل الأخير" in str(call) for call in call_args)
        
        assert found_active
        assert found_history


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_navigation_flow(self):
        """Test navigating through all screens"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            await pilot.pause()
            
            screen = app.screen
            initial_stack = len(app.screen_stack)
            
            screen.action_delivery()
            await pilot.pause()
            assert len(app.screen_stack) == initial_stack + 1
            
            app.pop_screen()
            await pilot.pause()
            assert len(app.screen_stack) == initial_stack
            
            screen.action_status()
            await pilot.pause()
            assert len(app.screen_stack) == initial_stack + 1
            
            app.pop_screen()
            await pilot.pause()
            assert len(app.screen_stack) == initial_stack
            
            screen.action_history()
            await pilot.pause()
            assert len(app.screen_stack) == initial_stack + 1
    
    @pytest.mark.asyncio
    async def test_workflow_types_all_accessible(self):
        """Test all workflow types are accessible"""
        coordinator = OpsCoordinatorAgent(dry_run=True)
        app = DeveloperCLI()
        app.coordinator = coordinator
        
        async with app.run_test() as pilot:
            screen = app.screen
            
            for workflow_type in [
                WorkflowType.DELIVERY_PIPELINE,
                WorkflowType.REGRESSION,
                WorkflowType.MAINTENANCE,
                WorkflowType.CUSTOM
            ]:
                wf_screen = WorkflowScreen(workflow_type, coordinator)
                assert wf_screen._get_workflow_description()
                assert len(wf_screen._get_workflow_description()) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
