<template>
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
    <el-menu-item index="/RentalPredictionScatterPlot">区域租金预测散点图</el-menu-item>
    <el-menu-item index="/RestAnalysis">租金分析</el-menu-item>
    <el-menu-item index="/restNumber">房源数量</el-menu-item>
    <el-menu-item index="/averageHousePrice">平均房价</el-menu-item>
    <el-menu-item index="/map">高德地图</el-menu-item>
    <div class="flex-grow"></div>
    
    <!-- 未登录状态 -->
    <template v-if="!isAuthenticated">
      <el-menu-item index="/login">
        <el-icon><UserFilled /></el-icon>
        登录
      </el-menu-item>
      <el-menu-item index="/register">
        <el-icon><Edit /></el-icon>
        注册
      </el-menu-item>
    </template>
    
    <!-- 已登录状态 -->
    <template v-else>
      <el-popover
        placement="bottom-end"
        :width="200"
        trigger="click"
        popper-class="user-popover">
        <template #reference>
          <div class="user-profile">
            <el-avatar size="small" :src="avatarUrl || require('@/assets/default-avatar.svg')" class="user-avatar">
              <el-icon v-if="!avatarUrl"><User /></el-icon>
            </el-avatar>
            <span class="username">{{ username }}</span>
            <el-icon class="arrow-icon"><ArrowDown /></el-icon>
          </div>
        </template>
        
        <div class="user-menu">
          <div class="user-info">
            <el-avatar size="large" :src="avatarUrl || require('@/assets/default-avatar.svg')">
              <el-icon v-if="!avatarUrl"><User /></el-icon>
            </el-avatar>
            <div class="user-details">
              <div class="user-name">{{ username }}</div>
              <div class="user-role">普通用户</div>
            </div>
          </div>
          
          <div class="menu-divider"></div>
          
          <el-menu class="dropdown-menu" mode="vertical">

            <el-menu-item v-if="isAdmin" index="/admin" @click="navigateTo('/admin')">
              <el-icon><Monitor /></el-icon>
              <span>管理后台</span>
            </el-menu-item>
            <el-menu-item index="/crawler" @click="navigateTo('/crawler')">
              <el-icon><Connection /></el-icon>
              <span>数据采集</span>
            </el-menu-item>
          </el-menu>
          
          <div class="menu-divider"></div>
          
          <div class="logout-option" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </div>
        </div>
      </el-popover>
    </template>
  </el-menu>
</template>

<script>
import { computed, defineProps, defineEmits } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { UserFilled, User, ArrowDown, Setting, Monitor, Connection, SwitchButton, Edit } from '@element-plus/icons-vue'

export default {
  name: 'NavBar',
  components: {
    UserFilled,
    User,
    ArrowDown,
    Setting,
    Monitor,
    Connection,
    SwitchButton,
    Edit
  },
  props: {
    activeIndex: {
      type: String,
      required: true
    }
  },
  setup(props, { emit }) {
    const store = useStore()
    const router = useRouter()
    
    const isAuthenticated = computed(() => store.state.isAuthenticated)
    const username = computed(() => store.state.user?.username || '用户')
    const avatarUrl = computed(() => store.state.user?.avatar || '')
    const isAdmin = computed(() => store.state.user?.role === 'admin')
    
    const handleLogout = () => {
      store.dispatch('logout')
      router.push('/')
      emit('logout')
    }
    
    const navigateTo = (path) => {
      router.push(path)
    }
    
    return {
      isAuthenticated,
      username,
      isAdmin,
      handleLogout,
      navigateTo
    }
  }
}
</script>

<style scoped lang="scss">
.nav-menu {
  padding: 0 20px;
}

.flex-grow {
  flex-grow: 1;
}

.user-profile {
  display: flex;
  align-items: center;
  padding: 0 15px;
  height: 60px;
  cursor: pointer;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
  
  .user-avatar {
    margin-right: 8px;
    background-color: #f5f7fa;
    color: #545c64;
    border: 2px solid #ffd04b;
  }
  
  .username {
    margin-right: 5px;
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .arrow-icon {
    font-size: 12px;
    margin-left: 2px;
    transition: transform 0.3s;
  }
  
  &:hover .arrow-icon {
    transform: rotate(180deg);
  }
}

:deep(.user-popover) {
  padding: 0;
  overflow: hidden;
  border-radius: 8px;
}

.user-menu {
  padding: 0;
  
  .user-info {
    padding: 20px 15px;
    display: flex;
    align-items: center;
    background-color: #f5f7fa;
    
    .user-details {
      margin-left: 15px;
      
      .user-name {
        font-weight: 500;
        font-size: 16px;
        color: #303133;
      }
      
      .user-role {
        font-size: 12px;
        color: #909399;
        margin-top: 5px;
      }
    }
  }
  
  .menu-divider {
    height: 1px;
    background-color: #ebeef5;
    margin: 0;
  }
  
  .dropdown-menu {
    border-right: none;
    
    :deep(.el-menu-item) {
      height: 50px;
      line-height: 50px;
      padding: 0 20px;
      
      &:hover {
        background-color: #f5f7fa;
      }
      
      .el-icon {
        margin-right: 10px;
        color: #909399;
      }
    }
  }
  
  .logout-option {
    padding: 15px 20px;
    display: flex;
    align-items: center;
    cursor: pointer;
    color: #f56c6c;
    
    &:hover {
      background-color: #fff0f0;
    }
    
    .el-icon {
      margin-right: 10px;
    }
  }
}
</style>