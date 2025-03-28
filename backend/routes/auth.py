import os
import pprint
import random

import pandas as pd
from flask import Blueprint, request, jsonify
from ..models.user import User, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '用户名和密码不能为空'}), 400
        
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400
        
    user = User(
        username=data['username'],
        email=data.get('email')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': '注册成功'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '用户名和密码不能为空'}), 400
        
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        user.last_login = datetime.utcnow()
        db.session.commit()
        return jsonify({
            'message': '登录成功',
            'user': user.to_dict()
        }), 200
    
    return jsonify({'message': '用户名或密码错误'}), 401


@auth_bp.route('/analysis', methods=['POST'])
def analysis():
    # 指定目标文件夹路径
    folder_path = 'data/districts'

    # 获取文件夹下的所有文件名
    file_names = os.listdir(folder_path)
    # 打印文件名列表
    print(file_names)

    data = request.get_json()
    city = file_names[int(data.get('index'))]
    # 假设你的CSV文件名为'rental_properties.csv'
    csv_file_name = folder_path+'/'+city
    cityName = city.split('.')[0];
    # 使用pandas读取CSV文件
    df = pd.read_csv(csv_file_name,nrows=10)

    # 打印出CSV文件的前几行，以验证数据是否正确读取
    print(df.head())
    # 放数据的
    info=[];

    # 如果你想遍历每一行并处理数据
    for index, row in df.iterrows():
        print(f"title: {row['title']}, Price: {row['price']}, Size: {row['size']}, Layout: {row['layout']},orientation: {row['orientation']},decoration:{row['decoration']},url:{row['url']}")
        # 你可以继续访问其他列，如row['orientation'], row['floor']等
        dirt={"city":cityName,"title":row['title'],"Price":row['price'],"Size":row['size'],"Layout":row['layout'],"orientation":row['orientation'],"floor":row['floor'],"url":row['url'],"tags":row['tags']}
        info.append(dirt);

    return jsonify({'info': info}), 200
# 区域租金预测散点图
@auth_bp.route('/RentalPredictionScatterPlot', methods=['POST'])
def RentalPredictionScatterPlot():
    folder_path = 'data/districts'

    # 获取文件夹下的所有文件名
    file_names = os.listdir(folder_path)
    # 打印文件名列表
    print(file_names)
    dataInfo=[];
    data = request.get_json()
    city = file_names[int(data.get('index'))]
    # 假设你的CSV文件名为'rental_properties.csv'
    csv_file_name = folder_path + '/' + city
    # 使用pandas读取CSV文件
    df = pd.read_csv(csv_file_name)
    # 如果你想遍历每一行并处理数据
    for index, row in df.iterrows():
        random_number = random.uniform(0, 100)
        price = row['price'];
        dataItem = [random_number,price]
        dataInfo.append(dataItem);
    return jsonify({'info': dataInfo}), 200


@auth_bp.route('/handleCurrentChange', methods=['POST'])
def handleCurrentChange():
    # 指定目标文件夹路径
    folder_path = 'data/districts'

    # 获取文件夹下的所有文件名
    file_names = os.listdir(folder_path)
    # 打印文件名列表
    print(file_names)

    data = request.get_json()
    city = file_names[int(data.get('index'))]
    page = int(data.get('page'))
    page = (page-1)*10;
    # 假设你的CSV文件名为'rental_properties.csv'
    csv_file_name = folder_path+'/'+city
    cityName = city.split('.')[0];
    df = "";
    # 使用pandas读取CSV文件
    if(page>0):
        df = pd.read_csv(csv_file_name,skiprows=lambda x: x in range(2,page+1),nrows=10)
    else:
        df = pd.read_csv(csv_file_name, nrows=10)
    # 打印出CSV文件的前几行，以验证数据是否正确读取
    for index, row in df.iterrows():
        pprint.pprint(row)
    # 放数据的
    info=[];

    # 如果你想遍历每一行并处理数据
    for index, row in df.iterrows():
        print(f"title: {row['title']}, Price: {row['price']}, Size: {row['size']}, Layout: {row['layout']},orientation: {row['orientation']},decoration:{row['decoration']},url:{row['url']}")
        # 你可以继续访问其他列，如row['orientation'], row['floor']等
        dirt={"city":cityName,"title":row['title'],"Price":row['price'],"Size":row['size'],"Layout":row['layout'],"orientation":row['orientation'],"floor":row['floor'],"url":row['url'],"tags":row['tags']}
        info.append(dirt);

    return jsonify({'info': info}), 200

@auth_bp.route('/RestAnalysis', methods=['POST'])
def RestAnalysis():
    # 指定目标文件夹路径
    folder_path = 'data/districts'

    # 获取文件夹下的所有文件名
    file_names = os.listdir(folder_path)
    orientations = ['南','东','北','西','东南','西南','东北','西北'];

    # 打印文件名列表
    print(file_names)
    data = request.get_json()
    orientation = orientations[int(data.get('orientations'))]
    city = file_names[int(data.get('index'))]
    # 假设你的CSV文件名为'rental_properties.csv'
    csv_file_name = folder_path+'/'+city
    cityName = city.split('.')[0];
    size = int(data.get('size'));
    orientations = data.get('orientations')
    df = "";
    # 使用pandas读取CSV文件
    df = pd.read_csv(csv_file_name)

    # 打印出CSV文件的前几行，以验证数据是否正确读取
    # 放数据的
    info=[];
    pricew = [
        {'value': 0, 'name': '0-1000元'},
        {'value': 0, 'name': '1000-3000元'},
        { 'value': 0, 'name': '3000-5000元' },
        { 'value': 0, 'name': '5000-8000元' },
        { 'value': 0, 'name': '大于8000元' }
        ]
    # 如果你想遍历每一行并处理数据
    for index, row in df.iterrows():
        print(f"title: {row['title']}, Price: {row['price']}, Size: {row['size']}, Layout: {row['layout']},orientation: {row['orientation']},decoration:{row['decoration']},url:{row['url']}")
        # 你可以继续访问其他列，如row['orientation'], row['floor']等
        dirt={"city":cityName,"title":row['title'],"Price":row['price'],"Size":row['size'],"Layout":row['layout'],"orientation":row['orientation'],"floor":row['floor'],"url":row['url'],"tags":row['tags']}
        if (size == 0):
            if (float(row['size']) <50 and orientation == row['orientation']):
                if (row['price'] < 1001):
                    pricew[0]['value'] = pricew[0]['value'] + 1
                elif (1000 < row['price'] and 3001 > row['price']):
                    pricew[1]['value'] = pricew[1]['value'] + 1
                elif (3000 < row['price'] and 5001 > row['price']):
                    pricew[2]['value'] = pricew[2]['value'] + 1
                elif (5000 < row['price'] and 8001 > row['price']):
                    pricew[3]['value'] = pricew[3]['value'] + 1
                else:
                    pricew[4]['value'] = pricew[4]['value'] + 1
        elif (size == 1):
            if (float(row['size']) > 49 and float(row['size']) < 91 and orientation == row['orientation']):
                if (row['price'] < 1001):
                    pricew[0]['value'] = pricew[0]['value'] + 1
                elif (1000 < row['price'] and 3001 > row['price']):
                    pricew[1]['value'] = pricew[1]['value'] + 1
                elif (3000 < row['price'] and 5001 > row['price']):
                    pricew[2]['value'] = pricew[2]['value'] + 1
                elif (5000 < row['price'] and 8001 > row['price']):
                    pricew[3]['value'] = pricew[3]['value'] + 1
                else:
                    pricew[4]['value'] = pricew[4]['value'] + 1
        elif (size == 2):
            if (float(row['size']) > 90 and float(row['size']) < 121 and orientation == row['orientation']):
                if (row['price'] < 1001):
                    pricew[0]['value'] = pricew[0]['value'] + 1
                elif (1000 < row['price'] and 3001 > row['price']):
                    pricew[1]['value'] = pricew[1]['value'] + 1
                elif (3000 < row['price'] and 5001 > row['price']):
                    pricew[2]['value'] = pricew[2]['value'] + 1
                elif (5000 < row['price'] and 8001 > row['price']):
                    pricew[3]['value'] = pricew[3]['value'] + 1
                else:
                    pricew[4]['value'] = pricew[4]['value'] + 1
        elif (size == 3):
            if (float(row['size']) > 120 and orientation == row['orientation']):
                if (row['price'] < 1001):
                    pricew[0]['value'] = pricew[0]['value'] + 1
                elif (1000 < row['price'] and 3001 > row['price']):
                    pricew[1]['value'] = pricew[1]['value'] + 1
                elif (3000 < row['price'] and 5001 > row['price']):
                    pricew[2]['value'] = pricew[2]['value'] + 1
                elif (5000 < row['price'] and 8001 > row['price']):
                    pricew[3]['value'] = pricew[3]['value'] + 1
                else:
                    pricew[4]['value'] = pricew[4]['value'] + 1


    return jsonify({'pricew': pricew}), 200


@auth_bp.route('/restNumber1', methods=['POST'])
def restNumber1():
    folder_path = 'data/districts'
    infox = [];
    infoy = [];
    # 获取文件夹下的所有文件名
    file_names = os.listdir(folder_path)
    for city in file_names:
        cityName = city.split('.')[0];
        csv_file_name = folder_path + '/' + city
        df = pd.read_csv(csv_file_name);
        row_cout = len(df);
        print(row_cout)
        infoy.append(row_cout);
        infox.append(cityName);
    # 打印文件名列表
    return jsonify({'infox': infox,'infoy':infoy}), 200

@auth_bp.route('/restNumber', methods=['POST'])
def restNumber():
    folder_path = 'data/districts'
    info = [];
    # 获取文件夹下的所有文件名
    file_names = os.listdir(folder_path)
    for city in file_names:
        csv_file_name = folder_path + '/' + city
        df = pd.read_csv(csv_file_name);
        row_cout = len(df);
        dirt = {"value":row_cout,"name":city}
        info.append(dirt);
    # 打印文件名列表
    return jsonify({'info': info}), 200

@auth_bp.route('/restNumber1', methods=['POST'])
def RestAnalysis1():
    folder_path = 'data/districts'
    infox = [];
    infoy = [];
    # 获取文件夹下的所有文件名
    file_names = os.listdir(folder_path)
    for city in file_names:
        cityName = city.split('.')[0];
        csv_file_name = folder_path + '/' + city
        df = pd.read_csv(csv_file_name);
        row_cout = len(df);
        print(row_cout);
        infoy.append(row_cout);
        infox.append(cityName);
    # 打印文件名列表
    return jsonify({'infox': infox,'infoy':infoy}), 200

@auth_bp.route('/averageHousePrice1', methods=['POST'])
def averageHousePrice():
    folder_path = 'data/districts'
    infox = [];
    infoy = [];
    # 获取文件夹下的所有文件名
    file_names = os.listdir(folder_path)
    for city in file_names:
        cityName = city.split('.')[0];
        csv_file_name = folder_path + '/' + city
        df = pd.read_csv(csv_file_name);
        amout_column = df['price']
        average_amount = amout_column.mean()
        infox.append(cityName);
        dirt = {"value": average_amount, "name": cityName}
        infoy.append(dirt);
        # 打印文件名列表
    return jsonify({'info': infoy}), 200
    # 打印文件名列表
    return jsonify({'info': info}), 200
@auth_bp.route('/averageHousePrice', methods=['POST'])
def averageHousePrice1():
    folder_path = 'data/districts'
    infox = [];
    infoy = [];
    # 获取文件夹下的所有文件名
    file_names = os.listdir(folder_path)
    for city in file_names:
        cityName = city.split('.')[0];
        csv_file_name = folder_path + '/' + city
        df = pd.read_csv(csv_file_name);
        amout_column = df['price']
        average_amount = amout_column.mean();
        infoy.append(average_amount);
        infox.append(cityName);
        # 打印文件名列表
    return jsonify({'infox': infox, 'infoy': infoy}), 200

@auth_bp.route('/prediction', methods=['POST'])
def forestpPrice():
    # 指定目标文件夹路径
    folder_path = 'data/districts'

    # 获取文件夹下的所有文件名
    file_names = os.listdir(folder_path)
    orientations = ['南','东','北','西','东南','西南','东北','西北'];

    # 打印文件名列表
    print(file_names)
    data = request.get_json()
    orientation = orientations[int(data.get('orientations'))]
    city = file_names[int(data.get('index'))]
    # 假设你的CSV文件名为'rental_properties.csv'
    csv_file_name = folder_path + '/' + city
    cityName = city.split('.')[0];
    size = int(data.get('size'));
    orientations = data.get('orientations')
    df = "";
    # 使用pandas读取CSV文件
    df = pd.read_csv(csv_file_name)
    # 数量
    sump = 0;
    # 金额
    moneys = 0;
    # 打印出CSV文件的前几行，以验证数据是否正确读取
    # 放数据的
    info=[];
    # 如果你想遍历每一行并处理数据
    for index, row in df.iterrows():
        print(f"title: {row['title']}, Price: {row['price']}, Size: {row['size']}, Layout: {row['layout']},orientation: {row['orientation']},decoration:{row['decoration']},url:{row['url']}")
        # 你可以继续访问其他列，如row['orientation'], row['floor']等
        dirt={"city":cityName,"title":row['title'],"Price":row['price'],"Size":row['size'],"Layout":row['layout'],"orientation":row['orientation'],"floor":row['floor'],"url":row['url'],"tags":row['tags']}
        sump = sump + 1;
        if (size == 0):
            if (float(row['size']) < 50 and orientation == row['orientation']):
                moneys = moneys+row['price'];
        elif (size == 1):
            if (float(row['size']) > 49 and float(row['size']) < 91 and orientation == row['orientation']):
                moneys = moneys + row['price'];
        elif (size == 2):
            if (float(row['size']) > 90 and float(row['size']) < 121 and orientation == row['orientation']):
                moneys = moneys + row['price'];
        elif (size == 3):
            if (float(row['size']) > 120 and orientation == row['orientation']):
                moneys = moneys + row['price'];
    moneys = round(moneys/sump,2);
    return jsonify({'moneys': moneys}), 200


@auth_bp.route('/map', methods=['POST'])
def map():
    folder_path = 'data/districts'
    infox = [];
    infoy = [];
    areas = [
    {'name': '0', 'coords': [114.43, 30.52]},
    {'name': '1', 'coords': [114.13, 30.62]},
    {'name': '2', 'coords': [114.80, 30.83]},
    {'name': '3', 'coords': [114.32, 30.55]},
    {'name': '4', 'coords': [114.20, 30.40]},
    {'name': '5', 'coords': [113.73, 30.32]},
    {'name': '6', 'coords': [114.27, 30.55]},
    {'name': '7', 'coords': [114.33, 30.35]},
    {'name': '8', 'coords': [114.30, 30.60]},
    {'name': '9', 'coords': [114.27, 30.58]},
    {'name': '10', 'coords': [114.18, 30.52]},
    {'name': '11', 'coords': [114.35, 30.50]},
    {'name': '12', 'coords': [114.23, 30.57]},
    {'name': '13', 'coords': [114.18, 30.48]},
    {'name': '14', 'coords': [114.03, 30.58]},
    {'name': '15', 'coords': [114.40, 30.63]},
    {'name': '16', 'coords': [114.38, 30.88]}
    ];
    index = 0;

    # 获取文件夹下的所有文件名
    file_names = os.listdir(folder_path)
    for city in file_names:
        cityName = city.split('.')[0];
        csv_file_name = folder_path + '/' + city
        df = pd.read_csv(csv_file_name);
        size = len(df);
        print(size);
        areas[index]['name'] = cityName+"："+size;
        # 打印文件名列表
    return jsonify({'areas': areas}), 200