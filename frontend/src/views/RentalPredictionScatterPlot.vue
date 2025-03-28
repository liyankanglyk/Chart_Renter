<template>

  <div>
    <!-- 顶部导航栏 -->
    <NavBar :active-index="activeIndex" @logout="handleLogout" />

    <div class="top">
      <text class="txt1">城市不同区域租房房价分布散点图</text>
      <text class="txt2"> 应用python爬虫、flask框架、eChats、VUE等技术实现</text>
    </div>
    <div class="ss">
      <el-select v-model="selectedCity" placeholder="请选择地区" @change="handleCityChange">
        <el-option
            v-for="city in cities"
            :key="city.value"
            :label="city.label"
            :value="city.value">
        </el-option>
      </el-select>
    </div>
    <div id="RentalPredictionScatterPlot" style="width: 90%; height: 600px;"></div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import {authApi} from "@/api/auth";
import NavBar from '../components/NavBar.vue'

export default {
  name: "RentalPredictionScatterPlot",
  components: {
    NavBar
  },
  setup() {

    const  chartInstance = ref('');
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

   const datas =ref([
     [10, 10000],
     [20, 15000],
     [30, 20000],
     [40, 25000],
     [50, 30000]
   ]);
    const selectedCity = ref('');
    const cityIndex = ref('0');
    const updateChart = () => {

        const option = {
          xAxis: {},
          yAxis: {},
          series: [
            {
              name: '租房价格',
              data: datas.value,
              type: 'scatter'
            }
          ]
        };
        chartInstance.value.setOption(option);

    };
    const handleCityChange = async (value) => {
      console.log('选中的城市值变化了：', value);
      cityIndex.value = value;
      try {
        // 设置请求的URL和数据
        const response = await authApi.RentalPredictionScatterPlot(value);
        datas.value = response.info
        updateChart();
      } catch (error) {
        console.error('请求失败:', error);
      }

    };

    const initChart = () => {
      const dom = document.getElementById('RentalPredictionScatterPlot');
      chartInstance.value = echarts.init(dom);
      updateChart();
    };


    onMounted(() => {
      nextTick(async() => {
        try {
          // 设置请求的URL和数据
          const response = await authApi.RentalPredictionScatterPlot(0);
          console.log(response);
          datas.value = response.info
        } catch (error) {
          console.error('请求失败:', error);
        }
        initChart();
      });
    });

    return {
      cities,
      selectedCity,
      handleCityChange,
    };
  }
};
</script>

<style scoped lang="scss">



.flex-grow {
  flex-grow: 1;
}

.main-content {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  padding: 40px 0;
  margin-bottom: 40px;

h1 {
  font-size: 2.5em;
  color: #303133;
  margin-bottom: 20px;
}

p {
  font-size: 1.2em;
  color: #606266;
}
}

.feature-cards {
  margin-top: 40px;

.feature-card {
  height: 100%;
  transition: all 0.3s;
  cursor: pointer;

&:hover {
   transform: translateY(-5px);
   box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
 }

.card-header {
  font-size: 1.2em;
  font-weight: bold;
}

.card-content {
  padding: 20px 0;

p {
  margin: 10px 0;
  color: #606266;
}
}
}
}

  #RentalPredictionScatterPlot{
    float: left;
    margin-left: 200px;
    margin-top: 100px;
  }
  .top{
    float: left;
    width: 100%;
    height: 100px;
    //border: solid black 1px;
  }
  .txt1{
    float: left;
    margin-top: 20px;
    width: 100%;
    font-size: 30px;
    color: #66b1ff;
  }
.txt2{
  float: left;
  margin-top: 20px;
  width: 100%;
  font-size: 16px;
}
.ss{
  position: absolute;
  top: 200px;
  left: 380px;
  width: 200px;
}
</style>