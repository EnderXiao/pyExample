# EducationNewsSpider
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import copy
from urllib import parse
import json
import queue

# 请求头模拟正常访问
requestHeader = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38',
    'Connection': 'keep-alive',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',  # Ajax异步请求
}

class Announcement(object):
    def __init__(self, url, title):
        self.__url = url
        self.__title = title

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        self.__title = value
    
    def __str__(self):
        return "title : %s\n url : %s\n" % (self.title, self.url)

    __repr__ = __str__

class Spider(object):
    def __init__(self, url, **kw):
        self.__url = url
        self.__attributes = kw

    @property
    def url(self):
        return self.__url
    
    @url.setter
    def url(self, value):
        self.__url = value
    
    @property
    def attributes(self):
        return self.__attributes

    @attributes.setter
    def attributes(self, **kw):
        self.__attributes = kw

    # 请求一个页面
    def get_one_page(self, url):
        with requests.get(url=url, headers= requestHeader) as res:
            if(res.status_code == 200):
                return res.text

    # 解析页面内容，获取标题
    def parse_one_page(self, html):
        if html is None :
            html = self.get_one_page(self.url)
        soup = BeautifulSoup(html, 'lxml')
        announce_list = soup.body.find_all(attrs = {'class' : 'announce_list'})
        for announce_box in announce_list:
            for title in announce_box.find_all('a'):
                announcement = Announcement(url=title['href'],title=title.string)
                if 'http' not in announcement.url and 'https' not in announcement.url:
                    announcement.url = parse.urljoin(self.url, announcement.url)
                yield announcement
    
    # 通过请求队列获取多个页面
    def parse_pages(self):
        page_num = 0
        request_queue = queue.Queue()
        html_first = self.get_one_page(self.url)
        if html_first is not None:
            for announcement in  self.parse_one_page(html_first):
                yield announcement
            page_num += 1
            request_queue.put(self.url+'index_'+str(page_num)+'.html')
            while not request_queue.empty():
                next_url = request_queue.get()
                next_html = self.get_one_page(next_url)
                if next_html is not None:
                    for announcement in self.parse_one_page(next_html):
                        yield announcement
                    page_num += 1
                    request_queue.put(self.url+'index_'+str(page_num)+'.html')



if __name__ == "__main__":
    spider = Spider('http://jw.beijing.gov.cn/jyzx/jyxw/')
    with open('./education_info_log.txt','w+') as log:
        for announcement in spider.parse_pages():
            print(announcement)
            print("所有数据已被保存至当前目录下的Education_info_log.txt")
            log.writelines(json.dumps(announcement, default=lambda obj: obj.__dict__, skipkeys=True, ensure_ascii=False, indent=4).replace('\u200b','') + '\n')
