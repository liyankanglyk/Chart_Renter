import apiClient from './auth.js'

export const crawlerApi = {
  // 启动爬虫
  startCrawler: async () => {
    try {
      const response = await apiClient.post('/crawler/start')
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  // 获取爬虫状态
  getCrawlerStatus: async () => {
    try {
      const response = await apiClient.get('/crawler/status')
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  // 获取爬取结果
  getCrawlerResults: async () => {
    try {
      const response = await apiClient.get('/crawler/results')
      return response.data
    } catch (error) {
      throw error
    }
  }
}