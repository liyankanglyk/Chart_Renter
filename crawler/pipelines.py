# -*- coding: utf-8 -*-
import csv
import os
from datetime import datetime
from config import PATH_CONFIG

class WuhanRentalPipeline:
    def __init__(self):
        self.items = []
        self.batch_size = 100  # 每100条数据批量写入一次
        
    def process_item(self, item, spider):
        self.items.append(dict(item))
        
        # 达到批量大小时写入文件
        if len(self.items) >= self.batch_size:
            self._write_items()
        return item
    
    def _write_items(self):
        if not self.items:
            return
            
        # 批量写入CSV
        with open(PATH_CONFIG['raw_data'], 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.items[0].keys())
            if f.tell() == 0:  # 如果文件为空，写入表头
                writer.writeheader()
            writer.writerows(self.items)
        
        self.items = []  # 清空列表
    
    def close_spider(self, spider):
        # 确保所有剩余数据都被写入
        self._write_items() 