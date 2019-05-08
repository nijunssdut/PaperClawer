# -*- coding:utf-8 -*-
from scopusTitleGetsid import dealInfo,titleGetRes
from scopusWholeInfo import getInfofromAbstractAPI,saveWholeArticletoDB
from scopusSupplyData import getJsonDict,authorGetRes,findArticle
from checkKeys import checkScopusKeyIndex
from databaseIO import dbIO
# 对于searchlist中的flag，如果flag为1，那么有scoops id，并且完成操作
# 如果flag为2可能，在插入有scops id数据时出现错误
# 如果flag为3，则进入补充数据Supply data阶段，表示数据补充完成，但其sid为semantic id
def getArticleInfo():
    if True: #try:
        server = dbIO()
        sql = "select title,flag,sid from searchlist2 where flag=0 and sid is NULL"
        totalNum = server.count(sql)
        if totalNum > 0:
            finishNum = 0
            passNum = 0
            print('totalNum:'+str(totalNum))
            keIndex = checkScopusKeyIndex()
            for row in server.load(sql):
                title, flag, sid = row
                passNum += 1
                # try:
                sid=dealInfo(titleGetRes(title), title)
                print("sid:",sid)
                # 有sid存在时
                if sid:
                    print(title, flag)
                    infodict, authorList, affilList = getInfofromAbstractAPI(int(sid),keIndex)

                    if infodict == []:
                        continue
                    flag = saveWholeArticletoDB(infodict, authorList, affilList)
                    if flag > -1:
                        sql = "update searchlist2 set flag = 1 where sid = '%s'"% (sid)
                        finishNum += 1
                        print("No."+str(finishNum)+" Finish: "+sid+" PassNum:"+str(passNum-finishNum))
                        server.save(sql)
                # 不存在sid，从semantic进行数据补充处理
                else:
                    print(title, flag)
                    m = getJsonDict(title)
                    # semantic也不存在与该标题一致的数据
                    if not m:
                        continue
                    else:
                        for author in m["authors"]:
                            if len(author["ids"])==0:
                                authorGetRes(author["name"],[],m["id"])
                            else:
                                authorGetRes(author["name"], author["ids"][0],m["id"])
                        findArticle(m)

if  __name__ == '__main__':
    getArticleInfo()
