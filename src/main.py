# coding=UTF-8

# import urllib
import urllib.request
from bs4 import BeautifulSoup
import chardet
import config


def connToUrl(url):
    '''请求URL获取数据'''
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


def GetDistrictData():
    '''获取行政区数据主函数'''
    bs = connToUrl(config.config.targetUrl)
    if bs is None:
        print('获取数据失败')
        return
    fullDistrict = {}
    for i in bs.find_all('tr', 'provincetr'):
        '''循环获取省信息'''
        for j in i.find_all('td'):
            provinceName = j.getText()
            elmenta = j.find('a')
            if elmenta is not None:
                hrefstr = elmenta.get('href')
            fullDistrict[provinceName] = hrefstr
    print(fullDistrict)


def DowLoadData(dicProvinces):
    '''下载数据'''
    pass


def CreateFile(fileName):
    '''创建文件'''
    pass


def writeDataToFile(rowDt):
    '''写入一行数据'''
    pass


if __name__ == "__main__":
    GetDistrictData()
