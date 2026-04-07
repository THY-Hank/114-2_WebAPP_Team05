<template>
  <li class="tree-node">
    <div
      class="tree-row"
      :class="{ clickable: node.type === 'file', selected: selectedFileId === node.file?.id }"
      @click="handleClick"
    >
      <button
        v-if="node.type === 'folder'"
        type="button"
        class="toggle-btn"
        @click.stop="$emit('toggle', node.path)"
      >
        {{ expanded ? '▼' : '▶' }}
      </button>
      <span v-else class="toggle-spacer"></span>
      <span class="tree-icon">{{ node.type === 'folder' ? '📁' : node.icon }}</span>
      <span class="tree-label">{{ node.name }}</span>
    </div>
    <ul v-if="node.type === 'folder' && expanded && node.children?.length" class="children">
      <ProjectFileTreeNode
        v-for="child in node.children"
        :key="child.path"
        :node="child"
        :expanded-paths="expandedPaths"
        :selected-file-id="selectedFileId"
        @toggle="$emit('toggle', $event)"
        @select-file="$emit('select-file', $event)"
      />
    </ul>
  </li>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type FileTreeNode = {
  type: 'folder' | 'file'
  name: string
  path: string
  icon?: string
  file?: any
  children?: FileTreeNode[]
}

const props = defineProps<{
  node: FileTreeNode
  expandedPaths: Set<string>
  selectedFileId?: number | null
}>()

const emit = defineEmits<{
  toggle: [path: string]
  'select-file': [file: unknown]
}>()

const expanded = computed(() => props.node.type === 'folder' && props.expandedPaths.has(props.node.path))

const handleClick = () => {
  if (props.node.type === 'file' && props.node.file) {
    emit('select-file', props.node.file)
  }
}
</script>

<script lang="ts">
export default {
  name: 'ProjectFileTreeNode',
}
</script>

<style scoped>
.tree-node {
  list-style: none;
}

.children {
  list-style: none;
  padding-left: 1rem;
  margin: 0.15rem 0 0;
}

.tree-row {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.45rem;
  border-radius: 8px;
}

.tree-row.clickable {
  cursor: pointer;
}

.tree-row.clickable:hover {
  background: #f5f8fb;
}

.tree-row.selected {
  background: #dbeefe;
  color: #15476c;
}

.toggle-btn,
.toggle-spacer {
  width: 1rem;
  flex-shrink: 0;
}

.toggle-btn {
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
  color: #5f7388;
}

.tree-icon {
  width: 1.1rem;
  text-align: center;
}

.tree-label {
  word-break: break-all;
}
</style>
