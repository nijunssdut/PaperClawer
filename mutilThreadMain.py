# -*- coding:utf-8 -*-
import logging
import time
import threading
import _thread
from scopusWholeInfo import getInfofromAbstractAPI, saveWholeArticletoDB
from databaseIO import dbIO
from checkKeys import checkScopusKeyIndex
import Settings

waitingTime = 50
searchNum = 20
restartNum = 3

control_flag = 0
global onceSum
global onceSuccess


class mainThread(threading.Thread):  # The timer class is derived from the class threading.Thread
    
    def __init__(self):  
        threading.Thread.__init__(self)               
        self.thread_stop = False 
        self.restart = 0
        
    def run(self):  # Overwrite run() method, put what you want the thread do here
        while self.thread_stop is False:
            num = main(self)
            counter = 0
            if num != 0:
               while control_flag == 1 and counter < waitingTime:
                    time.sleep(1)
                    counter += 1
            else:
                time.sleep(waitingTime)
                self.restart += 1
                if self.restart >= restartNum:
                    self.thread_stop = True
            # before the restart
            time.sleep(2)
          
    def stop(self):  
        self.thread_stop = True  


class singleThread(threading.Thread):  # The timer class is derived from the class threading.Thread
    """
    每一个线程对论文的处理 run()
    """
    def __init__(self, id, keyIndex):
        threading.Thread.__init__(self)  
        self.id = id
        self.keyIndex = keyIndex
        self.thread_stop = False
        
    def run(self):  # Overwrite run() method, put what you want the thread do here
        result = singlePaperRun(self.id, self.keyIndex)
        self.result = result
        self.thread_stop = True  
           
    def stop(self):  
        self.thread_stop = True  


def appControl():
    """
    入口函数，记录执行时间，创建mainThread对象
    :return:
    """
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    print("Work start %s" % time.strftime(ISOTIMEFORMAT, time.localtime()))
    # for i in range(1, len(sys.argv)):
    #   print "argv:", i, sys.argv[i] 
    mThread = mainThread()
    mThread.start()
    while mThread.thread_stop is False:
       continue
    print("Work completed! %s" % time.strftime(ISOTIMEFORMAT, time.localtime()))
    exit()


def main(mThread):
    """
    构建Scopus ID对应的线程池，其中线程的个数由searchNum决定，不断停止与启动其中线程资源，在mainThread对象中run调用开启多线程
    :param mThread: 当前线程
    :return: 已有scopus ID的未更新数据的条数
    """
        
    global onceSum, onceSuccess, control_flag
    onceSum = 0
    onceSuccess = 0

    # 计数并查询searchNum条更新的Scupus库中数据信息的论文信息
    sql = r"""select id,sid from searchlist where flag = 0 and sid != '' order by rand()
          limit 0,%d;""" % searchNum
    
    threadList = []
    server = dbIO()
    onceSum = server.count(sql)

    keyIndex = checkScopusKeyIndex()
    print("Available Key Index:", keyIndex, " Rent Keys:", len(Settings.apikeyList) - keyIndex)
    
    ISOTIMEFORMAT = '%X'
    print("Get %s Papers Into Cawler %s" % (onceSum, time.strftime(ISOTIMEFORMAT, time.localtime())))
           
    if onceSum > 0:
        # control thread working
        control_flag = 1
        maxID = '0'
        minID = '0'

        for row in server.load(sql):
            threadList.append(singleThread(row[1], keyIndex))
            if minID == '0':
                minID = row[0]
        maxID = row[0]
        _thread.start_new_thread(checkThreadActive, (threadList, mThread))
        for single in threadList:
            single.start()
            time.sleep(0.25)

        print("Threads %s-%s Running" % (minID, maxID))
    return onceSum


def checkThreadActive(threadList, mThread):
    """
    :param threadList: 线程列表
    :param mThread: 当前线程
    :return:检查线程活跃情况，从线程列表中移除停止的线程，以及停止线程
    """
    start = time.clock()
    global control_flag 
    while len(threadList) > 0 and time.clock()-start < waitingTime:
        for single in threadList:
            if single.thread_stop:
                threadList.remove(single)
    for single in threadList:
        single.stop()

    print("All Thread Over,Waiting,Success %d, Wrong %d" % (onceSuccess, onceSum-onceSuccess))
    print("---------------------------")
    control_flag = 0
    _thread.exit_thread()
    

def singlePaperRun(paperID, keyIndex):
    """
    每篇论文的处理，对应于一个singleThread对象
    :param paperID: 论文ID
    :param keyIndex:
    :return:  异常或没有信息返回，则返回0，更新论文信息并更新列表（searchlist）的flag =1，返回1
    """
    try:
        global onceSuccess
        start = time.clock()
        server = dbIO()
        infodict, authorList, affilList = getInfofromAbstractAPI(paperID, keyIndex)
        if infodict is []:
            return 0
        flag = saveWholeArticletoDB(infodict, authorList, affilList)
        if flag == 1:
            sql = "select id from searchlist where sid = " + paperID
            sql = "update searchlist set flag = 1 where id = " + str(server.load(sql)[0][0])
            server.save(sql)
        end = time.clock()
        onceSuccess = onceSuccess + 1
        print("Thread%s:Finished_CostTime:%d" % (paperID, (end - start)))
        return 1
    except ConnectionResetError as e:
        print("wrongThread%s:%s" % (paperID, str(e)))
        return 0

if __name__ == "__main__":
    appControl()
