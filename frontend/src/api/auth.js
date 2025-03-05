import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // 清除token并跳转到登录页
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  // 用户登录
  login: async (username, password) => {
    try {
      const response = await apiClient.post('/auth/login', {
        username,
        password
      })
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token)
      }
      return response.data
    } catch (error) {
      throw error.response ? error.response.data : { message: '网络错误' }
    }
  },

  // 用户注册
  register: async (username, password, email) => {
    try {
      const response = await apiClient.post('/auth/register', {
        username,
        password,
        email
      })
      return response.data
    } catch (error) {
      throw error.response ? error.response.data : { message: '网络错误' }
    }
  }
}

export default apiClient 