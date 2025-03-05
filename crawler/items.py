# -*- coding: utf-8 -*-
import scrapy


class WuhanHousingItem(scrapy.Item):
    """定义武汉租房数据结构"""
    # 基本信息
    house_id = scrapy.Field()  # 房源ID
    title = scrapy.Field()  # 标题
    url = scrapy.Field()  # 详情页URL

    # 位置信息
    district = scrapy.Field()  # 区域(如武昌区、洪山区等)
    area = scrapy.Field()  # 商圈(如水果湖、光谷等)
    address = scrapy.Field()  # 详细地址

    # 房屋特征
    layout = scrapy.Field()  # 户型(如2室1厅1卫)
    size = scrapy.Field()  # 面积(平方米)
    orientation = scrapy.Field()  # 朝向
    decoration = scrapy.Field()  # 装修状况
    floor = scrapy.Field()  # 楼层信息

    # 价格信息
    price = scrapy.Field()  # 月租金(元)
    price_per_sqm = scrapy.Field()  # 单位面积租金(元/平方米)

    # 其他信息
    tags = scrapy.Field()  # 标签(如近地铁、精装修等)
    facilities = scrapy.Field()  # 配套设施
    description = scrapy.Field()  # 房源描述
    images = scrapy.Field()  # 房源图片链接

    # 爬取信息
    crawl_time = scrapy.Field()  # 爬取时间
