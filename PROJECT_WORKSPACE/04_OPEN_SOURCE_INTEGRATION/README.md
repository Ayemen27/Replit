# 🔓 دليل المشاريع مفتوحة المصدر

> **🎯 الهدف**: استخراج ودمج مكونات من مشاريع مفتوحة المصدر مثبتة بدلاً من البناء من الصفر

**📍 أنت هنا**: `PROJECT_WORKSPACE/04_OPEN_SOURCE_INTEGRATION/README.md`  
**📅 آخر تحديث**: 2025-11-18

---

## ⚠️ قاعدة ذهبية

```
❌ لا تعد اختراع العجلة!
✅ استخدم مكونات مجربة ومختبرة من مشاريع كبيرة
✅ وفّر أسابيع من العمل
✅ قلل الأخطاء والثغرات الأمنية
```

---

## 📚 المشاريع المتوفرة

| المشروع | الاستخدام | الدليل التفصيلي | المطور المسؤول |
|---------|----------|-----------------|----------------|
| **MeshCentral** | WebSocket + Agent Installation | [MESHCENTRAL_GUIDE.md](MESHCENTRAL_GUIDE.md) | Developer 9 |
| **VSCode Tunnels** | Reverse Tunnel + Port Forwarding | [VSCODE_TUNNELS_GUIDE.md](VSCODE_TUNNELS_GUIDE.md) | Developer 9 |
| **Teleport** | RBAC + Audit Logging + Session Recording | [TELEPORT_GUIDE.md](TELEPORT_GUIDE.md) | Developer 3 |
| **Docker Engine** | Safe Code Execution + Sandboxing | [DOCKER_API_GUIDE.md](DOCKER_API_GUIDE.md) | Developer 5 |

---

## 🚀 كيف تستخدم هذه الأدلة؟

### قبل البدء بأي ميزة:

**✅ الخطوات**:
1. اقرأ الدليل المتعلق بمهمتك
2. افهم المكون المطلوب استخراجه
3. اتبع الأمثلة المقدمة
4. اختبر التكامل
5. وثّق أي تغييرات

**مثال**:
```
مهمتك: بناء Terminal component

❌ خطأ: كتابة WebSocket server من الصفر
✅ صحيح:
  1. راجع MESHCENTRAL_GUIDE.md
  2. راجع DOCKER_API_GUIDE.md
  3. استخرج WebSocket logic من MeshCentral
  4. استخرج execution logic من Docker API
  5. دمجهما معاً
```

---

## 📖 ملخص سريع لكل مشروع

### 1️⃣ MeshCentral
**ما نستخرج**: WebSocket bidirectional communication + Agent installer
**متى نستخدمه**: عند ربط Bridge Daemon بـ Control Plane
**الملفات**: `bridge_tool/services/websocket_client.py`, `installers/install.sh`

---

### 2️⃣ VSCode Remote Tunnels
**ما نستخرج**: Reverse tunnel implementation + Port forwarding
**متى نستخدمه**: للسماح للمستخدمين خلف Firewalls بالاتصال
**الملفات**: `bridge_tool/services/tunnel_server.py`, `daemon/tunnel_client.py`

---

### 3️⃣ Teleport
**ما نستخرج**: RBAC system + Audit logs + Session recording
**متى نستخدمه**: للصلاحيات الدقيقة وتسجيل العمليات
**الملفات**: `web/models/rbac.py`, `core/audit_logger.py`, `tools/session_recorder.py`

---

### 4️⃣ Docker Engine API
**ما نستخرج**: Container execution + Resource limits
**متى نستخدمه**: لتنفيذ أوامر Terminal بشكل آمن ومعزول
**الملفات**: `tools/docker_manager.py`

---

## 🎯 معايير القبول للدمج

### لكل مشروع مفتوح المصدر تدمجه:

- [ ] قرأت الدليل المخصص كاملاً
- [ ] فهمت المكون المطلوب
- [ ] استخرجت الكود الضروري فقط (لا تنسخ كل شيء!)
- [ ] كيّفت الكود ليتناسب مع مشروعنا
- [ ] اختبرت التكامل
- [ ] وثّقت الاستخدام
- [ ] أضفت الإسناد (attribution) في التعليقات:
  ```python
  # Inspired by MeshCentral WebSocket implementation
  # https://github.com/Ylianst/MeshCentral
  ```

---

## 🔗 الروابط ذات الصلة

- **INVENTORY.md**: قائمة الأنظمة الموجودة حالياً
- **03_SYSTEMS/**: توثيق الأنظمة الفرعية
- **05_OPERATIONS/AGENT_TASKS/**: مهام المطورين

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ جاهز للاستخدام
