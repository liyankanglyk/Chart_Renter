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
  },
  {
    path: '/RentalPredictionScatterPlot',
    name: 'RentalPredictionScatterPlot',
    component: () => import('../views/RentalPredictionScatterPlot.vue'),
    meta: {
      title: '区域租金预测散点图',
      requiresAuth: true  // 需要登录才能访问
    }
  },
  {
    path: '/RestAnalysis',
    name: 'RestAnalysis',
    component: () => import('../views/RestAnalysis.vue'),
    meta: {
      title: '租金分析',
      requiresAuth: true  // 需要登录才能访问
    }
  },
  {
    path: '/restNumber',
    name: 'restNumber',
    component: () => import('../views/restNumber.vue'),
    meta: {
      title: '房子数量',
      requiresAuth: true  // 需要登录才能访问
    }
  },
  {
    path: '/averageHousePrice',
    name: 'averageHousePrice',
    component: () => import('../views/averageHousePrice.vue'),
    meta: {
      title: '房子金额平均值',
      requiresAuth: true  // 需要登录才能访问
    }
  },
  {
    path: '/map',
    name: 'map',
    component: () => import('../views/map.vue'),
    meta: {
      title: '地图',
      requiresAuth: true  // 需要登录才能访问
    }
  },
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
    if (!store.state.isAuthenticated && to.path!== '/analysis') {
      next({
        path: '/login',
        query: { redirect: to.fullPath }  // 保存原本要去的路径
      })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router