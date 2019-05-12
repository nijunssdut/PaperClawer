from taskManage import getTasks
from scopusSearch import searchArticlesByQuery, getTotalNumFromSearchAPI


def getKeyQuery(key):
    """
    :param key: Scopus输入高级检索内容
    :return: 要求摘要、标题、关键词任一具有该内容的检索命令
    """
    return '(abs(%s) or title(%s) or key(%s))' % (key, key, key)

if __name__ == '__main__':
    key = "artificial intelligence"
    base_query = getKeyQuery(key)
    taskList = getTasks(key)
    print("Keyword: artificial intelligence ", "taskNum:", len(taskList))
    for task in taskList:
        taskQuery = base_query + " and "+task[1]
        print(task[0], taskQuery)
        # totalNum = getTotalNumFromSearchAPI(taskQuery)
        # print(totalNum,task[0])
        searchArticlesByQuery(taskQuery, task[0])
