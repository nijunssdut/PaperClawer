from taskAssign import buildOriginTask
from taskIntegration import getTaskQueryList, loadTaskfromFile
from databaseIO import dbIO


def saveTaskList(taskList,key):
    dbIOserver = dbIO()
    insertNum = 0
    for task in taskList:
        sql = "select * from tasklist where query = '" + task[1] + "'"
        if dbIOserver.count(sql) == 0:
            sql = "INSERT INTO tasklist (keyword,query,totalNum,taskType) VALUES ('" + key + "','" + task[1] + "','" + str(task[0]) + "','test')"
            if dbIOserver.save(sql) > 0:
                insertNum += 1
    return insertNum


def loadTaskList(key):
    dbIOserver = dbIO()
    sql = "select id, totalNum, query from tasklist where keyword = '" + key + "' and flag != 1"
    data = dbIOserver.load(sql)
    taskList = [[int(item[0]),item[2]] for item in data]
    return taskList


def getTasks(key):
    dbIOserver = dbIO()
    sql = "SELECT * FROM tasklist where keyword = '" + key + "'"
    # print(sql)
    taskList = []
    if dbIOserver.count(sql) <= 0:
        queryList = buildOriginTask(key)
        taskList = getTaskQueryList(queryList)
        saveTaskList(taskList,key)
    else:
        taskList = loadTaskList(key)
    return taskList

if __name__ == '__main__':
    key = "artificial intelligence"
    taskList = getTasks(key)
    for task in taskList:
        print(task)
