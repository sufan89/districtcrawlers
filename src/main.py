# coding=UTF-8

# import urllib
import urllib.request
from bs4 import BeautifulSoup
import chardet
import config
import os


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
    for i in bs.find_all('tr', config.config.classType[0]):
        '''循环获取省信息'''
        for j in i.find_all('td'):
            provinceName = j.getText()
            elmenta = j.find('a')
            if elmenta is not None:
                hrefstr = elmenta.get('href')
            fullDistrict[provinceName] = hrefstr
    DowLoadData(fullDistrict)


def DowLoadData(dicProvinces):
    '''下载数据'''
    if len(dicProvinces) == 0:
        print('没有要下载的数据')
    for key in dicProvinces.keys():
        '''创建文件'''
        filename = config.config.saveFloder + key + '.csv'
        if not CreateFile(filename):
            continue
        urlstr = config.config.targetUrl + dicProvinces[key]
        fs = os.open(filename, os.O_WRONLY)
        print('创建文件：%s.csv 成功' % key)
        GetUrlData(urlstr, 1, fs, [dicProvinces[key].split('.')[0], key])


def GetUrlData(url, classtype, filestream, rowdata):
    '''循环请求网页，并将数据存入到文件'''
    bs = connToUrl(url)
    if bs is None:
        print('请求地址失败:', url)
    if classtype == 4:
        '''村级，写数据到文件'''
    else:
        '''乡镇以上级，继续请求'''
        print(rowdata)
        GetUrlData(url, classtype + 1, filestream, rowdata)


def CreateFile(fileName):
    '''创建文件'''
    if os.path.exists(fileName):
        os.remove(fileName)
    try:
        os.mknod(fileName)
        return True
    except:
        print('创建文件：%s 失败！' % fileName)
        return False


def writeDataToFile(rowDt):
    '''写入一行数据'''
    pass


if __name__ == "__main__":
    GetDistrictData()
