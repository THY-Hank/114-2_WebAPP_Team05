<template>
  <div v-if="selectedFile" class="code-view">
    <div class="code-header" style="display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h3>{{ selectedFile.name }}</h3>
        <p class="file-path">{{ selectedFile.filepath || selectedFile.name }}</p>
        <p v-if="selectedFile.isBinary" class="binary-meta">
          Binary placeholder · {{ selectedFile.contentType || 'application/octet-stream' }} · {{ formatSize(selectedFile.sizeBytes || 0) }}
        </p>
      </div>
      <div>
        <button class="share-btn" @click="$emit('share-full-file')">Share to Chat</button>
        <button class="delete-file-btn" @click="$emit('delete-file')">Delete File</button>
      </div>
    </div>
    
    <!-- Code Editor with Line Numbers -->
    <div class="code-container">
      <div class="code-wrapper">
        <div class="line-numbers" ref="lineNumbersEl">
          <div v-for="(line, idx) in codeLines" :key="`line-num-${idx}`" class="line-number">
            {{ (idx as number) + 1 }}
          </div>
        </div>
        <div class="code-content" ref="codeContentEl" @scroll="syncScroll">
          <div
            v-for="(line, idx) in codeLines"
            :key="`code-line-${idx}`"
            class="line"
            :class="{ 'line-selected': isLineInSelection((idx as number) + 1) }"
            @mousedown="onLineMouseDown((idx as number) + 1)"
            @mouseenter="onLineMouseEnter((idx as number) + 1)"
            @mouseup="onLineMouseUp"
          >{{ line || '\u00A0' }}</div>
        </div>
      </div>
      
      <!-- Line Selection Action Button -->
      <div v-if="selectionStart !== null && selectionEnd !== null" class="selection-action">
        <button @click="$emit('comment-lines', { start: selectionStart, end: selectionEnd })" class="action-btn-comment">💬 Comment Lines {{ selectionStart }}-{{ selectionEnd }}</button>
        <button @click="$emit('share-lines', { start: selectionStart, end: selectionEnd })" class="action-btn-share">📤 Share Lines {{ selectionStart }}-{{ selectionEnd }}</button>
      </div>
    </div>
  </div>
  <div v-else>
    <p>Select a file to view its content and comments.</p>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { ref, computed } from 'vue'

const props = defineProps<{
  selectedFile: any
}>()

const emit = defineEmits<{
  'share-full-file': []
  'delete-file': []
  'comment-lines': [payload: { start: number; end: number }]
  'share-lines': [payload: { start: number; end: number }]
}>()

const selectionStart = ref<number | null>(null)
const selectionEnd = ref<number | null>(null)
const isSelecting = ref(false)
const lineNumbersEl = ref<HTMLDivElement>()
const codeContentEl = ref<HTMLDivElement>()

const codeLines = computed(() => {
  return props.selectedFile?.content?.split('\n') || []
})

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const syncScroll = () => {
  if (lineNumbersEl.value && codeContentEl.value) {
    lineNumbersEl.value.scrollTop = codeContentEl.value.scrollTop
  }
}

const isLineInSelection = (lineNum: number) => {
  if (selectionStart.value === null || selectionEnd.value === null) {
    return false
  }
  const min = Math.min(selectionStart.value, selectionEnd.value)
  const max = Math.max(selectionStart.value, selectionEnd.value)
  return lineNum >= min && lineNum <= max
}

const onLineMouseDown = (lineNum: number) => {
  isSelecting.value = true
  selectionStart.value = lineNum
  selectionEnd.value = lineNum
}

const onLineMouseEnter = (lineNum: number) => {
  if (isSelecting.value && selectionStart.value !== null) {
    selectionEnd.value = lineNum
  }
}

const onLineMouseUp = () => {
  isSelecting.value = false
}
</script>

<style scoped>
.code-view {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
}

.code-header {
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
  background: #f9f9f9;
}

.code-header h3 {
  margin: 0;
  color: #333;
}

.file-path,
.binary-meta {
  margin: 0.25rem 0 0;
  color: #6d8195;
  font-size: 0.85rem;
}

.share-btn,
.delete-file-btn {
  padding: 0.4rem 0.8rem;
  margin-left: 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.share-btn {
  background: #4caf50;
  color: white;
}

.share-btn:hover {
  background: #45a049;
}

.delete-file-btn {
  background: #ff5252;
  color: white;
}

.delete-file-btn:hover {
  background: #ff1744;
}

.code-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 400px;
  max-height: 600px;
}

.code-wrapper {
  display: flex;
  flex-grow: 1;
  overflow: hidden;
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 0.9rem;
  background: white;
  min-height: 0;
}

.line-numbers {
  background: #f5f5f5;
  border-right: 1px solid #e0e0e0;
  padding: 1rem 0.5rem;
  text-align: right;
  color: #999;
  font-size: 0.9rem;
  overflow: hidden;
  min-width: 60px;
  user-select: none;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  max-height: 100%;
  line-height: 1.4;
}

.line-number {
  height: 1.4em;
  line-height: 1.4;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.code-content {
  flex-grow: 1;
  overflow-y: auto;
  overflow-x: auto;
  padding: 1rem 0.5rem;
  white-space: pre;
  overflow-wrap: break-word;
  min-height: 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.line {
  height: 1.4em;
  line-height: 1.4;
  padding: 0;
  margin: 0;
  cursor: text;
  user-select: text;
  transition: background 0.1s;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.line:hover {
  background: #f9f9f9;
}

.line-selected {
  background: #c8e6c9;
}

.selection-action {
  padding: 1rem;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 0.5rem;
  background: #f9f9f9;
  flex-wrap: wrap;
}

.action-btn-comment,
.action-btn-share {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
  white-space: nowrap;
}

.action-btn-comment {
  background: #2196f3;
  color: white;
}

.action-btn-comment:hover {
  background: #1976d2;
}

.action-btn-share {
  background: #4caf50;
  color: white;
}

.action-btn-share:hover {
  background: #45a049;
}
</style>
