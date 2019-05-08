# -*- coding:utf-8 -*-
import urllib
import urllib.parse
import urllib.request
import random,ssl,json,xmltodict
from scopusTitleGetsid import titleGetRes
from semanticGetTitle import getJsonDict
from databaseIO import dbIO
import Settings
ssl._create_default_https_context = ssl._create_unverified_context
apikeyList = Settings.apikeyList
keyIndex = Settings.keyIndex

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


def authorGetRes(name,aid,pid):
    rNum = random.randint(0, 7)
    i_headers = {'User-Agent': user_agents[rNum]}
    dict={}
    audict = {}
    afdict={}
    values = {}
    a=name.rfind(' ')
    b=name.rfind('.')
    if b>a:
        lastname=name[b+1:]
        firstname=name[0:b]
    else:
        lastname=name[a+1:]
        firstname=name[0:a]
    values['query'] = 'authlast('+lastname+') and authfirst('+firstname+')'
    # print values
    data = urllib.parse.urlencode(values)
    # keyIndex=keyIndex+1
    url = "https://api.elsevier.com/content/search/author"
    geturl = url + '?' + data+'&apiKey='+apikeyList[keyIndex]
    try:
        request = urllib.request.Request(geturl, headers=i_headers)
        response = urllib.request.urlopen(request, timeout=5)
        dic = response.read().decode("utf-8")
    except Exception as e:
        print (str(e),geturl)
        return dict
    jsonDict = json.loads(dic)
    count=len(jsonDict["search-results"]["entry"])
    if not "error" in jsonDict["search-results"]["entry"][0] and count==1:
        # print (jsonDict["search-results"]["entry"])
        audict["id"]=jsonDict["search-results"]["entry"][0]["dc:identifier"].replace("AUTHOR_ID:","").replace("'", "''")if jsonDict["search-results"]["entry"][0]["dc:identifier"] != [] else ""
        audict["url"]=jsonDict["search-results"]["entry"][0]["prism:url"] if jsonDict["search-results"]["entry"][0]["prism:url"] is not None else ""
        audict["firstname"]=jsonDict["search-results"]["entry"][0]["preferred-name"]["surname"].replace("'", "''")if jsonDict["search-results"]["entry"][0]["preferred-name"]["surname"] is not None else ""
        audict["lastname"] = jsonDict["search-results"]["entry"][0]["preferred-name"]["given-name"].replace("'", "''")if jsonDict["search-results"]["entry"][0]["preferred-name"]["given-name"] is not None else ""
        audict["fullname"]=audict["firstname"].replace("'", "''")+" "+audict["lastname"].replace("'", "''")
        audict["simlastname"]=jsonDict["search-results"]["entry"][0]["preferred-name"]["initials"].replace("'", "''")if jsonDict["search-results"]["entry"][0]["preferred-name"]["initials"] is not None else ""
        audict["simname"]=audict["firstname"].replace("'", "''")+" "+audict["simlastname"].replace("'", "''")
        if "affiliation-current" in jsonDict["search-results"]["entry"][0]:
            # print (jsonDict["search-results"]["entry"][0]["affiliation-current"]["affiliation-id"].split(" ")[0])
            audict["affiliation"] = jsonDict["search-results"]["entry"][0]["affiliation-current"]["affiliation-id"].split(" ")[0]
            afdict["id"]=jsonDict["search-results"]["entry"][0]["affiliation-current"]["affiliation-id"].split(" ")[0]
            afdict["name"]=jsonDict["search-results"]["entry"][0]["affiliation-current"]["affiliation-name"].replace("'", "''")if jsonDict["search-results"]["entry"][0]["affiliation-current"]["affiliation-name"] is not None else ""
            afdict["city"]=jsonDict["search-results"]["entry"][0]["affiliation-current"]["affiliation-city"].replace("'", "''")if jsonDict["search-results"]["entry"][0]["affiliation-current"]["affiliation-city"] is not None else ""
            afdict["country"]=jsonDict["search-results"]["entry"][0]["affiliation-current"]["affiliation-country"].replace("'", "''")if jsonDict["search-results"]["entry"][0]["affiliation-current"]["affiliation-country"] is not None else ""
            afdict["url"]=jsonDict["search-results"]["entry"][0]["affiliation-current"]["affiliation-url"]
        # print dict
        updateSql(audict,afdict,pid)
    elif count==0:
        print ("no results")
    elif not aid:
        return
    else:
        dict["aid"]=aid
        dict["firstname"]=firstname
        dict["lastname"]=lastname
        dict["fullname"]=name
        dealaid(dict,pid)

def dealaid(dict,pid):
    dict2={}
    rNum = random.randint(0, 7)
    i_headers = {'User-Agent': user_agents[rNum]}
    url = "http://api.semanticscholar.org/v1/author/"
    geturl = url+dict["aid"]
    try:
        request = urllib.request.Request(geturl, headers=i_headers)
        response = urllib.request.urlopen(request, timeout=5)
        dic = response.read().decode("utf-8")
    except Exception as e:
        print (str(e),geturl)
        return []
    jsonDict = json.loads(dic)
    count = len(jsonDict["papers"])
    if count==0:
        print ("no way")
    else:
        for i in range(count):
            dict2=titleGetRes(jsonDict["papers"][i]["title"])
            if "rel" in dict2 and dict2["rel"]<=0.1:
                break
            if i>=4:
                break
        if "sid" in dict2:
            url2='http://api.elsevier.com/content/abstract/scopus_id/' + str(dict2["sid"])
            # keyIndex+=1
            url2 += '?field=author,affiliation,title&apiKey=' + apikeyList[keyIndex]
            # print url2
            try:
                request = urllib.request.Request(url2, headers=i_headers)
                response = urllib.request.urlopen(request, timeout=5)
                dic = response.read().decode("utf-8")
            except Exception as e:
                print (str(e),url2)
                return []
            dic=xmltodict.parse(dic)
            # jsonDict = json.loads(dic)
            author, affil = getInfofromAbstractAPI(dic, dict)
            # print author, affil
            if author and affil:
                updateSql(author,affil,pid)

def getInfofromAbstractAPI(dic,dic2):
    authors = {}
    affils = {}
    if 'authors' in dic['abstracts-retrieval-response'] and dic['abstracts-retrieval-response']['authors'] is not None:
      if 'author' in dic['abstracts-retrieval-response']['authors']:
        if isinstance(dic['abstracts-retrieval-response']['authors']['author'], list):
            for item in dic['abstracts-retrieval-response']['authors']['author']:
                # print item
                author = getAuthorInfofromXML(item)
                # if dic2["firstname"].lower()==author["lastname"].lower() and dic2["lastname"].lower()==author["firstname"].lower() or (dic2["firstname"].lower()==author["firstname"].lower() and dic2["lastname"].lower()==author["lastname"].lower()):
                if dic2["firstname"].lower() in author["lastname"].lower().split(" ") and dic2["lastname"].lower() in author["firstname"].lower().split(" ") or (dic2["firstname"].lower() in author["firstname"].lower().split(" ") and dic2["lastname"].lower() in author["lastname"].lower().split(" ")):
                # authorList.append(author)
                    authors=author
                    # print author
                    authors["affiliation"] = authors["affiliation"][0] if authors["affiliation"] != [] else ""
                    break
                else:
                    authors={}
        elif isinstance(dic['abstracts-retrieval-response']['authors']['author'], dict):
            item = dic['abstracts-retrieval-response']['authors']['author']
            author = getAuthorInfofromXML(item)
            if dic2["firstname"].lower() in author["lastname"].lower().split(" ") and dic2["lastname"].lower() in \
                    author["firstname"].lower().split(" ") or (
                    dic2["firstname"].lower() in author["firstname"].lower().split(" ") and dic2["lastname"].lower() in
                author["lastname"].lower().split(" ")):
            # if dic2["firstname"].lower() == author["lastname"].lower() and dic2["lastname"].lower()==author["firstname"].lower() or (dic2["firstname"].lower()==author["firstname"].lower() and dic2["lastname"].lower()==author["lastname"].lower()):
                authors = author
                authors["affiliation"]=authors["affiliation"][0]if authors["affiliation"] != [] else ""
            else:
                authors={}
            # authorList.append(author)
    if not authors:
        return {},{}
    # process affilInfo
    if 'affiliation' in dic['abstracts-retrieval-response']:
        if isinstance(dic['abstracts-retrieval-response']['affiliation'], list):
            for item in dic['abstracts-retrieval-response']['affiliation']:
                # print item
                affil = getAffilInfofromXML(item)
                # print affil
                if authors["affiliation"]==affil["id"][0]:
                    affils=affil
        elif isinstance(dic['abstracts-retrieval-response']['affiliation'], dict):
            item = dic['abstracts-retrieval-response']['affiliation']
            affil = getAffilInfofromXML(item)
            # print affil
            if authors["affiliation"] == affil["id"][0]:
                affils = affil
    return authors,affils

def getAuthorInfofromXML(item):
    author = {}
    author['id'] = item['@auid']
    author['url'] = item['author-url'].replace("'","''")
    author['rank'] = item['@seq']

    author['simname'] = item['ce:indexed-name'] if 'ce:indexed-name' in item else item['preferred-name']['ce:indexed-name']  # Bai Y.
    author['simname'] = author['simname'].replace("'", "''") if author['simname'] is not None else ""

    author['firstname'] = item['ce:surname'] if 'ce:surname' in item else item['preferred-name']['ce:surname'] # Bai
    author['firstname'] = author['firstname'].replace("'", "''") if author['firstname'] is not None else ""

    author['lastname'] = item['ce:given-name'] if 'ce:given-name' in item else item['preferred-name']['ce:given-name'] # Yang
    author['lastname'] = author['lastname'].replace("'", "''") if author['lastname'] is not None else ""

    author['simlastname'] = item['ce:initials'] if 'initials' in item else item['preferred-name']['ce:initials'] # Y.
    author['simlastname'] = author['simlastname'].replace("'", "''") if author['simlastname'] is not None else ""

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

def getAffilInfofromXML(item):
    affil = {}
    affil['id'] = item['@id']
    affil['url'] = item['@href'].replace("'","''")
    affil['name'] = item['affilname'].replace("'","''") if item['affilname'] is not None else ""

    affil['city'] = item['affiliation-city'] if item['affiliation-city'] is not None else ""
    affil['city'] = affil['city'].replace("'","''")

    affil['country'] = item['affiliation-country'] if item['affiliation-country'] is not None else ""
    affil['country'] = affil['country'].replace("'", "''")

    return affil

def updateSql(author,afil,pid):
    server = dbIO()
    sql = "select * from authorlist where aid='%s'" % (author["id"])
    if server.count(sql)<=0:
        if not afil:
            affiliation=""
        else:
            affiliation=author["affiliation"]
        sql="insert into authorlist (aid,url,fullname,simname,firstname,lastname,simlastname,articlelist,affillist) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (author["id"], author["url"], author["fullname"],author["simname"],author["firstname"],author["lastname"],author["simlastname"],pid,affiliation)
        # print sql
        server.save(sql)
        if afil:
            sql = "select * from affillist where afid='%s'" % (afil["id"])
            if server.count(sql) <= 0:
                sql = "insert into affillist (afid,name,city,country,url) values ('%s','%s','%s','%s','%s')" % (afil["id"], afil["name"], afil["city"], afil["country"], afil["url"])
                server.save(sql)

def findArticle(dict):
    authorList=[]
    dictsupply={}
    pid=dict["id"]
    # print ('dict',dict)
    authorList=getAuthorlist(pid)
    affillist=authoraffil(authorList)
    # print(authorList)
    dictsupply["title"] = dict["title"]
    dictsupply["keywords"] = dict["keyPhrases"]
    dictsupply["abstract"] = dict["paperAbstract"]
    dictsupply["journalName"] =dict["venue"]
    if "year" in dict and not dict["year"]=="":
        dictsupply["date"] = dict["year"] + '-01-01'
    else:
        dictsupply["date"]=""
    dictsupply["citation"] = dict["citations"]
    dictsupply["doi"] =dict["doi"]
    dictsupply["sid"] =dict["id"]
    dictsupply["authorlist"] =authorList
    dictsupply["affillist"] = affillist
    dictsupply["articleType"] = ""
    dictsupply["abstractLang"] = "eng"
    addArticle(dictsupply)

def authoraffil(authorlist):
    server = dbIO()
    affillist=[]
    for aid in authorlist:
        sql = "select affillist from authorlist where aid='%s'"%(aid)
        datarows=server.load(sql)
        for row in datarows:
            affillist.append(row[0])
    return affillist
def getAuthorlist(pid):
    server = dbIO()
    authorlist = []
    sql = "select aid from authorlist where articlelist='%s'" % (pid)
    datarows = server.load(sql)
    for row in datarows:
        authorlist.append(row[0])
    return authorlist

def addArticle(dict):
      authors=""
      authorlist= dict["authorlist"]
      for author in authorlist:
          authors+=author+"|"
      # print (authors[:-1])
      keywords=""
      keywordlist=dict["keywords"]
      for keyword in keywords:
          keywords+=keyword+"|"
      affils = ""
      affillist = dict["affillist"]
      for affil in affillist:
          affils += affil + "|"
      # print (affils[:-1])
# add in datebase
      server = dbIO()
      sql = "select * from articlelist where sid='%s'" % (dict["sid"])
      if server.count(sql) <= 0:
          sql="insert into articlelist(sid,doi,authorlist,affillist,title,abstract,keywords,date,journalName,articletype,abstractLang,citation)values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%d')" % (dict["sid"],dict["doi"],authors[:-1],affils[:-1],dict["title"].replace("'", "''"),dict["abstract"].replace("'", "''").replace("\n\n\n", " |").replace("\n", "| "),keywords[:-1].replace("'", "''"),dict["date"],dict["journalName"],dict["articleType"],dict["abstractLang"],dict["citation"])
          server.save(sql)
          sql="select flag from searchlist2 where title='%s'" %(dict["title"].replace("'","''"))
          # print (dict["title"],server.load(sql))
          server.load(sql)
          flag=server.load(sql)[0][0]
          if flag==0:
              sql="update searchlist2 set flag=3 where title='%s'" %(dict["title"].replace("'","''"))
              server.save(sql)

def getTittle():
    server=dbIO()
    sql="select title,flag from searchlist2 where sid=''"
    return server.load(sql)
def supplyData():
    datarows = getTittle()
    for row in datarows:
        title, flag = row
        print(title, flag)
        if flag:
            continue
        m = getJsonDict(title)
        if not m:
            continue
        else:
            for author in m["authors"]:
                authorGetRes(author["name"],author["ids"][0])
            findArticle(m)
if __name__ == "__main__":
   supplyData()

