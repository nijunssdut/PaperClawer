# -*- coding:utf-8 -*-
from databaseIO import dbIO

newDBStr = 'newStudent'
originDBStr = 'wholeai9011'


def getMaxFrequentAffilName(affillist):
    """
    for mutil-affil get the most frequent one （模糊获取高频机构）
    :param affillist: 机构列表
    :return: 打印机构与对应文章数
    """
    server = dbIO(originDBStr)
    for affil in affillist:
        sql = "select count(*) from articlelist where affillist like '%"+affil+"%'"
        num = server.load(sql)[0][0]
        print(affil, num)


def selectAffilName(affillist):
    """
    选取机构名称，优先选取第一机构
    :param affillist:
    :return: 机构的ID
    """
    server = dbIO(newDBStr)
    for affilId in affillist:
        sql = "select * from affiltest where afid = '%s'" % affilId
        if server.count(sql) > 0:
            return affilId


def updateAffilIDfromWholeData(affilID):
    """
    原库中没有该机构而新库中存在，查询到机构的信息并插入到原库的机构表中
    :param affilID: 机构的ID
    :return: 原库存在该机构，返回其ID，新库不存在该机构返回-1，否则返回0
    """
    server = dbIO(originDBStr)
    sql = "select id from affillist where afid = '%s'" % affilID
    wholerows = server.load(sql)
    if len(wholerows) > 0:
        singleID = wholerows[0][0]
        return singleID
    else:
        server2 = dbIO(newDBStr)
        sql = "select * from affiltest where afid = '%s'"% affilID
        data = server2.load(sql)
        if len(data) == 0: return -1
        alterdata = data[0]
        sql = "insert into affillist (afid,name,city,country,url) values ('%s','%s','%s','%s','%s')" \
              % (alterdata[1], alterdata[2].replace("'", "''"), alterdata[3].replace("'", "''"),
                 alterdata[4].replace("'", "''"), alterdata[5].replace("'", "''"))
        # print(sql)
        server.save(sql)
        return 0


def updateAuthorIDfromWholeData(authorID):
    """
    更新原库作者信息
    :param authorID:
    :return: 作者ID，作者机构ID
    """
    server = dbIO(originDBStr)
    sql = "select id,affillist from authorlist where aid = '%s'" % authorID
    wholerows = server.load(sql)
    if len(wholerows) > 0:
        singleID = wholerows[0][0]
        affilid = wholerows[0][1].split("|")[0]
    else:
        server2 = dbIO(newDBStr)
        sql = "select * from authortest where aid = '%s'" % authorID
        print(sql)
        alterdata = server2.load(sql)[0]
        affilid = alterdata[9]
        # print(affilid,alterdata)
        if len(affilid) > 9:
            affilid = selectAffilName(alterdata[9].split("|"))

        result = updateAffilIDfromWholeData(affilid)
        if result == -1: affilid = ''
        sql = "insert into authorlist (aid,url,fullname,simname,firstname,lastname,simlastname," \
              "articlelist,affillist)values ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"\
              % (alterdata[1], alterdata[2], alterdata[3].replace("'", "''"), alterdata[4].replace("'", "''"),
                 alterdata[5].replace("'", "''"), alterdata[6].replace("'", "''"), alterdata[7], '', affilid)
        # print(sql)
        server.save(sql)
    return authorID, affilid


def checkTitleInWholeData(title):
    """
    检查论文是否在原库出现过
    :param title: 文章标题
    :return: True表示文章出现过，否则未出现
    """
    server = dbIO(originDBStr)
    sql = "select * from articlelist where title = '%s'" % (title.replace("'", "''"))
    if server.count(sql) > 0:
        return True
    else:
        return False


def getAlterArticleData():
    """
    为原库更新论文信息，插入信息到articlelist
    :return:
    """
    server = dbIO(newDBStr)
    sql = "select * from articletest"
    articleData = server.load(sql)
    for item in articleData:
        authorlist = item[3].split("|")
        affillist = item[4].split("|")
        if len(authorlist) > 200 or checkTitleInWholeData(item[5]):  # pass the reviewers paper 作者过多或出现过的论文无用
            continue
        # print(item,len(authorlist),len(affillist))
        newAuthorlist = []
        newAffillist = []
        for author in authorlist:
            if author == '': continue
            authorID, affilID = updateAuthorIDfromWholeData(author)
            newAuthorlist.append(authorID)
            newAffillist.append(affilID)
        server2 = dbIO(originDBStr)
        sql = """insert into articlelist (sid,doi,authorlist,affillist,
            title,abstract,keywords,date,journalName,articleType,abstractLang,citation) 
            values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" \
            % (item[1], item[2], "|".join(newAuthorlist), "|".join(newAffillist),
               item[5].replace("'", "''"), item[6].replace("'", "''"), item[7].replace("'", "''"),
               item[8], item[9].replace("'", "''"), item[10], item[11], item[12])
        # print(sql)
        server2.save(sql)


def udpateSearchlist():
    """
    从新库中获取新的文章信息添加到原库中，更新检索列表
    :return:
    """
    server = dbIO(newDBStr)
    sql = """select title,url,year,publication_id,flag,sid from searchlist"""
    datarows = server.load(sql)
    server = dbIO(originDBStr)
    print(len(datarows))
    for data in datarows:
        title, url, year, publication_id, flag, sid = data
        if not sid: sid = ""
        sql = """insert into searchlist2 (title,url,year,publication_id,flag,sid) 
              values ('%s','%s','%s','%d','%d','%s')""" \
              % (title.replace("'", "''"), url.replace("'", "''"), year.replace("'", "''"),
                 publication_id, flag, sid.replace("'", "''"))
        server.save(sql)


if __name__ == "__main__":
    # getAlterArticleData()  # add alter papers into 3 tables
    udpateSearchlist()  # update searchlist
