<template>
  <div class="prediction">
    <!-- 顶部导航栏 -->
    <NavBar :active-index="activeIndex" @logout="handleLogout" />

    <div class="main-content">
      <div class="page-header">
        <h1>武汉租房价格预测</h1>
        <p class="page-description">基于机器学习算法的租金预测系统，帮助您了解不同区域、朝向和面积的房源价格</p>
      </div>

      <el-row :gutter="20" class="prediction-container">
        <el-col :xs="24" :md="14">
          <el-card class="prediction-card main-card">
            <template #header>
              <div class="card-header">
                <h2>房源条件选择</h2>
                <p>请选择您感兴趣的房源条件，获取预测租金</p>
              </div>
            </template>
            
            <div class="form-container">
              <div class="form-group">
                <label class="form-label">地区</label>
                <el-select 
                  v-model="selectedCity" 
                  placeholder="请选择城市" 
                  class="form-control"
                  size="large">
                  <el-option
                    v-for="city in cities"
                    :key="city.value"
                    :label="city.label"
                    :value="city.value">
                  </el-option>
                </el-select>
              </div>
              
              <div class="form-group">
                <label class="form-label">朝向</label>
                <el-select 
                  v-model="selectedOrientations" 
                  placeholder="请选择方向" 
                  class="form-control"
                  size="large">
                  <el-option
                    v-for="orientation in orientations"
                    :key="orientation.value"
                    :label="orientation.label"
                    :value="orientation.value">
                  </el-option>
                </el-select>
              </div>
              
              <div class="form-group">
                <label class="form-label">面积</label>
                <el-select 
                  v-model="selectedSize" 
                  placeholder="请选择面积" 
                  class="form-control"
                  size="large">
                  <el-option
                    v-for="size in sizes"
                    :key="size.value"
                    :label="size.label"
                    :value="size.value">
                  </el-option>
                </el-select>
              </div>
              
              <div class="form-action">
                <el-button 
                  type="primary" 
                  size="large" 
                  class="search-button" 
                  :loading="loading"
                  @click="predictRent">
                  <el-icon class="search-icon"><Search /></el-icon>
                  开始预测
                </el-button>
              </div>
            </div>
            
            <div class="result-container" v-if="datass">
              <div class="result-header">预测结果</div>
              <div class="money-box">
                <div class="money-content">
                  <div class="money-value">{{ Math.round(datass) }}</div>
                  <div class="money-unit">元/月</div>
                </div>
                <div class="money-location">
                  {{ getCityLabel(selectedCity) }} {{ getOrientationLabel(selectedOrientations) }} {{ getSizeLabel(selectedSize) }}
                </div>
              </div>
              
              <div class="result-info">
                <p><el-icon><InfoFilled /></el-icon> 此预测结果基于历史数据分析和机器学习算法生成，仅供参考</p>
                <p><el-icon><Clock /></el-icon> 数据更新时间：{{ formattedDate }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :md="10">
          <el-card class="prediction-card info-card">
            <template #header>
              <div class="card-header">
                <h2>租金预测指南</h2>
              </div>
            </template>
            
            <div class="info-content">
              <div class="info-section">
                <h3><el-icon><Location /></el-icon> 地区因素</h3>
                <p>武汉不同区域的租金差异显著。东湖高新区、武昌区等商业中心区域租金较高，而远城区如新洲、黄陂等租金相对较低。</p>
              </div>
              
              <div class="info-section">
                <h3><el-icon><HomeFilled /></el-icon> 朝向影响</h3>
                <p>在武汉，南向和东南向的房源通常更受欢迎，租金也相对较高。北向房源则价格较为经济。</p>
              </div>
              
              <div class="info-section">
                <h3><el-icon><Histogram /></el-icon> 面积考量</h3>
                <p>小户型（50平米以下）性价比较高，适合单身人士。50-90平米的中等户型适合小家庭，租金性价比适中。</p>
              </div>
              
              <div class="info-section tips-section">
                <h3><el-icon><Light /></el-icon> 租房小贴士</h3>
                <ul>
                  <li>交通便利性对租金影响很大，地铁沿线房源租金普遍较高</li>
                  <li>租金预测结果为平均水平，实际价格还与房屋装修、楼层、小区品质等因素相关</li>
                  <li>建议到实地考察后再做决定，关注房屋实际情况和周边配套</li>
                </ul>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import {ref, computed, onMounted, nextTick} from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import {authApi} from "@/api/auth";
import { Search, Location, HomeFilled, Histogram, InfoFilled, Light, Clock } from '@element-plus/icons-vue'
import NavBar from '../components/NavBar.vue'

export default {
  name: 'Prediction',
  components: {
    Search,
    Location,
    HomeFilled,
    Histogram,
    InfoFilled,
    Light,
    Clock,
    NavBar
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const activeIndex = ref('/prediction')
    const loading = ref(false)

    const cities = ref([
      { value: 0, label: '东湖高新区' },
      { value: 1, label: '东西湖' },
      { value: 2, label: '新洲' },
      { value: 3, label: '武昌' },
      { value: 4, label: '武汉周边' },
      { value: 5, label: '汉南' },
      { value: 6, label: '汉阳' },
      { value: 7, label: '江夏' },
      { value: 8, label: '江岸' },
      { value: 9, label: '江汉' },
      { value: 10, label: '沌口' },
      { value: 11, label: '洪山' },
      { value: 12, label: '硚口' },
      { value: 13, label: '经济开发区' },
      { value: 14, label: '蔡甸' },
      { value: 15, label: '青山' },
      { value: 16, label: '黄陂' },
    ]);
    
    const orientations = ref([
      { value: 0, label: '南' },
      { value: 1, label: '东' },
      { value: 2, label: '北' },
      { value: 3, label: '西' },
      { value: 4, label: '东南' },
      { value: 5, label: '西南' },
      { value: 6, label: '东北' },
      { value: 7, label: '西北' },
    ])
    
    const sizes = ref([
      { value: 0, label: '小于50m²' },
      { value: 1, label: '50m²-90m²' },
      { value: 2, label: '90m²-120m²' },
      { value: 3, label: '大于120m²' },
    ]);
    
    const datass = ref('')
    const selectedCity = ref(0);
    const selectedOrientations = ref(0);
    const selectedSize = ref(0);
    const isAuthenticated = computed(() => store.state.isAuthenticated);
    
    const formattedDate = computed(() => {
      const now = new Date();
      return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    });
    
    const getCityLabel = (value) => {
      const city = cities.value.find(item => item.value === value);
      return city ? city.label : '';
    };
    
    const getOrientationLabel = (value) => {
      const orientation = orientations.value.find(item => item.value === value);
      return orientation ? orientation.label + '向' : '';
    };
    
    const getSizeLabel = (value) => {
      const size = sizes.value.find(item => item.value === value);
      return size ? size.label : '';
    };
    
    const predictRent = async () => {
      loading.value = true;
      try {
        // 设置请求的URL和数据
        const response = await authApi.prediction(selectedCity.value, selectedSize.value, selectedOrientations.value);
        datass.value = response.moneys;
        console.log(datass.value);
      } catch (error) {
        console.error('请求失败:', error);
      } finally {
        loading.value = false;
      }
    };
    
    onMounted(() => {
      nextTick(async() => {
        loading.value = true;
        try {
          // 设置请求的URL和数据
          const response = await authApi.prediction(0,0,0)
          datass.value = response.moneys
          console.log(datass.value);
        } catch (error) {
          console.error('请求失败:', error);
        } finally {
          loading.value = false;
        }
      });
    });
    
    const handleLogout = () => {
      store.dispatch('logout')
      router.push('/')
    }

    return {
      activeIndex,
      isAuthenticated,
      handleLogout,
      cities,
      orientations,
      sizes,
      selectedCity,
      selectedOrientations,
      selectedSize,
      datass,
      loading,
      predictRent,
      formattedDate,
      getCityLabel,
      getOrientationLabel,
      getSizeLabel
    }
  }
}
</script>

<style scoped lang="scss">
.prediction {
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
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  
  h1 {
    font-size: 32px;
    color: #409EFF;
    margin-bottom: 15px;
  }
  
  .page-description {
    color: #606266;
    font-size: 16px;
  }
}

.prediction-container {
  margin-top: 20px;
}

.prediction-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 30px;
  
  .card-header {
    padding-bottom: 15px;
    
    h2 {
      font-size: 20px;
      color: #303133;
      margin-bottom: 8px;
    }
    
    p {
      color: #909399;
      font-size: 14px;
      margin: 0;
    }
  }
}

.main-card {
  height: 100%;
}

.form-container {
  padding: 10px 0;
}

.form-group {
  margin-bottom: 25px;
  
  .form-label {
    display: block;
    font-weight: 500;
    margin-bottom: 10px;
    color: #606266;
  }
  
  .form-control {
    width: 100%;
  }
}

.form-action {
  margin-top: 30px;
  text-align: center;
  
  .search-button {
    width: 180px;
    height: 50px;
    font-size: 16px;
    
    .search-icon {
      margin-right: 5px;
    }
  }
}

.result-container {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  
  .result-header {
    text-align: center;
    font-weight: 500;
    font-size: 18px;
    color: #303133;
    margin-bottom: 20px;
  }
}

.money-box {
  background: linear-gradient(135deg, #409EFF, #36D1DC);
  border-radius: 8px;
  padding: 30px;
  color: white;
  text-align: center;
  box-shadow: 0 4px 12px rgba(54, 209, 220, 0.3);
  
  .money-content {
    display: flex;
    justify-content: center;
    align-items: baseline;
    margin-bottom: 15px;
    
    .money-value {
      font-size: 48px;
      font-weight: 700;
    }
    
    .money-unit {
      font-size: 20px;
      margin-left: 5px;
      opacity: 0.9;
    }
  }
  
  .money-location {
    font-size: 16px;
    opacity: 0.85;
  }
}

.result-info {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  
  p {
    margin: 5px 0;
    color: #909399;
    font-size: 14px;
    display: flex;
    align-items: center;
    
    .el-icon {
      margin-right: 5px;
      color: #409EFF;
    }
  }
}

.info-card {
  height: 100%;
  
  .info-content {
    padding: 0 10px;
  }
  
  .info-section {
    margin-bottom: 25px;
    
    h3 {
      display: flex;
      align-items: center;
      font-size: 18px;
      color: #303133;
      margin-bottom: 10px;
      
      .el-icon {
        margin-right: 8px;
        color: #409EFF;
      }
    }
    
    p {
      color: #606266;
      line-height: 1.6;
      margin: 0;
    }
  }
  
  .tips-section {
    background-color: #f0f9eb;
    padding: 15px;
    border-radius: 6px;
    border-left: 4px solid #67c23a;
    
    h3 {
      color: #67c23a;
      
      .el-icon {
        color: #67c23a;
      }
    }
    
    ul {
      margin: 10px 0 0 0;
      padding-left: 20px;
      
      li {
        color: #606266;
        margin-bottom: 8px;
        
        &:last-child {
          margin-bottom: 0;
        }
      }
    }
  }
}

@media screen and (max-width: 768px) {
  .main-content {
    padding: 20px;
  }
  
  .page-header {
    h1 {
      font-size: 24px;
    }
    
    .page-description {
      font-size: 14px;
    }
  }
  
  .money-box {
    padding: 20px;
    
    .money-content {
      .money-value {
        font-size: 36px;
      }
      
      .money-unit {
        font-size: 16px;
      }
    }
  }
  
  .form-group {
    margin-bottom: 15px;
  }
  
  .form-action {
    margin-top: 20px;
    
    .search-button {
      width: 100%;
      height: 44px;
    }
  }
}
</style> 