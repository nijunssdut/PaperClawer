# -*- coding:utf-8 -*-
from scopusSearch import getTotalNumFromSearchAPI

docType = ["cp", "ar", "ab", "ip", "bk", "bz", "ch", "cr", "ed", "er", "le", "no", "pr", "re", "sh"]
affilCountry = ["United States", "China", "United Kingdom", "Germany", "Canada", "Japan", "India",
                "Italy", "South Korea", "France", "Australia", "Switzerland", "Spain"]
maxPubyear = 2020
maxSearchNum = 4000

### 根据搜索条件从Scopus中提取文章列表

def getKeyQuery(key):
    return '(abs("%s") or title("%s") or key("%s"))'% (key, key, key)

#Year for the remaining part
def getQueryBeforeYear(query,year):
    query = query + 'and PUBYEAR < %d '%(year)
    return query

#Year for single segment
def getQueryEqualYear(query,year):
    query = query + 'and PUBYEAR = %d '%(year)
    return query

#DocType single and remaining
def getQueryPlusDoctype(query,typeList):
    typestr = "DOCTYPE(%s)" % (typeList[0])
    if len(typeList) > 1:
        for type in typeList[1:]:
            typestr += " OR " + "DOCTYPE(%s)" % (type)
    query = query + 'and (%s) ' % (typestr)
    return query

def getQuerySubDoctype(query,typeList):
    typestr = "DOCTYPE(%s)"% (typeList[0])
    if len(typeList) > 1:
        for type in typeList[1:]:
            typestr += " OR " + "DOCTYPE(%s)"% (type)
    query = query + 'and not (%s) ' % (typestr)
    return query

#Country for single segment
def getQueryPlusCountry(query,countryList):
    countrystr = "affilcountry(%s)" % (countryList[0])
    if len(countryList) > 1:
        for type in countryList[1:]:
            countrystr += " OR " + "affilcountry(%s)" % (type)
    query = query + 'and (%s) ' % (countrystr)
    return query

#Country for remaining part
def getQuerySubCountry(query,countryList):
    countrystr = "affilcountry(%s)" % (countryList[0])
    if len(countryList) > 1:
        for type in countryList[1:]:
            countrystr += " OR " + "affilcountry(%s)" % (type)
    query = query + 'and not (%s) ' % (countrystr)
    return query

def getPaperNumEveryYear(base_query,sub_query,totalNum):
    subNum = totalNum
    subYear = maxPubyear
    yearList = []
    while subNum > maxSearchNum:
        query = getQueryEqualYear(base_query+sub_query, subYear)
        singleNum = getTotalNumFromSearchAPI(query)
        own_query = query.replace(base_query, "")   #save the addtional query
        if singleNum != 0:
            yearList.append([subYear, singleNum, own_query])
        subNum -= singleNum
        subYear -= 1
    remainQuery = getQueryBeforeYear(base_query+sub_query, subYear+1)   #build the remain query
    singleNum = getTotalNumFromSearchAPI(remainQuery)
    print(singleNum, remainQuery)
    yearList.append(["remainYear", singleNum, remainQuery.replace(base_query,"")])
    return yearList

def getPaperNumPerType(base_query,sub_query,totalNum):
    subNum = totalNum
    typeList = []
    typeIndex = 0
    while subNum > maxSearchNum and typeIndex < len(docType):
        query = getQueryPlusDoctype(base_query+sub_query,[docType[typeIndex]])
        #print(query)
        singleNum = getTotalNumFromSearchAPI(query)
        own_query = query.replace(base_query, "")
        if singleNum != 0:
            typeList.append([docType[typeIndex], singleNum, own_query])
            subNum -= singleNum
        typeIndex += 1
    if typeIndex < len(docType):
        remainQuery = getQuerySubDoctype(base_query+sub_query,docType[:typeIndex])
        singleNum = getTotalNumFromSearchAPI(remainQuery)
        print(singleNum, remainQuery)
        typeList.append(["remainDocType", singleNum, remainQuery.replace(base_query,"")])
    return typeList

def getPaperNumPerCountry(base_query,sub_query,totalNum):
    subNum = totalNum
    countryList = []
    countryIndex = 0

    while subNum > maxSearchNum and countryIndex < len(affilCountry):
        query = getQueryPlusCountry(base_query+sub_query,[affilCountry[countryIndex]])
        #print(query)
        singleNum = getTotalNumFromSearchAPI(query)
        own_query = query.replace(base_query,"")
        if singleNum != 0:
            countryList.append([affilCountry[countryIndex], singleNum, own_query])
            subNum -= singleNum
        countryIndex += 1
    if countryIndex < len(affilCountry):
        remainQuery = getQuerySubCountry(base_query+sub_query,affilCountry[:countryIndex])
        singleNum = getTotalNumFromSearchAPI(remainQuery)
        print(singleNum, remainQuery)
        countryList.append(["remainCountry", singleNum, remainQuery.replace(base_query,"")])
    return countryList

def buildOriginTask(key):
    base_query = getKeyQuery(key)  # 256480
    # base_query = getKeyQuery("machine learning")    #79671
    taskList = []
    totalNum = getTotalNumFromSearchAPI(base_query)
    print("totalNum:", totalNum)
    yearList = getPaperNumEveryYear(base_query, "", totalNum)  # Year
    for item in yearList:
        print(item)
        if item[1] > maxSearchNum:
            docTypeList = getPaperNumPerType(base_query, item[2], item[1])  # DocType
            for item2 in docTypeList:
                print(item2)
                if item2[1] > maxSearchNum:
                    countryList = getPaperNumPerCountry(base_query, item2[2], item2[1])  # Country
                    for item3 in countryList:
                        print(item3)
                        taskList.append([str(len(taskList)), str(item3[1]), item3[2].lstrip("and")])
                else:
                    taskList.append([str(len(taskList)), str(item2[1]), item2[2].lstrip("and")])
        else:
            taskList.append([str(len(taskList)), str(item[1]), item[2].lstrip("and")])
    return taskList

if __name__ == '__main__':
    key = "artificial intelligence"
    taskList = buildOriginTask(key)
    print(len(taskList))
    totalNum = 0
    f1 = open("saveTask.txt","w")
    for item in taskList:
        f1.write("\t".join(item)+"\n")
        totalNum += int(item[1])
    print(totalNum)
    f1.close()



