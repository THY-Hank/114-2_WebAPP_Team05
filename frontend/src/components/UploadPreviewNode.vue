<template>
  <li class="tree-node">
    <div class="tree-row">
      <span class="tree-icon">{{ node.type === 'folder' ? '📁' : node.displayIcon }}</span>
      <span class="tree-label">{{ node.name }}</span>
      <span v-if="node.type === 'file'" class="tree-meta">
        {{ formatSize(node.sizeBytes || 0) }}
        <span v-if="node.isBinary"> · binary</span>
        <span v-if="node.willRenameTo"> · rename to {{ node.willRenameTo }}</span>
      </span>
    </div>
    <ul v-if="node.children?.length" class="tree-children">
      <UploadPreviewNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
      />
    </ul>
  </li>
</template>

<script setup lang="ts">
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

defineProps<{
  node: TreeNode
}>()

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
</script>

<script lang="ts">
export default {
  name: 'UploadPreviewNode',
}
</script>

<style scoped>
.tree-node {
  list-style: none;
}

.tree-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
}

.tree-icon {
  width: 1.2rem;
  text-align: center;
}

.tree-label {
  color: #18324d;
  font-weight: 500;
  word-break: break-all;
}

.tree-meta {
  color: #71869c;
  font-size: 0.82rem;
}

.tree-children {
  list-style: none;
  padding-left: 1.2rem;
  margin: 0;
}
</style>
