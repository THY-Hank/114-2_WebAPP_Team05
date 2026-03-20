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
      redirect: '/main/code',
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
      path: '/main',
      component: MainLayout,
      children: [
        {
          path: 'code',
          name: 'code',
          component: CodeView,
        },
        {
          path: 'chat',
          name: 'chat',
          component: ChatView,
        },
      ],
    },
  ],
})

export default router
