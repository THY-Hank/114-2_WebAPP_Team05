import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import MainLayout from '../layouts/MainLayout.vue'
import CodeView from '../views/CodeView.vue'
import ChatView from '../views/ChatView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/',
      component: MainLayout,
      children: [
        {
          path: 'projects',
          name: 'projects',
          component: () => import('../views/ProjectListView.vue'),
        },
        {
          path: 'projects/new',
          name: 'createProject',
          component: () => import('../views/CreateProjectView.vue'),
        },
        {
          path: 'projects/:projectId/code',
          name: 'code',
          component: CodeView,
        },
        {
          path: 'projects/:projectId/settings',
          name: 'projectSettings',
          component: () => import('../views/ProjectSettingsView.vue'),
        },
        {
          path: 'invitations',
          name: 'invitations',
          component: () => import('../views/InvitationsView.vue'),
        },
        {
          path: 'projects/:projectId/chat',
          name: 'chat',
          component: ChatView,
        },
      ],
    },
  ],
})

export default router
