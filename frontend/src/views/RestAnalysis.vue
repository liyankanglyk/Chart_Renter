<template>
  <div>
    <!-- 顶部导航栏 -->
    <NavBar :active-index="activeIndex" @logout="handleLogout" />

    <div class="page-wrapper">
      <div class="top">
        <text class="txt1">城市不同区域租金区间分布分析</text>
        <text class="txt2">应用python爬虫、flask框架、eCharts、VUE等技术实现</text>
      </div>
      
      <div class="filter-container">
        <div class="filter-group">
          <div class="filter-item">
            <span class="filter-label">区域：</span>
            <el-select v-model="selectedCity" placeholder="请选择城市" class="filter-select">
              <el-option
                  v-for="city in cities"
                  :key="city.value"
                  :label="city.label"
                  :value="city.value">
              </el-option>
            </el-select>
          </div>
          <div class="filter-item">
            <span class="filter-label">朝向：</span>
            <el-select v-model="selectedOrientations" placeholder="请选择方向" class="filter-select">
              <el-option
                  v-for="city in orientations"
                  :key="city.value"
                  :label="city.label"
                  :value="city.value">
              </el-option>
            </el-select>
          </div>
          <div class="filter-item">
            <span class="filter-label">面积：</span>
            <el-select v-model="selectedSize" placeholder="请选择面积" class="filter-select">
              <el-option
                  v-for="city in sizes"
                  :key="city.value"
                  :label="city.label"
                  :value="city.value">
              </el-option>
            </el-select>
          </div>
          <div class="filter-item search-item">
            <el-button class="search-button" type="primary" @click="CityChange">
              <el-icon><Search /></el-icon> 搜索
            </el-button>
          </div>
        </div>
        <p class="filter-tip">选择不同条件组合，查看租金区间分布情况</p>
      </div>
  
      <div class="chart-container">
        <div v-if="loading" class="loading-overlay">
          <el-icon class="is-loading loading-icon"><Loading /></el-icon>
          <p>数据加载中...</p>
        </div>
        <div id="RestAnalysis" style="width: 100%; height: 600px;"></div>
      </div>
      
      <div class="price-insights">
        <h3>租金区间解读</h3>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8">
            <el-card class="insight-card" shadow="hover">
              <div class="insight-icon low-price">
                <el-icon><Money /></el-icon>
              </div>
              <div class="insight-content">
                <h4>0-3000元</h4>
                <p>经济实惠型，通常为小户型或位置较远的房源</p>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-card class="insight-card" shadow="hover">
              <div class="insight-icon mid-price">
                <el-icon><Money /></el-icon>
              </div>
              <div class="insight-content">
                <h4>3000-5000元</h4>
                <p>中端舒适型，多为中等面积、配套较全的房源</p>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-card class="insight-card" shadow="hover">
              <div class="insight-icon high-price">
                <el-icon><Money /></el-icon>
              </div>
              <div class="insight-content">
                <h4>5000元以上</h4>
                <p>高端品质型，通常为大户型或位置优越的精装房源</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, computed } from 'vue';
import * as echarts from 'echarts';
import {authApi} from "@/api/auth";
import { Loading, Search, Money } from '@element-plus/icons-vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import NavBar from '../components/NavBar.vue';

export default {
  name: "RestAnalysis",
  components: {
    Loading,
    Search,
    Money,
    NavBar
  },
  setup(){
    const store = useStore();
    const router = useRouter();
    const activeIndex = ref('/RestAnalysis');
    const isAuthenticated = computed(() => store.state.isAuthenticated);
    const chartInstance = ref('');
    const loading = ref(false);
    
    const handleLogout = () => {
      store.dispatch('logout');
      router.push('/');
    };
    
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
      // 可以继续添加更多城市
    ]);
    const orientations = ref(
        [
          { value: 0, label: '南' },
          { value: 1, label: '东' },
          { value: 2, label: '北' },
          { value: 3, label: '西' },
          { value: 4, label: '东南' },
          { value: 5, label: '西南' },
          { value: 6, label: '东北' },
          { value: 7, label: '西北' },
        ]
    );
    const sizes = ref([
      { value: 0, label: '小于50m²' },
      { value: 1, label: '50m²-90m²' },
      { value: 2, label: '90m²-120m²' },
      { value: 3, label: '大于120m²' },
    ]);
    const selectedCity = ref(0);
    const selectedOrientations = ref(0);
    const selectedSize = ref(0);
    const datass = ref(
        [
          { value: 0, name: '0-1000元' },
          { value: 0, name: '1000-3000元' },
          { value: 2, name: '3000-5000元' },
          { value: 4, name: '5000-8000元' },
          { value: 3, name: '大于8000元' }
        ]
    );
    
    // 获取选中区域、朝向和面积的名称
    const getSelectedLabels = () => {
      const cityLabel = cities.value.find(city => city.value === selectedCity.value)?.label || '全部';
      const orientationLabel = orientations.value.find(o => o.value === selectedOrientations.value)?.label || '全部';
      const sizeLabel = sizes.value.find(s => s.value === selectedSize.value)?.label || '全部';
      return { cityLabel, orientationLabel, sizeLabel };
    };
    
    const CityChange = async () => {
      loading.value = true;
      try {
        // 设置请求的URL和数据
        console.log(selectedCity.value);
        console.log(selectedOrientations.value);
        console.log(selectedSize.value);
        const response = await authApi.restAnalysis(selectedCity.value,selectedSize.value,selectedOrientations.value);
        console.log(response);
        datass.value = response.pricew;
        updateChart();
      } catch (error) {
        console.error('请求失败:', error);
      } finally {
        loading.value = false;
      }
    };
    
    const updateChart = () => {
      const { cityLabel, orientationLabel, sizeLabel } = getSelectedLabels();
      const chartTitle = `${cityLabel} ${orientationLabel}朝向 ${sizeLabel}房源租金区间分布`;
      
      const option = {
        title: {
          text: chartTitle,
          left: 'center',
          textStyle: {
            fontSize: 18,
            color: '#333'
          },
          subtextStyle: {
            fontSize: 14,
            color: '#666'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 'bottom',
          padding: [15, 0, 0, 0],
          itemGap: 20,
          textStyle: {
            fontSize: 14
          }
        },
        series: [
          {
            name: '租金区间',
            type: 'pie',
            radius: ['30%', '60%'],
            avoidLabelOverlap: true,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: true,
              formatter: '{b}: {c} ({d}%)',
              fontSize: 14
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 16,
                fontWeight: 'bold'
              },
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            data: datass.value
          }
        ],
        color: ['#36a3f7', '#4ecb73', '#fad337', '#f95959', '#9b59b6'] // 自定义颜色
      };
      
      if (chartInstance.value) {
        chartInstance.value.setOption(option);
      }
    };
    
    const initChart = () => {
      const dom = document.getElementById('RestAnalysis');
      if (dom) {
        chartInstance.value = echarts.init(dom);
        updateChart();
        
        // 添加窗口大小变化时自动调整图表尺寸
        window.addEventListener('resize', () => {
          if (chartInstance.value) {
            chartInstance.value.resize();
          }
        });
      }
    };
    
    onMounted(() => {
      nextTick(async() => {
        loading.value = true;
        try {
          // 设置请求的URL和数据
          const response = await authApi.restAnalysis(0,0,0);
          console.log(response);
          datass.value = response.pricew;
        } catch (error) {
          console.error('请求失败:', error);
        } finally {
          loading.value = false;
          initChart();
        }
      });
    });

    return {
      activeIndex,
      isAuthenticated,
      handleLogout,
      cities,
      orientations,
      sizes,
      CityChange,
      selectedSize,
      selectedCity,
      selectedOrientations,
      loading,
    };
  }
};
</script>

<style scoped lang="scss">
.flex-grow {
  flex-grow: 1;
}

.page-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.top {
  width: 100%;
  padding: 30px 0 10px;
  text-align: center;
}

.txt1 {
  display: block;
  font-size: 30px;
  color: #66b1ff;
  font-weight: bold;
  margin-bottom: 10px;
}

.txt2 {
  display: block;
  font-size: 16px;
  color: #606266;
}

.filter-container {
  max-width: 1000px;
  margin: 20px auto;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 25px;
  margin-bottom: 15px;
}

.filter-item {
  display: flex;
  align-items: center;
  min-width: 220px;
}

.filter-label {
  margin-right: 12px;
  font-weight: bold;
  color: #606266;
  white-space: nowrap;
  min-width: 45px;
  text-align: right;
}

.filter-select {
  width: 150px;
}

.search-item {
  min-width: unset;
  margin-left: 10px;
}

.search-button {
  width: 120px;
  height: 40px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-button .el-icon {
  margin-right: 5px;
}

.filter-tip {
  text-align: center;
  color: #909399;
  font-size: 14px;
  margin: 10px 0 0;
}

.chart-container {
  position: relative;
  max-width: 1200px;
  margin: 0 auto 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  overflow: hidden;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 100;
  border-radius: 8px;
}

.loading-icon {
  font-size: 40px;
  color: #409EFF;
  margin-bottom: 15px;
}

.price-insights {
  max-width: 1200px;
  margin: 0 auto 40px;
  
  h3 {
    font-size: 22px;
    color: #303133;
    margin-bottom: 20px;
    text-align: center;
  }
  
  .insight-card {
    margin-bottom: 20px;
    transition: transform 0.3s;
    
    &:hover {
      transform: translateY(-5px);
    }
  }
  
  .insight-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    margin: 0 auto 15px;
    
    .el-icon {
      font-size: 24px;
      color: white;
    }
  }
  
  .low-price {
    background-color: #67c23a;
  }
  
  .mid-price {
    background-color: #e6a23c;
  }
  
  .high-price {
    background-color: #f56c6c;
  }
  
  .insight-content {
    text-align: center;
    
    h4 {
      font-size: 18px;
      margin-bottom: 10px;
      color: #303133;
    }
    
    p {
      color: #606266;
      font-size: 14px;
      line-height: 1.6;
    }
  }
}

// 媒体查询，适配移动设备
@media (max-width: 768px) {
  .filter-group {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .filter-item {
    width: 100%;
    justify-content: space-between;
  }
  
  .filter-label {
    margin-right: 10px;
    min-width: 60px;
  }
  
  .filter-select {
    width: 75%;
    max-width: none;
  }
  
  .search-item {
    margin-left: 0;
    margin-top: 10px;
  }
  
  .search-button {
    width: 100%;
    height: 44px;
    font-size: 16px;
  }
  
  .search-button .el-icon {
    margin-right: 8px;
    font-size: 18px;
  }
  
  .filter-container {
    padding: 15px;
  }
  
  .filter-tip {
    font-size: 13px;
  }
  
  .chart-container {
    padding: 15px 10px;
    margin-bottom: 20px;
  }
  
  #RestAnalysis {
    height: 450px !important;
  }
  
  .top {
    padding: 20px 0 5px;
  }
  
  .txt1 {
    font-size: 24px;
  }
  
  .txt2 {
    font-size: 14px;
  }
  
  .page-wrapper {
    padding: 0 10px;
  }
  
  .price-insights h3 {
    font-size: 20px;
  }
}

// 较小屏幕设备
@media (max-width: 480px) {
  .chart-container {
    padding: 10px 5px;
  }
  
  #RestAnalysis {
    height: 400px !important;
  }
  
  .txt1 {
    font-size: 20px;
  }
  
  .page-wrapper {
    padding: 0 5px;
  }
}
</style>
