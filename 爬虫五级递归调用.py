# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 01:01:32 2018

@author: shine
"""


import urllib
from bs4 import BeautifulSoup  
import bs4  
import re
import pandas as pd
import os,sys
import time
import chardet 
import redis
import json
import shutil
#sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

r = redis.Redis(host = '127.0.0.1', port = 6379 )

#r.type('dic2')

path = 'D:/data/国五爬虫数据'
url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/'
import requests
response = requests.get(url)
#print(response.text)
html = response.text.encode('iso-8859-1').decode('gbk')
 

# content.encoding('utf-8')

#url = suburl
def connToUrl(url):
    user_agent='IP'  
    headers={'User-agent':user_agent}  
    request=urllib.request.Request(url,headers=headers)  
    content=urllib.request.urlopen(request).read()
    char = chardet.detect(content)['encoding']
    if char == 'GB2312':
        content = urllib.request.urlopen(request).read().decode('gbk').encode('utf-8')
    
#    content = urllib.request.urlopen(request).read().decode('ISO-8859-1').encode('utf-8')
    bs=BeautifulSoup(content,'html.parser')
    return bs

##level5 递归调用


def urlretry(keyname,mergehtmlcol,fileSet):
    if r.type(keyname) == b'list':
        if r.llen(keyname)>0:
            print('list个数',r.llen(keyname))
            #有数据
            value = r.lpop(keyname)
#            value= r.lindex(keyname,0)
            try:
                valuestr = str(value,encoding = 'utf8')
                valuestr = re.sub('[\"\'\{\}]','',valuestr)
                valueList = valuestr.split(',')
                msgDic = {}
                for i in range(len(valueList)):
                    valuestr=valueList[i]
                    tempList = valuestr.split(': ')
                    keyN = tempList[0].strip()
                    value = tempList[1].strip()
                    msgDic[keyN] = value            
                filename = msgDic['FileName']
                if filename in fileSet:
                    print('存在')
                    r.rpush('A_StreetInOld',msgDic)
                else:
                    tempL = filename.split('_')
                    lastfilename = '_'.join(tempL[:-1])+'available.xlsx'
                    streetwd = tempL[-1]
                    lastfiledir = path +'/Street'+'/'+lastfilename
                    lastLevelDf = pd.read_excel(lastfiledir)
                    lastLevelColList = list(lastLevelDf.columns)
                    ind = list(lastLevelDf['Street']).index(streetwd)
            except:
                print('Create Url Error')
                r.rpush('A_StreetUrlError',value)
#            lastword = msgDic['Name']  
#            suburl = msgDic[mergehtmlcol]
            else:
                searchlevel5(msgDic,lastLevelDf,lastLevelColList,ind,filepath,newcodecol,newcountrycol,newhtml,errorwordcol,errorhtml)
                urlretry(keyname,mergehtmlcol,filenameList)
        else:
            pass
    else:
        pass
    return 'finish retry' 


#lastword = lastLevelDf['Province'][ind] + '_'+ lastLevelDf['City'][ind]+ '_'+ lastLevelDf['Zone'][ind]+ '_'+ lastLevelDf[levelcol][ind]

def searchlevel5(msgDic,lastLevelDf,lastLevelColList,ind,filepath,newcodecol,newcountrycol,newhtml,errorwordcol,errorhtml):
    try :
        lastword = msgDic['FileName']
        suburl = msgDic[mergehtmlcol]  
    except:
        r.rpush('A_StreetUrlError',msgDic)#下一次通过dic处理
        print('存入list')        
    else:
        sub_availableDf = pd.DataFrame()
        sub_errorDf = pd.DataFrame()
        sub_availableDf_nohtml = pd.DataFrame()
        sub_errorDf_nohtml = pd.DataFrame()
        code = []
        countrycode = []
        word = []
        endhtml = []
        error_word = []
        error_endhtml = []     
        
        try:
    #        print(1)
            bs = connToUrl(suburl)

            nameL = ['统计用区划代码','城乡分类代码','名称']
            tag = 0                
            for i in bs.find_all('tr'):
                if i.attrs !={}:
#                    print(i)
#                    print('---',type(i))
#                    print(i.attrs)
                    
#                        print('判断是否开始')
                    if tag == 0:
                        for j in i.find_all('td'):
                            print('td:',j.string)
                            if j.string in nameL:
                                tag += 1   
                    
#                    print('next_element:',i.next_element)
                        print(i.next_element)
                    elif tag == 3:
#                            print('tag:',tag)
#                            print('开始加词')
                        for j in i.find_all('td'):
#                            print(j.string)
                            if re.sub('[0-9]','',j.string) != '':
                                word.append(j.string)
#                                print('选中文',j.string)
                            elif re.findall('[0-9]+',j.string) !=[]:
                                print(j.string)
                                
                                if len(j.string) > 6:
                                    code.append(j.string)
                                else:
                                    countrycode.append(j.string)
#                                    print('加入word')
                                
                            #不记录其他错误情况   
                    else:
                        error_endhtml.append(suburl)#能获取html 记录不符合数字规则的
                        error_word.append(lastword)                         
            sub_availableDf_nohtml = pd.DataFrame({newcodecol:code,newcountrycol:countrycode,newlevelcol:word})
            sub_errorDf_nohtml = pd.DataFrame({errorwordcol:error_word,errorhtml:error_endhtml})                                                               
            print(lastword)
            print('有效个数：',len(word))
            print('无效个数：',len(error_word))            

                    
            if len(sub_availableDf_nohtml)>0:
                for ind_col in range(len(lastLevelColList)):
                    lastcol = lastLevelColList[ind_col]
                    sub_availableDf_nohtml[lastcol]=str(lastLevelDf[lastcol][ind])
    #                availableDf_nohtml = pd.concat([availableDf_nohtml,sub_availableDf_nohtml])
                sub_availableDf_nohtml.to_excel(filepath+'/'+lastword+'available_nohtml.xlsx')
#            if len(sub_errorDf_nohtml)>0:
#                for ind_col in range(len(lastLevelColList)):
#                    lastcol = lastLevelColList[ind_col]
#                    sub_errorDf_nohtml[lastcol]=str(lastLevelDf[lastcol][ind])  
#    #                errorDf_nohtml = pd.concat([errorDf_nohtml,sub_errorDf_nohtml])
#                sub_errorDf_nohtml.to_excel(filepath+'/'+lastword+'error_nohtml.xlsx')
        except :
            
            print('发生错误')
#            savemsg = json.dumps(msgDic)
#    #            r.zincrby('A_SpyderRetry',savemsg)#计数式存储
#            time.sleep(2)
            
            r.rpush('A_Street2Error',msgDic)#先进先出
            print('存入list')
    return 'complete search'



keyname = 'A_Street2Error'
newlevelcol = 'Village'
filepath = path +'/' + newlevelcol
newcodecol = newlevelcol+'_code'
newcountrycol = newlevelcol+'_countrycode'
newhtml = newlevelcol+'_html'
errorwordcol = newlevelcol
errorhtml = newlevelcol+'_html' 

mergehtmlcol = 'Url'

filenameList = os.listdir(path +'/VillageOld' )
fileSet = []
for ind in range(len(filenameList)):
    if filenameList[ind].find('available_nohtml.xlsx') != -1:
        filename = re.sub('available_nohtml.xlsx','',filenameList[ind])
    elif filenameList[ind].find('available.xlsx') != -1:
        filename = re.sub('available.xlsx','',filenameList[ind])
    if filename not in fileSet:
        fileSet.append(filename)

filepath = path +'/Village'
if os.path.exists(filepath):
    pass
else:
    os.mkdir(filepath)    

urlretry(keyname,mergehtmlcol,filenameList)



####五级查重

fileOldList = os.listdir(path + '/VillageOld')
fileOld = []
for ind in range(len(fileOldList)):
    filename = re.sub('available_nohtml.xlsx','',fileOldList[ind])
    if filename not in fileOld:
        fileOld.append(filename)

fileList = os.listdir(path + '/Village')
fileNew = []
for ind in range(len(fileList)):
    filename = re.sub('available_nohtml.xlsx','',fileList[ind])
    if filename not in fileNew:
        fileNew.append(filename)

#新文件中有旧中没有的
diff_New = list(set(fileNew).difference(set(fileOld)))

#旧中有 新文件中没有的
diff_Old = list(set(fileOld).difference(set(fileNew)))

#移动
for ind in range(len(diff_Old)):
    oldDir = path + '/VillageOld'+'/'+diff_Old[ind]+'available_nohtml.xlsx'
    newDir = path + '/Village'+'/'+diff_Old[ind]+'available_nohtml.xlsx'
    if os.path.exists(newDir):
        pass
    else:
        shutil.copyfile(oldDir,newDir)        
# 
level1 = pd.read_excel(path+'/level1Html.xlsx')

filepath = path + '/Village'
fileList = os.listdir(filepath)
proL = []
proL = list(map(lambda x : x.split('_')[0],fileList))
fileDf = pd.DataFrame({'Province':proL,'filename':fileList})

outputpath = path + '/output'
if os.path.exists(outputpath):
    pass
else:
    os.mkdir(outputpath)

errorpro = []
for ind_pro in range(len(level1)):
    pro = level1['Province'][ind_pro]
#    pro = '广东省'
    outdir = outputpath+'/'+pro+'.xlsx'
    if os.path.exists(outdir):
        continue
    else:
        try:
            proDf = pd.DataFrame()
            subfile = fileDf[fileDf['Province']==pro].reset_index(drop = True)
            for ind_f in range(len(subfile)):
                print(ind_f)
                print(filepath+'/'+subfile['filename'][ind_f])
                try:
                    df = pd.read_excel(filepath+'/'+subfile['filename'][ind_f])
#                    df = pd.read_excel(filepath+'/'+'广东省_广州市_天河区_前进街道available_nohtml.xlsx')
                    proDf = pd.concat([proDf,df])
                except:
                    errorpro.append(subfile['filename'][ind_f])
#                print('finish')
            proDf.reset_index(drop = True , inplace = True)
            proDf.to_excel(outputpath+'/'+pro+'.xlsx')
            print('finish :', pro,'剩余:',(len(level1)-ind_pro-1))
        except:
            errorpro.append(pro)
            continue
    
    
#################4级特殊合并


filepath = path + '/Only4levels'
fileList = os.listdir(filepath)
proL = []
proL = list(map(lambda x : x.split('_')[0],fileList))
fileDf = pd.DataFrame({'Province':proL,'filename':fileList})

outputpath = path + '/output'
if os.path.exists(outputpath):
    pass
else:
    os.mkdir(outputpath)

level1 = ['广东省','海南省']
for ind_pro in range(len(level1)):
    pro = level1[ind_pro]
    proDf = pd.DataFrame()
    subfile = fileDf[fileDf['Province']==pro].reset_index(drop = True)
    for ind_f in range(len(subfile)):
        df = pd.read_excel(filepath+'/'+subfile['filename'][ind_f])
        proDf = pd.concat([proDf,df])
    proDf.reset_index(drop = True , inplace = True)
    proDf.to_excel(outputpath+'/'+pro+'_4级.xlsx')
    print('finish :', pro,'剩余:',(len(level1)-ind_pro-1))


