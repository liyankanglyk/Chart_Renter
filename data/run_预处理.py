import pandas as pd
import os
import re


def process_data():
    # 获取当前脚本的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 创建必要的目录
    processed_dir = os.path.join(current_dir, 'processed')
    districts_dir = os.path.join(current_dir, 'districts')

    # 创建目录（如果不存在）
    for directory in [processed_dir, districts_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f'创建目录: {directory}')

    # 构建输入文件的绝对路径
    input_file = os.path.join(current_dir, 'raw', 'wuhan_housing.csv')

    # 直接使用UTF-8读取文件
    df = pd.read_csv(input_file, encoding='utf-8')
    print('使用UTF-8编码读取文件成功')

    # 数据清洗：删除area字段为空或未知的记录
    if 'area' in df.columns:
        # 记录清洗前的数量
        before_count = len(df)
        # 删除area为空的记录
        df = df.dropna(subset=['area'])
        # 删除area为'未知'的记录
        df = df[df['area'] != '未知']
        # 记录清洗后的数量
        after_count = len(df)
        print(f'已清洗area字段，删除空值和未知值的记录：从{before_count}条减少到{after_count}条')

    # 数据清洗：处理floor字段，去掉括号内容
    def clean_floor(floor):
        if pd.isna(floor):
            return floor
        # 使用正则表达式去掉括号及其内容
        return re.sub(r'\s*\([^)]*\)', '', str(floor))

    # 应用floor字段清洗
    if 'floor' in df.columns:
        df['floor'] = df['floor'].apply(clean_floor)
        print('已清洗floor字段，去除括号内容')

    # 数据清洗：处理description字段
    if 'description' in df.columns:
        df['description'] = df['description'].replace('房源亮点', '无')
        print('已清洗description字段，将"房源亮点"替换为"无"')

    # 打印列名，以检查实际存在的列
    print(f'数据中的列名: {df.columns.tolist()}')

    # 检查是否有包含"id"的列（不区分大小写）
    id_columns = [col for col in df.columns if 'id' in col.lower()]
    print(f'包含"id"的列: {id_columns}')

    # 去重前的记录数
    print(f'去重前的记录数: {len(df)}')

    # 如果找到了id列，就用它来去重
    if id_columns:
        id_column = id_columns[0]  # 使用第一个找到的id列
        print(f'使用列 "{id_column}" 进行去重')
        df = df.drop_duplicates(subset=[id_column])
    else:
        # 如果没有id列，尝试使用所有列进行去重
        print('未找到id列，使用所有列进行去重')
        df = df.drop_duplicates()

    print(f'去重后的记录数: {len(df)}')

    # 保存去重后的数据
    deduplicated_file = os.path.join(processed_dir, 'wuhan_housing_deduplicated.csv')
    df.to_csv(deduplicated_file, index=False, encoding='utf-8')
    print(f'已保存去重后的数据到: {deduplicated_file}')

    # 获取所有不同的区域
    districts = df['district'].unique()

    # 函数用于生成安全的文件名
    def safe_filename(name):
        if pd.isna(name):
            return "unknown_district"
        # 将非字母数字字符替换为下划线
        return re.sub(r'[^\w\s]', '_', name)

    # 按区域拆分并保存
    for district in districts:
        district_df = df[df['district'] == district]

        # 生成安全的文件名
        if pd.isna(district):
            safe_name = "unknown_district"
            display_name = "未知区域"
        else:
            safe_name = safe_filename(district)
            display_name = district

        output_file = os.path.join(districts_dir, f'{safe_name}.csv')
        district_df.to_csv(output_file, index=False, encoding='utf-8')

        print(f'已保存区域 [{display_name}] 的数据到: {output_file}')


if __name__ == '__main__':
    process_data()
