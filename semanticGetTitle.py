# -*- coding:utf-8 -*-
import urllib
import json
import random
import Levenshtein
import urllib.parse
import urllib.request

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


def getJsonDict(row):
    """
    :param row: 标题
    :return: 异常或者标题间编辑距离/给定标题长度<0.1时，返回[]，否则返回semantic库中论文的信息
    """
    rNum = random.randint(0, 7)
    i_headers = {'User-Agent': user_agents[rNum]}
    title = row
    dict = {}
    values = {}
    values['q'] = title
    data = urllib.parse.urlencode(values)
    url = "https://www.semanticscholar.org/search"
    geturl = url + '?' + data
    try:
        request = urllib.request.Request(geturl, headers=i_headers)
        response = urllib.request.urlopen(request, timeout=10)
        dic = response.read().decode("utf-8")
    except Exception as e:
        print(str(e), geturl)
        return []
    a = dic.find('[{"id"')  # 取第一条开头
    b = dic.find('{"id"', a + 2)
    c = dic[a + 1:b - 1].find("],\"query")
    if c >= 0:
        dic = dic[a + 1:1 + a + c].replace("\n\r", "")
    else:
        dic = dic[a + 1:b - 1].replace("\n\r", "")
    jsonDict = json.loads(dic)
    if not "title" in jsonDict:
        return []
    # 计算标题间的编辑距离，推断模糊匹配度
    dict["rel"] = Levenshtein.distance(str(jsonDict["title"]["text"].lower()),
                                       str(values["q"].lower())) / float(len(title))
    print("semantic compared title data:", dict["rel"])
    if dict["rel"] <= 0.1:
        temp = []
        for i in range(len(jsonDict["authors"])):
            tempsdict = {}
            tempsdict["name"] = jsonDict["authors"][i][0]["name"]
            tempsdict["ids"] = jsonDict["authors"][i][0]["ids"]
            temp.append(tempsdict)
        url2 = "http://api.semanticscholar.org/v1/paper/"
        geturl2 = url2 + jsonDict["id"]
        try:
            request2 = urllib.request.Request(geturl2, headers=i_headers)
            response2 = urllib.request.urlopen(request2, timeout=10)
            dic2 = response2.read().decode("utf-8")
            dic2 = dic2.replace("\n\r", "")
        except Exception as e:
            print(str(e), geturl2)
            return []
        jsonDict2 = json.loads(dic2)
        dict["citations"] = len(jsonDict2["citations"])
        if "doi" in jsonDict2 and not jsonDict2["doi"] is None:
            dict["doi"] = jsonDict2["doi"]
        else:
            dict["doi"] = ""
        dict["id"] = jsonDict["id"]
        dict["title"] = jsonDict["title"]["text"]
        dict["paperAbstract"] = jsonDict["paperAbstract"]["text"]
        if "keyPhrases" in jsonDict:
            dict["keyPhrases"] = jsonDict["keyPhrases"]
        else:
            dict["keyPhrases"] = ""
        dict["authors"] = temp
        if "year" in jsonDict:
            dict["year"] = jsonDict["year"]["text"]
        else:
            dict["year"] = ""
        if "links" in jsonDict:
            list3 = []
            for k in range(len(jsonDict["links"])):
                list3.append(jsonDict["links"][k]["url"])
            dict["pdfUrls"] = list3
        else:
            dict["pdfUrls"] = ""
        dict["s2Url"] = "http://semanticscholar.org/paper/" + str(dict["id"])
        if "venue" in jsonDict:
            dict["venue"] = jsonDict["venue"]["text"]
        else:
            dict["venue"] = ""
        if not dict["rel"] == 0:
            dict["title"] = title
        print("semantic id", dict["id"])
        return dict
    else:
        return []




