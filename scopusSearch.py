# -*- coding:utf-8 -*-
import urllib
import urllib.parse
import urllib.request
import Settings
from databaseIO import dbIO
from crawler_tools import getHTMLFromURLlib, getJSONFromHtml

apikey = Settings.apikey  # 98fed43850c47f7b0ed4d5db222320af
singleSearchNum = Settings.singleSearchNum
maxSearchNum = Settings.maxSearchNum


def getTotalNumFromSearchAPI(query):
    """
    :param query: Scopus高级检索命令语句
    :return: 符合条件的结果数目
    """
    urlL = "http://api.elsevier.com/content/search/scopus?" + urllib.parse.urlencode(
        {'query': query}) + "&httpAccept=application/json&apiKey=%s&count=%d&start=%d" % (apikey, 10, 0)
    html = getJSONFromHtml(getHTMLFromURLlib(urlL))
    total = html["search-results"]["opensearch:totalResults"]
    if total == 'null':
        return 0
    return int(total)


def getArticlefromAPI(query, totalNum, taskStart):
    """
    :param query: Scopus高级检索命令语句
    :param totalNum: 任务总数
    :param taskStart: 任务开始起点位置
    :return: Scopus文章信息列表
    """
    url = "http://api.elsevier.com/content/search/scopus?" + urllib.parse.urlencode(
        {'query': query}) + "&httpAccept=application/json&apiKey=%s" % apikey

    articleList = []
    startIndex = taskStart
    try:
        if startIndex != totalNum:
            singleCount = singleSearchNum    # 7.19 modified
            if totalNum - startIndex < singleSearchNum:
                singleCount = totalNum - startIndex
            urlL = url + "&count=%d&start=%d" % (singleCount, startIndex)
            html = getJSONFromHtml(getHTMLFromURLlib(urlL))
            # startIndex = html["search-results"]["opensearch:startIndex"]
            if 'error' in html["search-results"]["entry"][0]:
                return []
            articleList.extend(html["search-results"]["entry"])
            print("tN:%d,sI:%d,aL:%d" % (totalNum, startIndex, len(articleList)))

            startIndex = taskStart+len(articleList)
    except Exception as e:
        print(str(e))
        # print("totalnum:"+str(totalNum)+ "finish num:"+str(len(articleList)))

    # print(articleList)
    dataList = []
    for item in articleList:
        articleDict = {}
        articleDict['url'] = item["prism:url"]
        if "dc:identifier" in item:
            articleDict['id'] = item["dc:identifier"].replace("SCOPUS_ID:", "")
        elif "prism:url" in item:
            articleDict['id'] = item["prism:url"].replace("http://api.elsevier.com/content/abstract/scopus_id/", "")
        else:
            continue
        if 'prism:doi' in item:
            articleDict['doi'] = item["prism:doi"]
        else:
            articleDict['doi'] = ''

        if 'citedby-count' in item:
            articleDict['citation'] = item["citedby-count"]
        else:
            articleDict['citation'] = '0'

        if 'prism:coverDate' in item:
            articleDict['date'] = item["prism:coverDate"]

        dataList.append(articleDict)
    # print(dataList)
    return dataList


def searchArticlesByQuery(query, taskID):
    """
    :param query: Scopus高级检索命令语句
    :param taskID: 任务序号
    :return: 插入文章信息到searchlist数据库中
    """
    dbIOserver = dbIO()
    totalNum = getTotalNumFromSearchAPI(query)
    print("searchResults:" + str(totalNum))
    sql = "SELECT * FROM searchlist where taskID = " + str(taskID)
    dataLength = dbIOserver.count(sql)
    print(dataLength)
    repeatNum = 0
    lastNum = 0
    maxRepeatNum = 5
    while (totalNum > 0 and dataLength < totalNum and dataLength < 5000) and repeatNum <= maxRepeatNum:
        if lastNum != totalNum + dataLength:
            repeatNum = 0
            lastNum = totalNum + dataLength
        else:
            repeatNum += 1
        articlesList = getArticlefromAPI(query, totalNum, dataLength)
        insertNum = 0
        for article in articlesList:
            sql = "select * from searchlist where sid = " + article['id']
            if dbIOserver.count(sql) == 0:
                sql = "INSERT INTO searchlist (sid,doi,flag,taskID) VALUES ('" + str(article['id'])\
                      + "','" + article['doi'] + "',0,'"+str(taskID)+"')"
                if dbIOserver.save(sql) > 0:
                    insertNum += 1
        dataLength += len(articlesList)
        print("dataLength:" + str(dataLength))

    if repeatNum > 3:
        sql = "update tasklist set flag = 0 where id = " + str(taskID)
        dbIOserver.save(sql)
        return
    sql = "update tasklist set flag = 1 where id = " + str(taskID)
    dbIOserver.save(sql)


if __name__ == '__main__':

    # search articles from Scopus

    query = """(abs(artificial intelligence) or title(artificial intelligence) or key(artificial intelligence)) 
    and (( PUBYEAR = 2017 and (DOCTYPE(cp)) and not (affilcountry(United States) OR affilcountry(China)) ) 
    OR ( PUBYEAR = 2010 and (DOCTYPE(cp)) and (affilcountry(Germany)) ))"""

    taskID = 75
    searchArticlesByQuery(query, taskID)



