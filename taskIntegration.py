import Settings

maxSearchNum = Settings.maxSearchNum

def loadTaskfromFile(filename):
    taskList = []
    f = open(filename, "r")
    for line in f.readlines():
        taskList.append(line.replace("\n","").split("\t"))
    f.close()
    return taskList

def computeGroupSum(list):
    total = 0
    for item in list:
        total += item[1]
    return total

def findMinIndexMoreThanTarget(valuelist,target):
    minSub = maxSearchNum - target
    minIndex = -1
    for i in range(0,len(valuelist)):
        if valuelist[i] > target and valuelist[i] - target < minSub:
             minSub = valuelist[i] - target
             minIndex = i
    return minIndex

def findMaxIndexLessThanTarget(valuelist,target):
    minSub = target
    minIndex = -1
    for i in range(0,len(valuelist)):
        if valuelist[i] < target and target - valuelist[i] < minSub:
             minSub = target - valuelist[i]
             minIndex = i
    return minIndex

#reduce task num
def taskIntegration(groupList):
    while True:   # find > 2500 least gap and find biggest stone to fill
        valueList = [computeGroupSum(group) for group in groupList]
        #print(len(valueList), valueList)
        selectIndex = findMinIndexMoreThanTarget(valueList,maxSearchNum/2)
        if selectIndex == -1:break
        #print(selectIndex, valueList[selectIndex])
        subIndex = findMaxIndexLessThanTarget(valueList,maxSearchNum-valueList[selectIndex])
        if subIndex == -1: break
        #print(subIndex, valueList[subIndex])
        #print([valueList[selectIndex], valueList[subIndex]])
        if selectIndex == subIndex:
            break
        if valueList[selectIndex] + valueList[subIndex] > maxSearchNum:
            break
        groupList[selectIndex].extend(groupList[subIndex])
        #print(selectIndex,subIndex)
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
        #print(id1, id2)
        valueList = [computeGroupSum(group) for group in groupList]
        #print(len(valueList),valueList)

    return groupList

#main function
def getTaskQueryList(taskList):

    groupList = [[[i, int(taskList[i][1]), taskList[i][2]]] for i in range(0, len(taskList))]

    groupList = taskIntegration(groupList)
    totalNum = []
    for group in groupList:
        totalNum.extend([item[0] for item in group])
    totalNum.sort()
    #print(len(groupList), len(totalNum))
    queryList = []
    for group in groupList:
        singleQuery = "(" + group[0][2] + ")"
        groupTotal = group[0][1]
        for item in group[1:]:
            groupTotal += item[1]
            singleQuery += " OR (" + item[2] + ")"
        queryList.append([groupTotal, "(" + singleQuery + ")"])
    return queryList

if __name__ == "__main__":
    taskList = loadTaskfromFile("saveTask.txt")
    "taskList dataformat: id, searchNum, query"
    queryList = getTaskQueryList(taskList)
    for item in queryList:
        print(item)







