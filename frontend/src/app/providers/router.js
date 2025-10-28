import { createRouter, createWebHistory } from 'vue-router'
import { TaskListPage } from '@pages/task-list'
import { TaskDetailPage } from '@pages/task-detail'

const routes = [
  {
    path: '/',
    name: 'TaskList',
    component: TaskListPage,
    meta: {
      title: '任务列表'
    }
  },
  {
    path: '/tasks/:id',
    name: 'TaskDetail',
    component: TaskDetailPage,
    meta: {
      title: '任务详情'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - YouTube 下载器`
  }
  next()
})

export { router }

