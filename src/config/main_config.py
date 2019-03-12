# coding=UTF-8

class config:
    def __init__(self):
        pass

    '''目标URL'''
    targetUrl = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/'
    '''结果存储位置'''
    saveFloder = '/home/sufan/Desktop/data/dicdata/'
    '''样式表'''
    classType = {0: 'provincetr', 1: 'citytr', 2: 'countytr', 3: 'towntr', 4: 'villagetr'}
    '''日志文件'''
    errorLogFile = '/home/sufan/Desktop/data/dicdata/log/'
    '''重试次数'''
    retryCount = 0
    '''已下载的数据记录'''
    doneDataFile = '/home/sufan/Desktop/data/dicdata/log/done.txt'
    '''已下载的省份s'''
    doneData = []
    ''' 没有区县的市'''
    # noquxian=['广州市','韶关市','深圳市',
    #           '珠海市','汕头市','佛山市','江门市','湛江市',
    #           '茂名市','肇庆市','惠州市','梅州市','汕尾市','河源市','阳江市','清远市','潮州市','揭阳市','云浮市']
    noquxian=['东莞市','中山市']