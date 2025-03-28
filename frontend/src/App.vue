<template>
  <router-view />
</template>

<script>
import { onMounted } from 'vue'
import { useStore } from 'vuex'
import { authApi } from './api/auth'

export default {
  name: 'App',
  setup() {
    const store = useStore()
    
    const checkUserStatus = async () => {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          // 尝试获取用户信息
          const response = await authApi.getUserInfo()
          store.dispatch('login', response.user)
        } catch (error) {
          console.error('获取用户信息失败:', error)
          // 如果获取失败，清除token
          localStorage.removeItem('token')
        }
      }
    }
    
    onMounted(() => {
      checkUserStatus()
    })
    
    return {}
  }
}
</script>

<style>
#app {
  font-family: 'PingFang SC', 'Helvetica Neue', Helvetica, 'microsoft yahei', arial, STHeiTi, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
}
</style>
