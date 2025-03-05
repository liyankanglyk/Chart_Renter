import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: {
      title: '武汉租房数据分析',
      requiresAuth: true  // 需要登录才能访问
    }
  },
  {
    path: '/crawler',
    name: 'crawler',
    component: () => import('../views/Crawler.vue'),
    meta: {
      title: '数据采集',
      requiresAuth: true
    }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: {
      title: '用户登录'
    }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/Register.vue'),
    meta: {
      title: '用户注册'
    }
  },
  {
    path: '/analysis',
    name: 'analysis',
    component: () => import('../views/Analysis.vue'),
    meta: {
      title: '数据分析',
      requiresAuth: true  // 需要登录才能访问
    }
  },
  {
    path: '/prediction',
    name: 'prediction',
    component: () => import('../views/Prediction.vue'),
    meta: {
      title: '租金预测',
      requiresAuth: true  // 需要登录才能访问
    }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || '武汉租房数据分析系统'
  
  // 检查该路由是否需要登录权限
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 如果需要登录权限且未登录，则重定向到登录页
    if (!store.state.isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }  // 保存原本要去的路径
      })
    } else {
      next()
    }
  } else {
    // 如果已登录且访问登录/注册页，重定向到首页
    if (store.state.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
      next('/')
    } else {
      next()
    }
  }
})

export default router 