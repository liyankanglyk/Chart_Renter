const fs = require('fs');
const path = require('path');

// 获取views目录路径
const viewsDir = path.join(__dirname, '..', 'views');

// 读取目录中的所有文件
const files = fs.readdirSync(viewsDir);

// 过滤出.vue文件
const vueFiles = files.filter(file => file.endsWith('.vue'));

// 处理每个Vue文件
vueFiles.forEach(file => {
  const filePath = path.join(viewsDir, file);
  let content = fs.readFileSync(filePath, 'utf8');
  
  // 检查文件是否包含导航栏
  if (content.includes('<el-menu') && content.includes(':default-active="activeIndex"')) {
    console.log(`处理文件: ${file}`);
    
    // 替换导航栏为NavBar组件
    content = content.replace(
      /<!-- 顶部导航栏 -->\s*<el-menu[\s\S]*?<\/el-menu>/,
      '<!-- 顶部导航栏 -->\n    <NavBar :active-index="activeIndex" @logout="handleLogout" />'
    );
    
    // 添加NavBar组件导入
    if (!content.includes("import NavBar from '../components/NavBar.vue'")) {
      // 找到import块的结束位置
      const importEndIndex = content.lastIndexOf('import');
      const importEndLine = content.indexOf('\n', importEndIndex);
      
      // 插入NavBar导入
      content = content.slice(0, importEndLine + 1) + 
                "import NavBar from '../components/NavBar.vue'\n" + 
                content.slice(importEndLine + 1);
    }
    
    // 添加NavBar到components部分
    if (content.includes('components: {')) {
      // 找到现有的components block
      const componentsStart = content.indexOf('components: {');
      const componentsEnd = content.indexOf('}', componentsStart);
      
      // 检查是否已经包含NavBar
      if (!content.slice(componentsStart, componentsEnd).includes('NavBar')) {
        // 在components块的末尾添加NavBar
        content = content.slice(0, componentsEnd) + 
                  ',\n    NavBar' + 
                  content.slice(componentsEnd);
      }
    } else if (content.includes('export default {')) {
      // 没有components部分，添加一个
      const exportStart = content.indexOf('export default {');
      const nameEnd = content.indexOf(',', exportStart + 'export default {'.length);
      
      // 在name后面添加components部分
      content = content.slice(0, nameEnd + 1) + 
                '\n  components: {\n    NavBar\n  }' + 
                content.slice(nameEnd + 1);
    }
    
    // 移除多余的nav-menu样式
    content = content.replace(/\.nav-menu\s*{[\s\S]*?}/g, '');
    
    // 保存修改后的文件
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`更新完成: ${file}`);
  } else {
    console.log(`跳过文件: ${file} (没有找到导航栏)`);
  }
});

console.log('所有文件处理完成!'); 