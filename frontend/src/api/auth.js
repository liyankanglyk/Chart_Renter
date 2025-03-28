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
  },
  analysis: async (index) => {
    try {
      const response = await apiClient.post('/auth/analysis', {
        index
      })
      return response.data
    } catch (error) {
      throw error.response ? error.response.data : { message: '网络错误' }
    }
  },
  handleCurrentChange: async (index,page) => {
    try {
      const response = await apiClient.post('/auth/handleCurrentChange', {
        index,
        page
      })
      return response.data
    } catch (error) {
      throw error.response ? error.response.data : { message: '网络错误' }
    }
  },

  RentalPredictionScatterPlot: async (index) => {
    try {
      const response = await apiClient.post('/auth/RentalPredictionScatterPlot', {
        index,
      })
      return response.data
    } catch (error) {
      throw error.response ? error.response.data : { message: '网络错误' }
    }
  },
  restAnalysis: async (index,size,orientations) => {
    try {
      const response = await apiClient.post('/auth/RestAnalysis', {
        index,
        size,
        orientations,
      })
      console.log(index,size,orientations)
      return response.data
    } catch (error) {
      throw error.response ? error.response.data : { message: '网络错误' }
    }
  },
  restNumber: async () => {
    try {
      const response = await apiClient.post('/auth/restNumber', {
      })
      return response.data
    } catch (error) {
      throw error.response ? error.response.data : { message: '网络错误' }
    }
  },
  restNumber1: async () => {
    try {
      const response = await apiClient.post('/auth/restNumber1', {
      })
      return response.data
    } catch (error) {
      throw error.response ? error.response.data : { message: '网络错误' }
    }
  },
  averageHousePrice: async () => {
    try {
      const response = await apiClient.post('/auth/averageHousePrice', {
      })
      return response.data
    } catch (error) {
      throw error.response ? error.response.data : { message: '网络错误' }
    }
  },
  averageHousePrice1: async () => {
    try {
      const response = await apiClient.post('/auth/averageHousePrice1', {
      })
      return response.data
    } catch (error) {
      throw error.response ? error.response.data : { message: '网络错误' }
    }
  },
  prediction: async (index,size,orientations) => {
    try {
      const response = await apiClient.post('/auth/prediction', {
        index,
        size,
        orientations,
      })
      return response.data
    } catch (error) {
      throw error.response ? error.response.data : { message: '网络错误' }
    }
  },
  map: async () => {
    try {
      const response = await apiClient.post('/auth/map', {
      })
      return response.data
    } catch (error) {
      throw error.response ? error.response.data : { message: '网络错误' }
    }
  },
}

export default apiClient 