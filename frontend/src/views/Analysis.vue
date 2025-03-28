<template>
  <div class="analysis">
    <!-- 顶部导航栏 -->
    <NavBar :active-index="activeIndex" @logout="handleLogout" />

    <div class="main-content">
      <h1>数据分析</h1>
      <div style="width:200px">
        <el-select v-model="selectedCity" placeholder="请选择地区" @change="handleCityChange">
          <el-option
              v-for="city in cities"
              :key="city.value"
              :label="city.label"
              :value="city.value">
          </el-option>
        </el-select>
      </div>
      <div class="analysis-container">

        <el-card class="chart-card">

           <div>
            <el-table :data="houseList" >
              <el-table-column prop="citys" label="" width="100"></el-table-column>
              <el-table-column prop="city" label="地区" width="100"></el-table-column>
              <el-table-column prop="title" label="详细地址" width="400"></el-table-column>
              <el-table-column prop="orientation" label="朝向" width="100"></el-table-column>
              <el-table-column prop="Price" label="每月租金" width="100"></el-table-column>
              <el-table-column prop="Size" label="房屋面积" width="150"></el-table-column>
              <el-table-column prop="floor" label="格局" width="250"></el-table-column>
              <el-table-column prop="tags" label="标签" width="400"></el-table-column>
              <el-table-column prop="url" label="操作" width="120">
                <template #default="scope">
                  <a :href="`${scope.row.url}`">详情</a>
                  <!-- 注意：type="text" 会给出一个没有背景色只有文字颜色的按钮，如果您想要蓝色背景，请使用 type="primary" 并自定义背景色或在样式中定义 -->
                </template>
              </el-table-column>
            </el-table>
            <el-pagination
              background
              layout="prev, pager, next"
              :total="total"
              page-size="10"
              @current-change="handleCurrentChange"
            ></el-pagination>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import {authApi} from "@/api/auth";
import NavBar from '../components/NavBar.vue'

export default {
  name: 'Analysis',
  components: {
    NavBar
  },
  setup() {

    const store = useStore()
    const router = useRouter()
    const activeIndex = ref('/analysis')
    const houseList=ref('')
        // ... 其他房源数据，

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
    const selectedCity = ref('');
    const cityIndex = ref('0');
    const isAuthenticated = computed(() => store.state.isAuthenticated)
    const currentPage = ref(1)
    // 定义一个方法来查看 selectedCity 的值
    // 方法：处理城市变化（如果不需要执行任何逻辑，这个方法也可以移除）
    const handleCityChange = async (value) => {
      currentPage.value = 1;
      console.log('选中的城市值变化了：', value);
      cityIndex.value = value;

      try {
        // 设置请求的URL和数据
        const response = await authApi.analysis(value);

        console.log(response);
        houseList.value = response.info
      } catch (error) {
        console.error('请求失败:', error);
      }
    };

    const handleLogout = () => {
      store.dispatch('logout')
      router.push('/')
    }
    // 新添加的方法，例如：获取下一页房源数据
    const handleCurrentChange = async(page) => {
      // 这里可以添加你的分页逻辑，比如从API获取下一页的数据
      // 并更新houseList或当前显示的数据集
      console.log('Fetching next page...')
      console.log(page)
      // 示例：假设有一个函数getNextPageHouses()可以从API获取下一页的数据
      // const nextPageHouses = getNextPageHouses();
      // 然后你需要更新你的数据状态，这可能涉及到合并数据或替换当前数据
      // 注意：这里的getNextPageHouses()函数需要你根据实际情况实现
      try {
        // 设置请求的URL和数据
        const response = await authApi.handleCurrentChange(cityIndex.value,page);
        console.log(response);
        houseList.value = response.info
      } catch (error) {
        console.error('请求失败:', error);
      }
    }
    onMounted(async () => {
      try {
        // 设置请求的URL和数据
        const response = await authApi.analysis(0);
        console.log(response);
        houseList.value = response.info
      } catch (error) {
        console.error('请求失败:', error);
      }
    });

    return {
      activeIndex,
      isAuthenticated,
      handleLogout,
      houseList,
      handleCurrentChange,    // 新添加的方法，例如：获取下一页房源数据
      selectedCity,
      handleCityChange,    // 定义一个方法来查看 selectedCity 的值
      currentPage,
      cities, // 可以继续添加更多城市
      total: 875 // 总房源数
    }
  }
}
</script>

<style scoped lang="scss">
.analysis {
  min-height:300vh;
  background-color: #f5f7fa;
}



.flex-grow {
  flex-grow: 1;
}

.main-content {
  padding: 40px;
  max-width: 1800px;
  margin: 0 auto;

  h1 {
    margin-bottom: 30px;
    color: #303133;
  }
}

.analysis-container {
  width: 100%;
  .chart-card {
    margin-bottom: 20px;

    .card-header {
      font-weight: bold;
    }
    
    .card-content {
      padding: 20px;
      text-align: center;
      color: #909399;
    }

  }
}
</style> 