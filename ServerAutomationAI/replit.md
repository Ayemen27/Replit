# لوحة تحكم بالذكاء الاصطناعي (AI Control Dashboard)

## Overview

هذا المشروع عبارة عن لوحة تحكم بالذكاء الاصطناعي مصممة لتطوير التطبيقات الكاملة بشكل تلقائي، مشابهة لـ Replit Agent. تدمج المنصة وكلاء البنية التحتية ووكلاء التطوير لإنشاء بيئة تطوير شاملة ذاتية الإدارة. تهدف المنصة إلى توفير حل قوي وفعال وفعّال من حيث التكلفة للتطوير التلقائي للبرمجيات.

**القدرات الرئيسية:**
- 6 وكلاء للبنية التحتية (المراقبة والأمان والنسخ الاحتياطي).
- 4 وكلاء للتطوير (التخطيط والتنفيذ والاختبار والتنسيق).
- أتمتة كاملة لدورة حياة تطوير التطبيقات.
- تصميم محسّن للموارد، قادر على العمل على أجهزة منخفضة المواصفات.
- تعريب كامل لواجهات المستخدم (CLI/TUI + لوحة التحكم الويب)، نظام الإشعارات، ورسائل الحالة والتقدم.

## User Preferences

- لغة بسيطة وشرح مفصل
- سير عمل تطوير تكراري
- الاستئذان قبل إجراء تغييرات كبيرة
- **اللغة:** جميع الواجهات يجب أن تكون بالعربية
- **الاسم:** "لوحة تحكم بالذكاء الاصطناعي"

## System Architecture

The platform combines a **Development Platform Layer** (Planner, Code Executor, QA/Test, Ops Coordinator) with a **Core Infrastructure Layer** (Secrets Management, Cache/State, Model Routing, Tool Registry, Execution Sandbox) and a **Monitoring Layer** (AI Manager and 5 infrastructure agents).

**UI/UX Decisions:**
- **CLI/TUI Interface:** Utilizes Textual/Rich for a lightweight, interactive command-line interface with real-time workflow execution.
- **Web Dashboard:** Implemented using FastAPI and HTMX/Bootstrap for a lightweight web interface with real-time system metrics, workflow history, agent registry, and token-based API authentication.
  - **UI Overhaul (Nov 2025):** Comprehensive redesign meeting WCAG 2.1 AA, Material Design 3, and Replit RUI standards
    - Responsive SCSS system with 8px baseline grid
    - Arabic-first typography (Cairo + IBM Plex Sans Arabic)
    - Full UX improvements: loading states, toast notifications, smooth transitions, interactive states
    - Performance optimized: CSS minified to 46KB
    - Documentation: `/docs/dashboard_ui/` with compliance tracking

**Technical Implementations & Feature Specifications:**
- **Secrets Management:** `python-dotenv` and `Fernet` encryption.
- **Cache & State Management:** `SQLite` and `diskcache` for persistent workflow history and data caching.
- **Model Router:** `LiteLLM` for routing and utilizing various free AI models.
- **Execution Sandbox:** Provides a secure and resource-isolated environment for code execution.
- **Tool Registry:** A collection of 12 essential tools for development tasks.
- **Agent Base Class:** A foundational class promoting reusability and consistent structure for all agents.
- **Async Workflows:** Implemented with `asyncio` for non-blocking operations and real-time progress streaming.
- **Workflow Orchestration:** `Ops Coordinator` manages core workflows (Delivery, Regression, Maintenance, Custom).
- **Localization:** Full Arabic localization for all UI elements, notifications, and project naming.
- **Bridge Tool (Nov 2025):** GitHub-mediated deployment pipeline supporting Replit → GitHub → Server workflow
  - Git operations management with GitManager service
  - Automated commit, tag, and push to GitHub
  - Server deployment via Git clone/checkout from GitHub
  - Tag-based versioning and rollback support
  - Comprehensive deployment reporting in Arabic/English
  - Secrets integration for GitHub Token and SSH credentials

**System Design Choices:**
- **Resource Optimization:** Designed for efficient operation on minimal RAM.
- **Modularity:** Clear separation of concerns with distinct agents.
- **Extensibility:** A well-defined agent base class and tool registry facilitate easy addition of new functionalities.
- **100% Open Source:** Leverages open-source components and free AI models to ensure zero operational cost.

## External Dependencies

-   **AI Models:** Groq, Gemini, Mistral, HuggingFace (accessed via LiteLLM).
-   **Databases:** SQLite (for cache and state management), PostgreSQL, MongoDB (monitored by Database Manager).
-   **Python Libraries:**
    -   `python-dotenv`, `cryptography`
    -   `diskcache`
    -   `litellm`
    -   `textual`, `rich`
    -   `psutil`, `PyYAML`, `requests`, `watchdog`, `colorama`, `tabulate`
    -   `psycopg2-binary`, `pymongo`
    -   `tree-sitter`
    -   `FastAPI`, `Uvicorn`, `Jinja2`
-   **Frontend Frameworks:** HTMX, Bootstrap.