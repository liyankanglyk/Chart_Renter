<template>
  <div class="login-page">
    <div class="login-container">
      <el-card class="login-card">
        <template #header>
          <h2>用户登录</h2>
        </template>
        
        <el-form 
          ref="loginFormRef"
          :model="loginForm"
          :rules="rules"
          label-width="0"
          @submit.prevent="handleLogin">
          
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="用户名">
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="密码"
              show-password>
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              class="login-button"
              :loading="loading"
              @click="handleLogin">
              登录
            </el-button>
          </el-form-item>
          
          <div class="form-footer">
            <router-link to="/register">还没有账号？立即注册</router-link>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { authApi } from '../api/auth'

export default {
  name: 'Login',
  components: {
    User,
    Lock
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const loginForm = reactive({
      username: '',
      password: ''
    })
    const loading = ref(false)
    const loginFormRef = ref(null)

    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
      ]
    }

    const handleLogin = async () => {
      if (!loginFormRef.value) return
      
      await loginFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            loading.value = true
            const response = await authApi.login(loginForm.username, loginForm.password)
            // 保存token到localStorage
            localStorage.setItem('token', response.access_token)
            store.dispatch('login', response.user)
            ElMessage.success('登录成功')
            
            // 获取重定向地址，如果没有则跳转到首页
            const redirect = router.currentRoute.value.query.redirect || '/'
            router.push(redirect)
          } catch (error) {
            ElMessage.error(error.message || '登录失败')
          } finally {
            loading.value = false
          }
        }
      })
    }

    return {
      loginForm,
      loginFormRef,
      rules,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.login-card {
  :deep(.el-card__header) {
    text-align: center;
    padding: 20px;
    
    h2 {
      margin: 0;
      color: #303133;
    }
  }
}

.login-button {
  width: 100%;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  
  a {
    color: #409EFF;
    text-decoration: none;
    
    &:hover {
      color: #66b1ff;
    }
  }
}
</style> 