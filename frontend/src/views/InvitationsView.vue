<template>
  <div class="invitations-container">
    <h2>Invitations Inbox</h2>
    <div v-if="store.invitations.length === 0" class="empty-state">
      <p>No pending project invitations right now.</p>
    </div>
    <ul class="invitation-list" v-else>
      <li v-for="inv in store.invitations" :key="inv.id" class="invitation-card">
        <div class="inv-info">
          <h3>{{ inv.project_name }}</h3>
          <p>Invited by <strong>{{ inv.inviter_name }}</strong></p>
          <small>{{ new Date(inv.created_at).toLocaleString() }}</small>
        </div>
        <div class="inv-actions">
          <button class="btn-accept" @click="respond(inv.id, 'accept')">Accept</button>
          <button class="btn-decline" @click="respond(inv.id, 'decline')">Decline</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { useMainStore } from '@/stores/main'

const store = useMainStore()

const respond = async (invId: number, action: 'accept'|'decline') => {
  await store.respondInvitation(invId, action)
}
</script>

<style scoped>
.invitations-container {
  padding: 2rem;
  max-width: 800px;
}
.empty-state {
  color: var(--medium-gray);
  font-style: italic;
  margin-top: 1rem;
}
.invitation-list {
  list-style: none;
  padding: 0;
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.invitation-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 1.5rem;
  border-radius: var(--border-radius);
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  border: 1px solid #eaeaea;
}
.inv-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--primary-color);
}
.inv-info p {
  margin: 0;
  color: var(--text-color);
}
.inv-info small {
  color: #888;
}
.inv-actions {
  display: flex;
  gap: 1rem;
}
.btn-accept {
  background: #38a169;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-weight: bold;
}
.btn-accept:hover { background: #2f855a; }
.btn-decline {
  background: white;
  color: #e53e3e;
  border: 1px solid #e53e3e;
  padding: 0.6rem 1.2rem;
  border-radius: var(--border-radius);
  cursor: pointer;
}
.btn-decline:hover { background: #fff5f5; }
</style>
