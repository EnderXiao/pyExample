# Hello.py
# -*- coding: utf-8 -*-
from bs4.element import CData, NavigableString
import requests
import copy
from bs4 import BeautifulSoup
from requests.api import head

html_doc_test = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>
<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>
<p class="story">...</p>
"""


requestHeader = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)  Mobile/15E148 wxwork/3.1.12 MicroMessenger/7.0.1 Language/zh ColorScheme/Light',
    'Connection': 'keep-alive',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',  # Ajax异步请求
}


def setRequestHeader(**kwargs):
    header = copy.deepcopy(requestHeader)
    for key, value in kwargs:
        header[key] = value
    return header


def myRequest(type, url, **kwargs):
    setRequestHeader(**kwargs)
    myRespond = None
    if type.lower() == 'get':
        myRespond = requests.get(url, **kwargs)
    elif type.lower() == 'post':
        myRespond = requests.post(url, **kwargs)
    return myRespond


if __name__ == "__main__":
    html_doc = myRequest("get", "http://quotes.toscrape.com/").text
    soup = BeautifulSoup(html_doc, "lxml")
    tag = soup.title
    print(soup.prettify())  # 输出格式化后的html
    print('---------分界线---------')
    print(soup.title.parent)
    soup.title.name = "fuck"  # 修改标签名
    print('-----分界线-----')
    print(tag)
    css_soup = BeautifulSoup("<p class='fuck shit'></p>", 'lxml')
    print(css_soup.p['class'])
    rel_soup = BeautifulSoup('<p>Back to the <a rel="index">homepage</a></p>','lxml')
    rel_soup.a['rel'] = ['index', 'contents']
    print(rel_soup.a['rel'])
    print(rel_soup.p)
    print(rel_soup.a.string)
    print(type(rel_soup.a.string))
    print(type(str(rel_soup.a.string)))
    tag = rel_soup.a
    print(tag.string)
    tag.string.replace_with('hhhhh')
    print(css_soup.name)
    print(css_soup.attrs)
    print('-----分界线-----')
    doc = BeautifulSoup("<head>INSERT FOOTER HERE</head>", "xml")
    foot = BeautifulSoup("<footer>Here is the footer</footer>", "xml")
    doc.head.string.replace_with(foot)
    print(doc)
    print('-----分界线-----')
    markup = "<b><!-- Hey, buddy. Want to buy a used parser? --></b>"
    soup = BeautifulSoup(markup, "lxml")
    comment = soup.b.string
    print(type(comment))
    print(comment)
    print(isinstance(comment, NavigableString))
    print(soup.prettify())
    cdata = CData("A CDATA block <")
    comment.replace_with(cdata)
    print(soup.prettify())
    print("-----分界线-----")
    soup_test = BeautifulSoup(html_doc_test, 'lxml')
    tag = soup_test.body
    print(tag.contents)
    print(tag.contents[1].contents[0].contents)
    print(soup_test.contents)
    print(soup_test.find_all('a'))
    print(soup_test.contents[0].name)
    for child in soup_test.body.children:
        print(child)
    headTag = soup_test.head
    for child in headTag.descendants:
        print(child)
# <title>The Dormouse's story</title>
# The Dormouse's story
    print(len(soup_test.contents)) # 1
    print(len(list(soup_test.descendants))) # 26
    print(soup_test.string)
    print(headTag.title.string)
# None
# The Dormouse's story
    for string in soup_test.strings:
        print(string)
# The Dormouse's story




# The Dormouse's story


# Once upon a time there were three little sisters; and their names were

# Elsie
# ,

# Lacie
#  and

# Tillie
# ;
# and they lived at the bottom of a well.


# ...
    print('-------')
    for string in soup_test.stripped_strings:
        print(string)
# The Dormouse's story
# The Dormouse's story
# Once upon a time there were three little sisters; and their names were
# Elsie
# ,
# Lacie
# and
# Tillie
# ;
# and they lived at the bottom of a well.
# ...
    print('--------')
    title_tag = soup_test.head.title
    print(title_tag)
    print(title_tag.parent)
    print(title_tag.string.parent)
    html_tag = soup_test.html
    # print(html_tag)
    print(type(html_tag.parent))
    print(soup_test.parent)
# <title>The Dormouse's story</title>
# <head><title>The Dormouse's story</title></head>
# <title>The Dormouse's story</title>
# <class 'bs4.BeautifulSoup'>
# None
    print('----------')
    a_tag = soup_test.a
    print(a_tag)
    for parent in a_tag.parents:
        print(parent.name)
# <a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>
# p
# body
# html
# [document]
    print('----------')
    last_a_tag = soup_test.find("a",id = 'link3')
    print(last_a_tag)
    print(last_a_tag.next_sibling)
    for child in last_a_tag.children:
        print(child)
    print(last_a_tag.next_element)
# <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>
# ;
# and they lived at the bottom of a well.
# Tillie
# Tillie
    for element in last_a_tag.next_elements:
        print(repr(element))