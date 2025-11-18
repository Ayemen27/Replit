"""
Interactive CLI/TUI Interface for Developer Platform
Built with Textual for rich terminal experience
"""

from typing import Optional
from datetime import datetime
import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static, Label, ProgressBar, ListItem, ListView
from textual.screen import Screen
from textual.binding import Binding
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import logging

from dev_platform.agents.ops_coordinator_agent import OpsCoordinatorAgent
from dev_platform.agents.schemas import WorkflowType, WorkflowStatus

logger = logging.getLogger(__name__)


class WorkflowScreen(Screen):
    """شاشة اختيار وتشغيل سير العمل"""
    
    BINDINGS = [
        Binding("q", "quit", "خروج"),
        Binding("escape", "back", "العودة للقائمة"),
        Binding("c", "cancel_workflow", "إلغاء سير العمل", show=False),
    ]
    
    def __init__(self, workflow_type: WorkflowType, coordinator: OpsCoordinatorAgent):
        super().__init__()
        self.workflow_type = workflow_type
        self.coordinator = coordinator
        self.workflow_id: Optional[str] = None
        self._is_running = False
        self._stream_worker = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label(f"سير العمل: {self.workflow_type.value}", id="workflow-title"),
            Static(self._get_workflow_description(), id="workflow-description"),
            Horizontal(
                Button("بدء التشغيل", id="start-workflow", variant="primary"),
                Button("إلغاء", id="cancel-workflow", variant="error", disabled=True),
                id="button-row"
            ),
            ProgressBar(id="progress-bar", total=100, show_eta=False),
            Static("", id="workflow-status"),
            Static("", id="workflow-output"),
            id="workflow-container"
        )
        yield Footer()
    
    def _get_workflow_description(self) -> str:
        """الحصول على وصف سير العمل"""
        descriptions = {
            WorkflowType.DELIVERY_PIPELINE: "خط التسليم الكامل: التخطيط ← التنفيذ ← ضمان الجودة ← التقرير",
            WorkflowType.REGRESSION: "اختبار الانحدار: فشل ضمان الجودة ← إعادة الإنتاج ← حلقة التغذية الراجعة",
            WorkflowType.MAINTENANCE: "صيانة النظام: فحوصات الصحة ← فحص التبعيات ← تحليل الجودة",
            WorkflowType.CUSTOM: "سير عمل مخصص مع أوامر محددة من المستخدم"
        }
        return descriptions.get(self.workflow_type, "سير عمل غير معروف")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press"""
        if event.button.id == "start-workflow":
            if not self._is_running:
                self.run_worker(self._start_workflow_async())
        elif event.button.id == "cancel-workflow":
            if self._is_running:
                self.run_worker(self._handle_cancel())
    
    async def _start_workflow_async(self) -> None:
        """Start the selected workflow asynchronously using unified async API"""
        try:
            status_widget = self.query_one("#workflow-status", Static)
            start_btn = self.query_one("#start-workflow", Button)
            cancel_btn = self.query_one("#cancel-workflow", Button)
            
            status_widget.update("🚀 جاري تهيئة سير العمل...")
            
            # Use unified async method (combines create + execute)
            self.workflow_id = await self.coordinator.start_and_execute_workflow_async(
                workflow_type=self.workflow_type,
                project_name="cli_project",
                user_request="سير عمل بدأ من CLI/TUI",
                parameters={},
                auto_execute=True
            )
            
            status_widget.update(f"🚀 جاري تنفيذ سير العمل {self.workflow_id}...")
            
            # Update UI state
            self._is_running = True
            start_btn.disabled = True
            cancel_btn.disabled = False
            
            # Start streaming progress
            self._stream_worker = self.run_worker(self._stream_progress_updates())
        
        except Exception as e:
            logger.error(f"خطأ في بدء سير العمل: {e}", exc_info=True)
            status_widget = self.query_one("#workflow-status", Static)
            status_widget.update(f"❌ خطأ: {str(e)}")
    
    async def _stream_progress_updates(self) -> None:
        """بث تحديثات التقدم في الوقت الفعلي من سير العمل"""
        try:
            if not self.workflow_id:
                return
            
            progress_bar = self.query_one("#progress-bar", ProgressBar)
            status_widget = self.query_one("#workflow-status", Static)
            output_widget = self.query_one("#workflow-output", Static)
            
            output_lines = []
            
            async for update in self.coordinator.get_progress_stream(self.workflow_id):
                # Update progress bar
                if "progress_percent" in update:
                    progress_bar.update(progress=update["progress_percent"])
                
                # Update status message
                if "message" in update:
                    message = update["message"]
                    output_lines.append(f"• {message}")
                    output_widget.update("\n".join(output_lines[-10:]))  # Show last 10 lines
                
                # Update status based on workflow state
                if "status" in update:
                    status_text = update["status"]
                    
                    if status_text == WorkflowStatus.COMPLETED.value:
                        status_widget.update(f"✅ اكتمل سير العمل بنجاح")
                        self._cleanup_after_completion()
                        break
                    elif status_text == WorkflowStatus.FAILED.value:
                        error = update.get("error", "خطأ غير معروف")
                        status_widget.update(f"❌ فشل سير العمل: {error}")
                        self._cleanup_after_completion()
                        break
                    elif status_text == WorkflowStatus.CANCELLED.value:
                        status_widget.update(f"🚫 تم إلغاء سير العمل")
                        self._cleanup_after_completion()
                        break
                    elif status_text == WorkflowStatus.RUNNING.value:
                        status_widget.update(f"🔄 سير العمل قيد التشغيل...")
        
        except asyncio.CancelledError:
            logger.info("تم إلغاء بث التقدم")
        except Exception as e:
            logger.error(f"خطأ في بث التقدم: {e}", exc_info=True)
            status_widget = self.query_one("#workflow-status", Static)
            status_widget.update(f"❌ خطأ في البث: {str(e)}")
            self._cleanup_after_completion()
    
    async def _handle_cancel(self) -> None:
        """معالجة إلغاء سير العمل"""
        try:
            if not self.workflow_id:
                return
            
            status_widget = self.query_one("#workflow-status", Static)
            status_widget.update("🚫 جاري إلغاء سير العمل...")
            
            # Cancel async workflow
            success = await self.coordinator.cancel_workflow_async(self.workflow_id)
            
            if success:
                status_widget.update("🚫 تم إلغاء سير العمل")
            else:
                status_widget.update("⚠️ فشل إلغاء سير العمل")
            
            self._cleanup_after_completion()
        
        except Exception as e:
            logger.error(f"خطأ في إلغاء سير العمل: {e}", exc_info=True)
            status_widget = self.query_one("#workflow-status", Static)
            status_widget.update(f"❌ خطأ في الإلغاء: {str(e)}")
    
    def _cleanup_after_completion(self) -> None:
        """تنظيف حالة الواجهة بعد اكتمال/فشل/إلغاء سير العمل"""
        try:
            self._is_running = False
            start_btn = self.query_one("#start-workflow", Button)
            cancel_btn = self.query_one("#cancel-workflow", Button)
            start_btn.disabled = False
            cancel_btn.disabled = True
        except Exception as e:
            logger.error(f"خطأ في التنظيف: {e}")
    
    def action_cancel_workflow(self) -> None:
        """إجراء إلغاء سير العمل (مفتاح 'c')"""
        if self._is_running:
            self.run_worker(self._handle_cancel())
    
    def _format_workflow_steps(self, steps: list) -> str:
        """تنسيق خطوات سير العمل للعرض"""
        if not steps:
            return ""
        
        output = "\n📋 خطوات سير العمل:\n\n"
        for i, step in enumerate(steps, 1):
            title = step.get("title", f"خطوة {i}")
            description = step.get("description", "")
            status = step.get("status", "pending")
            
            status_icon = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✅",
                "failed": "❌"
            }.get(status, "⏳")
            
            output += f"{i}. {status_icon} {title}\n"
            if description:
                output += f"   {description}\n"
        
        return output
    
    def action_back(self) -> None:
        """العودة إلى القائمة الرئيسية"""
        self.app.pop_screen()


class MainMenuScreen(Screen):
    """شاشة القائمة الرئيسية لاختيار سير العمل"""
    
    BINDINGS = [
        Binding("q", "quit", "خروج"),
        Binding("1", "delivery", "خط التسليم"),
        Binding("2", "regression", "اختبار الانحدار"),
        Binding("3", "maintenance", "الصيانة"),
        Binding("4", "custom", "سير عمل مخصص"),
        Binding("s", "status", "عرض الحالة"),
        Binding("h", "history", "عرض السجل"),
    ]
    
    def __init__(self, coordinator: OpsCoordinatorAgent):
        super().__init__()
        self.coordinator = coordinator
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("🤖 لوحة تحكم بالذكاء الاصطناعي", id="app-title"),
            Static("المرحلة 2أ: واجهة المطور\n", id="subtitle"),
            ListView(
                ListItem(Label("1️⃣  خط التسليم - التخطيط ← التنفيذ ← ضمان الجودة ← التقرير")),
                ListItem(Label("2️⃣  اختبار الانحدار - فشل ضمان الجودة ← إعادة الإنتاج ← التغذية الراجعة")),
                ListItem(Label("3️⃣  الصيانة - فحوصات الصحة ← الفحوصات ← الجودة")),
                ListItem(Label("4️⃣  سير عمل مخصص - أوامر محددة من المستخدم")),
                ListItem(Label("📊 عرض الحالة - التحقق من سير العمل النشط")),
                ListItem(Label("📜 عرض السجل - مشاهدة سجل سير العمل")),
            ),
            Static("\nاضغط على رقم لاختيار سير العمل، 's' للحالة، 'h' للسجل، 'q' للخروج", id="help-text"),
            id="menu-container"
        )
        yield Footer()
    
    def action_delivery(self) -> None:
        """بدء سير عمل خط التسليم"""
        self.app.push_screen(WorkflowScreen(WorkflowType.DELIVERY_PIPELINE, self.coordinator))
    
    def action_regression(self) -> None:
        """بدء سير عمل اختبار الانحدار"""
        self.app.push_screen(WorkflowScreen(WorkflowType.REGRESSION, self.coordinator))
    
    def action_maintenance(self) -> None:
        """بدء سير عمل الصيانة"""
        self.app.push_screen(WorkflowScreen(WorkflowType.MAINTENANCE, self.coordinator))
    
    def action_custom(self) -> None:
        """بدء سير عمل مخصص"""
        self.app.push_screen(WorkflowScreen(WorkflowType.CUSTOM, self.coordinator))
    
    def action_status(self) -> None:
        """عرض حالة سير العمل"""
        self.app.push_screen(StatusScreen(self.coordinator))
    
    def action_history(self) -> None:
        """عرض سجل سير العمل"""
        self.app.push_screen(HistoryScreen(self.coordinator))


class StatusScreen(Screen):
    """شاشة عرض حالة سير العمل النشط"""
    
    BINDINGS = [
        Binding("escape", "back", "العودة"),
        Binding("r", "refresh", "تحديث"),
    ]
    
    def __init__(self, coordinator: OpsCoordinatorAgent):
        super().__init__()
        self.coordinator = coordinator
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("📊 حالة سير العمل النشط", id="status-title"),
            Static(self._get_status_display(), id="status-content"),
            Button("تحديث", id="refresh-btn"),
            id="status-container"
        )
        yield Footer()
    
    def _get_status_display(self) -> str:
        """الحصول على عرض الحالة المنسق"""
        try:
            result = self.coordinator.execute({"action": "list_workflows"})
            workflows = result.get("active_workflows", [])
            
            if not workflows:
                return "\n✨ لا يوجد سير عمل نشط\n"
            
            output = f"\n🔄 سير العمل النشط ({len(workflows)}):\n\n"
            for wf in workflows:
                wf_id = wf.get("workflow_id", "غير معروف")
                wf_type = wf.get("workflow_type", "غير معروف")
                status = wf.get("status", "unknown")
                started_at = wf.get("started_at", "")
                
                status_icon = {
                    "running": "🔄",
                    "completed": "✅",
                    "failed": "❌",
                    "paused": "⏸️"
                }.get(status, "❓")
                
                status_ar = {
                    "running": "قيد التشغيل",
                    "completed": "مكتمل",
                    "failed": "فشل",
                    "paused": "متوقف مؤقتاً"
                }.get(status, status)
                
                output += f"{status_icon} {wf_id[:8]}... - {wf_type}\n"
                output += f"   الحالة: {status_ar}\n"
                output += f"   البدء: {started_at}\n\n"
            
            return output
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على الحالة: {e}", exc_info=True)
            return f"\n❌ خطأ: {str(e)}\n"
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press"""
        if event.button.id == "refresh-btn":
            self.action_refresh()
    
    def action_refresh(self) -> None:
        """تحديث عرض الحالة"""
        content_widget = self.query_one("#status-content", Static)
        content_widget.update(self._get_status_display())
    
    def action_back(self) -> None:
        """العودة إلى القائمة الرئيسية"""
        self.app.pop_screen()


class HistoryScreen(Screen):
    """شاشة عرض سجل سير العمل"""
    
    BINDINGS = [
        Binding("escape", "back", "العودة"),
    ]
    
    def __init__(self, coordinator: OpsCoordinatorAgent):
        super().__init__()
        self.coordinator = coordinator
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("📜 سجل سير العمل", id="history-title"),
            Static(self._get_history_display(), id="history-content"),
            id="history-container"
        )
        yield Footer()
    
    def _get_history_display(self) -> str:
        """الحصول على عرض السجل المنسق من SQLite"""
        try:
            # Get history from persistent storage (SQLite)
            history = self.coordinator.get_persistent_history(limit=100)
            
            if not history:
                return "\n✨ لا يوجد سجل سير عمل\n"
            
            output = f"\n📜 سير العمل الأخير (آخر {len(history)}):\n\n"
            for wf in history[-10:]:  # Show last 10
                wf_id = wf.get("workflow_id", "غير معروف")
                wf_type = wf.get("workflow_type", "غير معروف")
                status = wf.get("final_status", wf.get("status", "unknown"))
                started_at = wf.get("started_at", "")
                completed_at = wf.get("completed_at", "")
                
                status_icon = {
                    "completed": "✅",
                    "failed": "❌",
                    "cancelled": "🚫",
                    "running": "🔄",
                    "pending": "⏳"
                }.get(status, "❓")
                
                status_ar = {
                    "completed": "مكتمل",
                    "failed": "فشل",
                    "cancelled": "ملغى",
                    "running": "قيد التشغيل",
                    "pending": "معلق"
                }.get(status, status)
                
                output += f"{status_icon} {wf_id[:8]}... - {wf_type}\n"
                output += f"   الحالة: {status_ar}\n"
                output += f"   البدء: {started_at}\n"
                if completed_at:
                    output += f"   الاكتمال: {completed_at}\n"
                output += "\n"
            
            return output
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على السجل: {e}", exc_info=True)
            return f"\n❌ خطأ: {str(e)}\n"
    
    def action_back(self) -> None:
        """العودة إلى القائمة الرئيسية"""
        self.app.pop_screen()


class DeveloperCLI(App):
    """Main Developer Platform CLI/TUI Application"""
    
    CSS = """
    #app-title {
        text-align: center;
        text-style: bold;
        color: #00ff00;
        padding: 1;
    }
    
    #subtitle {
        text-align: center;
        color: #888888;
    }
    
    #menu-container {
        padding: 2;
    }
    
    #workflow-title {
        text-style: bold;
        color: #00aaff;
        padding: 1;
    }
    
    #workflow-description {
        color: #cccccc;
        padding: 1;
    }
    
    #workflow-container {
        padding: 2;
    }
    
    #status-title, #history-title {
        text-style: bold;
        color: #ffaa00;
        padding: 1;
    }
    
    #help-text {
        text-align: center;
        color: #666666;
        padding: 1;
    }
    
    Button {
        margin: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "خروج", priority=True),
    ]
    
    def __init__(self):
        super().__init__()
        self.coordinator = OpsCoordinatorAgent()
    
    def on_mount(self) -> None:
        """تهيئة التطبيق"""
        self.title = "لوحة تحكم بالذكاء الاصطناعي"
        self.sub_title = "المرحلة 2أ: واجهة المطور"
        self.push_screen(MainMenuScreen(self.coordinator))
    
    async def action_quit(self) -> None:
        """الخروج من التطبيق"""
        self.exit()


def run_cli():
    """تشغيل واجهة CLI/TUI"""
    app = DeveloperCLI()
    app.run()


def run_simple_cli():
    """تشغيل واجهة Rich CLI البسيطة (غير تفاعلية)"""
    console = Console()
    coordinator = OpsCoordinatorAgent()
    
    console.print(Panel.fit(
        "[bold cyan]لوحة تحكم بالذكاء الاصطناعي[/bold cyan]\n"
        "[dim]المرحلة 2أ: واجهة المطور[/dim]",
        border_style="cyan"
    ))
    
    console.print("\n[bold]سير العمل المتاحة:[/bold]\n")
    
    workflows = [
        ("1", "خط التسليم", "التخطيط ← التنفيذ ← ضمان الجودة ← التقرير"),
        ("2", "اختبار الانحدار", "فشل ضمان الجودة ← إعادة الإنتاج ← التغذية الراجعة"),
        ("3", "الصيانة", "فحوصات الصحة ← الفحوصات ← الجودة"),
        ("4", "سير عمل مخصص", "أوامر محددة من المستخدم"),
    ]
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("سير العمل", style="cyan")
    table.add_column("الوصف", style="dim")
    
    for num, name, desc in workflows:
        table.add_row(num, name, desc)
    
    console.print(table)
    
    console.print("\n[bold]سير العمل النشط:[/bold]")
    result = coordinator.list_workflows()
    active = result.get("active_workflows", [])
    
    if active:
        for wf in active:
            console.print(f"  • {wf.get('workflow_id')} - {wf.get('workflow_type')} - {wf.get('status')}")
    else:
        console.print("  [dim]لا يوجد سير عمل نشط[/dim]")
    
    console.print("\n[bold]السجل الأخير:[/bold]")
    # Get history from persistent storage (SQLite)
    history = coordinator.get_persistent_history(limit=5)
    
    if history:
        for wf in history:
            status_icon = "✅" if wf.get("final_status") == "completed" else "❌"
            console.print(f"  {status_icon} {wf.get('workflow_type')} - {wf.get('final_status')}")
    else:
        console.print("  [dim]لا يوجد سجل سير عمل[/dim]")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--simple":
        run_simple_cli()
    else:
        run_cli()
