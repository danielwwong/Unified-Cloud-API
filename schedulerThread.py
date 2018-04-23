import threading
import time


class writeThread(threading.Thread):
    def __init__(self, threadID, name, counter, main):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.main = main

    def run(self):
        print
        "Starting " + self.name
        while True:
            self.main.queueLock.acquire()
            # print(self.name + self.counter)
            self.main.createMissionTest()
            # 释放锁

            self.main.queueLock.release()
            time.sleep(5)


class readThread(threading.Thread):
    def __init__(self, threadID, name, counter, main):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print
        "Starting " + self.name
        while True:
            self.main.queueLock.acquire()
            self.main.redoMission()
            #             print(self.name + self.counter)
            # 释放锁
            self.main.queueLock.release()
            time.sleep(5)


class backupThread(threading.Thread):
    def __init__(self, threadID, name, counter, main):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        print
        "backup " + self.name + " created"

    def run(self):
        print
        "backup " + self.name
        backUpNeeded = False
        while True:
            if backUpNeeded == False:
                time.sleep(1)
            backUpNeeded = True
            while backUpNeeded == True:
                self.main.queueLock.acquire()
                print
                "back up to file"
                self.main.toFile()
                backUpNeeded = False
                #             print(self.name + self.counter)
                # 释放锁
                self.main.queueLock.release()
                time.sleep(0.1)