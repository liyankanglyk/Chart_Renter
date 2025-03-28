<template>
  <div>
    <!-- 顶部导航栏 -->
    <NavBar :active-index="activeIndex" @logout="handleLogout" />

    <div class="page-content">
      <div class="page-header">
        <h1 class="page-title">武汉各区域平均房价分析</h1>
        <p class="page-description">应用python爬虫、flask框架、eCharts、VUE等技术实现</p>
      </div>
      
      <div class="chart-section">
        <!-- 图表描述 -->
        <div class="chart-description">
          <h2>平均房价趋势与分布</h2>
          <p>左侧折线图展示了武汉各区域平均租金，右侧玫瑰图展示了各区域房源租金分布情况。通过这两个图表，您可以直观地了解武汉市不同区域的租房市场价格差异。</p>
          <p>根据数据分析，<strong>东湖高新区、武昌区、洪山区</strong>的平均租金较高，而<strong>蔡甸区、黄陂区</strong>等郊区的租金相对较低。</p>
        </div>
        
        <div class="charts-container">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-overlay">
            <el-icon class="is-loading loading-icon"><Loading /></el-icon>
            <p>数据加载中...</p>
          </div>
          
          <!-- 左侧图表 - 折线图 -->
          <div class="chart-card left-chart">
            <h3 class="chart-title">各区域平均房价趋势</h3>
            <div id="echartsRight" class="chart-content"></div>
          </div>
          
          <!-- 右侧图表 - 玫瑰图 -->
          <div class="chart-card right-chart">
            <h3 class="chart-title">各区域房价分布情况</h3>
            <div id="echartsLeft" class="chart-content"></div>
          </div>
        </div>
        
        <!-- 数据分析结果 -->
        <div class="data-insights">
          <h3>数据分析洞察</h3>
          <el-card>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="8">
                <div class="insight-item">
                  <div class="insight-icon price-high">
                    <el-icon><ArrowUp /></el-icon>
                  </div>
                  <div class="insight-content">
                    <h4>租金最高区域</h4>
                    <p>东湖高新区 - 科技园区聚集、高端人才集中</p>
                  </div>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8">
                <div class="insight-item">
                  <div class="insight-icon price-low">
                    <el-icon><ArrowDown /></el-icon>
                  </div>
                  <div class="insight-content">
                    <h4>租金最低区域</h4>
                    <p>新洲、黄陂 - 城市郊区，交通相对不便</p>
                  </div>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8">
                <div class="insight-item">
                  <div class="insight-icon price-value">
                    <el-icon><GoldMedal /></el-icon>
                  </div>
                  <div class="insight-content">
                    <h4>最具性价比区域</h4>
                    <p>江汉、硚口 - 价格中等，交通便利</p>
                  </div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {nextTick, onMounted, ref, computed} from "vue";
import * as echarts from "echarts";
import {authApi} from "@/api/auth";
import { Loading, ArrowUp, ArrowDown, GoldMedal } from '@element-plus/icons-vue';
import { useStore } from 'vuex';
import NavBar from '../components/NavBar.vue'

export default {
  name: "averageHousePrice",
  components: {
    Loading,
    ArrowUp,
    ArrowDown,
    GoldMedal
  ,
    NavBar},
  setup(){
    const store = useStore();
    const activeIndex = ref('/averageHousePrice');
    const isAuthenticated = computed(() => store.state.isAuthenticated);
    
    const loading = ref(false);
    const datass = ref('');
    const datax = ref('');
    const datay = ref('');
    const dataw = ref('');
    const chartInstance = ref('');
    const chartInstance1 = ref('');
    
    const updateChart = () => {
      const option = {
        title: {
          text: '武汉市各区域平均租金对比',
          left: 'center',
          top: 10,
          textStyle: {
            fontSize: 16
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: (params) => {
            const data = params[0];
            return `${data.name}<br/>${data.marker}平均租金: ${Math.round(data.value)} 元/月`;
          }
        },
        grid: {
          left: '5%',
          right: '5%',
          bottom: '15%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: datax.value,
          axisLabel: {
            interval: 0,
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          name: '元/月',
          nameTextStyle: {
            padding: [0, 0, 0, 40]
          },
          axisLabel: {
            formatter: (value) => {
              return Math.round(value);
            }
          }
        },
        series: [
          {
            name: '平均租金',
            data: datay.value.map(value => Math.round(value)),
            type: 'line',
            smooth: true,
            lineStyle: {
              width: 3,
              shadowColor: 'rgba(0,0,0,0.3)',
              shadowBlur: 10,
              shadowOffsetY: 8
            },
            itemStyle: {
              color: '#5470c6',
              borderWidth: 3
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 20,
                borderWidth: 5
              }
            },
            markPoint: {
              symbolSize: 60,
              data: [
                { type: 'max', name: '最高值' },
                { type: 'min', name: '最低值' }
              ],
              label: {
                formatter: (params) => {
                  return `${params.name}: ${Math.round(params.value)}`;
                }
              }
            }
          }
        ]
      };
      
      if (chartInstance.value) {
        chartInstance.value.setOption(option);
      }
    };
    
    const updateChart1 = () => {
      const option1 = {
        title: {
          text: '武汉市各区域租金分布',
          left: 'center',
          top: 10,
          textStyle: {
            fontSize: 16
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          type: 'scroll',
          orient: 'horizontal',
          bottom: 10,
          data: dataw.value.map(item => item.name)
        },
        series: [
          {
            name: '租金分布',
            type: 'pie',
            radius: [30, 110],
            center: ['50%', '50%'],
            roseType: 'radius',
            itemStyle: {
              borderRadius: 8
            },
            label: {
              show: true,
              formatter: (params) => {
                return `${params.name}: ${Math.round(params.value)}`;
              }
            },
            emphasis: {
              label: {
                fontSize: 14,
                fontWeight: 'bold'
              }
            },
            data: dataw.value.map(item => ({
              ...item,
              value: Math.round(item.value)
            }))
          }
        ]
      };
      
      if (chartInstance1.value) {
        chartInstance1.value.setOption(option1);
      }
    };
    
    const initChart = () => {
      const dom = document.getElementById('echartsRight');
      if (dom) {
        chartInstance.value = echarts.init(dom);
        updateChart();
        
        // 窗口大小变化时自动调整图表尺寸
        window.addEventListener('resize', () => {
          if (chartInstance.value) {
            chartInstance.value.resize();
          }
        });
      }
    };
    
    const initChart1 = () => {
      const dom1 = document.getElementById('echartsLeft');
      if (dom1) {
        chartInstance1.value = echarts.init(dom1);
        updateChart1();
        
        // 窗口大小变化时自动调整图表尺寸
        window.addEventListener('resize', () => {
          if (chartInstance1.value) {
            chartInstance1.value.resize();
          }
        });
      }
    };
    
    onMounted(() => {
      nextTick(async() => {
        loading.value = true;
        try {
          // 设置请求的URL和数据
          const response1 = await authApi.averageHousePrice1();
          dataw.value = response1.info;
          const response = await authApi.averageHousePrice();
          datax.value = response.infox;
          datay.value = response.infoy;
          
          // 对数据进行整数处理
          datay.value = datay.value.map(value => Math.round(value));
          dataw.value = dataw.value.map(item => ({
            ...item,
            value: Math.round(item.value)
          }));
          
          initChart();
          initChart1();
        } catch (error) {
          console.error('请求失败:', error);
        } finally {
          loading.value = false;
        }
      });
    });
    
    return {
      activeIndex,
      isAuthenticated,
      loading
    };
  }
}
</script>

<style scoped lang="scss">


.flex-grow {
  flex-grow: 1;
}

.page-content {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 28px;
  color: #409EFF;
  margin-bottom: 10px;
}

.page-description {
  color: #606266;
  font-size: 16px;
}

.chart-section {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart-description {
  margin-bottom: 20px;
  padding: 15px;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  
  h2 {
    font-size: 20px;
    color: #303133;
    margin-bottom: 10px;
  }
  
  p {
    color: #606266;
    line-height: 1.6;
    margin-bottom: 10px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
}

.charts-container {
  position: relative;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 30px;
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

.chart-card {
  flex: 1;
  min-width: 300px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.chart-title {
  text-align: center;
  font-size: 18px;
  color: #303133;
  margin-bottom: 15px;
}

.chart-content {
  height: 500px;
}

.data-insights {
  h3 {
    font-size: 20px;
    color: #303133;
    margin-bottom: 15px;
  }
  
  .insight-item {
    display: flex;
    align-items: center;
    padding: 15px 0;
    
    .insight-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 15px;
      
      .el-icon {
        font-size: 20px;
        color: white;
      }
    }
    
    &:hover .insight-icon {
      transform: scale(1.1);
      transition: transform 0.3s;
    }
    
    .insight-content {
      h4 {
        font-size: 16px;
        margin-bottom: 5px;
        color: #303133;
      }
      
      p {
        color: #606266;
        margin: 0;
      }
    }
  }
  
  .price-high {
    background-color: #f56c6c;
  }
  
  .price-low {
    background-color: #67c23a;
  }
  
  .price-value {
    background-color: #e6a23c;
  }
}

@media (max-width: 768px) {
  .charts-container {
    flex-direction: column;
  }
  
  .chart-card {
    width: 100%;
  }
  
  .chart-content {
    height: 400px;
  }
}
</style>