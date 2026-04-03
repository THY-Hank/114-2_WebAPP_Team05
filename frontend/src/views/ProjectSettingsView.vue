<template>
  <div class="settings-container">
    <h2>Project Settings</h2>
    
    <!-- Basic Project Info -->
    <div class="info-section">
      <h3>📋 Basic Information</h3>
      <div class="info-card">
        <div class="info-field">
          <label>Project Name:</label>
          <div style="display: flex; gap: 0.5rem; align-items: center;">
            <input 
              v-if="isEditing" 
              v-model="editedName"
              class="project-name-input"
              placeholder="Enter project name"
            />
            <span v-else class="project-name-display">{{ currentProject?.name }}</span>
            <button 
              v-if="isOwner"
              @click="toggleEdit"
              :class="isEditing ? 'cancel-btn' : 'edit-btn'"
            >
              {{ isEditing ? 'Cancel' : 'Edit' }}
            </button>
            <button 
              v-if="isEditing"
              @click="saveName"
              class="save-btn"
              :disabled="!editedName || editedName === currentProject?.name"
            >
              Save
            </button>
          </div>
        </div>
        <div class="info-field">
          <label>Owner:</label>
          <span>{{ ownerName }}</span>
        </div>
      </div>
    </div>

    <!-- Access Permissions -->
    <div class="permissions-section">
      <h3>🔐 Access Permissions</h3>
      <div class="permission-info">
        <p class="owner-badge" v-if="isOwner">✓ You are the Owner of this Project</p>
        <p v-else>You are a Member of this Project</p>
        <div class="permission-description">
          <strong>Owner Rights:</strong> Can edit project settings, manage members, delete project
          <br/>
          <strong>Member Rights:</strong> Can view files, add files, comment on code
        </div>
      </div>
    </div>

    <!-- Members Management -->
    <div class="members-section">
      <h3>👥 Team Members</h3>
      <div class="members-card">
        <!-- Add Member Form (Owner only) -->
        <div v-if="isOwner" class="add-member-form">
          <input 
            v-model="newMemberEmail"
            type="email"
            placeholder="Enter member email to invite"
            class="member-email-input"
            @keyup.enter="inviteMember"
          />
          <button @click="inviteMember" :disabled="!newMemberEmail">Invite</button>
        </div>

        <!-- Members List -->
        <div class="members-list">
          <div v-if="members.length === 0" class="no-members">
            No members in this project yet
          </div>
          <div v-for="member in members" :key="member.id" class="member-item">
            <div class="member-info">
              <div class="member-name">
                {{ member.name }}
                <span v-if="member.isOwner" class="owner-badge-small">Owner</span>
              </div>
              <div class="member-email">{{ member.email }}</div>
            </div>
            <div class="member-actions">
              <button 
                v-if="isOwner && !member.isOwner && member.id !== currentUser?.id"
                @click="removeMember(member.id)"
                class="remove-btn"
              >
                Remove
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Danger Zone -->
    <div v-if="isOwner" class="danger-zone">
      <h3>⚠️ Danger Zone</h3>
      <p>Deleting this project is irreversible. It will destroy all associated code files, comments, and member assignments permanently.</p>
      <button class="delete-project-btn" @click="handleDeleteProject">Delete Project</button>
    </div>
    <div v-else class="danger-zone warning">
      <h3>🚫 Restricted Danger Zone</h3>
      <p>Only the owner of this project can authorize a catastrophic deletion.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { computed, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMainStore } from '@/stores/main'
import { projectsApi } from '@/api/projects'

const store = useMainStore()
const router = useRouter()
const route = useRoute()

const projectId = computed(() => Number(route.params.projectId))
const members = ref<any[]>([])
const newMemberEmail = ref('')
const isEditing = ref(false)
const editedName = ref('')

// Retrieve the project from the current user bounds
const currentProject = computed(() => {
  if (!store.currentUser) return null
  return store.currentUser.projects.find((p: any) => p.id === projectId.value)
})

const currentUser = computed(() => store.currentUser)

const isOwner = computed(() => {
  if (!store.currentUser || !currentProject.value) return false
  return currentProject.value.owner_id === store.currentUser.id
})

const ownerName = computed(() => {
  const owner = members.value.find(m => m.isOwner)
  return owner ? (owner.name || owner.email) : 'Unknown'
})

onMounted(() => {
  loadProjectSettings()
})

const loadProjectSettings = async () => {
  try {
    const res = await projectsApi.fetchProjectSettings(projectId.value)
    if (res.ok) {
      const data = await res.json()
      members.value = data.members || []
    } else {
      console.error('Failed to load project settings')
    }
  } catch (error) {
    console.error('Error loading project settings:', error)
  }
}

const toggleEdit = () => {
  if (!isEditing.value) {
    editedName.value = currentProject.value?.name || ''
  }
  isEditing.value = !isEditing.value
}

const saveName = async () => {
  if (!editedName.value || editedName.value === currentProject.value?.name) {
    isEditing.value = false
    return
  }

  try {
    const res = await projectsApi.updateProjectName(projectId.value, editedName.value)
    if (res.ok) {
      // Update local project name
      if (currentProject.value) {
        currentProject.value.name = editedName.value
      }
      isEditing.value = false
      alert('Project name updated successfully!')
    } else {
      alert('Failed to update project name')
    }
  } catch (error) {
    console.error('Error updating project name:', error)
    alert('Error updating project name')
  }
}

const inviteMember = async () => {
  if (!newMemberEmail.value.trim()) {
    alert('Please enter an email address')
    return
  }

  try {
    const res = await projectsApi.addProjectMember(projectId.value, newMemberEmail.value)
    if (res.ok) {
      alert('Invitation sent successfully!')
      newMemberEmail.value = ''
    } else {
      const data = await res.json()
      alert(data.error || 'Failed to send invitation')
    }
  } catch (error) {
    console.error('Error inviting member:', error)
    alert('Error sending invitation')
  }
}

const removeMember = async (memberId: number) => {
  const confirmed = confirm('Are you sure you want to remove this member from the project?')
  if (!confirmed) return

  try {
    const res = await projectsApi.removeProjectMember(projectId.value, memberId)
    if (res.ok) {
      // Remove from local list
      members.value = members.value.filter(m => m.id !== memberId)
      alert('Member removed successfully!')
    } else {
      const data = await res.json()
      alert(data.error || 'Failed to remove member')
    }
  } catch (error) {
    console.error('Error removing member:', error)
    alert('Error removing member')
  }
}

const handleDeleteProject = async () => {
  const confirmed = confirm(`Are you absolutely sure you want to delete this workspace? This action CANNOT be undone.`)
  if (confirmed) {
    try {
      const res = await projectsApi.deleteProject(projectId.value)
      if (res.ok || res.status === 204) {
        alert('Project deleted successfully')
        router.push('/projects')
      } else {
        alert('Failed to delete project. You may not be the owner or a network error occurred.')
      }
    } catch (error) {
      console.error('Error deleting project:', error)
      alert('Error deleting project')
    }
  }
}
</script>

<style scoped>
.settings-container {
  padding: 2rem;
  max-width: 1000px;
}

.settings-container h2 {
  margin-bottom: 2rem;
  color: #333;
}

.info-section,
.permissions-section,
.members-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  margin-bottom: 2rem;
}

.info-section h3,
.permissions-section h3,
.members-section h3 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.1rem;
}

.info-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-field {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.info-field label {
  min-width: 150px;
  font-weight: 600;
  color: #555;
}

.project-name-display {
  font-size: 1.1rem;
  color: #333;
  font-weight: 500;
}

.project-name-input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1.1rem;
  min-width: 300px;
}

.project-name-input:focus {
  outline: none;
  border-color: #4caf50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.edit-btn,
.save-btn,
.cancel-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.edit-btn {
  background: #2196f3;
  color: white;
}

.edit-btn:hover {
  background: #1976d2;
}

.save-btn {
  background: #4caf50;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #45a049;
}

.save-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.cancel-btn {
  background: #ff9800;
  color: white;
}

.cancel-btn:hover {
  background: #f57c00;
}

.permission-info {
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 6px;
}

.permission-info p {
  margin: 0.5rem 0;
}

.owner-badge {
  color: #4caf50;
  font-weight: 600;
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #e8f5e9;
  border-radius: 20px;
  font-size: 0.9rem;
}

.permission-description {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
  font-size: 0.9rem;
  color: #666;
  line-height: 1.6;
}

.members-card {
  background: #f9f9f9;
  padding: 1.5rem;
  border-radius: 6px;
}

.add-member-form {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.member-email-input {
  flex: 1;
  padding: 0.6rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.member-email-input:focus {
  outline: none;
  border-color: #4caf50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.add-member-form button {
  padding: 0.6rem 1.5rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  white-space: nowrap;
}

.add-member-form button:hover:not(:disabled) {
  background: #45a049;
}

.add-member-form button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.members-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.no-members {
  padding: 2rem;
  text-align: center;
  color: #999;
  background: white;
  border-radius: 4px;
}

.member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.member-info {
  flex: 1;
}

.member-name {
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.owner-badge-small {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  background: #fff3e0;
  color: #f57c00;
  border-radius: 12px;
  font-weight: 600;
}

.member-email {
  font-size: 0.85rem;
  color: #999;
  margin-top: 0.25rem;
}

.member-actions {
  display: flex;
  gap: 0.5rem;
}

.remove-btn {
  padding: 0.4rem 1rem;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.remove-btn:hover {
  background: #d32f2f;
}

.danger-zone {
  background: #fff5f5;
  border: 1px solid #fc8181;
  padding: 1.5rem;
  border-radius: 8px;
}

.danger-zone h3 {
  color: #c53030;
  margin: 0 0 1rem 0;
}

.danger-zone p {
  color: #744210;
  margin: 0 0 1rem 0;
  line-height: 1.6;
}

.danger-zone.warning {
  border-color: #f6ad55;
  background: #fffaf0;
}

.danger-zone.warning h3 {
  color: #dd6b20;
}

.danger-zone.warning p {
  color: #7c2d12;
}

.delete-project-btn {
  padding: 0.7rem 1.5rem;
  background: #c53030;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.delete-project-btn:hover {
  background: #a71d1d;
}
</style>
