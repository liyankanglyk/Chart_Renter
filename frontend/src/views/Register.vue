<template>
  <div class="register-page">
    <div class="register-container">
      <el-card class="register-card">
        <template #header>
          <h2>用户注册</h2>
        </template>
        
        <el-form 
          ref="registerFormRef"
          :model="registerForm"
          :rules="rules"
          label-width="0"
          @submit.prevent="handleRegister">
          
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="用户名">
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="密码"
              show-password>
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="确认密码"
              show-password>
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item prop="email">
            <el-input
              v-model="registerForm.email"
              placeholder="邮箱">
              <template #prefix>
                <el-icon><Message /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              class="register-button"
              :loading="loading"
              @click="handleRegister">
              注册
            </el-button>
          </el-form-item>
          
          <div class="form-footer">
            <router-link to="/login">已有账号？立即登录</router-link>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { authApi } from '../api/auth'

export default {
  name: 'Register',
  components: {
    User,
    Lock,
    Message
  },
  setup() {
    const router = useRouter()
    const registerForm = reactive({
      username: '',
      password: '',
      confirmPassword: '',
      email: ''
    })
    const loading = ref(false)
    const registerFormRef = ref(null)

    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== registerForm.password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }

    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        { validator: validatePass, trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
      ]
    }

    const handleRegister = async () => {
      if (!registerFormRef.value) return

      await registerFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            loading.value = true
            await authApi.register(
              registerForm.username,
              registerForm.password,
              registerForm.email
            )
            ElMessage.success('注册成功，请登录')
            router.push('/login')
          } catch (error) {
            ElMessage.error(error.message || '注册失败')
          } finally {
            loading.value = false
          }
        }
      })
    }

    return {
      registerForm,
      registerFormRef,
      rules,
      loading,
      handleRegister
    }
  }
}
</script>

<style scoped lang="scss">
.register-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.register-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.register-card {
  :deep(.el-card__header) {
    text-align: center;
    padding: 20px;
    
    h2 {
      margin: 0;
      color: #303133;
    }
  }
}

.register-button {
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