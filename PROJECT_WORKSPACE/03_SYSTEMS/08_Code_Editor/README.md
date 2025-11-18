# 💻 Code Editor System

## نظرة عامة

**Code Editor** هو محرر الأكواد المدمج في المنصة - يوفر تجربة تطوير متقدمة مباشرة من المتصفح باستخدام Monaco Editor (نفس محرر VS Code).

---

## المكونات

### 1. Monaco Editor Integration
```yaml
التقنية: @monaco-editor/react + Monaco Editor API
المسؤولية: محرر أكواد متقدم في المتصفح
```

**الميزات الأساسية:**
- Syntax highlighting لأكثر من 100 لغة برمجة
- IntelliSense & Auto-completion
- Multi-cursor editing
- Find & Replace (with regex support)
- Code folding
- Bracket matching
- Minimap
- Diff viewer (لمقارنة التغييرات)

### 2. File System Integration
```yaml
المسؤولية: التكامل مع نظام إدارة الملفات
```

**القدرات:**
- فتح ملفات من File Manager
- حفظ التغييرات تلقائياً (auto-save)
- تتبع التغييرات غير المحفوظة
- دعم التراجع والإعادة (undo/redo)

### 3. Language Server Protocol (LSP)
```yaml
المسؤولية: توفير ميزات IDE متقدمة
```

**الميزات:**
- Error highlighting في الوقت الفعلي
- Go to definition
- Find references
- Rename symbol
- Code formatting

### 4. Theme Support
```yaml
المسؤولية: تخصيص مظهر المحرر
```

**الثيمات المدعومة:**
- VS Code Dark (الافتراضي)
- VS Code Light
- Monokai
- Dracula
- Nord
- Custom themes

---

## البنية المعمارية

```
src/components/features/CodeEditor/
├── CodeEditor.tsx           # المكون الرئيسي
├── EditorControls.tsx       # أزرار التحكم (Save, Format, etc)
├── FileTab.tsx              # عرض الملفات المفتوحة كتابات
├── EditorSettings.tsx       # إعدادات المحرر
├── hooks/
│   ├── useMonaco.ts         # Hook للتفاعل مع Monaco
│   ├── useAutoSave.ts       # Hook للحفظ التلقائي
│   └── useSyntaxCheck.ts    # Hook للتحقق من الأخطاء
└── utils/
    ├── languageDetector.ts  # اكتشاف لغة البرمجة تلقائياً
    └── themeManager.ts      # إدارة الثيمات
```

---

## التكامل مع الأنظمة الأخرى

### مع File Manager:
```typescript
// فتح ملف من File Manager
import { useCodeEditor } from '@/hooks/useCodeEditor'

const { openFile } = useCodeEditor()

// عند النقر على ملف في File Manager
const handleFileClick = (file) => {
  openFile({
    path: file.path,
    content: file.content,
    language: detectLanguage(file.extension)
  })
}
```

### مع AI Chat:
```typescript
// AI يكتب/يعدل كود
import { useCodeEditor } from '@/hooks/useCodeEditor'

const { insertCode, replaceSelection } = useCodeEditor()

// AI Agent يرسل كود جديد
aiAgent.onCodeGenerated((code) => {
  insertCode(code, { autoFormat: true })
})
```

### مع Remote Execution:
```typescript
// تشغيل الكود الحالي
import { useRemoteExecution } from '@/hooks/useRemoteExecution'

const { runCode } = useRemoteExecution()
const { getCurrentFile } = useCodeEditor()

const handleRunCode = async () => {
  const file = getCurrentFile()
  await runCode(file.path)
}
```

### مع Git Integration:
```typescript
// عرض Git diff
import { useGitDiff } from '@/hooks/useGit'

const { getDiff } = useGitDiff()

const showDiffViewer = async (filePath) => {
  const diff = await getDiff(filePath)
  // عرض الفروقات في Monaco Diff Editor
}
```

---

## المهام ذات الصلة

- المطور 7: Code Editor Integration
- المطور 6: File Manager UI
- المطور 8: AI Chat Interface
- المطور 3: Git Integration

---

## الحالة الحالية

**ما هو موجود:**
- ❌ لا شيء بعد - يجب بناء كل شيء من الصفر

**ما يجب إضافته:**
- [ ] تثبيت `@monaco-editor/react`
- [ ] إنشاء CodeEditor component
- [ ] دمج Monaco Editor
- [ ] إضافة File tabs system
- [ ] Auto-save functionality
- [ ] Syntax checking
- [ ] Theme switcher
- [ ] LSP integration (اختياري - متقدم)
- [ ] Diff viewer
- [ ] Settings panel

---

## التوسعة المطلوبة

### مثال: CodeEditor Component

```typescript
// components/features/CodeEditor/CodeEditor.tsx

import Editor, { Monaco } from '@monaco-editor/react'
import { useState, useRef } from 'react'

interface CodeEditorProps {
  file: {
    path: string
    content: string
    language: string
  }
  onSave?: (content: string) => void
}

export default function CodeEditor({ file, onSave }: CodeEditorProps) {
  const [value, setValue] = useState(file.content)
  const [isDirty, setIsDirty] = useState(false)
  const editorRef = useRef(null)

  const handleEditorDidMount = (editor: any, monaco: Monaco) => {
    editorRef.current = editor
    
    // Register save command (Ctrl+S)
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      handleSave()
    })
  }

  const handleChange = (newValue: string | undefined) => {
    setValue(newValue || '')
    setIsDirty(true)
  }

  const handleSave = async () => {
    if (onSave) {
      await onSave(value)
      setIsDirty(false)
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* File Tab */}
      <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-white">{file.path}</span>
          {isDirty && <span className="text-yellow-500">●</span>}
        </div>
        <button
          onClick={handleSave}
          className="px-3 py-1 bg-blue-600 text-white rounded"
        >
          Save
        </button>
      </div>

      {/* Monaco Editor */}
      <div className="flex-1">
        <Editor
          height="100%"
          language={file.language}
          value={value}
          onChange={handleChange}
          onMount={handleEditorDidMount}
          theme="vs-dark"
          options={{
            minimap: { enabled: true },
            fontSize: 14,
            wordWrap: 'on',
            automaticLayout: true,
            scrollBeyondLastLine: false,
            tabSize: 2,
          }}
        />
      </div>
    </div>
  )
}
```

### مثال: Auto-Save Hook

```typescript
// hooks/useAutoSave.ts

import { useEffect, useRef } from 'react'

export function useAutoSave(
  value: string,
  onSave: (value: string) => void,
  delay: number = 2000
) {
  const timeoutRef = useRef<NodeJS.Timeout>()

  useEffect(() => {
    // Clear previous timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    // Set new timeout
    timeoutRef.current = setTimeout(() => {
      onSave(value)
    }, delay)

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [value, onSave, delay])
}
```

---

## التحديات التقنية

### 1. Performance مع ملفات كبيرة
```typescript
// حل: Virtual scrolling + lazy loading
const editorOptions = {
  scrollBeyondLastLine: false,
  renderValidationDecorations: 'on',
  // تحسين الأداء للملفات الكبيرة
  maxTokenizationLineLength: 20000,
}
```

### 2. Sync مع File System
```typescript
// حل: WebSocket للتحديثات الفورية
socket.on('file:changed', (filePath) => {
  if (currentFile.path === filePath) {
    // Show notification: "File changed externally, reload?"
  }
})
```

### 3. Multi-file editing
```typescript
// حل: Tabs system مع cache
const [openFiles, setOpenFiles] = useState<Map<string, FileContent>>()

const switchTab = (filePath: string) => {
  // Cache current file state
  openFiles.set(currentFile.path, {
    content: editorRef.current.getValue(),
    cursorPosition: editorRef.current.getPosition()
  })
  
  // Load new file
  const cached = openFiles.get(filePath)
  editorRef.current.setValue(cached.content)
  editorRef.current.setPosition(cached.cursorPosition)
}
```

---

## الوثائق ذات الصلة

- [`../01_ARCHITECTURE/SYSTEM_OVERVIEW.md`](../../01_ARCHITECTURE/SYSTEM_OVERVIEW.md)
- [`../05_OPERATIONS/AGENT_TASKS/DEVELOPER_07.md`](../../05_OPERATIONS/AGENT_TASKS/DEVELOPER_07.md)
- [Monaco Editor Docs](https://microsoft.github.io/monaco-editor/)

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ موثق
