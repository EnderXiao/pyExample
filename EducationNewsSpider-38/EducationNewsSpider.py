# EducationNewsSpider
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
from urllib import parse
import json
import queue
import random
import chardet

# 请求头模拟正常访问
requestHeader = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Cookie': 'zh_choose=n',
    'Host': 'jyt.shaanxi.gov.cn',
    'Pragma': 'no-cache',
    'If-Modified-Since': 'Tue, 07 Sep 2021 06:04:01 GMT',
    'If-None-Match': "805e5127aea3d71:0",
    'Proxy-Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38'
}


class UserAgentUtils(object):
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
        # print(index)
        return self.__UserAgentList[index]


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
        print(value)
        self.__title = value.encode("utf-8")

    def __str__(self):
        return "title : %s\n url : %s\n" % (self.title, self.url)

    __repr__ = __str__


# 爬虫工具类
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
        print(url)
        requestHeader['User-Agent'] = UserAgentUtils.getRadomUserAgent()  # 随机请求头用户代理类型
        # time.sleep(random.random()*3)  # 随机休息一段时间
        # print(requestHeader)
        try:
            res = requests.get(url=url, headers=requestHeader, timeout=15)
            if(res.status_code == 200):
                htmlEncoding = chardet.detect(res.content)['encoding']  # 获取目标字符集
                res.encoding = htmlEncoding
                return res.text
            else:
                print("请求失败，错误代码" + str(res.status_code))
        except requests.exceptions.RequestException as e:
            print('------ConnectionResetError------!')
            print(e)

    # 解析页面内容，获取标题
    def parse_one_page(self, html):
        if html is None:
            html = self.get_one_page(self.url)
        soup = BeautifulSoup(html, 'lxml')
        # 针对自定义404页面的处理
        if '404' in soup.head.title.string:
            print('访问页面不存在，或该线程被网站禁止')
            return None
        announce_list = soup.body.find_all(attrs={'class': 'catlist'})
        for announce_box in announce_list:
            for title in announce_box.ul.find_all('a'):
                announcement = Announcement(url=title['href'], title=str(title.string))
                if 'http' not in announcement.url and 'https' not in announcement.url:
                    announcement.url = parse.urljoin(self.url, announcement.url)
                yield announcement

    # 通过请求队列获取多个页面
    def parse_pages(self):
        page_num = 1
        request_queue = queue.Queue()
        html_first = self.get_one_page(self.url)
        if html_first is not None:
            for announcement in self.parse_one_page(html_first):
                yield announcement
            page_num += 1
            request_queue.put(self.url+str(page_num)+'.html')
            while not request_queue.empty():
                next_url = request_queue.get()
                next_html = self.get_one_page(next_url)
                if next_html is not None:
                    for announcement in self.parse_one_page(next_html):
                        if announcement is not None:
                            yield announcement
                    page_num += 1
                    request_queue.put(self.url+str(page_num)+'.html')


if __name__ == "__main__":
    spider = Spider('http://jyt.shaanxi.gov.cn/jynews/jyyw/')
    with open('./education_info_log.txt', 'w+', encoding='utf-8') as log:
        for announcement in spider.parse_pages():
            # print(announcement)
            log.writelines((json.dumps(announcement, default=lambda obj: obj.__dict__, skipkeys=True, ensure_ascii=False, indent=4) + '\n'))
        print("所有数据已被保存至当前目录下的Education_info_log.txt")
