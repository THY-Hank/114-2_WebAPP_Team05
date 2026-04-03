<template>
  <div v-if="selectedFile" class="comments-container">
    <!-- Line Comments Section -->
    <div class="line-comments-section">
      <h4>Line Comments</h4>
      <div v-if="lineComments.length === 0" class="no-comments">No line comments yet</div>
      <div v-for="comment in lineComments" :key="comment.id" class="line-comment">
        <strong>{{ comment.author }}</strong>
        <span class="line-range">Lines {{ comment.startLine }}-{{ comment.endLine }}</span>
        <p>{{ comment.text }}</p>
      </div>
    </div>

    <!-- File-level Comments Section -->
    <div class="comments-section">
      <h4>File Comments</h4>
      <div v-for="comment in fileComments" :key="comment.id" class="comment">
        <p>
          <strong>{{ comment.author }}</strong>
        </p>
        <p>{{ comment.text }}</p>
      </div>
      <div class="comment-form">
        <textarea v-model="newComment" placeholder="Add a file comment..."></textarea>
        <button @click="$emit('add-comment', newComment)" class="add-comment-btn">Add File Comment</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { ref, computed } from 'vue'

const props = defineProps<{
  selectedFile: any
}>()

const emit = defineEmits<{
  'add-comment': [text: string]
}>()

const newComment = ref('')

const fileComments = computed(() => {
  return props.selectedFile?.comments?.filter((c: any) => !c.startLine) || []
})

const lineComments = computed(() => {
  return props.selectedFile?.comments?.filter((c: any) => c.startLine) || []
})
</script>

<style scoped>
.comments-container {
  padding: 1rem;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.line-comments-section,
.comments-section {
  margin-bottom: 1.5rem;
}

.line-comments-section h4,
.comments-section h4 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1rem;
}

.no-comments {
  color: #999;
  font-size: 0.9rem;
  padding: 1rem;
  text-align: center;
  background: #f9f9f9;
  border-radius: 4px;
}

.line-comment,
.comment {
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  background: #f9f9f9;
  border-left: 3px solid #4caf50;
  border-radius: 4px;
}

.line-comment strong,
.comment strong {
  color: #333;
}

.line-range {
  display: inline-block;
  margin-left: 0.5rem;
  padding: 0.2rem 0.5rem;
  background: #e8f5e9;
  border-radius: 3px;
  font-size: 0.85rem;
  color: #4caf50;
}

.line-comment p,
.comment p {
  margin: 0.5rem 0 0 0;
  color: #666;
  line-height: 1.5;
}

.comment-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 6px;
}

.comment-form textarea {
  padding: 0.5rem;
  font-family: inherit;
  font-size: 0.9rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  resize: vertical;
  min-height: 80px;
}

.comment-form textarea:focus {
  outline: none;
  border-color: #4caf50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.add-comment-btn {
  padding: 0.5rem 1rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.add-comment-btn:hover {
  background: #45a049;
}
</style>
