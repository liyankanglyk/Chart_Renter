# -*- coding: utf-8 -*-
from scrapy import signals
from .settings import USER_AGENT_LIST
import random

class OptimizedUserAgentMiddleware:
    """优化User-Agent的中间件"""
    
    def __init__(self, user_agent_list):
        self.user_agent_list = user_agent_list
        self.current_ua = random.choice(user_agent_list)
        self.ua_update_interval = 100  # 每100次请求更换一次UA
        self.request_count = 0
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(USER_AGENT_LIST)
    
    def process_request(self, request, spider):
        self.request_count += 1
        if self.request_count % self.ua_update_interval == 0:
            self.current_ua = random.choice(self.user_agent_list)
        
        request.headers['User-Agent'] = self.current_ua
        # 添加常用请求头
        request.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        })
        spider.logger.debug(f'使用User-Agent: {self.current_ua}') 