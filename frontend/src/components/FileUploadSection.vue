<template>
  <div class="upload-container">
    <div class="upload-header">
      <div>
        <h3>Project Upload</h3>
        <p class="upload-subtitle">Upload files, whole folders, or zip archives with preserved paths.</p>
      </div>
      <div class="upload-actions">
        <input
          ref="fileInput"
          type="file"
          multiple
          class="hidden-input"
          @change="onFileChange"
        />
        <input
          ref="folderInput"
          type="file"
          multiple
          webkitdirectory
          directory
          class="hidden-input"
          @change="onFileChange"
        />
        <input
          ref="zipInput"
          type="file"
          accept=".zip,application/zip"
          class="hidden-input"
          @change="onZipChange"
        />
        <button type="button" class="secondary-btn" @click="browseFiles">Files</button>
        <button type="button" class="secondary-btn" @click="browseFolder">Folder</button>
        <button type="button" class="secondary-btn" @click="browseZip">Zip</button>
      </div>
    </div>

    <div
      class="upload-zone"
      :class="{ 'drag-over': isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onFileDrop"
    >
      <p class="upload-zone-title">Drop files or folders here</p>
      <p class="upload-zone-meta">
        Max {{ MAX_FILES }} entries, {{ formatSize(MAX_FILE_SIZE_BYTES) }} per file,
        {{ formatSize(MAX_TOTAL_SIZE_BYTES) }} total.
      </p>
    </div>

    <div v-if="validationErrors.length > 0" class="feedback feedback-error">
      <p v-for="error in validationErrors" :key="error">{{ error }}</p>
    </div>

    <div v-if="queuedFiles.length > 0" class="queue-panel">
      <div class="queue-summary">
        <div>
          <strong>{{ queuedFiles.length }}</strong> item(s) queued
        </div>
        <div>{{ formatSize(totalQueuedBytes) }}</div>
      </div>

      <div class="tree-preview">
        <ul class="tree-root">
          <UploadPreviewNode v-for="node in queueTree" :key="node.id" :node="node" />
        </ul>
      </div>

      <div class="queue-actions">
        <button type="button" class="primary-btn" :disabled="uploading || queuedFiles.length === 0" @click="uploadFiles">
          {{ uploading ? 'Uploading...' : 'Upload Project Files' }}
        </button>
        <button type="button" class="ghost-btn" :disabled="uploading" @click="clearQueue">Clear</button>
      </div>
    </div>

    <div v-if="uploadNotes.length > 0" class="feedback feedback-info">
      <p v-for="note in uploadNotes" :key="note">{{ note }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useMainStore } from '@/stores/main'
import { projectsApi } from '@/api/projects'
import UploadPreviewNode from '@/components/UploadPreviewNode.vue'

type UploadEntry = {
  id: string
  file: File
  filepath: string
  name: string
  sizeBytes: number
  contentType: string
  isBinary: boolean
  displayIcon: string
  willRenameTo: string | null
}

type TreeNode = {
  id: string
  name: string
  type: 'folder' | 'file'
  children?: TreeNode[]
  sizeBytes?: number
  isBinary?: boolean
  willRenameTo?: string | null
  displayIcon?: string
}

const MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024
const MAX_TOTAL_SIZE_BYTES = 12 * 1024 * 1024
const MAX_FILES = 150

const route = useRoute()
const store = useMainStore()

const isDragging = ref(false)
const uploading = ref(false)
const queuedFiles = ref<UploadEntry[]>([])
const validationErrors = ref<string[]>([])
const uploadNotes = ref<string[]>([])

const fileInput = ref<HTMLInputElement>()
const folderInput = ref<HTMLInputElement>()
const zipInput = ref<HTMLInputElement>()

const projectId = computed(() => parseInt(route.params.projectId as string, 10))
const existingPaths = computed(() => new Set(store.getProjectFiles(projectId.value).map((file: any) => file.filepath || file.name)))
const totalQueuedBytes = computed(() => queuedFiles.value.reduce((sum, entry) => sum + entry.sizeBytes, 0))

const normalizePath = (value: string) => value.replace(/\\/g, '/').replace(/^\/+/, '')

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const getFileIcon = (fileName: string) => {
  const ext = fileName.split('.').pop()?.toLowerCase()
  const iconMap: Record<string, string> = {
    ts: '🔵',
    tsx: '⚛️',
    vue: '💚',
    js: '🟨',
    jsx: '⚛️',
    py: '🐍',
    java: '☕',
    html: '🌐',
    css: '🎨',
    json: '📋',
    md: '📝',
    zip: '🗜️',
    png: '🖼️',
    jpg: '🖼️',
    jpeg: '🖼️',
    gif: '🖼️',
  }
  return iconMap[ext || ''] || '📄'
}

const isProbablyBinary = (file: File) => {
  if (!file.type) {
    return !/\.(txt|md|json|js|ts|tsx|jsx|vue|py|java|c|cpp|h|css|html|xml|yml|yaml|csv|env|gitignore)$/i.test(file.name)
  }
  return !file.type.startsWith('text/') && !/json|javascript|typescript|xml|svg/.test(file.type)
}

const buildUniquePath = (filepath: string, usedPaths: Set<string>) => {
  const normalized = normalizePath(filepath)
  if (!usedPaths.has(normalized)) {
    usedPaths.add(normalized)
    return normalized
  }

  const parts = normalized.split('/')
  const fileName = parts.pop() || normalized
  const dotIndex = fileName.lastIndexOf('.')
  const stem = dotIndex > 0 ? fileName.slice(0, dotIndex) : fileName
  const ext = dotIndex > 0 ? fileName.slice(dotIndex) : ''
  let counter = 2
  let candidate = normalized

  while (usedPaths.has(candidate)) {
    const renamed = `${stem} (${counter})${ext}`
    candidate = [...parts, renamed].join('/')
    counter += 1
  }

  usedPaths.add(candidate)
  return candidate
}

const readFileContent = async (entry: UploadEntry) => {
  if (entry.isBinary) {
    return `[Binary file stored as metadata only]\nname: ${entry.name}\ncontentType: ${entry.contentType || 'application/octet-stream'}\nsize: ${entry.sizeBytes} bytes`
  }

  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (event) => resolve((event.target?.result as string) || '')
    reader.onerror = () => reject(new Error(`Failed to read ${entry.filepath}`))
    reader.readAsText(entry.file)
  })
}

const queueTree = computed<TreeNode[]>(() => {
  const root: TreeNode[] = []
  const rootMap = new Map<string, TreeNode>()

  const ensureNode = (container: TreeNode[], map: Map<string, TreeNode>, name: string, id: string) => {
    let node = map.get(id)
    if (!node) {
      node = { id, name, type: 'folder', children: [] }
      map.set(id, node)
      container.push(node)
    }
    return node
  }

  queuedFiles.value.forEach((entry) => {
    const parts = entry.filepath.split('/')
    let currentChildren = root
    let currentMap = rootMap
    let runningPath = ''

    parts.forEach((part, index) => {
      runningPath = runningPath ? `${runningPath}/${part}` : part
      const isFile = index === parts.length - 1
      if (isFile) {
        currentChildren.push({
          id: entry.id,
          name: part,
          type: 'file',
          sizeBytes: entry.sizeBytes,
          isBinary: entry.isBinary,
          willRenameTo: entry.willRenameTo,
          displayIcon: entry.displayIcon,
        })
      } else {
        const folder = ensureNode(currentChildren, currentMap, part, runningPath)
        const nextMap = new Map<string, TreeNode>()
        folder.children?.forEach((child) => nextMap.set(child.id, child))
        currentChildren = folder.children || []
        currentMap = nextMap
      }
    })
  })

  const sortNodes = (nodes: TreeNode[]) => {
    nodes.sort((a, b) => {
      if (a.type !== b.type) {
        return a.type === 'folder' ? -1 : 1
      }
      return a.name.localeCompare(b.name)
    })
    nodes.forEach((node) => {
      if (node.children?.length) {
        sortNodes(node.children)
      }
    })
  }

  sortNodes(root)
  return root
})

const browseFiles = () => fileInput.value?.click()
const browseFolder = () => folderInput.value?.click()
const browseZip = () => zipInput.value?.click()

const clearNativeInputs = () => {
  if (fileInput.value) fileInput.value.value = ''
  if (folderInput.value) folderInput.value.value = ''
  if (zipInput.value) zipInput.value.value = ''
}

const makeEntries = (files: File[]) => {
  const nextErrors: string[] = []
  const nextNotes: string[] = []
  const usedPaths = new Set<string>([
    ...existingPaths.value,
    ...queuedFiles.value.map((entry) => entry.willRenameTo || entry.filepath),
  ])

  const newEntries: UploadEntry[] = []
  for (const file of files) {
    const rawPath = normalizePath((file as File & { webkitRelativePath?: string }).webkitRelativePath || file.name)
    const filepath = rawPath || file.name

    if (file.size > MAX_FILE_SIZE_BYTES) {
      nextErrors.push(`${filepath} exceeds ${formatSize(MAX_FILE_SIZE_BYTES)}.`)
      continue
    }

    if (queuedFiles.value.length + newEntries.length >= MAX_FILES) {
      nextErrors.push(`Upload queue is limited to ${MAX_FILES} items.`)
      break
    }

    const isBinary = isProbablyBinary(file)
    const finalPath = buildUniquePath(filepath, usedPaths)
    newEntries.push({
      id: `${filepath}-${file.size}-${file.lastModified}`,
      file,
      filepath,
      name: file.name,
      sizeBytes: file.size,
      contentType: file.type,
      isBinary,
      displayIcon: getFileIcon(file.name),
      willRenameTo: finalPath !== filepath ? finalPath : null,
    })

    if (isBinary) {
      nextNotes.push(`${filepath} will be stored as a binary placeholder with metadata.`)
    }
  }

  const nextTotal = totalQueuedBytes.value + newEntries.reduce((sum, entry) => sum + entry.sizeBytes, 0)
  if (nextTotal > MAX_TOTAL_SIZE_BYTES) {
    nextErrors.push(`Total upload size exceeds ${formatSize(MAX_TOTAL_SIZE_BYTES)}.`)
    validationErrors.value = nextErrors
    uploadNotes.value = nextNotes
    clearNativeInputs()
    return
  }

  queuedFiles.value = [...queuedFiles.value, ...newEntries]
  validationErrors.value = nextErrors
  uploadNotes.value = nextNotes
  clearNativeInputs()
}

const onFileChange = (event: Event) => {
  const files = Array.from((event.target as HTMLInputElement).files || [])
  if (files.length > 0) {
    makeEntries(files)
  }
}

const onZipChange = (event: Event) => {
  const files = Array.from((event.target as HTMLInputElement).files || []).filter((file) => /\.zip$/i.test(file.name))
  makeEntries(files)
}

const onFileDrop = (event: DragEvent) => {
  isDragging.value = false
  const files = Array.from(event.dataTransfer?.files || [])
  makeEntries(files)
}

const clearQueue = () => {
  queuedFiles.value = []
  validationErrors.value = []
  uploadNotes.value = []
  clearNativeInputs()
}

const uploadFiles = async () => {
  if (queuedFiles.value.length === 0) return

  uploading.value = true
  validationErrors.value = []

  try {
    for (const entry of queuedFiles.value) {
      const finalPath = entry.willRenameTo || entry.filepath
      const content = await readFileContent(entry)
      await projectsApi.addFile(projectId.value, {
        name: finalPath.split('/').pop() || entry.name,
        filepath: finalPath,
        content,
        contentType: entry.contentType,
        sizeBytes: entry.sizeBytes,
        isBinary: entry.isBinary,
      } as {
        name: string
        filepath?: string
        content: string
        contentType?: string
        sizeBytes?: number
        isBinary?: boolean
      })
    }

    uploadNotes.value = [`Uploaded ${queuedFiles.value.length} item(s) successfully.`]
    queuedFiles.value = []
    await store.loadProjectFiles(projectId.value)
  } catch (error) {
    console.error('Upload error:', error)
    validationErrors.value = ['Upload failed. Please try again.']
  } finally {
    uploading.value = false
    clearNativeInputs()
  }
}
</script>

<style scoped>
.upload-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #dde5f0;
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(244, 247, 251, 0.98)),
    #fff;
}

.upload-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.upload-header h3 {
  margin: 0;
  color: #17324d;
}

.upload-subtitle {
  margin: 0.35rem 0 0;
  color: #60758d;
  font-size: 0.9rem;
  line-height: 1.5;
}

.upload-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.hidden-input {
  display: none;
}

.secondary-btn,
.primary-btn,
.ghost-btn {
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.secondary-btn {
  border: 1px solid #b8c7d9;
  background: white;
  color: #264a68;
  padding: 0.6rem 0.95rem;
}

.primary-btn {
  border: none;
  background: linear-gradient(135deg, #227c9d, #17a398);
  color: white;
  padding: 0.75rem 1.2rem;
}

.ghost-btn {
  border: 1px solid #d3dbe5;
  background: transparent;
  color: #546779;
  padding: 0.75rem 1.2rem;
}

.secondary-btn:hover,
.primary-btn:hover,
.ghost-btn:hover {
  transform: translateY(-1px);
}

.upload-zone {
  border: 2px dashed #a8bdd2;
  border-radius: 18px;
  padding: 1.2rem;
  background: linear-gradient(135deg, rgba(34, 124, 157, 0.05), rgba(23, 163, 152, 0.08));
  text-align: center;
}

.upload-zone.drag-over {
  border-color: #227c9d;
  box-shadow: 0 0 0 4px rgba(34, 124, 157, 0.08);
}

.upload-zone-title {
  margin: 0;
  color: #17324d;
  font-weight: 700;
}

.upload-zone-meta {
  margin: 0.4rem 0 0;
  color: #64768a;
  font-size: 0.88rem;
}

.feedback {
  border-radius: 14px;
  padding: 0.85rem 1rem;
  font-size: 0.9rem;
}

.feedback p {
  margin: 0.2rem 0;
}

.feedback-error {
  background: #fff1f0;
  color: #aa3d37;
  border: 1px solid #f3c5c0;
}

.feedback-info {
  background: #eef9ff;
  color: #26506b;
  border: 1px solid #cce8f5;
}

.queue-panel {
  border: 1px solid #dde5f0;
  border-radius: 16px;
  background: white;
  overflow: hidden;
}

.queue-summary {
  display: flex;
  justify-content: space-between;
  padding: 0.9rem 1rem;
  background: #f6f9fc;
  color: #2d465e;
  border-bottom: 1px solid #ebf1f7;
}

.tree-preview {
  max-height: 300px;
  overflow: auto;
  padding: 0.75rem 1rem 1rem;
}

.tree-root {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.queue-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 0.9rem 1rem 1rem;
  border-top: 1px solid #ebf1f7;
}

@media (max-width: 900px) {
  .upload-header {
    flex-direction: column;
  }

  .queue-actions {
    flex-direction: column;
  }
}
</style>
