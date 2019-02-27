# coding=UTF-8

# import urllib
import urllib.request
from bs4 import BeautifulSoup
import chardet
import config


def connToUrl(url):
    user_agent = 'IP'
    headers = {'User-agent': user_agent}
    request = urllib.request.Request(url, headers=headers)
    content = urllib.request.urlopen(request).read()
    char = chardet.detect(content)['encoding']
    if char == 'GB2312':
        content = urllib.request.urlopen(request).read().decode('gbk').encode('utf-8')

    #    content = urllib.request.urlopen(request).read().decode('ISO-8859-1').encode('utf-8')
    bs = BeautifulSoup(content, 'html.parser')
    return bs


if __name__ == "__main__":
    print(connToUrl(config.config.targetUrl))
