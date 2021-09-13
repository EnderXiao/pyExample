# EducationNewsCollection
# -*- coding: utf-8 -*-
from typing import Generator
import chardet
import threading
import requests
import queue
import random
import json
import time
from urllib import parse
from bs4 import BeautifulSoup
import pathlib
import os


q_html = queue.Queue()  # 内容池
q_page = queue.Queue()  # 任务队列
flag = False  # 写进程完成标记
write_lock = threading.Lock()


# 用于序列化的类
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
        self.__title = value.encode("utf-8")

    def __str__(self):
        return "title : %s\n url : %s\n" % (self.title, self.url)

    __repr__ = __str__


class RandomUserAgentUtils(object):
    __UserAgentList = [
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
        "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 7.0; InfoPath.3; .NET CLR 3.1.40767; Trident/6.0; en-IN)",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/4.0; InfoPath.2; SV1; .NET CLR 2.0.50727; WOW64)",
        "Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)",
        "Mozilla/4.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.2 (KHTML, like Gecko) ChromePlus/4.0.222.3 Chrome/4.0.222.3 Safari/532.2",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.28.3 (KHTML, like Gecko) Version/3.2.3 ChromePlus/4.0.222.3 Chrome/4.0.222.3 Safari/525.28.3",
        "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16",
        "Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14",
        "Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14",
        "Opera/12.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.02",
        "Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00",
        "Opera/9.80 (Windows NT 5.1; U; zh-sg) Presto/2.9.181 Version/12.00",
        "Opera/12.0(Windows NT 5.2;U;en)Presto/22.9.168 Version/12.00",
        "Opera/12.0(Windows NT 5.1;U;en)Presto/22.9.168 Version/12.00",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
        "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
        "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0",
        "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0",
    ]

    def __init__(self):
        super.__init__()

    @classmethod
    def getRadomUserAgent(self):
        max = 30
        min = 0
        index = random.randint(min, max)
        return self.__UserAgentList[index]


# 生产者模块，实现异步IO
class Crawler(threading.Thread):
    def __init__(self, base_url, crawl_name, q_page, parser):
        super().__init__()
        self.__base_url = base_url
        self.__crawl_name = crawl_name
        self.__q_page = q_page
        self.__parser = parser

    @property
    def base_url(self):
        return self.__base_url

    @base_url.setter
    def base_url(self, value):
        self.__base_url = value

    @property
    def crawl_name(self):
        return self.__crawl_name

    @crawl_name.setter
    def crawl_name(self, value):
        self.__crawl_name = value

    @property
    def q_page(self):
        return self.__q_page

    @property
    def parser(self):
        return self.__parser

    @parser.setter
    def parser(self, value):
        if isinstance(value, Generator):
            raise TypeError("Excepted a Generator")
        self.parser = value

    def downLoad_page(self, url, page):
        # 请求头模拟正常访问
        requestHeader = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Cookie': 'zh_choose=n',
            'Host': 'jyt.shaanxi.gov.cn',
            # 'Host': 'jw.beijing.gov.cn',
            # 'Referer': 'http://jw.beijing.gov.cn/jyzx/',
            'Pragma': 'no-cache',
            # 'If-Modified-Since': 'Tue, 07 Sep 2021 06:04:01 GMT',
            'If-None-Match': "805e5127aea3d71:0",
            'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38'
        }
        requestHeader['User_Agent'] = RandomUserAgentUtils.getRadomUserAgent()  # 随机请求头
        if page != 0:
            url = url + str(page) + '.html'
            # url = url + 'index_' + str(page) + '.html'
        print(url)
        time.sleep(random.random()*3)  # 休眠一段时间
        html_response = requests.get(url=url, headers=requestHeader, timeout=15)
        if html_response.status_code == 200:
            html_encoding = chardet.detect(html_response.content)  # 推断字符集
            html_response.encoding = html_encoding['encoding']
            return html_response.text
        else:
            print(f"该线程{self.crawl_name}请求出错，错误代码" + str(html_response.status_code))
            return None

    def parse_html(self, html_page):
        for announcement in self.parser(self.base_url, html_page):
            yield announcement

    def run(self):
        while True:
            if self.__q_page.empty():
                break
            # 1. 取出页码
            page = self.q_page.get()
            print(f'===========第{page}页====================@{self.crawl_name}')
            # 2. 下载
            htmlPage = self.downLoad_page(self.base_url, page)
            # 3. 解析
            if htmlPage is not None:
                announcements = self.parse_html(htmlPage)
                for announcement in announcements:
                    # 4.入池
                    if announcement is not None:
                        q_html.put(announcement)


# 消费者模块，实现异步IO
class Parse_man(threading.Thread):
    def __init__(self, path, thread_name):
        super().__init__()
        self.__path = path
        self.__thread_name = thread_name

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, value):
        self.__path = value

    @property
    def thread_name(self):
        return self.__thread_name

    @thread_name.setter
    def thread_name(self, value):
        self.__thread_name = value

    def run(self):
        while True:
            if q_html.empty() and flag:
                break
            try:
                announcement = q_html.get(block=False)  # 防止由于IO线程读取过快导致queue暂时没有数据，进而导致IO线程读取队列时被阻塞
                if write_lock.acquire(True):
                    # print(f'============写入模块{self.thread_name}=====正在写入')
                    with open(self.path, 'a+', encoding='utf-8') as log:
                        # print(announcement)
                        log.writelines((json.dumps(announcement, default=lambda obj: obj.__dict__, skipkeys=True, ensure_ascii=False, indent=4) + '\n'))
                        write_lock.release()
            except Exception as e:
                if isinstance(e, queue.Empty):
                    continue
                print(type(e))
                continue


# 定义解析接口
def parser(base_url, html_page):
    soup = BeautifulSoup(html_page, 'lxml')
    # 针对自定义404页面的处理
    if '404' in soup.head.title.string:
        print('访问页面不存在，或该线程被网站禁止')
        return None
    announce_list = soup.body.find_all(attrs={'class': 'catlist'})
    for announce_box in announce_list:
        for title in announce_box.ul.find_all('a'):
            announcement = Announcement(url=title['href'], title=str(title.string))
            if 'http' not in announcement.url and 'https' not in announcement.url:
                announcement.url = parse.urljoin(base_url, announcement.url)
            # print(announcement)
            yield announcement
    # announce_list = soup.body.find(attrs={'class': 'announce_list'}).find_all('ul')
    # for announce_box in announce_list:
    #     for title in announce_box.find_all('a'):
    #         announcement = Announcement(url=title['href'], title=str(title.string))
    #         if 'http' not in announcement.url and 'https' not in announcement.url:
    #             announcement.url = parse.urljoin(self.base_url, announcement.url)
    #         yield announcement


if __name__ == '__main__':
    # 设置代理
    # SOCKS5_PROXY_HOST = '127.0.0.1'		 # socks 代理IP地址
    # SOCKS5_PROXY_PORT = 1080           # socks 代理本地端口
    # default_socket = socket.socket
    # socks.set_default_proxy(socks.SOCKS5, SOCKS5_PROXY_HOST, SOCKS5_PROXY_PORT)
    # socket.socket = socks.socksocket
    # base_url = 'http://jw.beijing.gov.cn/jyzx/jyxw/'
    base_url = 'http://jyt.shaanxi.gov.cn/jynews/jyyw/'
    # 轮询参数
    flag = False  # p还没下班
    # 内容池
    q_html = q_html

    # 创建任务队列
    q_page = q_page
    max_page = input("请输入爬取页面数:")
    for page in range(0, int(max_page)):
        q_page.put(page)

    # 开启爬虫线程
    crawls = []
    for i in range(4):
        t = Crawler(base_url, i, q_page, parser)
        t.start()
        crawls.append(t)

    # 开启IO线程
    write_lock = threading.Lock()  # 写入锁
    site_name = base_url.split('.')[1]
    pathStr = './'+site_name+'_page_0-'+max_page+'.txt'
    print(pathStr)
    path = pathlib.Path(pathStr)
    if(path.exists()):
        os.remove(path)
    for i in range(4):
        c = Parse_man(pathStr, i)
        c.start()

    # 等待爬虫进程全部结束
    a = [p.join() for p in crawls]
    flag = True
