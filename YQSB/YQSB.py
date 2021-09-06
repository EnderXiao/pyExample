import time
import json
import requests
import copy

requestHeader = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)  Mobile/15E148 wxwork/3.1.12 MicroMessenger/7.0.1 Language/zh ColorScheme/Light',
    'Connection': 'keep-alive',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',  # Ajax异步请求
}


def myRequest(type,session: requests.sessions.session, url, referer = None, accept = None, **kwargs):
    headers = copy.deepcopy(requestHeader)
    if isinstance(referer, str):
        headers['Referer'] = referer
    if isinstance(accept, str):
        headers['Accept'] = accept
    s.headers.update(headers)
    if type == 'get':
        getRequest = session.get(url, **kwargs)
        return getRequest
    if type == 'post':
        postRequest = session.post(url, **kwargs)
        return postRequest


if __name__ == '__main__':
    s = requests.session();
    s.cookies.set('id','402880c97b5d8ad1017bb5e341801fe8')
    s.cookies.set('token','226BCEE3769EDA70A6AB1156E8A07C3D')

    # 请求企业微信session
    res = myRequest('get', s, url='http://bjut.sanyth.com:81/nonlogin/qywx/authentication.htm?appId=402880c97b1aa5f7017b1ad2bd97001b&urlb64=L3dlaXhpbi9zYW55dGgvaG9tZS5odG1s',
                    accept='text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    # 请求xmid
    data = {
        "pageIndex" : "0",
        "pageSize" : "10",
        "type" : "YQSJSB",
    }
    res = myRequest('post', s, url='http://bjut.sanyth.com:81/syt/zzapply/queryxmqks.htm',
                    referer='http://bjut.sanyth.com:81/webApp/xuegong/index.html',
                    accept='application/json, text/plain, */*',data=data)
    jsonRespons = json.loads(res.content)
    xmid = jsonRespons['data'][0]['id']
    # 请求PDNF
    data = {
        "type":"YQSJSB"
    }
    res = myRequest('post', s, url='http://bjut.sanyth.com:81/syt/zzapi/getPDNF.htm',
                    referer='http://bjut.sanyth.com:81/webApp/xuegong/index.html',
                    accept='application/json, text/plain, */*',data = data)
    pdnf = res.text
    # 请求签到状态
    data={
        "xmid":xmid,
        "pdnf":pdnf,
        "type":"YQSJSB"
    }
    res = myRequest('post', s, url="http://bjut.sanyth.com:81/syt/zzapply/checkrestrict.htm",
                    referer='http://bjut.sanyth.com:81/webApp/xuegong/index.html',
                    accept='application/json, text/plain, */*',data = data)
    logMessage = "打卡失败"
    if "今日已经上报" not in res.text:
        # 打卡请求
        c1 = "21级研究生新生"
        c2 = "在校内居住"
        c3 = "今日入校"
        c4 = "否"
        c5 = "正常"
        c6 = "正常"
        c7 = "无情况"
        c8 = "在京内"
        c9 = "否"
        c10 = "否"
        c11 = "否"
        c12 = "北京市,北京市,朝阳区,大望路27号中蓝学生公寓"
        location_longitude = 116.48051452636719
        location_latitude = 39.88443374633789
        location_address = "北京市朝阳区南磨房镇南磨房路平乐园小区"
        data = {
            "data" : '{"xmqkb":{"id":"%s"},"c1":"%s","c2":"%s","c3":"%s","c4":"%s","c5":"%s","c6":"%s","c7":"%s","c8":"%s","c12":"%s","c9":"%s","c10":"%s","c11":"%s","type":"YQSJSB","location_longitude":%s,"location_latitude":%s,"location_address":"%s"}' % (xmid,c1,c2,c3,c4,c5,c6,c7,c8,c12,c9,c10,c11,location_longitude,location_latitude,location_address),
            "msgurl" : "syt/zzapply/list.htm?type=YQSJSB&xmid=%s" % (xmid),
            "uploadFileStr" : {},
            "multiSelectData" : {},
            "type":"YQSJSB"
        }
        print(data)
        res = myRequest("post", s, url="http://bjut.sanyth.com:81/syt/zzapply/operation.htm",
                        referer='http://bjut.sanyth.com:81/webApp/xuegong/index.html',
                        accept='application/json, text/plain, */*',data = data)
        if "success" in res.text:
            logMessage = "打卡成功"
            print("打卡成功")
        else:
            logMessage = "打卡请求失败"
            print("打卡请求失败")
    else:
        print('今日已打卡')
        logMessage = "今日已打卡"
    requestRecord = res.text
    requestTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    logText = requestTime + ' ' + logMessage + ' ' + res.text +  '\n'
    with open("COVID19Report2021.txt",'a') as f:
        f.writelines(logText)