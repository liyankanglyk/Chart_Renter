<template>
  <div class="crawler">
    <!-- 顶部导航栏 -->
    <NavBar :active-index="activeIndex" @logout="handleLogout" />

    <div class="main-content">
      <h1>数据采集</h1>
      
      <div class="crawler-container">
        <el-card class="crawler-card">
          <div class="crawler-header">
            <h3>武汉租房数据采集</h3>
            <p>当前状态：{{ statusText }}</p>
          </div>
          
          <div class="progress-section">
            <el-progress 
              :percentage="progress" 
              :status="progressStatus"
              :stroke-width="20"
              :format="progressFormat" />
          </div>
          
          <div class="control-section">
            <el-button 
              type="primary" 
              :loading="isRunning"
              :disabled="isRunning"
              @click="startCrawler">
              {{ isRunning ? '采集中...' : '开始采集' }}
            </el-button>
            
            <el-button 
              type="danger" 
              :disabled="!isRunning"
              @click="stopCrawler">
              停止采集
            </el-button>
          </div>
          
          <div class="info-section">
            <p>已采集数据：{{ collectedCount }} 条</p>
            <p>预计剩余时间：{{ remainingTime }}</p>
          </div>
          
          <div class="log-section">
            <h4>采集日志</h4>
            <div class="log-content" ref="logContent">
              <p v-for="(log, index) in logs" :key="index" :class="log.type">
                {{ log.time }} - {{ log.message }}
              </p>
            </div>
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
import { ElMessage } from 'element-plus'
import apiClient from '../api/auth'
import NavBar from '../components/NavBar.vue'

export default {
  name: 'Crawler',
  components: {
    NavBar
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const activeIndex = ref('/crawler')
    const isAuthenticated = computed(() => store.state.isAuthenticated)
    
    // 爬虫状态
    const isRunning = ref(false)
    const progress = ref(0)
    const collectedCount = ref(0)
    const remainingTime = ref('--:--')
    const logs = ref([])
    const logContent = ref(null)
    
    // 用于存储定时器ID
    let progressTimer = null;
    const currentTaskId = ref(null);
    
    const statusText = computed(() => {
      return isRunning.value ? '运行中' : '已停止'
    })
    
    const progressStatus = computed(() => {
      if (progress.value === 100) return 'success'
      return isRunning.value ? '' : 'exception'
    })
    
    const progressFormat = (percentage) => {
      return isRunning.value ? `${percentage.toFixed(3)}%` : '已停止'
    }
    
    // 添加日志
    const addLog = (message, type = 'info') => {
      const time = new Date().toLocaleTimeString()
      logs.value.push({ time, message, type })
      // 自动滚动到底部
      setTimeout(() => {
        if (logContent.value) {
          logContent.value.scrollTop = logContent.value.scrollHeight
        }
      }, 100)
    }
    
    // 开始爬虫
    const startCrawler = async () => {
      try {
        // 清除之前的轮询
        if (progressTimer) {
          clearInterval(progressTimer);
          progressTimer = null;
        }
        
        isRunning.value = true
        progress.value = 0
        collectedCount.value = 0
        logs.value = []
        addLog('开始数据采集...', 'info')
        
        // 调用后端接口启动爬虫
        const response = await apiClient.post('/crawler/start')
        const taskId = response.data.task_id
        
        // 更新当前任务ID
        currentTaskId.value = taskId;
        
        // 保存上一次消息，避免重复显示
        let lastMessage = '';
        
        // 开始轮询进度
        progressTimer = setInterval(async () => {
          try {
            const progressResponse = await apiClient.get(`/crawler/progress/${currentTaskId.value}`)
            const { progress: currentProgress, count, status, message } = progressResponse.data
            
            // 格式化进度，保留3位小数
            progress.value = parseFloat(currentProgress.toFixed(3))
            collectedCount.value = count
            
            // 只有当消息变化时才添加日志
            if (message && message !== lastMessage) {
              addLog(message)
              lastMessage = message
            }
            
            if (status === 'completed') {
              clearInterval(progressTimer)
              progressTimer = null;
              isRunning.value = false
              ElMessage.success('数据采集完成！')
              addLog('采集完成！', 'success')
            } else if (status === 'failed') {
              clearInterval(progressTimer)
              progressTimer = null;
              isRunning.value = false
              ElMessage.error('数据采集失败！')
              addLog('采集失败：' + message, 'error')
            }
          } catch (error) {
            console.error('Progress check failed:', error)
          }
        }, 1000)
        
      } catch (error) {
        isRunning.value = false
        ElMessage.error(error.response?.data?.message || '启动爬虫失败')
        addLog('启动失败：' + (error.response?.data?.message || '未知错误'), 'error')
      }
    }
    
    // 停止爬虫
    const stopCrawler = async () => {
      try {
        await apiClient.post('/crawler/stop')
        
        // 清除定时器
        if (progressTimer) {
          clearInterval(progressTimer);
          progressTimer = null;
        }
        
        isRunning.value = false
        ElMessage.warning('已停止数据采集')
        addLog('手动停止采集', 'warning')
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '停止爬虫失败')
      }
    }
    
    const handleLogout = () => {
      store.dispatch('logout')
      router.push('/')
    }

    return {
      activeIndex,
      isAuthenticated,
      handleLogout,
      isRunning,
      progress,
      progressStatus,
      progressFormat,
      collectedCount,
      remainingTime,
      statusText,
      logs,
      logContent,
      startCrawler,
      stopCrawler
    }
  }
}
</script>

<style scoped lang="scss">
.crawler {
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
  
  h1 {
    margin-bottom: 30px;
    color: #303133;
  }
}

.crawler-container {
  .crawler-card {
    .crawler-header {
      margin-bottom: 30px;
      text-align: center;
      
      h3 {
        margin-bottom: 10px;
        color: #303133;
      }
      
      p {
        color: #606266;
      }
    }
    
    .progress-section {
      margin: 30px 0;
    }
    
    .control-section {
      display: flex;
      justify-content: center;
      gap: 20px;
      margin: 20px 0;
    }
    
    .info-section {
      margin: 20px 0;
      text-align: center;
      color: #606266;
      
      p {
        margin: 5px 0;
      }
    }
    
    .log-section {
      margin-top: 30px;
      
      h4 {
        margin-bottom: 10px;
        color: #303133;
      }
      
      .log-content {
        height: 200px;
        overflow-y: auto;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 4px;
        font-family: monospace;
        
        p {
          margin: 5px 0;
          font-size: 14px;
          
          &.error {
            color: #f56c6c;
          }
          
          &.warning {
            color: #e6a23c;
          }
          
          &.success {
            color: #67c23a;
          }
          
          &.info {
            color: #909399;
          }
        }
      }
    }
  }
}
</style> 