<template>
  <div class="analysis">
    <!-- 顶部导航栏 -->
    <el-menu
      :default-active="activeIndex"
      class="nav-menu"
      mode="horizontal"
      router
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#ffd04b">
      <el-menu-item index="/">首页</el-menu-item>
      <el-menu-item index="/analysis">数据分析</el-menu-item>
      <el-menu-item index="/prediction">租金预测</el-menu-item>
      <div class="flex-grow"></div>
      <el-menu-item v-if="!isAuthenticated" index="/login">登录</el-menu-item>
      <el-menu-item v-if="isAuthenticated" @click="handleLogout">退出</el-menu-item>
    </el-menu>

    <div class="main-content">
      <h1>数据分析</h1>
      <div class="analysis-container">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>开发中...</span>
            </div>
          </template>
          <div class="card-content">
            <p>数据分析功能正在开发中，敬请期待！</p>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Analysis',
  setup() {
    const store = useStore()
    const router = useRouter()
    const activeIndex = ref('/analysis')

    const isAuthenticated = computed(() => store.state.isAuthenticated)

    const handleLogout = () => {
      store.dispatch('logout')
      router.push('/')
    }

    return {
      activeIndex,
      isAuthenticated,
      handleLogout
    }
  }
}
</script>

<style scoped lang="scss">
.analysis {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.nav-menu {
  padding: 0 20px;
}

.flex-grow {
  flex-grow: 1;
}

.main-content {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;

  h1 {
    margin-bottom: 30px;
    color: #303133;
  }
}

.analysis-container {
  .chart-card {
    margin-bottom: 20px;
    
    .card-header {
      font-weight: bold;
    }
    
    .card-content {
      padding: 20px;
      text-align: center;
      color: #909399;
    }
  }
}
</style> 