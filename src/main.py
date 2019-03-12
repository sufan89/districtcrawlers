# coding=UTF-8

# import urllib
import urllib.request
from bs4 import BeautifulSoup
import chardet
import config
import os
import datetime


def connToUrl(url):
    '''请求URL获取数据'''
    try:
        user_agent = 'IP'
        headers = {'User-agent': user_agent}
        request = urllib.request.Request(url, headers=headers)
        content = urllib.request.urlopen(request).read()
        char = chardet.detect(content)['encoding']
        if char == 'GB2312':
            content = urllib.request.urlopen(request).read().decode('gbk').encode('utf-8')
        bs = BeautifulSoup(content, 'html.parser')
        config.config.retryCount = 0
        return bs
    except (Exception) as error:
        if hasattr(error, 'code') == False:
            if config.config.retryCount <= 3:
                '''重试'''
                config.config.retryCount = config.config.retryCount + 1
                return connToUrl(url)
            else:
                config.config.retryCount = 0
                return None
        if error.code == 403:
            return None
        elif error.code == 404:
            return None
        elif config.config.retryCount <= 3:
            '''重试'''
            config.config.retryCount = config.config.retryCount + 1
            return connToUrl(url)
        else:
            print(url)
            print(error)
            config.config.retryCount = 0
            return None


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
        if key in config.config.doneData:
            continue
        filename = config.config.saveFloder + key + '.csv'
        if not CreateFile(filename):
            continue
        urlstr = config.config.targetUrl + dicProvinces[key]
        fs = open(filename, mode='w', buffering=-1, encoding='gbk', newline='\n')
        print(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), '创建文件：%s.csv 成功' % key)
        GetUrlData(urlstr, 1, fs, [dicProvinces[key].split('.')[0], key])
        fs.close()
        print(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), '%s:下载成功' % key)
        config.config.doneData.append(key)
        writeDoneData()


def GetUrlData(url, classtype, filestream, rowdata):
    '''循环请求网页，并将数据存入到文件'''
    bs = connToUrl(url)
    if bs is None:
        errorStr = '请求地址：' + url + '\n' + ','.join(rowdata)
        writeErrorData(errorStr)
        return False

    if classtype == 4:
        '''村级，写数据到文件'''
        for i in bs.find_all('tr', config.config.classType[classtype]):
            rowDt = rowdata.copy()
            for j in i.find_all('td'):
                rowDt.append(j.getText())
            writeDataToFile(filestream, rowDt)
            filestream.flush()
        return True
    elif classtype == 2 and rowdata[len(rowdata) - 1] in config.config.noquxian:
        '''没有区县情况处理'''
        for i in bs.find_all('tr', config.config.classType[classtype + 1]):
            element = i.find('a')
            # hrefStr = ''
            newRow = rowdata.copy()
            newRow.append(rowdata[len(rowdata) - 2])
            newRow.append(rowdata[len(rowdata) - 1])
            for j in i.find_all('td'):
                newRow.append(j.getText())
            if element is not None:
                hrefStr = element.get('href')
            else:
                writeDataToFile(filestream, newRow.copy())
                continue
            strUrl = GetUrl(classtype, url, hrefStr)
            if GetUrlData(strUrl, classtype + 2, filestream, newRow.copy()) == False:
                writeDataToFile(filestream, newRow.copy())
            print(strUrl)
    else:
        '''乡镇以上级，继续请求'''
        for i in bs.find_all('tr', config.config.classType[classtype]):
            element = i.find('a')
            # hrefStr = ''
            newRow = rowdata.copy()
            for j in i.find_all('td'):
                newRow.append(j.getText())
            if element is not None:
                hrefStr = element.get('href')
            else:
                writeDataToFile(filestream, newRow.copy())
                continue
            strUrl = GetUrl(classtype, url, hrefStr)
            if GetUrlData(strUrl, classtype + 1, filestream, newRow.copy()) == False:
                writeDataToFile(filestream, newRow.copy())
            print(strUrl)


def CreateFile(fileName):
    '''创建文件'''
    if os.path.exists(fileName):
        os.remove(fileName)
    try:
        if hasattr(os, 'mknod'):
            os.mknod(fileName)
        else:
            open(fileName, mode='a+')
        return True
    except:
        print('创建文件：%s 失败！' % fileName)
        return False


def GetUrl(classtype, url, hrefStr):
    '''获取请求URL'''
    if classtype == 0:
        return config.config.targetUrl
    elif classtype == 1:
        return config.config.targetUrl + hrefStr
    elif classtype == 2:
        return url[:-9] + hrefStr
    elif classtype == 3:
        return url[:-11] + hrefStr


def writeDataToFile(filestream, rowDt):
    '''写入一行数据'''
    if filestream is None:
        print("无法获取文件")
        return
    else:
        filestream.write(','.join(rowDt) + '\n')


def writeErrorData(errorLog):
    '''写错误日志'''
    fs = open(config.config.errorLogFile, mode='a', buffering=-1, encoding='gbk')
    if fs is None:
        print('无法打开错误日志')
    fs.write(errorLog + '\n')
    fs.flush()
    fs.close()


def readDoneData():
    '''读取已下载的数据'''
    if os.path.exists(config.config.doneDataFile):
        fs = open(config.config.doneDataFile, mode='r', buffering=-1, encoding='utf-8', newline='\n')
        shen = fs.readline().rstrip()
        while shen != '':
            config.config.doneData.append(shen)
            shen = fs.readline().rstrip()
    else:
        CreateFile(config.config.doneDataFile)


def writeDoneData():
    if os.path.exists(config.config.doneDataFile):
        fs = open(config.config.doneDataFile, mode='w', buffering=-1, encoding='utf-8')
        fs.write('\n'.join(config.config.doneData))
        fs.flush()
        fs.close()


if __name__ == "__main__":
    # 初始化日志文件
    nowDate = datetime.datetime.today()
    config.config.errorLogFile = config.config.errorLogFile + nowDate.strftime('%Y%m%d') + '.txt'
    CreateFile(config.config.errorLogFile)
    # 读取已下载数据列表
    readDoneData()
    # 开始下载国家行政区数据
    GetDistrictData()
