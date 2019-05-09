# -*- coding:utf-8 -*-
import urllib
import urllib.request
import random
import ssl
import json
import Levenshtein
from databaseIO import dbIO
import Settings
ssl._create_default_https_context = ssl._create_unverified_context
apikeyList = Settings.apikeyList
keyIndex = Settings.keyIndex

user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
               'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+'
               '(KHTML, like Gecko) Element Browser 5.0',
               'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
               'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
               'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko)'
               'Version/6.0 Mobile/10A5355d Safari/8536.25',
               'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)'
               'Chrome/28.0.1468.0 Safari/537.36',
               'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)']
# def getInfo():
#     server = dbIO()
#     sql = "select title,flag from searchlist2"
#     return server.load(sql)

# def doiGetRes(doi):
#     rNum = random.randint(0, 7)
#     i_headers = {'User-Agent': user_agents[rNum]}
#     dict = {}
#     values = {}
#     values['query'] = 'DOI('+doi+')'
#     data = urllib.urlencode(values)
#     url = "http://api.elsevier.com/content/search/index:SCOPUS"
#     geturl = url + '?' + data+'&field=citedby-count&apiKey=6cc0daebe40902be3b9dd9dffdd76484'
#     try:
#         request = urllib2.Request(geturl, headers=i_headers)
#         response = urllib2.urlopen(request, timeout=10)
#         dic = response.read().decode("utf-8")
#     except Exception as e:
#         print(str(e))
#     jsonDict=json.loads(dic)
#     # print jsonDict
#     if jsonDict["search-results"]["entry"][0].has_key("prism:url"):
#         temp=jsonDict["search-results"]["entry"][0]["prism:url"]
#         temp=str(temp).split('/')
#         print temp[-1]
#     else:
#         print []


def titleGetRes(title):
    """
    论文标题获得sid和标题相关性rel字典
    :param title:论文标题
    :return: 从scopus中获取的论文sid对应的数据字典
    """
    rNum = random.randint(0, 7)
    i_headers = {'User-Agent': user_agents[rNum]}
    dict = {}
    values = {}
    values['query'] = 'title('+title+')'
    data = urllib.parse.urlencode(values)
    url = "http://api.elsevier.com/content/search/scopus"
    geturl = url + '?' + data+'&apiKey='+apikeyList[keyIndex]+'&field=title&httpAccept=application/json'
    try:
        request = urllib.request.Request(geturl, headers=i_headers)
        response = urllib.request.urlopen(request, timeout=5)
        dic = response.read().decode("utf-8")
    except Exception as e:
        print(str(e), geturl)
        return dict
    jsonDict = json.loads(dic)
    count = len(jsonDict["search-results"]["entry"])  # scopus返回结果数不超过4
    if count >= 4:
        count = 4
    for i in range(count):
        if not "dc:title" in jsonDict["search-results"]["entry"][i]:
            continue
        num = Levenshtein.distance(str(jsonDict["search-results"]["entry"][i]["dc:title"].lower()), str(title.lower()))
        # 标题完全一致，则采纳结果
        if "prism:url" in jsonDict["search-results"]["entry"][i] and num == 0:
            temp = jsonDict["search-results"]["entry"][i]["prism:url"]
            temp = str(temp).split('/')
            dict["sid"] = temp[-1]
            dict["rel"] = 0
            return dict
        # 没有可匹配的，取第一条结果
        elif i == count-1 and not num == 0 and "prism:url" in jsonDict["search-results"]["entry"][i]:
            temp = jsonDict["search-results"]["entry"][0]["prism:url"]
            temp = str(temp).split('/')
            dict["sid"] = temp[-1]
            dict["rel"] = Levenshtein.distance(str(jsonDict["search-results"]["entry"][0]["dc:title"].lower()),
                                               str(title.lower()))/float(len(title))
            return dict
        else:
            continue
    return dict


def dealInfo(dict, title):
    """
    更新检索列表searchlist2，flag=2为模糊匹配的标题，flag=1 为完全匹配的标题
    :param dict: sid与rel字典
    :param title: 标题
    :return: 有sid则返回sid，没有则返回None
    """
    if "sid" in dict:
        server = dbIO()
        # sql = "select * from searchlist2 where sid='%s'" % (dict["sid"])
        if True:  # server.count(sql) <= 0:
            if dict["rel"] == 0:
                sql = "update searchlist2 set flag=1,sid='%s'where title='%s'" % (dict["sid"], title.replace("'", "''"))
                server.save(sql)
            elif dict["rel"] <= 0.1:
                sql = "update searchlist2  set flag=2,sid='%s'where title='%s'" % (dict["sid"], title.replace("'", "''"))
                server.save(sql)
        print("contains sid dict:", dict)
        return dict["sid"]
    else:
        return None

# def getSid():
#     datarows = getInfo()
#     for row in datarows:
#         title, flag = row
#         # print title,flag
#         if not flag == 0:
#             continue
#         # keyIndex = keyIndex + 1
#         dealInfo(titleGetRes(title),title)


# if __name__ == "__main__":
#     getSid()
#

