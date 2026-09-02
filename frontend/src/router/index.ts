import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/chat' },
    { path: '/chat', component: () => import('@/views/ChatView.vue') },
    { path: '/operations', component: () => import('@/views/OperationsView.vue') },
    { path: '/repositories', redirect: '/operations' },
    { path: '/builds', redirect: '/operations' },
    { path: '/deployments', redirect: '/operations' },
    { path: '/incidents', redirect: '/operations' },
    { path: '/issues', redirect: '/operations' },
    { path: '/:pathMatch(.*)*', component: () => import('@/views/NotFoundView.vue') },
  ],
})

export default router
