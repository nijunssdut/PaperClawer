import random
import xmltodict
import json
import urllib.parse
import urllib.request

user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0', \
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0', \
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+ \
    (KHTML, like Gecko) Element Browser 5.0', \
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)', \
    'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14', \
    'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) \
    Version/6.0 Mobile/10A5355d Safari/8536.25', \
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/28.0.1468.0 Safari/537.36', \
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)']


def getJSONFromHtml(htmlText):
    """
    HTML格式转JSON格式
    :param htmlText: 输入HTML内容
    :return: JSON
    """
    html = json.loads(htmlText)
    return html


def getXMLFromHtml(htmlText):
    """
    HTML格式转XML格式
    :param htmlText: 输入HTML内容
    :return: XML
    """
    html = htmlText
    html = xmltodict.parse(html)
    return html


def getHTMLFromURLlib(url, maxTime=3, time=0):
    """
    从URL中获取到网页内容
    :param url: 爬取连接
    :param maxTime: 允许最大异常次数
    :param time: 异常次数
    :return:爬取内容
    """
    # print(url,time)
    rNum = random.randint(0, 7)
    i_headers = {'User-Agent': user_agents[rNum]}
    html = ""
    try:
        req = urllib.request.Request(url, headers=i_headers)
        html = urllib.request.urlopen(req).read().decode("utf-8")
    except Exception as e:
        time += 1
        if time > maxTime:   # at most 5 error times to retry
            raise Exception("Error:More over test number", url, e)
        getHTMLFromURLlib(url, maxTime, time)
    return html

apikeyList = ['c0eed40e635653f65a417c0f0e74d2d8',
              'c0eed40e635653f65a417c0f0e74d2d9',
              'c0eed40e635653f65a417c0f0e74d210',
              'ff690ff74b75d44394d401f972e408c1']
keyIndex = 0


def textUrl(sid):
    """
    爬取scopus上文章ID为sid的数据
    :param sid: Scopus上的文章ID
    :return: 数据内容
    """
    global keyIndex
    url = 'http://api.elsevier.com/content/abstract/scopus_id/' + str(sid)
    url += '?field=citedby-count,aggregationType,doi,coverDate,publicationName,authkeywords,' \
           'url,identifier,description,author,affiliation,title&apiKey=' + \
           apikeyList[keyIndex]
    html = ""
    try:
        html = getHTMLFromURLlib(url)
    except Exception as e:
        if 'Unauthorized' in str(e):
            keyIndex += 1
            if keyIndex >= len(apikeyList):
                raise Exception("all apiKeys are invalid")
            html = textUrl(sid)
    return html


if __name__ == "__main__":
    html = textUrl(85020008218)
    print(html)
