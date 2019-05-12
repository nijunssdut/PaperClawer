# -*- coding:utf-8 -*-
import urllib
import urllib.parse
import urllib.request
import pymysql
import Settings
from databaseIO import dbIO
from crawler_tools import getHTMLFromURLlib,getJSONFromHtml,getXMLFromHtml
from checkKeys import checkScopusKeyIndex

apikey = 'ff690ff74b75d44394d401f972e408c1'   # 1

singleSearchNum = Settings.singleSearchNum
maxSearchNum = Settings.maxSearchNum+500


def saveWholeArticletoDB(infoDict, authorList, affilList):
    """
    保存爬取到的内容到数据库中
    :param infoDict: 文章信息字典
    :param authorList: 对应的作者信息列表（可能多作者）
    :param affilList: 对应的机构信息列表（可能多机构）
    :return:
    """
    server = dbIO()
    sql = "select * from articlelist where sid = '%s'"%(infoDict['id'])
    if server.count(sql) != 0:
        return 0
    # save the affilication data
    affils = ""
    for affil in affilList:
        affils += affil['id'] + "|"
        sql = "select * from affillist where afid = " + affil['id']
        if server.count(sql) == 0:
            sql = "insert into affillist (afid,name,country,city,url) VALUES ('" + affil['id'] + "','" + affil['name'] + "','" + affil['country'] + "','" + affil['city'] + "','" + affil['url'] + "')"
            sta = server.save(sql)
        """
        else:
            sql = "udpate affillist set name = '" + affil['name'] + "',city = '" + affil['city'] + "',country = '" + affil['country'] + "', url = '" + affil['url'] + "' where afid = " + affil['id']
            sta = cur.execute(sql)"""
    affils = affils[:-1]

    # save the author data
    authors = ""
    for author in authorList:
        authors += author['id'] + "|"
        sql = "select * from authorlist where aid = " + author['id']
        if server.count(sql) == 0:
            affiliation = author['affiliation']
            affilids = ""
            for affil in affiliation:
                affilids += affil + "|"
            articles = infoDict['id']
            sql = "insert into authorlist (aid,url,fullname,simname,firstname,lastname,simlastname,affillist,articlelist) VALUES ('" +\
                  author['id'] + "','" + author['url'] + "','" + author['fullname'] + "','" + author['simname'] + "','" +\
                  author['firstname'] + "','" + author['lastname'] + "','" + author['simlastname'] +\
                  "','" + affilids[:-1] + "','" + articles + "')"
            sta = server.save(sql)
        else:
            articles = server.load(sql)[0][8]
            articleStrs = articles.split("|")
            if infoDict['id'] not in articleStrs:
                articles += "|" + infoDict['id']
                sql = "select id from authorlist where aid = " + author['id']
                if server.count(sql) == 0:
                    sql = "update authorlist set articlelist = '" + articles + "' where id = " + server.load(sql)[0][0]
                    sta = server.save(sql)
    authors = authors[:-1]

    # save the article data
    keywords = ""
    for key in infoDict['authorKeywords']:
        keywords += key.replace("'","''") + "|"
    keywords = keywords[:-1]
    #print(infoDict)
    sql = "insert into articlelist (sid,doi,title,abstract,journalName,articleType,date,citation,abstractLang,keywords,authorlist,affillist) VALUES ('" + \
          infoDict['id'] + "','" + infoDict['doi'] + "','" + infoDict['title'] + "','" + infoDict['abstract'] + "','" + \
          infoDict['journal'] + "','" + infoDict['articleType'] + "','" + infoDict['date'] + \
          "','" + infoDict['citation'] + "','" + infoDict['abstractLang'] + "','" + keywords + \
          "','" + authors + "','" + affils + "')"
    sta = server.save(sql)
    return 1


def getAffilInfofromXML(item):
    """
    :param item:机构XML格式的信息
    :return:返回机构信息字典
    """
    affil = {}
    affil['id'] = item['@id']
    affil['url'] = item['@href'].replace("'","''")
    affil['name'] = item['affilname'].replace("'","''") if item['affilname'] is not None else ""

    affil['city'] = item['affiliation-city'] if item['affiliation-city'] is not None else ""
    affil['city'] = affil['city'].replace("'","''")

    affil['country'] = item['affiliation-country'] if item['affiliation-country'] is not None else ""
    affil['country'] = affil['country'].replace("'", "''")

    return affil


def getAuthorInfofromXML(item):
    """
    :param item: 作者XML格式的信息
    :return: 返回作者信息字典
    """
    author = {}
    author['id'] = item['@auid']
    author['url'] = item['author-url'].replace("'","''")
    author['rank'] = item['@seq']

    author['simname'] = item['ce:indexed-name']\
        if 'ce:indexed-name' in item else item['preferred-name']['ce:indexed-name']  # Bai Y.缩写
    author['simname'] = author['simname'].replace("'", "''")\
        if author['simname'] is not None else ""

    author['firstname'] = item['ce:surname']\
        if 'ce:surname' in item else item['preferred-name']['ce:surname']  # Bai
    author['firstname'] = author['firstname'].replace("'", "''")\
        if author['firstname'] is not None else ""

    author['lastname'] = item['ce:given-name']\
        if 'ce:given-name' in item else item['preferred-name']['ce:given-name']  # Yang
    author['lastname'] = author['lastname'].replace("'", "''")\
        if author['lastname'] is not None else ""

    author['simlastname'] = item['ce:initials']\
        if 'initials' in item else item['preferred-name']['ce:initials']  # Y.
    author['simlastname'] = author['simlastname'].replace("'", "''")\
        if author['simlastname'] is not None else ""

    author['fullname'] = author['firstname'] + " " + author['lastname']  # Bai Yang
    affils = []
    if 'affiliation' in item:
        if isinstance(item['affiliation'], list):
            for singleaffil in item['affiliation']:
                affils.append(singleaffil['@id'])
        elif isinstance(item['affiliation'], dict):
            affils.append(item['affiliation']['@id'])
    author['affiliation'] = affils
    return author

apikeyList = Settings.apikeyList
keyIndex = Settings.keyIndex


def getDocfromAbstractAPI(sid, keyIndex):
    """
    :param sid: 文章Scopus ID
    :param keyIndex: API调用密钥索引
    :return: 返回XML格式网页爬取内容，或者异常
    """
    url = 'http://api.elsevier.com/content/abstract/scopus_id/' + str(sid)
    url += '?field=citedby-count,aggregationType,doi,coverDate,publicationName,authkeywords,url,identifier,' \
           'description,author,affiliation,title&apiKey=' + apikeyList[keyIndex]
    print(url)
    doc = ""
    try:
        doc = getXMLFromHtml(getHTMLFromURLlib(url, 1))
    except Exception as e:
        if '401' in str(e) or '429' in str(e):
            keyIndex += 1
            if keyIndex >= len(apikeyList):
                raise Exception("all apiKeys are invalid")
            doc = getDocfromAbstractAPI(id, keyIndex)
    return doc


def getInfofromAbstractAPI(sid, keyIndex = 0):
    """
    :param sid: 文章Scopus ID
    :param keyIndex: API调用密钥索引
    :return: 返回文章信息字典，作者列表，机构列表
    """
    authorList = []
    affilList = []
    infodict = {}
    doc = getDocfromAbstractAPI(sid, keyIndex)
    if isinstance(doc, str):
        return [], [], []
    # 获取字典或列表形式作者信息，从XML中抽取出来
    if 'authors' in doc['abstracts-retrieval-response'] and doc['abstracts-retrieval-response']['authors'] is not None:
        if 'author' in doc['abstracts-retrieval-response']['authors']:
            if isinstance(doc['abstracts-retrieval-response']['authors']['author'], list):
                for item in doc['abstracts-retrieval-response']['authors']['author']:
                    author = getAuthorInfofromXML(item)
                    authorList.append(author)
            elif isinstance(doc['abstracts-retrieval-response']['authors']['author'], dict):
                item = doc['abstracts-retrieval-response']['authors']['author']
                author = getAuthorInfofromXML(item)
                authorList.append(author)

    # 获取字典或列表形式机构信息，从XML中抽取出来
    if 'affiliation' in doc['abstracts-retrieval-response']:
        if isinstance(doc['abstracts-retrieval-response']['affiliation'], list):
            for item in doc['abstracts-retrieval-response']['affiliation']:
                affil = getAffilInfofromXML(item)
                affilList.append(affil)
        elif isinstance(doc['abstracts-retrieval-response']['affiliation'], dict):
            item = doc['abstracts-retrieval-response']['affiliation']
            affil = getAffilInfofromXML(item)
            affilList.append(affil)

    # process basicInfo
    infodict['id'] = str(sid)
    infodict['doi'] = doc['abstracts-retrieval-response']['coredata']['prism:doi']\
        if 'prism:doi' in doc['abstracts-retrieval-response']['coredata'] else ""
    infodict['title'] = doc['abstracts-retrieval-response']['coredata']['dc:title'].replace("'", "''")
    infodict['articleType'] = doc['abstracts-retrieval-response']['coredata']['prism:aggregationType']\
        if 'prism:aggregationType' in doc['abstracts-retrieval-response']['coredata'] else ""
    infodict['citation'] = doc['abstracts-retrieval-response']['coredata']['citedby-count']\
        if 'citedby-count' in doc['abstracts-retrieval-response']['coredata'] else ""
    infodict['journal'] = ""
    if 'prism:publicationName' in doc['abstracts-retrieval-response']['coredata']:
        infodict['journal'] = doc['abstracts-retrieval-response']['coredata']['prism:publicationName']\
            .replace("'", "''")
    infodict['date'] = doc['abstracts-retrieval-response']['coredata']['prism:coverDate']
    if 'dc:description' in doc['abstracts-retrieval-response']['coredata']:
        infodict['abstractLang'] = doc['abstracts-retrieval-response']['coredata']
        ['dc:description']['abstract']['@xml:lang']
        abstractList = doc['abstracts-retrieval-response']['coredata']['dc:description']['abstract']['ce:para']
        # 摘要是字符串，字典，列表不同形式的处理
        if isinstance(abstractList, list):
            abstractStr = ""
            for abstract in abstractList:
                if isinstance(abstract, dict):
                    abstractStr += abstract['#text']
                else:
                    abstractStr += abstract
            infodict['abstract'] = abstractStr
        elif isinstance(abstractList, dict):
            infodict['abstract'] = abstractList['#text']
        else:
            infodict['abstract'] = abstractList

        infodict['abstract'] = infodict['abstract'].replace("'", "''")
    else:
        infodict['abstractLang'] = ""
        infodict['abstract'] = ""

    infodict['authorKeywords'] = []
    # 关键词是列表或字典处理
    if 'authkeywords' in doc['abstracts-retrieval-response']:
        keywords = doc['abstracts-retrieval-response']['authkeywords']['author-keyword']
        if isinstance(keywords, list):
            infodict['authorKeywords'] = keywords
        elif isinstance(keywords, str):
            infodict['authorKeywords'] = [keywords]

    return infodict, authorList, affilList


# backup main function
def getArticleInfo():
    if True:  # try:
        server = dbIO()
        sql = "select sid from searchlist2 where flag = 0  and" \
              " id > (SELECT max(id) FROM paper_data.searchlist2 where flag = 1)"
        totalNum = server.count(sql)
        if totalNum > 0:
            finishNum = 0
            passNum = 0
            print('totalNum:'+str(totalNum))
            keIndex = checkScopusKeyIndex()
            for row in server.load(sql):
                sid = row[0]
                passNum += 1
                try:
                    infodict, authorList, affilList = getInfofromAbstractAPI(int(sid), keIndex)
                    if infodict == []:
                        continue
                    flag = saveWholeArticletoDB(infodict, authorList, affilList)
                    if flag > -1:
                        sql = "update searchlist2 set flag = 1 where sid = "+sid
                        finishNum += 1
                        print("No."+str(finishNum)+" Finish: "+sid+" PassNum:"+str(passNum-finishNum))
                        server.save(sql)

                except Exception as e:  # ConnectionResetError
                    print("Wrong: " + sid + "*" * 20)
                    print(e)
                    continue


if __name__ == '__main__':
    # search articles from Scopus
    # searchAreaArticles()
    # getWholeDatabyArticles(articlesList)

    getArticleInfo()

    """
    sid = 85019085044
    infodict, authorList, affilList = getInfofromAbstractAPI(sid)
    for key in infodict:
        print(key,"——",infodict[key])
    for item in authorList:
        print(item)
    for item in affilList:
        print(item)"""



