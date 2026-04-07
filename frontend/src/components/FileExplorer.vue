<template>
  <div class="file-explorer">
    <div class="file-explorer-header">
      <h3>Project Files</h3>
      <p>{{ projectFiles.length }} item(s)</p>
    </div>

    <ul class="tree-root">
      <ProjectFileTreeNode
        v-for="node in fileTree"
        :key="node.path"
        :node="node"
        :expanded-paths="expandedPaths"
        :selected-file-id="selectedFileId"
        @toggle="toggleFolder"
        @select-file="selectFile"
      />
    </ul>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useMainStore } from '@/stores/main'
import ProjectFileTreeNode from '@/components/ProjectFileTreeNode.vue'

type TreeNode = {
  type: 'folder' | 'file'
  name: string
  path: string
  icon?: string
  file?: any
  children?: TreeNode[]
}

const route = useRoute()
const store = useMainStore()

const expandedPaths = ref(new Set<string>(['src', 'root']))
const selectedFileId = ref<number | null>(null)

const emit = defineEmits<{
  'select-file': [file: any]
}>()

const projectId = computed(() => parseInt(route.params.projectId as string, 10))
const projectFiles = computed(() => store.getProjectFiles(projectId.value))

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
    cpp: '⬜',
    c: '⬜',
    h: '⬜',
    cs: '🔷',
    rb: '💎',
    go: '🐹',
    rs: '🦀',
    html: '🌐',
    css: '🎨',
    json: '📋',
    xml: '📄',
    yaml: '⚙️',
    yml: '⚙️',
    md: '📝',
    zip: '🗜️',
  }
  return iconMap[ext || ''] || '📄'
}

const fileTree = computed<TreeNode[]>(() => {
  const root: TreeNode[] = []
  const folderMap = new Map<string, TreeNode>()

  const ensureFolder = (path: string, name: string, container: TreeNode[]) => {
    const existing = folderMap.get(path)
    if (existing) {
      return existing
    }
    const node: TreeNode = { type: 'folder', name, path, children: [] }
    folderMap.set(path, node)
    container.push(node)
    return node
  }

  projectFiles.value.forEach((file: any) => {
    const filepath = (file.filepath || file.name || '').replace(/\\/g, '/')
    const segments = filepath.split('/').filter(Boolean)
    const finalSegments = segments.length > 0 ? segments : [file.name]

    let children = root
    let currentPath = ''

    finalSegments.forEach((segment: string, index: number) => {
      currentPath = currentPath ? `${currentPath}/${segment}` : segment
      const isFile = index === finalSegments.length - 1

      if (isFile) {
        children.push({
          type: 'file',
          name: segment,
          path: currentPath,
          icon: getFileIcon(segment),
          file,
        })
      } else {
        const folder = ensureFolder(currentPath, segment, children)
        children = folder.children || []
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
      if (node.children) {
        sortNodes(node.children)
      }
    })
  }

  sortNodes(root)
  return root
})

const toggleFolder = (folderPath: string) => {
  if (expandedPaths.value.has(folderPath)) {
    expandedPaths.value.delete(folderPath)
  } else {
    expandedPaths.value.add(folderPath)
  }
}

const selectFile = (file: any) => {
  selectedFileId.value = file.id
  emit('select-file', file)
}
</script>

<style scoped>
.file-explorer {
  flex-grow: 1;
  overflow-y: auto;
  border: 1px solid #dae4ef;
  border-radius: 16px;
  padding: 1rem;
  background: linear-gradient(180deg, #ffffff, #f7fafd);
}

.file-explorer-header {
  margin-bottom: 0.85rem;
}

.file-explorer-header h3 {
  margin: 0;
  color: #17324d;
}

.file-explorer-header p {
  margin: 0.3rem 0 0;
  font-size: 0.85rem;
  color: #667b90;
}

.tree-root {
  list-style: none;
  padding: 0;
  margin: 0;
}
</style>
