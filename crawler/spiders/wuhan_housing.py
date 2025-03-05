# -*- coding: utf-8 -*-
import scrapy
import re
import time
import random
import os
import json
from crawler.items import WuhanHousingItem
from config import CRAWLER_CONFIG, PATH_CONFIG
from scrapy.utils.log import configure_logging
import logging
from urllib.parse import urljoin
from twisted.internet.error import TimeoutError, TCPTimedOutError
from datetime import datetime
import csv

# 配置日志
configure_logging(install_root_handler=False)

# 创建日志文件名（包含时间戳）
log_filename = f'crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
log_filepath = os.path.join(PATH_CONFIG['log_dir'], log_filename)

# 确保日志目录存在
os.makedirs(os.path.dirname(log_filepath), exist_ok=True)

# 配置日志
logging.basicConfig(
    filename=log_filepath,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    level=logging.DEBUG,
    encoding='utf-8'
)


class WuhanHousingSpider(scrapy.Spider):
    name = 'wuhan_housing'
    allowed_domains = ['zu.fang.com']
    start_urls = ['https://wuhan.zu.fang.com/house/i31/']  # 直接指定起始URL

    # 定义输出字段和顺序
    custom_settings = {
        'FEED_EXPORT_FIELDS': [
            'house_id',  # 房源ID
            'title',  # 标题
            'price',  # 价格
            'size',  # 面积
            'layout',  # 户型
            'orientation',  # 朝向
            'floor',  # 楼层
            'decoration',  # 装修情况
            'district',  # 区域
            'area',  # 小区
            'address',  # 地址
            'tags',  # 标签
            'description',  # 描述
            'price_per_sqm',  # 每平米价格
            'images',  # 图片链接
            'facilities',  # 配套设施
            'url',  # 详情页URL
            'crawl_time'  # 爬取时间
        ],
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 2,
        'COOKIES_ENABLED': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def __init__(self, *args, **kwargs):
        super(WuhanHousingSpider, self).__init__(*args, **kwargs)
        # 创建输出目录
        self.output_dir = os.path.dirname(PATH_CONFIG['raw_data'])
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # 记录已爬取的房源ID
        self.crawled_ids = set()

        # 记录爬虫开始时间
        self.start_time = datetime.now()

        # 配置彩色日志
        self.setup_colored_logging()

        # 修改页数限制
        self.max_items = 6000  # 最多爬取6000条数据
        self.max_pages = 300  # 增加最大页数限制到200页
        self.current_count = 0
        self.current_page = 0

    def setup_colored_logging(self):
        """配置彩色日志输出"""
        try:
            import colorama
            colorama.init()  # 初始化colorama来支持Windows系统

            # 定义颜色代码
            self.colors = {
                'RED': '\033[91m',
                'GREEN': '\033[92m',
                'YELLOW': '\033[93m',
                'BLUE': '\033[94m',
                'MAGENTA': '\033[95m',
                'CYAN': '\033[96m',
                'WHITE': '\033[97m',
                'RESET': '\033[0m',
                'BOLD': '\033[1m',
                'UNDERLINE': '\033[4m'
            }
        except ImportError:
            # 如果colorama不可用，使用空字符串
            self.colors = {k: '' for k in
                           ['RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE', 'RESET', 'BOLD', 'UNDERLINE']}

    def parse(self, response):
        """解析列表页"""
        c = self.colors
        house_items = response.css('dl.list.hiddenMap.rel')
        house_count = len(house_items)

        # 修改页码提取逻辑
        page_match = re.search(r'/i3(\d+)/', response.url)
        if page_match:
            self.current_page = int(page_match.group(1))
        else:
            # 如果是第一页，URL可能没有页码
            self.current_page = 1

        # 检查是否达到最大页数限制（只有在已达到目标数据量时才停止）
        if self.current_page > self.max_pages and self.current_count >= self.max_items:
            self.logger.info(
                f"{c['BOLD']}{c['YELLOW']}已达到最大页数限制 {self.max_pages} 页且数据量充足，停止爬取{c['RESET']}")
            return

        # 只在开始新页面时显示一次信息
        self.logger.info(
            f"\n{c['BOLD']}{c['MAGENTA']}正在爬取第 {self.current_page} 页, 找到 {house_count} 个房源{c['RESET']}")

        # 记录当前页可用的房源数量，用于调试
        self.valid_houses_on_page = 0

        # 处理当前页面的房源
        for item in house_items:
            # 检查是否达到最大爬取量
            if self.current_count >= self.max_items:
                self.logger.info(f"{c['BOLD']}{c['YELLOW']}已达到最大爬取量 {self.max_items} 条，停止爬取{c['RESET']}")
                return

            # 提取详情页链接
            detail_link = item.css('dt.img a::attr(href)').get()

            if detail_link:
                self.valid_houses_on_page += 1
                yield scrapy.Request(
                    response.urljoin(detail_link),
                    callback=self.parse_detail,
                    meta={
                        'dont_redirect': True,
                        'handle_httpstatus_list': [302]
                    }
                )

        # 显示进度条
        progress = min(self.current_count / self.max_items, 1.0) * 100
        bar_length = 40
        filled_length = int(bar_length * progress / 100)
        bar = c['GREEN'] + '█' * filled_length + c['RESET'] + '░' * (bar_length - filled_length)

        self.logger.info(f"{c['BOLD']}进度: [{bar}] {c['YELLOW']}{progress:.1f}%{c['RESET']}")
        self.logger.info(f"{c['BOLD']}当前页发现 {house_count} 个房源，成功发起 {self.valid_houses_on_page} 个详情页请求{c['RESET']}")

        # 修改翻页逻辑
        if (house_count > 0 and
                (self.current_page < self.max_pages or self.current_count < self.max_items)):

            next_page = self.current_page + 1
            # 修改URL构建方式
            next_page_url = f"https://wuhan.zu.fang.com/house/i3{next_page}/"

            # 使用智能延迟策略
            delay = random.uniform(1.0, 2.0) if self.current_page < 10 else random.uniform(2.0, 3.5)

            self.logger.info(f"{c['BOLD']}{c['CYAN']}准备爬取下一页: {next_page}{c['RESET']}")

            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta={
                    'dont_redirect': True,
                    'handle_httpstatus_list': [302],
                    'download_delay': delay
                }
            )
        else:
            if self.current_count >= self.max_items:
                self.logger.info(f"{c['BOLD']}{c['YELLOW']}已达到目标爬取量 {self.max_items}{c['RESET']}")
            elif self.current_page >= self.max_pages:
                self.logger.info(f"{c['BOLD']}{c['YELLOW']}已达到最大页数 {self.max_pages}{c['RESET']}")
            else:
                self.logger.info(f"{c['BOLD']}{c['YELLOW']}当前页面没有房源，停止爬取{c['RESET']}")

    def parse_detail(self, response):
        """解析房源详情页"""
        try:
            # 检查跳转，如果需要跳转则处理
            redirect_request = self.handle_redirect(response)
            if redirect_request:
                return redirect_request

            # 创建房源项
            item = WuhanHousingItem()

            # 初始化所有字段，防止KeyError
            item['description'] = ''
            item['tags'] = '无标签' if not item.get('tags') else item['tags']
            item['price_per_sqm'] = 0
            item['facilities'] = ''
            item['url'] = response.url
            item['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 直接提取图片 - 添加这段代码
            images = self.extract_images(response)
            if images:
                item['images'] = images[0]  # 使用第一张图片
            else:
                # 使用列表页传递的图片
                item['images'] = response.meta.get('list_image', '')

            # 1. 直接从页面提取房源ID (更精确的方法)
            id_text = response.css('p.gray9.fybh-zf span.mr10::text').get()
            if id_text:
                house_id = re.search(r'房源编号\s*(\d+)', id_text)
                if house_id:
                    item['house_id'] = house_id.group(1)

            # 如果上面方法失败，尝试备用方法
            if not item.get('house_id'):
                id_pattern = re.search(r'[/_](\d{6,9})[._]', response.url)
                if id_pattern:
                    item['house_id'] = id_pattern.group(1)

            # 如果仍未找到有效ID，使用URL生成随机ID
            if not item.get('house_id'):
                import hashlib
                url_hash = hashlib.md5(response.url.encode()).hexdigest()
                item['house_id'] = f"gen_{url_hash[:8]}"
                self.logger.warning(f"无法提取房源ID，生成临时ID: {item['house_id']}")

            # 2. 提取标题
            item['title'] = response.css('div.title::text').get() or \
                            response.css('h1.title::text').get() or \
                            response.meta.get('list_title', '')
            item['title'] = item['title'].strip() if item['title'] else '未知'

            # 3. 提取价格 - 直接针对新结构
            price_text = response.css('div.trl-item.sty1.rel i.zf_fee::text').get() or \
                         response.css('div.trl-item.sty1.rel i.num::text').get()

            if price_text:
                item['price'] = self.validate_price(price_text)
            elif response.meta.get('list_price'):
                item['price'] = self.validate_price(response.meta.get('list_price'))
            else:
                item['price'] = '未知'

            # 4. 提取户型 - 新结构
            layout_text = response.css('div.trl-item1.w182 div.tt::text').get()
            if layout_text:
                item['layout'] = layout_text.strip()
            elif response.meta.get('list_layout'):
                item['layout'] = response.meta.get('list_layout')
            else:
                item['layout'] = '未知'

            # 5. 提取面积 - 新结构
            size_text = response.css('div.trl-item1.w132 div.tt::text').get()
            if size_text:
                # 提取数字部分
                size_match = re.search(r'(\d+(\.\d+)?)', size_text)
                if size_match:
                    item['size'] = size_match.group(1)  # 直接存储数字字符串
                else:
                    item['size'] = '未知'
            elif response.meta.get('list_size'):
                size_text = response.meta.get('list_size')
                size_match = re.search(r'(\d+(\.\d+)?)', size_text)
                if size_match:
                    item['size'] = size_match.group(1)  # 直接存储数字字符串
                else:
                    item['size'] = '未知'
            else:
                item['size'] = '未知'

            # 6. 提取朝向 - 新结构
            orientation_text = response.css('div.tr-line.clearfix div.trl-item1.w146 div.tt::text').get()
            if orientation_text:
                item['orientation'] = orientation_text.strip()
            elif response.meta.get('list_orientation'):
                item['orientation'] = response.meta.get('list_orientation')
            else:
                item['orientation'] = '未知'

            # 7. 提取楼层 - 新结构
            floor_text = response.css('div.tr-line.clearfix div.trl-item1.w182 div.tt::text').get() or \
                         response.css('div.tr-line.clearfix div.trl-item1.w182 div.tt a::text').get()
            if not floor_text:
                # 尝试从其他位置提取
                for item_div in response.css('div.tr-line.clearfix div.trl-item1'):
                    label = item_div.css('div.font14::text').get('')
                    if '楼层' in label:
                        floor_text = item_div.css('div.tt::text').get() or item_div.css('div.tt a::text').get()
                        break

            if floor_text:
                # 提取楼层详细信息
                floor_match = re.search(r'(\d+)层.*?(\d+)层', response.text)
                if floor_match:
                    current_floor = floor_match.group(1)
                    total_floors = floor_match.group(2)
                    item['floor'] = f"{floor_text.strip()}（{current_floor}/{total_floors}）"
                else:
                    item['floor'] = floor_text.strip()
            else:
                item['floor'] = '未知'

            # 8. 提取装修 - 新结构
            decoration_text = response.css('div.tr-line.clearfix div.trl-item1.w132 div.tt a::text').get() or \
                              response.css('div.tr-line.clearfix div.trl-item1.w132 div.tt::text').get()
            if decoration_text:
                item['decoration'] = decoration_text.strip()
            else:
                item['decoration'] = '未知'

            # 9. 提取小区名称 - 新结构
            area_text = response.css('div.trl-item2.clearfix div.rcont.address_zf a:first-child::text').get()
            if area_text:
                item['area'] = area_text.strip()
            else:
                item['area'] = '未知'

            # 10. 提取区域信息 - 新结构
            district_links = response.css('div.trl-item2.clearfix div.rcont.address_zf a::text').getall()
            if district_links and len(district_links) >= 2:
                item['district'] = district_links[1].strip()
            else:
                # 尝试从URL或其他来源获取区域
                district_info = self.extract_district_from_detail(response)
                item['district'] = district_info if district_info else '未知'

            # 提取地址 - 使用正确的选择器匹配详情页中的地址结构
            address = response.xpath(
                '//div[contains(@class, "trl-item2")][.//div[contains(text(), "地")]]//div[@class="rcont"]/a/text()').get()
            if address and address.strip():
                item['address'] = address.strip()
            else:
                # 备用选择器，没有<a>标签的情况
                address = response.xpath(
                    '//div[contains(@class, "trl-item2")][.//div[contains(text(), "地")]]//div[@class="rcont"]/text()').get()
                if address and address.strip():
                    item['address'] = address.strip()

            # 如果上述方法都失败，使用区域和小区名构建地址
            if not item.get('address') or item['address'] == '未知':
                if response.meta.get('list_district') and response.meta.get('list_community'):
                    item['address'] = f"{response.meta.get('list_district')} {response.meta.get('list_community')}"

            # 检查是否已经爬取过
            if item['house_id'] in self.crawled_ids:
                self.logger.info(f"房源 {item['house_id']} 已爬取过，跳过")
                return

            # 添加到已爬取集合
            self.crawled_ids.add(item['house_id'])

            # 提取房源描述
            description = response.css('div.fyms_con.floatl.gray3::text').get()
            if description:
                item['description'] = description.strip()
            else:
                # 如果没有找到描述，设置为空字符串
                item['description'] = ''

            # 如果描述为空，尝试提取经纪人信息作为备用
            if not item['description']:
                agent_name = response.css('span.zf_jjname a::text').get()
                agent_company = response.css('span.text_card_n::text').get()

                if agent_name or agent_company:
                    agent_info = []
                    if agent_name:
                        agent_info.append(f"联系人：{agent_name}")
                    if agent_company:
                        agent_info.append(f"所属：{agent_company.strip()}")
                    item['description'] = '，'.join(agent_info)

            # 提取房源标签
            tags = response.css('div.bqian span::text').getall() or \
                   response.css('p.tag_ico span::text').getall()
            if tags:
                item['tags'] = ','.join([tag.strip() for tag in tags if tag.strip()])

            # 提取交通信息
            transport_info = response.css('div.zbpt li:contains("交通")::text').get() or \
                             response.css('li.jiaotong::text').get()
            if transport_info and transport_info.strip():
                if not item['description']:
                    item['description'] = f"交通：{transport_info.strip()}"
                else:
                    item['description'] += f"\n交通：{transport_info.strip()}"

            # 提取更多详细位置信息
            location_details = []
            location_items = response.css('div.fyms-item ul.fyms_list li')
            for li in location_items:
                text = li.xpath('string(.)').get()
                if text and ('地址' in text or '位置' in text or '小区' in text):
                    location_details.append(text.strip())

            if location_details:
                if item['address'] == '未知' and len(location_details) > 0:
                    # 尝试从位置描述中提取地址
                    for loc in location_details:
                        if '地址' in loc or '位置' in loc:
                            item['address'] = loc.split('：')[-1].strip()
                            break

                # 添加到描述中
                if not item['description']:
                    item['description'] = '\n'.join(location_details)
                else:
                    item['description'] += '\n' + '\n'.join(location_details)

            # 提取小区环境信息
            community_info = response.css('div.xqdt-cont p::text').getall()
            if community_info:
                community_desc = '\n'.join([text.strip() for text in community_info if text.strip()])
                if community_desc:
                    if not item['description']:
                        item['description'] = f"小区环境：{community_desc}"
                    else:
                        item['description'] += f"\n小区环境：{community_desc}"

            # 计算每平米价格
            try:
                if item['price'] != '未知' and item['size'] != '未知':
                    # 自己实现数字提取，确保能够提取到数字
                    price_str = item['price']
                    price_match = re.search(r'(\d+(\.\d+)?)', price_str)
                    price_value = float(price_match.group(1)) if price_match else 0

                    size_str = item['size']
                    size_match = re.search(r'(\d+(\.\d+)?)', size_str)
                    size_value = float(size_match.group(1)) if size_match else 0

                    # 确保尺寸不为0，避免除以0错误
                    if price_value > 0 and size_value > 0:
                        item['price_per_sqm'] = round(price_value / size_value, 2)
                    else:
                        item['price_per_sqm'] = 0
            except Exception as e:
                print(f"计算每平米价格出错: {str(e)}")
                item['price_per_sqm'] = 0

            # 提取房屋配套设施
            self.infer_facilities(item, response)

            # 标准化区域名称
            district_name = self.normalize_district_name(item['district'])

            # 检查是否已经达到总的最大限制
            if self.current_count >= self.max_items:
                self.logger.info(f"已达到总的最大数量限制 {self.max_items}，停止爬取")
                return

            # 简化输出，只显示一行关键信息
            c = self.colors
            self.logger.info(
                f"{c['BOLD']}[{self.current_count + 1}/{self.max_items}] "
                f"{c['GREEN']}ID:{item['house_id']} "
                f"{c['YELLOW']}{item['price']} "
                f"{c['BLUE']}{item['layout']} "
                f"{c['CYAN']}{item['size']} "
                f"{c['WHITE']}{item['title'][:20]}..."
                f"{c['RESET']}"
            )

            # 保存数据并增加计数
            self.save_item_to_temp(item, district_name)
            self.current_count += 1  # 移到这里，只有在成功保存后才增加计数

        except Exception as e:
            self.logger.error(f"解析详情页出错: {response.url}, 错误: {str(e)}")

    def normalize_district_name(self, district):
        """标准化区域名称，去除不能用于文件名的字符"""
        if not district or district == '未知':
            return '未分类'

        # 去除不能用于文件名的字符
        district = re.sub(r'[\\/:*?"<>|]', '', district)
        return district

    def save_item_to_temp(self, item, district_name):
        """保存房源到CSV文件"""
        try:
            # 检查ID是否有效 - 放宽条件，允许生成的ID
            if not item['house_id']:
                self.logger.warning(f"跳过保存：房源ID为空")
                return

            # 保存到主CSV文件
            with open(PATH_CONFIG['raw_data'], 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.custom_settings['FEED_EXPORT_FIELDS'])
                # 如果文件为空，写入表头
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerow(item)

        except Exception as e:
            self.logger.error(f"保存房源失败: {str(e)}")
            # 保存失败时不要增加计数，这由调用者处理
            raise  # 重新抛出异常，让调用者知道保存失败

    def handle_redirect(self, response):
        """处理房天下可能的页面跳转"""
        if '跳转' in response.css('title::text').get(''):
            # 提取跳转URL
            script = response.xpath('//script[contains(text(), "var t4")]/text()').get()
            if script:
                t4_match = re.search(r"var t4='(.*?)';", script)
                t3_match = re.search(r"var t3='(.*?)';", script)
                if t4_match and t3_match:
                    t4 = t4_match.group(1)
                    t3 = t3_match.group(1)
                    new_url = f"{t4}?{t3}"
                    return scrapy.Request(new_url, callback=self.parse_detail)
        return None

    def errback_httpbin(self, failure):
        """处理请求错误"""
        self.logger.error(f"请求失败: {failure}")
        request = failure.request

        if failure.check(TimeoutError, TCPTimedOutError):
            self.logger.warning(f"连接超时，URL: {request.url}，将重试...")
            return request.replace(dont_filter=True)

        self.logger.error(f"未处理的错误: {repr(failure)}")

    def extract_district_from_detail(self, response):
        """综合提取区域信息"""
        district_info = None

        # 方法1: 从面包屑导航提取
        bread_links = response.css('div.bread a::text').getall()
        if bread_links:
            for text in bread_links:
                if '租房' in text and '武汉' not in text:
                    district_info = text.replace('租房', '').strip()
                    self.logger.debug(f"从面包屑提取到区域: {district_info}")
                    return district_info

        # 方法2: 从页面标题提取
        title = response.css('title::text').get()
        if title:
            district_match = re.search(r'武汉([\u4e00-\u9fa5]{1,4})租房', title)
            if district_match:
                district_info = district_match.group(1)
                self.logger.debug(f"从标题提取到区域: {district_info}")
                return district_info

        # 方法3: 从地址信息提取
        location_info = response.css('div.rcont a::text').getall()
        if location_info and len(location_info) > 0:
            district_info = location_info[0].strip()
            self.logger.debug(f"从地址信息提取到区域: {district_info}")
            return district_info

        # 方法4: 从列表页获取
        district_info = response.meta.get('list_district')
        if district_info:
            self.logger.debug(f"使用列表页区域信息: {district_info}")
            return district_info

        self.logger.warning(f"无法提取区域信息: {response.url}")
        return '未知'

    def debug_item(self, item, response):
        """打印详细的调试信息"""
        self.logger.debug(f"房源 {item['house_id']} 详细信息:")
        self.logger.debug(f"  URL: {response.url}")
        self.logger.debug(f"  标题: {item['title']}")
        self.logger.debug(f"  价格: {item['price']}")
        self.logger.debug(f"  户型: {item['layout']}")
        self.logger.debug(f"  面积: {item['size']}")
        self.logger.debug(f"  朝向: {item['orientation']}")
        self.logger.debug(f"  楼层: {item['floor']}")
        self.logger.debug(f"  装修: {item['decoration']}")
        self.logger.debug(f"  区域: {item['district']}")
        self.logger.debug(f"  小区: {item['area']}")
        self.logger.debug(f"  地址: {item['address']}")
        self.logger.debug(f"  图片链接: {item['images']}")
        self.logger.debug(f"  设施: {item.get('facilities', '')}")

        # 输出缺失字段
        missing_fields = [field for field, value in item.items() if value == '未知']
        if missing_fields:
            self.logger.warning(f"  房源 {item['house_id']} 缺失字段: {', '.join(missing_fields)}")

    def extract_location_info(self, response, item):
        """综合提取地址、区域和小区信息"""
        # 小区名称提取
        area_selectors = [
            'div.rcont a:last-child::text',  # 常见位置
            'a.gray3:contains("租房")::text',  # 另一种格式
            'p.gray6.mt12 a:last-child::text',  # 列表格式
            'div.trl-item2.clearfix div.rcont a::text',  # 详情页格式
            'div.title h1.cont::text'  # 从标题中提取
        ]

        for selector in area_selectors:
            area_text = None
            try:
                if 'contains' in selector:
                    # 特殊处理包含文本的选择器
                    elements = response.css('a.gray3')
                    for el in elements:
                        if '租房' in el.get():
                            area_text = el.css('::text').get()
                            break
                else:
                    area_text = response.css(selector).get()
            except:
                continue

            if area_text:
                # 清理小区名称
                area_text = re.sub(r'租房.*$', '', area_text).strip()
                if area_text and len(area_text) > 1:
                    item['area'] = area_text
                    break

        # 地址提取 - 尝试多种选择器
        address_selectors = [
            'div.tr-line clearfix div.rcont::text',  # 常见地址位置
            'div.rcont:contains("地址")::text',  # 包含"地址"的元素
            'li:contains("地址") label::text',  # 表格中的地址
        ]

        # 先尝试特定选择器
        for selector in address_selectors:
            try:
                address_text = response.css(selector).get()
                if address_text:
                    item['address'] = address_text.strip()
                    break
            except:
                continue

        # 备用方法：从小区信息中推断地址
        if item['address'] == '未知' and item['area'] != '未知':
            # 尝试查找包含小区名的地址信息
            address_elements = response.xpath(f'//div[contains(text(), "{item["area"]}")]')
            for el in address_elements:
                address_text = el.get()
                if address_text and len(address_text) > len(item['area']):
                    item['address'] = clean_text(address_text)
                    break

    def extract_images(self, response):
        """优化的图片提取方法"""
        # 只提取第一张图片即可，不需要提取所有图片
        if 'list_image' in response.meta and response.meta['list_image']:
            return [response.meta['list_image']]

        # 快速选择器列表
        selectors = [
            'div.bigImg img::attr(src)',
            'div.bigImg img::attr(data-original)',
            '.bd img::attr(src)'
        ]

        for selector in selectors:
            img_url = response.css(selector).get()
            if img_url:
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                return [img_url]

        return []

    def infer_facilities(self, item, response):
        """根据详情页面提取房屋配套设施"""
        facilities = []

        # 直接从HTML结构中提取设施信息
        facility_elements = response.css('div.cont.clearfix ul li')
        if facility_elements:
            # 如果找到了设施元素，直接提取文本
            for element in facility_elements:
                facility_text = element.css('::text').get()
                if facility_text:
                    facilities.append(facility_text.strip())

        # 如果上面的方法没有找到设施，尝试其他可能的HTML结构
        if not facilities:
            # 一些网站可能将设施放在特定class的元素中
            alternative_elements = response.css('li.fl.showIcon')
            for element in alternative_elements:
                facility_text = element.css('::text').get()
                if facility_text:
                    facilities.append(facility_text.strip())

        # 最后检查描述文本是否包含设施信息
        if not facilities and 'description' in item:
            description = item['description']

            # 常见的设施关键词
            facility_keywords = ['床', '宽带', '暖气', '电视', '空调', '冰箱', '洗衣机',
                                 '热水器', '可做饭', '沙发', '衣柜', '电梯', 'WiFi', '网络']

            # 从描述中提取可能的设施
            for keyword in facility_keywords:
                if keyword in description:
                    facilities.append(keyword)

        # 将列表转换为字符串
        item['facilities'] = '、'.join(facilities) if facilities else '暂无信息'
        return item

    def enhance_tags(self, item, response):
        """增强标签提取，结合列表页和详情页信息"""
        # 首先尝试使用传递的标签
        tags = set()
        if 'list_tags' in response.meta and response.meta['list_tags']:
            tags.update(response.meta['list_tags'].split(','))

        # 从详情页提取更多标签
        detail_tags = response.css(
            'span.note::text, span.colorGreen::text, span.colorRed::text, span.colorBlue::text').getall()
        for tag in detail_tags:
            if tag and tag.strip():
                tags.add(tag.strip())

        # 根据房源信息推断标签
        if '精装' in item['decoration'] or '豪华' in item['decoration']:
            tags.add('精装修')

        if '地铁' in item['title'] or '轨道' in item['title']:
            tags.add('紧邻地铁')

        if '首次' in item['title']:
            tags.add('首次出租')

        if item['orientation'] == '南北' or '通透' in item['title']:
            tags.add('南北通透')

        # 如果设施字段包含基本家电
        basic_appliances = ['电视', '冰箱', '洗衣机', '空调']
        appliance_count = 0
        for appliance in basic_appliances:
            if appliance in item['facilities']:
                appliance_count += 1

        if appliance_count >= 2:
            tags.add('家电齐全')

        # 增加空标签判断
        if not tags:
            if '低价' in item['title'] or int(self.extract_number(item['price']) or 2000) < 1500:
                tags.add('低价出租')

            if '商圈' in item['title'] or '广场' in item['title'] or '中心' in item['title']:
                tags.add('繁华地段')

        return ','.join(tags) if tags else '舒适住宅'

    def ensure_data_quality(self, item, response):
        """确保数据完整性，填充缺失值"""
        # 1. 确保URL字段有值
        if not item['url']:
            item['url'] = response.url

        # 2. 确保图片字段有值
        if not item['images'] or item['images'] == '未知':
            images = self.extract_images(response)
            if images:
                item['images'] = images[0]
            else:
                # 使用房源ID构建默认图片URL
                item['images'] = f"https://img.fang.com/house/{item['house_id']}/pic.jpg"

        # 3. 确保小区字段有值
        if not item['area'] or item['area'] == '未知':
            # 尝试从详情页提取小区名
            community_selectors = [
                'div.trl-item2.clearfix div.rcont.address_zf a:last-child::text',
                'p.gray6.mt12 a:last-child span::text'
            ]

            for selector in community_selectors:
                community = response.css(selector).get()
                if community:
                    item['area'] = community.strip()
                    break

            # 如果仍未找到，尝试从标题提取
            if not item['area'] or item['area'] == '未知':
                for name in ['小区', '花园', '公寓', '大厦', '广场', '名苑', '家园']:
                    if name in item['title']:
                        parts = item['title'].split(name)
                        if len(parts) > 1:
                            for i in range(len(parts) - 1):
                                # 取name前面的最多5个中文字符
                                area_name = re.search(r'([\u4e00-\u9fa5]{1,5})$', parts[i])
                                if area_name:
                                    item['area'] = f"{area_name.group(1)}{name}"
                                    break

        # 4. 确保地址字段有值
        if not item['address'] or item['address'] == '未知':
            # 直接使用CSS选择器提取地址
            address = response.css(
                'div.trl-item2.clearfix:contains("地址") div.rcont a::text, div.trl-item2.clearfix:contains("地址") div.rcont::text').get()
            if address and address.strip():
                item['address'] = address.strip()
            else:
                # 最后尝试使用完全精确的XPath匹配
                address = response.xpath(
                    '//div[@class="trl-item2 clearfix"]/div[@class="lab" and contains(text(), "地")]/following-sibling::div[@class="rcont"]/a/text()').get()
                if address and address.strip():
                    item['address'] = address.strip()

        return item

    def close_spider(self, spider):
        """爬虫结束时的处理函数"""
        c = self.colors
        end_time = datetime.now()
        duration = end_time - self.start_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        print(f"\n{c['BOLD']}{c['BLUE']}{'=' * 80}{c['RESET']}")
        print(f"{c['BOLD']}{c['GREEN']} 武汉租房数据爬取完成 {c['RESET']}")
        print(f"{c['BOLD']}{c['BLUE']}{'=' * 80}{c['RESET']}\n")

        self.logger.info(
            f"{c['BOLD']}运行时间: {c['YELLOW']}{int(hours)}小时{int(minutes)}分钟{int(seconds)}秒{c['RESET']}")

        total_houses = self.current_count
        self.logger.info(f"{c['BOLD']}总共爬取了 {c['YELLOW']}{total_houses}{c['RESET']} 个房源")

        # 创建一个表格样式的输出
        print(f"\n{c['BOLD']}{'区域ID':<15}{'区域名称':<15}{'爬取数量':<10}{c['RESET']}")
        print(f"{c['BOLD']}{'-' * 40}{c['RESET']}")

        for district_id, count in sorted(self.district_counts.items(), key=lambda x: x[1], reverse=True):
            district_name = self.district_mapping.get(district_id, f"区域{district_id}")
            print(f"{c['BOLD']}{district_id:<15}{c['GREEN']}{district_name:<15}{c['YELLOW']}{count:<10}{c['RESET']}")

        print(f"\n{c['BOLD']}数据保存在目录: {c['CYAN']}{self.output_dir}{c['RESET']}")

    def validate_price(self, price_text):
        """验证并格式化价格"""
        if not price_text:
            return '未知'
        # 提取数字
        price_match = re.search(r'(\d+(\.\d+)?)', str(price_text))
        if price_match:
            return price_match.group(1)  # 直接返回数字部分的字符串
        return '未知'


def clean_text(text):
    """清理文本，去除多余空格和特殊字符"""
    if not text:
        return ''
    return re.sub(r'\s+', ' ', text).strip()


def extract_number(text):
    """从文本中提取数字"""
    if not text:
        return None
    match = re.search(r'(\d+(\.\d+)?)', text)
    if match:
        return float(match.group(1))
    return None
