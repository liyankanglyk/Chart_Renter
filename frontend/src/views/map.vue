<template>
  <div>
    <el-menu
        :default-active="activeIndex"
        class="nav-menu"
        mode="horizontal"
        router
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b">
      <el-menu-item index="/">首页</el-menu-item>
      <el-menu-item index="/analysis">数据分析</el-menu-item>
      <el-menu-item index="/prediction">租金预测</el-menu-item>
      <el-menu-item index="/RentalPredictionScatterPlot">区域租金预测散点图</el-menu-item>
      <el-menu-item index="/RestAnalysis">租金分析</el-menu-item>
      <el-menu-item index="/restNumber">房源数量</el-menu-item>
      <el-menu-item index="/averageHousePrice">平均房价</el-menu-item>
      <el-menu-item index="/map">高德地图</el-menu-item>
      <div class="flex-grow"></div>
      <el-menu-item v-if="!isAuthenticated" index="/login">登录</el-menu-item>
      <el-menu-item v-if="isAuthenticated" @click="handleLogout">退出</el-menu-item>
    </el-menu>

    <div class="map-container">
      <div class="map-title">
        <h2>武汉市租房分布地图</h2>
        <p>各区域房源数量分布情况</p>
      </div>
      <div id="map-container" class="map-content"></div>
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>地图加载中...</span>
        </div>
      </div>
      <div class="map-legend">
        <div class="legend-title">房源数量</div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #3498db;"></div>
          <span>少量 (＜50)</span>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #2ecc71;"></div>
          <span>中等 (50-500)</span>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #e74c3c;"></div>
          <span>大量 (＞500)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import AMapLoader from '@amap/amap-jsapi-loader';
import { Loading } from '@element-plus/icons-vue';
import NavBar from '../components/NavBar.vue'

const store = useStore();
const router = useRouter();
const activeIndex = ref('/map');
const isAuthenticated = computed(() => store.state.isAuthenticated);
const loading = ref(true);

const handleLogout = () => {
  store.dispatch('logout');
  router.push('/');
};

const mapContainerStyle = {
  width: '100%',
  height: '500px'
};

// 定义区域数据，包括名称、坐标、房源数量
const areas = [
  { name: '东湖高新区', count: 2123, coords: [114.43, 30.52] },
  { name: '东西湖', count: 40, coords: [114.13, 30.62] },
  { name: '新洲', count: 1, coords: [114.80, 30.83] },
  { name: '武昌', count: 997, coords: [114.32, 30.55] },
  { name: '武汉周边', count: 1, coords: [114.20, 30.40] },
  { name: '汉南', count: 2, coords: [113.73, 30.32] },
  { name: '汉阳', count: 336, coords: [114.27, 30.55] },
  { name: '江夏', count: 238, coords: [114.33, 30.35] },
  { name: '江岸', count: 288, coords: [114.30, 30.60] },
  { name: '江汉', count: 425, coords: [114.27, 30.58] },
  { name: '沌口', count: 19, coords: [114.18, 30.52] },
  { name: '洪山', count: 772, coords: [114.35, 30.50] },
  { name: '硚口', count: 555, coords: [114.23, 30.57] },
  { name: '经济开发区', count: 1, coords: [114.18, 30.48] },
  { name: '蔡甸', count: 8, coords: [114.03, 30.58] },
  { name: '青山', count: 80, coords: [114.40, 30.63] },
  { name: '黄陂', count: 3, coords: [114.38, 30.88] }
];

// 根据房源数量获取标记颜色
const getMarkerColor = (count) => {
  if (count > 500) return '#e74c3c'; // 红色，大量房源
  if (count > 50) return '#2ecc71';  // 绿色，中等房源
  return '#3498db';                  // 蓝色，少量房源
};

// 获取简单的价格评估
const getPriceLevel = (count) => {
  if (count > 500) return '价格较高';
  if (count > 100) return '价格适中';
  return '价格较低';
};

onMounted(() => {
  loading.value = true;
  AMapLoader.load({
    key: 'f90241e76ce2ac3a4cab98cb651834d5', // 您的API Key
    version: '2.0',
    AMapUI: {
      version: '1.1',
      plugins: []
    },
    Loca: {
      version: '2.0.0'
    },
    plugins: [
      'AMap.ToolBar',
      'AMap.Scale',
      'AMap.HawkEye',
      'AMap.MapType',
      'AMap.Geolocation',
      'AMap.Marker',
      'AMap.InfoWindow'
    ]
  }).then((AMap) => {
    // 创建地图实例
    const map = new AMap.Map('map-container', {
      center: [114.3, 30.5], // 武汉市中心坐标
      zoom: 11,
      viewMode: '3D'  // 3D视角
    });
    
    // 添加地图控件
    map.addControl(new AMap.ToolBar());  // 工具条
    map.addControl(new AMap.Scale());    // 比例尺
    map.addControl(new AMap.HawkEye({ isOpen: false })); // 鹰眼
    map.addControl(new AMap.MapType()); // 地图类型切换
    map.addControl(new AMap.Geolocation({
      position: 'RB',
      offset: [10, 20]
    })); // 定位控件

    // 遍历区域数据，添加标记
    areas.forEach((area) => {
      const color = getMarkerColor(area.count);
      
      // 创建自定义标记样式
      const markerContent = document.createElement('div');
      markerContent.className = 'custom-marker';
      markerContent.style.backgroundColor = color;
      markerContent.innerHTML = `<span>${area.name}</span>`;
      
      // 创建标记
      const marker = new AMap.Marker({
        position: area.coords,
        content: markerContent,
        offset: new AMap.Pixel(-15, -15), // 偏移量
        zIndex: Math.floor(area.count / 10) // 根据房源数量设置层级
      });
      
      // 将标记添加到地图
      marker.setMap(map);

      // 点击标记时显示信息窗口
      marker.on('click', () => {
        const infoWindow = new AMap.InfoWindow({
          content: `
            <div class="info-window">
              <div class="info-header" style="background-color:${color}">
                <h3>${area.name}</h3>
              </div>
              <div class="info-body">
                <p><strong>房源数量:</strong> ${area.count} 套</p>
                <p><strong>区域评估:</strong> ${getPriceLevel(area.count)}</p>
                <p><strong>位置:</strong> ${area.coords[0].toFixed(2)}, ${area.coords[1].toFixed(2)}</p>
                <p><a href="/analysis?area=${area.name}" target="_blank">查看区域房源详情</a></p>
              </div>
            </div>
          `,
          offset: new AMap.Pixel(0, -30),
          closeWhenClickMap: true,        // 点击地图关闭
          autoMove: true,                 // 自动调整窗体到视野内
          contentStyle: {                 // 信息窗体样式
            padding: '0',
            borderRadius: '8px',
            boxShadow: '0 2px 6px rgba(0,0,0,0.3)'
          }
        });
        
        infoWindow.open(map, marker.getPosition());
      });
    });
    
    // 地图加载完成
    loading.value = false;
    
  }).catch((e) => {
    console.error('高德地图API加载失败', e);
    loading.value = false;
  });
});
</script>

<style scoped lang="scss">


.flex-grow {
  flex-grow: 1;
}

.map-container {
  position: relative;
  width: 100%;
  padding: 20px;
  background-color: #f5f7fa;
}

.map-title {
  text-align: center;
  margin-bottom: 20px;
  
  h2 {
    font-size: 24px;
    color: #333;
    margin-bottom: 5px;
  }
  
  p {
    font-size: 16px;
    color: #666;
  }
}

.map-content {
  width: 100%;
  height: 680px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.loading-spinner {
  text-align: center;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  
  .el-icon {
    font-size: 32px;
    color: #409EFF;
    margin-bottom: 10px;
  }
}

.map-legend {
  position: absolute;
  bottom: 40px;
  right: 40px;
  background-color: white;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 100;
  
  .legend-title {
    font-weight: bold;
    margin-bottom: 8px;
    text-align: center;
  }
  
  .legend-item {
    display: flex;
    align-items: center;
    margin-bottom: 5px;
    
    .legend-color {
      width: 16px;
      height: 16px;
      border-radius: 50%;
      margin-right: 8px;
    }
  }
}

// 自定义标记样式
:deep(.custom-marker) {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  color: white;
  text-align: center;
  line-height: 30px;
  font-weight: bold;
  border: 2px solid white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  
  span {
    display: none;
  }
  
  &:hover {
    transform: scale(1.2);
    
    span {
      display: block;
      position: absolute;
      top: -25px;
      left: 50%;
      transform: translateX(-50%);
      white-space: nowrap;
      background-color: rgba(0, 0, 0, 0.7);
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 12px;
    }
  }
}

// 信息窗口样式
:deep(.info-window) {
  width: 250px;
  
  .info-header {
    padding: 10px;
    color: white;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    
    h3 {
      margin: 0;
      font-size: 16px;
    }
  }
  
  .info-body {
    padding: 10px;
    
    p {
      margin: 5px 0;
      font-size: 14px;
    }
    
    a {
      color: #409EFF;
      text-decoration: none;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }
}
</style>