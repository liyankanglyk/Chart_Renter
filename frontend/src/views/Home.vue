<template>
  <div class="home">
    <!-- 使用导航栏组件 -->
    <NavBar :active-index="activeIndex" @logout="handleLogout" />

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-row :gutter="20">
        <el-col :span="24">
          <div class="welcome-section">
            <h1>武汉租房市场数据分析系统</h1>
            <p>基于Python的数据采集、分析与可视化平台</p>
          </div>
        </el-col>
      </el-row>

      <!-- 功能卡片区域 -->
      <el-row :gutter="20" class="feature-cards">
        <el-col :span="8">
          <el-card class="feature-card" @click="handleCrawlerClick">
            <template #header>
              <div class="card-header">
                <span>数据采集</span>
              </div>
            </template>
            <div class="card-content">
              <p>实时爬取武汉各区域租房数据</p>
              <p>自动更新市场动态信息</p>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <span>数据分析</span>
              </div>
            </template>
            <div class="card-content">
              <p>多维度分析租房市场趋势</p>
              <p>可视化展示分析结果</p>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <span>租金预测</span>
              </div>
            </template>
            <div class="card-content">
              <p>基于机器学习的租金预测</p>
              <p>辅助租房决策支持</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'

export default {
  name: 'Home',
  components: {
    NavBar
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const activeIndex = ref('/')

    const isAuthenticated = computed(() => store.state.isAuthenticated)

    const handleLogout = () => {
      store.dispatch('logout')
      router.push('/')
    }

    const handleCrawlerClick = () => {
      if (!isAuthenticated.value) {
        router.push('/login')
      } else {
        router.push('/crawler')
      }
    }

    return {
      activeIndex,
      isAuthenticated,
      handleLogout,
      handleCrawlerClick
    }
  }
}
</script>

<style scoped lang="scss">
.home {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.flex-grow {
  flex-grow: 1;
}

.main-content {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  padding: 40px 0;
  margin-bottom: 40px;
  
  h1 {
    font-size: 2.5em;
    color: #303133;
    margin-bottom: 20px;
  }
  
  p {
    font-size: 1.2em;
    color: #606266;
  }
}

.feature-cards {
  margin-top: 40px;
  
  .feature-card {
    height: 100%;
    transition: all 0.3s;
    cursor: pointer;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
    }
    
    .card-header {
      font-size: 1.2em;
      font-weight: bold;
    }
    
    .card-content {
      padding: 20px 0;
      
      p {
        margin: 10px 0;
        color: #606266;
      }
    }
  }
}
</style> 