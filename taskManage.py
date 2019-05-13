from taskAssign import buildOriginTask
from taskIntegration import getTaskQueryList, loadTaskfromFile
from databaseIO import dbIO


def saveTaskList(taskList, key):
    """
    :param taskList: [任务数量，Scopus高级子命令]，getTaskQueryList计算获得
    :param key: 关键词（例如人工智能）
    :return: 保存到数据库的任务列表的数目
    """
    dbIOserver = dbIO()
    insertNum = 0
    for task in taskList:
        sql = "select * from tasklist where query = '" + task[1] + "'"
        if dbIOserver.count(sql) == 0:
            sql = "INSERT INTO tasklist (keyword,query,totalNum,taskType) VALUES " \
                  "('" + key + "','" + task[1] + "','" + str(task[0]) + "','test')"
            if dbIOserver.save(sql) > 0:
                insertNum += 1
    return insertNum


def loadTaskList(key):
    """
    :param key: 关键词
    :return: 查询未被处理的任务对应列表
    """
    dbIOserver = dbIO()
    sql = "select id, totalNum, query from tasklist where keyword = '" + key + "' and flag != 1"
    data = dbIOserver.load(sql)
    taskList = [[int(item[0]), item[2]] for item in data]
    return taskList


def getTasks(key):
    """
    入口函数
    :param key:关键词
    :return: 没有关键词对应的任务，则获取依关键词查找的全部子命令，并存成任务列表到数据库，有对应任务则查看，返回任务列表
    """
    dbIOserver = dbIO()
    sql = "SELECT * FROM tasklist where keyword = '" + key + "'"
    # print(sql)
    taskList = []
    if dbIOserver.count(sql) <= 0:
        queryList = buildOriginTask(key)
        taskList = getTaskQueryList(queryList)
        saveTaskList(taskList, key)
    else:
        taskList = loadTaskList(key)
    return taskList

if __name__ == '__main__':
    key = "artificial intelligence"
    taskList = getTasks(key)
    for task in taskList:
        print(task)
