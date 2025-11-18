# 📁 نظام إدارة الملفات (File Manager System)

> **🎯 الهدف**: إدارة ملفات المشاريع والتنقل في شجرة الملفات عبر الواجهة

**📍 الموقع**: `PROJECT_WORKSPACE/03_SYSTEMS/03_File_Manager/README.md`  
**📅 آخر تحديث**: 2025-11-18  
**🔄 حالة الجاهزية**: ✅ **جاهز 80%** - الأدوات الخلفية موجودة، الواجهة قيد البناء

---

## 📦 ما هو موجود حالياً؟

### 🗂️ المسارات والمكونات:

| المكون | المسار | الحالة | الوظيفة |
|--------|---------|--------|---------|
| **File Operations** | `ServerAutomationAI/dev_platform/tools/file_ops.py` | ✅ جاهز | CRUD operations |
| **File Manager UI** | قيد الإنشاء | ⏳ 20% | React component |
| **Monaco Editor** | في SaaS Boilerplate | ⚠️ يحتاج دمج | Code editing |

---

## 🎯 المكونات الرئيسية

### 1️⃣ File Operations Backend (جاهز ✅)

**المسار**: `ServerAutomationAI/dev_platform/tools/file_ops.py`

**الوظائف المتوفرة**:

```python
from ServerAutomationAI.dev_platform.tools.file_ops import FileOps

# إنشاء instance
file_ops = FileOps(workspace_path="/workspace/project")

# 1. إنشاء ملف
file_ops.create_file(
    path="src/index.ts",
    content="console.log('Hello World!')"
)

# 2. قراءة ملف
content = file_ops.read_file("src/index.ts")
print(content)  # console.log('Hello World!')

# 3. تحديث ملف
file_ops.update_file(
    path="src/index.ts",
    content="console.log('Updated!')"
)

# 4. حذف ملف
file_ops.delete_file("src/old-file.ts")

# 5. عرض شجرة الملفات
tree = file_ops.list_tree(max_depth=3)
print(tree)
# Output:
# /workspace/project/
# ├── src/
# │   ├── index.ts
# │   └── components/
# │       └── Button.tsx
# └── package.json

# 6. البحث عن ملفات
results = file_ops.search_files(pattern="*.ts", content="console.log")
# ["/workspace/project/src/index.ts", ...]

# 7. نسخ ملف
file_ops.copy_file(
    source="src/component.tsx",
    destination="src/component.backup.tsx"
)

# 8. نقل ملف
file_ops.move_file(
    source="src/old-folder/file.ts",
    destination="src/new-folder/file.ts"
)
```

---

### 2️⃣ File Manager API (للبناء)

**المسار المستهدف**: `src/app/api/files/route.ts`

**ما يجب بناؤه**:

```typescript
// src/app/api/files/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const workspace_id = searchParams.get('workspace_id')
  const path = searchParams.get('path') || '/'
  
  // استدعاء Python backend
  const response = await fetch(`http://backend:8000/files/list`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ workspace_id, path })
  })
  
  const data = await response.json()
  return NextResponse.json(data)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const { action, workspace_id, path, content } = body
  
  // استدعاء العمليات المختلفة
  let result
  switch (action) {
    case 'create':
      result = await createFile(workspace_id, path, content)
      break
    case 'read':
      result = await readFile(workspace_id, path)
      break
    case 'update':
      result = await updateFile(workspace_id, path, content)
      break
    case 'delete':
      result = await deleteFile(workspace_id, path)
      break
  }
  
  return NextResponse.json(result)
}
```

**المطور المسؤول**: Developer 6

---

### 3️⃣ File Manager UI Component (للبناء)

**المسار المستهدف**: `src/components/workspace/FileManager.tsx`

**ما يجب بناؤه**:

```typescript
'use client'

import { useState, useEffect } from 'react'
import { File, Folder, ChevronRight, ChevronDown } from 'lucide-react'

interface FileNode {
  name: string
  type: 'file' | 'folder'
  path: string
  children?: FileNode[]
}

export function FileManager({ workspaceId }: { workspaceId: string }) {
  const [tree, setTree] = useState<FileNode[]>([])
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  
  useEffect(() => {
    // جلب شجرة الملفات
    fetch(`/api/files?workspace_id=${workspaceId}`)
      .then(res => res.json())
      .then(data => setTree(data.tree))
  }, [workspaceId])
  
  const handleFileClick = (path: string) => {
    setSelectedFile(path)
    // فتح الملف في Monaco Editor
  }
  
  const handleCreateFile = async () => {
    const name = prompt('اسم الملف:')
    if (!name) return
    
    await fetch('/api/files', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'create',
        workspace_id: workspaceId,
        path: name,
        content: ''
      })
    })
    
    // تحديث الشجرة
  }
  
  return (
    <div className="file-manager">
      <div className="toolbar">
        <button onClick={handleCreateFile}>+ ملف جديد</button>
      </div>
      
      <div className="tree">
        {tree.map(node => (
          <FileTreeNode
            key={node.path}
            node={node}
            onSelect={handleFileClick}
          />
        ))}
      </div>
    </div>
  )
}

function FileTreeNode({ node, onSelect }: any) {
  const [isOpen, setIsOpen] = useState(false)
  
  return (
    <div>
      <div
        className="tree-node"
        onClick={() => node.type === 'file' ? onSelect(node.path) : setIsOpen(!isOpen)}
      >
        {node.type === 'folder' ? (
          <>
            {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            <Folder size={16} />
          </>
        ) : (
          <File size={16} />
        )}
        <span>{node.name}</span>
      </div>
      
      {isOpen && node.children && (
        <div className="tree-children">
          {node.children.map(child => (
            <FileTreeNode key={child.path} node={child} onSelect={onSelect} />
          ))}
        </div>
      )}
    </div>
  )
}
```

**المطور المسؤول**: Developer 6

---

### 4️⃣ Monaco Editor Integration (جزئياً ✅)

**الموقع**: يوجد في SaaS Boilerplate (يحتاج دمج)

**ما هو موجود**:
- ⚠️ Monaco editor في dependencies
- ⚠️ لكن لا يوجد component جاهز

**ما يجب عمله**:

```typescript
// src/components/workspace/CodeEditor.tsx
'use client'

import Editor from '@monaco-editor/react'
import { useState, useEffect } from 'react'

export function CodeEditor({ 
  filePath, 
  workspaceId 
}: { 
  filePath: string
  workspaceId: string
}) {
  const [content, setContent] = useState('')
  const [language, setLanguage] = useState('typescript')
  
  useEffect(() => {
    // جلب محتوى الملف
    fetch(`/api/files?workspace_id=${workspaceId}&path=${filePath}`)
      .then(res => res.json())
      .then(data => {
        setContent(data.content)
        setLanguage(detectLanguage(filePath))
      })
  }, [filePath])
  
  const handleSave = async (value: string | undefined) => {
    if (!value) return
    
    await fetch('/api/files', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'update',
        workspace_id: workspaceId,
        path: filePath,
        content: value
      })
    })
  }
  
  return (
    <Editor
      height="90vh"
      language={language}
      value={content}
      onChange={(value) => setContent(value || '')}
      onMount={(editor) => {
        // Ctrl+S للحفظ
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S, () => {
          handleSave(editor.getValue())
        })
      }}
      options={{
        minimap: { enabled: true },
        fontSize: 14,
        tabSize: 2,
        automaticLayout: true
      }}
    />
  )
}

function detectLanguage(filename: string): string {
  const ext = filename.split('.').pop()
  const languageMap: Record<string, string> = {
    'ts': 'typescript',
    'tsx': 'typescript',
    'js': 'javascript',
    'jsx': 'javascript',
    'py': 'python',
    'css': 'css',
    'html': 'html',
    'json': 'json'
  }
  return languageMap[ext || ''] || 'plaintext'
}
```

**المطور المسؤول**: Developer 7

---

## 🎯 معايير القبول

### للاستخدام الحالي:

- [ ] File Operations backend يعمل (CRUD)
- [ ] API endpoints للملفات
- [ ] File tree listing يعمل

### للتطوير (Developer 6-7):

- [ ] File Manager UI component كامل
- [ ] Monaco Editor مدمج
- [ ] Auto-save يعمل
- [ ] Syntax highlighting للغات مختلفة
- [ ] Search في الملفات
- [ ] Upload/Download files

---

## 🔗 الروابط ذات الصلة

**الجرد الكامل**: [`01_CURRENT_STATE/INVENTORY.md`](../../01_CURRENT_STATE/INVENTORY.md)  
**المكونات الجاهزة**: SaaS Boilerplate UI Components  
**المطورون**: Developer 6 (File Manager UI) + Developer 7 (Code Editor)

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ Backend جاهز، ⏳ Frontend قيد البناء  
**المراجع**: Developer 1
