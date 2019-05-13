import Settings

maxSearchNum = Settings.maxSearchNum


def loadTaskfromFile(filename):
    """
    :param filename: Scopus高级检索命令集合文件
    :return:任务列表 【序号，任务总数，子命令】
    """
    taskList = []
    f = open(filename, "r")
    for line in f.readlines():
        taskList.append(line.replace("\n", "").split("\t"))
    f.close()
    return taskList


def computeGroupSum(list):
    """
    :param list:[[序号，任务数量，子命令]]
    :return: 计算一组的总任务数
    """
    total = 0
    for item in list:
        total += item[1]
    return total


def findMinIndexMoreThanTarget(valuelist, target):
    """
    :param valuelist: 每个子命令任务数量列表
    :param target: 目标任务总数
    :return: 找到索引 （下一组的起始位置，即最小超过任务总数量的位置索引）
    """
    minSub = maxSearchNum - target  # minSub余下任务数量
    minIndex = -1
    for i in range(0, len(valuelist)):
        if valuelist[i] > target and valuelist[i] - target < minSub:
             minSub = valuelist[i] - target
             minIndex = i
    return minIndex


def findMaxIndexLessThanTarget(valuelist, target):
    """
    :param valuelist: 每个子命令任务数量列表
    :param target: 目标任务总数
    :return: 找到索引（最大任务总数量小于目标任务总数量）
    """
    minSub = target  # minSub余下任务数量
    minIndex = -1
    for i in range(0, len(valuelist)):
        if valuelist[i] < target and target - valuelist[i] < minSub:
             minSub = target - valuelist[i]
             minIndex = i
    return minIndex


def taskIntegration(groupList):
    """
    :param groupList: [[[序号，任务数量，子命令]]]
    :return: 整合任务，减少任务数量，对于命令如果任务数量家和小于maxSearchNum/2，将命令合成一个
    """
    while True:   # find > 2500 least gap and find biggest stone to fill
        valueList = [computeGroupSum(group) for group in groupList]
        # print(len(valueList), valueList)
        selectIndex = findMinIndexMoreThanTarget(valueList, maxSearchNum/2)
        if selectIndex == -1: break
        # print(selectIndex, valueList[selectIndex])
        subIndex = findMaxIndexLessThanTarget(valueList, maxSearchNum-valueList[selectIndex])
        if subIndex == -1: break
        # print(subIndex, valueList[subIndex])
        # print([valueList[selectIndex], valueList[subIndex]])
        if selectIndex == subIndex:
            break
        if valueList[selectIndex] + valueList[subIndex] > maxSearchNum:
            break
        groupList[selectIndex].extend(groupList[subIndex])
        # print(selectIndex,subIndex)
        groupList.pop(subIndex)

    while True:  # find two least group to add
        repeat = valueList[:]
        repeat.sort()
        id1 = valueList.index(repeat[0])
        id2 = valueList.index(repeat[1])
        if id1 == id2:
            id2 = valueList[id1:].index(repeat[1])+id1+1
        if valueList[id1] + valueList[id2] > maxSearchNum:
            break
        groupList[id1].extend(groupList[id2])
        groupList.pop(id2)
        # print(id1, id2)
        valueList = [computeGroupSum(group) for group in groupList]
        # print(len(valueList),valueList)

    return groupList


def getTaskQueryList(taskList):
    """
    :param taskList: [[序号，任务数量，子命令]]
    :return: 入口函数
    """
    groupList = [[[i, int(taskList[i][1]), taskList[i][2]]] for i in range(0, len(taskList))]
    # print(groupList)
    groupList = taskIntegration(groupList)
    totalNum = []
    for group in groupList:
        totalNum.extend([item1[0] for item1 in group])
    totalNum.sort()
    # print(len(groupList), len(totalNum))
    # 合并子命令与任务数
    queryList = []
    for group in groupList:
        singleQuery = "(" + group[0][2] + ")"
        groupTotal = group[0][1]
        for item2 in group[1:]:
            groupTotal += item2[1]
            singleQuery += " OR (" + item2[2] + ")"
        queryList.append([groupTotal, "(" + singleQuery + ")"])
    return queryList

if __name__ == "__main__":

    taskList = loadTaskfromFile("saveTask.txt")
    "taskList data_format: id, searchNum, query"
    queryList = getTaskQueryList(taskList)
    for item in queryList:
        print(item)







