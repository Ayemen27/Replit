# 🤖 AI Chat System

## نظرة عامة

**AI Chat** هو واجهة المحادثة الذكية التي تتيح للمستخدمين التفاعل مع الوكلاء الذكية (AI Agents) لإنجاز المهام البرمجية والتطويرية.

---

## المكونات

### 1. Chat Interface
```yaml
التقنية: React + WebSocket + Streaming
المسؤولية: عرض المحادثة والتفاعل مع AI
```

**الميزات:**
- Real-time messaging مع AI Agents
- Streaming responses (الردود تظهر كلمة بكلمة)
- Markdown rendering (للأكواد والنصوص المنسقة)
- Code syntax highlighting في الرسائل
- Copy code snippets
- Export chat history

### 2. Context Management
```yaml
المسؤولية: إدارة سياق المحادثة
```

**القدرات:**
- تتبع السياق الحالي (أي مشروع، أي ملف)
- حفظ تاريخ المحادثات
- استئناف المحادثات السابقة
- مشاركة المحادثات مع الفريق

### 3. Multi-Agent Orchestration
```yaml
المسؤولية: التنسيق بين الوكلاء المختلفة
```

**الوكلاء:**
- **Infrastructure Agents** (6 وكلاء):
  - Server Setup Agent
  - Security Hardening Agent
  - Monitoring Setup Agent
  - Backup Agent
  - Deployment Agent
  - Maintenance Agent

- **Development Agents** (4 وكلاء):
  - Frontend Developer Agent
  - Backend Developer Agent
  - DevOps Agent
  - QA/Testing Agent

### 4. Command Palette
```yaml
المسؤولية: اختصارات سريعة للمهام الشائعة
```

**الأوامر:**
- `/create-project <type>` - إنشاء مشروع جديد
- `/deploy` - نشر المشروع
- `/test` - تشغيل الاختبارات
- `/debug <issue>` - تصحيح مشكلة
- `/optimize` - تحسين الكود

---

## البنية المعمارية

```
src/components/features/AIChat/
├── ChatInterface.tsx        # الواجهة الرئيسية
├── MessageList.tsx          # قائمة الرسائل
├── MessageInput.tsx         # إدخال الرسائل
├── AgentSelector.tsx        # اختيار الوكيل
├── ContextPanel.tsx         # عرض السياق الحالي
├── CommandPalette.tsx       # لوحة الأوامر
├── hooks/
│   ├── useChat.ts           # Hook للمحادثة
│   ├── useAgentStream.ts    # Hook لـ streaming responses
│   └── useContext.ts        # Hook لإدارة السياق
└── utils/
    ├── messageParser.ts     # تحليل الرسائل
    └── codeExtractor.ts     # استخراج الأكواد من الردود
```

---

## التكامل مع الأنظمة الأخرى

### مع Code Editor:
```typescript
// AI يكتب كود ويرسله للـ Editor
import { useCodeEditor } from '@/hooks/useCodeEditor'
import { useChat } from '@/hooks/useChat'

const { sendMessage } = useChat()
const { insertCode } = useCodeEditor()

// User: "أنشئ مكون React للـ Login"
sendMessage("أنشئ مكون React للـ Login")
  .then((response) => {
    // AI يرد بكود
    if (response.containsCode) {
      insertCode(response.extractedCode)
    }
  })
```

### مع File Manager:
```typescript
// AI يطلب ملف للمراجعة
const { sendMessage, setContext } = useChat()
const { getFileContent } = useFileManager()

// AI: "اعرض لي ملف package.json"
const file = await getFileContent('package.json')
setContext({ currentFile: file })
```

### مع Remote Execution:
```typescript
// AI يقترح تشغيل أمر
import { useRemoteExecution } from '@/hooks/useRemoteExecution'

const { runCommand } = useRemoteExecution()

// AI: "جرب هذا الأمر: npm test"
const handleAICommand = async (command: string) => {
  const result = await runCommand(command)
  // إرسال النتيجة للـ AI للتحليل
  sendMessage(`النتيجة: ${result.output}`)
}
```

### مع Agents System:
```typescript
// تفويض مهمة لوكيل معين
import { useAgentOrchestration } from '@/hooks/useAgents'

const { delegateTask } = useAgentOrchestration()

// User: "قم بتحسين أداء قاعدة البيانات"
const result = await delegateTask({
  agent: 'backend_developer',
  task: 'optimize database queries',
  context: { project: currentProject }
})
```

---

## المهام ذات الصلة

- المطور 8: AI Chat Interface
- المطور 1: Infrastructure Agents
- المطور 2: Development Agents
- المطور 7: Code Editor Integration

---

## الحالة الحالية

**ما هو موجود:**
- ❌ لا شيء بعد - يجب بناء كل شيء من الصفر

**ما يجب إضافته:**
- [ ] Chat UI components
- [ ] WebSocket connection للـ real-time messaging
- [ ] Streaming response handler
- [ ] Markdown renderer مع syntax highlighting
- [ ] Context management system
- [ ] Agent selector
- [ ] Command palette
- [ ] Chat history storage
- [ ] Export/Import conversations
- [ ] Code extraction من الرسائل

---

## التوسعة المطلوبة

### مثال: Chat Interface Component

```typescript
// components/features/AIChat/ChatInterface.tsx

import { useState, useRef, useEffect } from 'react'
import { useChat } from '@/hooks/useChat'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import AgentSelector from './AgentSelector'

export default function ChatInterface() {
  const {
    messages,
    sendMessage,
    isTyping,
    currentAgent,
    setAgent
  } = useChat()

  return (
    <div className="flex flex-col h-full bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 p-4 border-b border-gray-700">
        <AgentSelector
          currentAgent={currentAgent}
          onSelectAgent={setAgent}
        />
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={messages} isTyping={isTyping} />
      </div>

      {/* Input */}
      <div className="bg-gray-800 p-4 border-t border-gray-700">
        <MessageInput onSend={sendMessage} />
      </div>
    </div>
  )
}
```

### مثال: Streaming Response Hook

```typescript
// hooks/useAgentStream.ts

import { useState, useEffect } from 'react'

export function useAgentStream(agentId: string) {
  const [streamedText, setStreamedText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)

  const streamResponse = async (message: string) => {
    setIsStreaming(true)
    setStreamedText('')

    const response = await fetch('/api/ai/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent: agentId, message })
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) return

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      setStreamedText((prev) => prev + chunk)
    }

    setIsStreaming(false)
  }

  return { streamedText, isStreaming, streamResponse }
}
```

### مثال: Code Extraction Utility

```typescript
// utils/codeExtractor.ts

export function extractCodeBlocks(text: string) {
  const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g
  const blocks: Array<{ language: string; code: string }> = []

  let match
  while ((match = codeBlockRegex.exec(text)) !== null) {
    blocks.push({
      language: match[1] || 'text',
      code: match[2].trim()
    })
  }

  return blocks
}

export function extractInlineCode(text: string) {
  const inlineCodeRegex = /`([^`]+)`/g
  const codes: string[] = []

  let match
  while ((match = inlineCodeRegex.exec(text)) !== null) {
    codes.push(match[1])
  }

  return codes
}
```

### مثال: Command Palette

```typescript
// components/features/AIChat/CommandPalette.tsx

const COMMANDS = [
  {
    command: '/create-project',
    description: 'إنشاء مشروع جديد',
    args: ['<type>'],
    example: '/create-project react'
  },
  {
    command: '/deploy',
    description: 'نشر المشروع الحالي',
    args: [],
    example: '/deploy'
  },
  {
    command: '/test',
    description: 'تشغيل الاختبارات',
    args: ['<file>?'],
    example: '/test auth.test.ts'
  }
]

export default function CommandPalette({ onSelect }: Props) {
  const [search, setSearch] = useState('')

  const filtered = COMMANDS.filter(cmd =>
    cmd.command.includes(search) || cmd.description.includes(search)
  )

  return (
    <div className="bg-gray-800 rounded p-4">
      <input
        type="text"
        placeholder="ابحث عن أمر..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full bg-gray-700 px-3 py-2 rounded"
      />
      
      <div className="mt-4 space-y-2">
        {filtered.map((cmd) => (
          <button
            key={cmd.command}
            onClick={() => onSelect(cmd.command)}
            className="w-full text-left px-3 py-2 hover:bg-gray-700 rounded"
          >
            <div className="font-mono text-blue-400">{cmd.command}</div>
            <div className="text-sm text-gray-400">{cmd.description}</div>
            <div className="text-xs text-gray-500">مثال: {cmd.example}</div>
          </button>
        ))}
      </div>
    </div>
  )
}
```

---

## التحديات التقنية

### 1. Streaming Performance
```typescript
// حل: Debouncing للتحديثات المتكررة
import { useDebouncedCallback } from 'use-debounce'

const updateUI = useDebouncedCallback((text) => {
  setDisplayedText(text)
}, 50)
```

### 2. Context Window Management
```typescript
// حل: Sliding window للرسائل
const MAX_CONTEXT_MESSAGES = 20

const getRelevantContext = (messages: Message[]) => {
  return messages.slice(-MAX_CONTEXT_MESSAGES)
}
```

### 3. Multi-Agent Coordination
```typescript
// حل: Agent Router
const routeToAgent = (message: string) => {
  if (message.includes('deploy') || message.includes('نشر')) {
    return 'devops_agent'
  }
  if (message.includes('test') || message.includes('اختبار')) {
    return 'qa_agent'
  }
  // Default
  return 'general_agent'
}
```

---

## الوثائق ذات الصلة

- [`../01_ARCHITECTURE/SYSTEM_OVERVIEW.md`](../../01_ARCHITECTURE/SYSTEM_OVERVIEW.md)
- [`../03_SYSTEMS/01_Agents/README.md`](../01_Agents/README.md)
- [`../05_OPERATIONS/AGENT_TASKS/DEVELOPER_08.md`](../../05_OPERATIONS/AGENT_TASKS/DEVELOPER_08.md)

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ موثق
