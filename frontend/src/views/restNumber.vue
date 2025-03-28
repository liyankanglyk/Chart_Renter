<template>
  <div>
    <!-- 顶部导航栏 -->
    <NavBar :active-index="activeIndex" @logout="handleLogout" />

    <div class="top">
      <text class="txt1">城市不同区域房源分布图</text>
      <text class="txt2"> 应用python爬虫、flask框架、eChats、VUE等技术实现</text>
    </div>
    <div id="echartsRight"></div>
    <div id="echartsLeft"></div>
  </div>
</template>

<script>
import {nextTick, onMounted, ref} from "vue";
import * as echarts from "echarts";
import {authApi} from "@/api/auth";
import NavBar from '../components/NavBar.vue'

export default {
  name: "restNumber",
  components: {
    NavBar
  },
  setup(){
    const datass = ref('')
    const datax = ref('')
    const datay = ref('')
    const  chartInstance = ref('');
    const  chartInstance1 = ref('');
    const updateChart = () => {

      const option = {
        title: {
          text: '收入区间分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          // data: ['3000-5000元', '5000-7000元', '大于7000元']
        },
        series: [
          {
            name: '访问来源',
            type: 'pie',
            radius: '50%',
            // roseType: 'area',
            data:datass.value,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      };
      chartInstance.value.setOption(option);

    };
    const updateChart1 = () => {

      const option1 = {
        xAxis: {
          type: 'category',
          data: datax.value,
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            data: datay.value,
            type: 'bar'
          }
        ]
      };
      chartInstance1.value.setOption(option1);

    };
    const initChart = () => {
      const dom = document.getElementById('echartsRight');
      chartInstance.value = echarts.init(dom);
      updateChart();
    };
    const initChart1 = () => {
      const dom1 = document.getElementById('echartsLeft');
      chartInstance1.value = echarts.init(dom1);
      updateChart1();
    };
    onMounted(() => {
      nextTick(async() => {
        try {
          // 设置请求的URL和数据
          const response = await authApi.restNumber();
          console.log(response);
          datass.value = response.info
          const response1 = await authApi.restNumber1();
          datax.value = response1.infox;
          datay.value = response1.infoy;
        } catch (error) {
          console.error('请求失败:', error);
        }
        initChart();
        initChart1();
      });
    });
  }
}
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

#RestAnalysis{
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
#echartsRight{
  float: left;
  margin-left: 8%;
  margin-top: 100px;
  width: 42%;
  height: 500px;
  border: solid black 1px;
}
#echartsLeft{
  float: left;
  margin-left: 2%;
  margin-top: 100px;
  width: 42%;
  height: 500px;
  border: solid black 1px;
}
</style>