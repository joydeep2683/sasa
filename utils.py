import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import requests
import random
import json
from requests.auth import HTTPBasicAuth

# create a single instance of a class
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance
        
@singleton
class ProxyManager():
    def __init__(self):
        self.proxy_set = set()

    #load more proxies when the list is less than 10
    def __load_more_proxies(self):
        if len(self.proxy_set) < 10:
            self.get_proxy_uslist()
            if len(self.proxy_set) < 10:
                self.get_proxy_hidemyna()

    # it will return the list of proxies whenever called
    def get_proxy_hidemyna(self):
        url = 'https://hidemyna.me/en/proxy-list/'
        gs = get_source(url, True, 10)
        table = gs.find( "table", {"class":"proxy__t"} )
        rows=[row for row in table.find_all("tr")]
        need = [i for i in rows if '#79bc00' in str(i)]
        for i in need:
            ip_port = i.find_all('td')[:2]
            ip = ip_port[0].get_text()
            port = ip_port[1].get_text()
            proxy = '{}:{}'.format(ip, port)
            self.proxy_set.add(proxy)

    # will return proxy list by using requests.get
    # recommended
    def get_proxy_uslist(self):
        url = 'https://free-proxy-list.net/'
        gs = get_source(url, False)
        table = gs.find( "table", {"id":"proxylisttable"} )
        rows=[row for row in table.find_all("tr")]
        for i in rows:
            ip_port = i.find_all('td')[:2]
            if len(ip_port)>0:
                ip = ip_port[0].get_text()
                port = ip_port[1].get_text()
                proxy = '{}:{}'.format(ip, port)
                self.proxy_set.add(proxy)

    # pass the list of proxies to this function and it wil return one random proxy and rest of the list
    def getProxy(self):
        self.__load_more_proxies()
        proxy = random.sample(self.proxy_set, 1)[0]
        self.proxy_set.remove(proxy)
        print(len(self.proxy_set))
        return proxy

# returns website raw source as beautifulsoup object
def get_source(url, dynamic=True, wait=0, proxy=False):
    # get proxy and then calls requests.get with that
    if dynamic:
        options = Options()
        options.headless = True
        browser = webdriver.Chrome(options=options)
        browser.get(url)
        time.sleep(wait)
        html_code = browser.page_source
        soup = BeautifulSoup(html_code, 'lxml')
    elif proxy:
        R = requests.get(url, proxy)
        soup = BeautifulSoup(R.text, "html.parser")
    else:
        R = requests.get(url)
        soup = BeautifulSoup(R.text, "html.parser")
    return soup


