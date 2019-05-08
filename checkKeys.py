from crawler_tools import getHTMLFromURLlib
import Settings
# Scopus API 接口序列码列表及索引
apikeyList = Settings.apikeyList
keyIndex = Settings.keyIndex


def checkScopusKeyIndex():
    """
    检查爬虫是否因为key造成异常
    :return: key的索引
    """
    global keyIndex
    sid = 85020008218
    url = 'http://api.elsevier.com/content/abstract/scopus_id/' + str(sid)
    url += '?field=title&apiKey=' + apikeyList[keyIndex]
    # print(url)
    try:
        getHTMLFromURLlib(url, 1)
    except Exception as e:
        # print(e) 出现异常，可能key次数用尽，需要加1
        if '401' in str(e) or '429' in str(e):
            keyIndex += 1
            if keyIndex >= len(apikeyList):
                raise Exception("all apiKeys are invalid")
            checkScopusKeyIndex()

    return keyIndex

if __name__ == "__main__":   # artificial intelligence （针对于人工智能领域的数据）
    keyIndex = checkScopusKeyIndex()
    print(keyIndex)
