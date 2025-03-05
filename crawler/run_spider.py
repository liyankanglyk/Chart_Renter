#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
武汉租房爬虫启动脚本
"""

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.spiders.wuhan_housing import WuhanHousingSpider
import os
import sys

# 添加项目根目录到路径，以便导入config模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """启动爬虫"""
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(WuhanHousingSpider)
    print("开始爬取武汉租房数据...")
    process.start()  # 启动爬虫，该函数会阻塞，直到爬取完成
    print("爬取完成!")


if __name__ == '__main__':
    main()
