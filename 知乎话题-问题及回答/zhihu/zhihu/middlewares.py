# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
import json
import requests


class ProxyMiddleware(object):
    def __init__(self):
        self.getIP_url = "http://d.jghttp.alicloudecs.com/getip?num=10&type=2&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions="
        self.test_url = "http://www.baidu.com/"
        self.ip_list = []
        # 用来记录使用ip的个数
        self.count = 0
        # 用来记录每个ip的使用次数
        self.eve_count = 0

    def getIPData(self):
        """
        从ip网站获取代理ip
        :return:
        """
        temp_data = requests.get(url=self.getIP_url).text
        self.ip_list.clear()
        for eve_ip in json.loads(temp_data)["data"]:
            self.ip_list.append({
                "ip": eve_ip["ip"],
                "port": eve_ip["port"]
            })
        print(self.ip_list)
        return None

    def getIP(self):
        """
        获取当前使用的IP及端口号
        :return:
        """
        temp_ip = str(self.ip_list[self.count - 1]["ip"])
        temp_port = str(self.ip_list[self.count - 1]["port"])
        return temp_ip, temp_port

    def changeProxy(self, request):
        """
        切换IP
        :param request:
        :return:
        """
        if self.count == 0 or self.count == 10:
            self.getIPData()
            self.count = 1
        else:
            self.count = self.count + 1
        temp_ip, temp_port = self.getIP()
        print("changeProxy", "http://" + temp_ip + ":" + temp_port)
        self.ifUsed(request)

    def yanzheng(self, request):
        temp_ip, temp_port = self.getIP()
        proxyMeta = "http://%(host)s:%(port)s" % {
            "host": temp_ip,
            "port": temp_port
        }
        proxies = {
            "http": proxyMeta
        }
        s = requests.session()
        s.keep_alive = False
        resp = s.get(url=self.test_url, proxies=proxies, timeout=3, verify=False)
        print("验证", proxies['http'], '：', resp.status_code)
        # 捕获状态码为40x/50x的response
        if str(resp.status_code).startswith('4') or str(resp.status_code).startswith('5'):
            self.changeProxy(request)

    def ifUsed(self, request):
        try:
            temp_ip, temp_port = self.getIP()
            request.meta["proxy"] = "http://" + temp_ip + ":" + temp_port
            self.yanzheng(request)
        except Exception as e:
            print("爬取失败！！！")
            print(e)
            self.changeProxy(request)

    def process_request(self, request, spider):
        if self.count == 0 or self.count == 10:
            self.getIPData()
            self.count = 1

        if self.eve_count == 50000:
            self.count = self.count + 1
            self.eve_count = 0
        else:
            self.eve_count = self.eve_count + 1
        self.ifUsed(request)
