from TaskQueue import TaskQueue
import threading
import time
# import random
from  monitor import Monitor

class scheduler():
    def __init__(self, num_workers=3):
        self.monitor = Monitor()
        self.google_queue = TaskQueue(-1,"Google", self.monitor, num_workers=num_workers)
        self.azure_queue = TaskQueue(-1,"Azure", self.monitor, num_workers=num_workers)
        self.amazon_queue = TaskQueue(-1,"Amazon", self.monitor, num_workers=num_workers)
        self.maxID = 1


    def push_task(self, task):
        # when certain platform is down, its queue size will be set as bif value to deny enqueue
        if self.monitor.googleOn:
            g_size = self.google_queue.qsize()
        else:
            g_size = 100000
        if self.monitor.azureOn:
            m_size = self.azure_queue.qsize()
        else:
            m_size = 100000
        if self.monitor.awsOn:
            a_size = self.amazon_queue.qsize()
        else:
            a_size = 100000
        if g_size < m_size and g_size < a_size:
            task["platform"] = "Google"
            self.google_queue.put(task)
            print("choose google")
        elif m_size < a_size:
            task["platform"] = "Azure"
            self.azure_queue.put(task)
            print("choose azure")
        else:
            task["platform"] = "AWS"
            self.amazon_queue.put(task)
            print "choose aws"


    def task2Json(self, mission, path, filename, bucket):
        self.maxID += 1
        task = {"id": self.maxID, "mission": mission, "path": path, "file_name": filename, "time_stamp": time.time(),"platform": " ", "bucket": bucket}
        return task

    def input(self, mission, path, filename, bucket_name):
        if self.maxID == 1:
            self.monitor.connection_test("google", 3, 1)
            self.monitor.connection_test("azure", 3, 1)
            self.monitor.connection_test("AWS", 3, 1)
            self.monitor.start_regular_monitor()
        if self.monitor.googleOn | self.monitor.azureOn | self.monitor.awsOn:
            print "some one work"
        else:
            print "noe one work"
        self.push_task(self.task2Json(mission, path, filename, bucket_name))

# m_list = ["uplaod","download","delete"]
# p_list = ["google","amazon","azure"]
# path_list = [".//f:", "e:backup", "cd:could up"]
# b_list = ["bucket_1", "bucket_2", "bucket_3"]
#
# s = scheduler()
#
# for i in range(3):
#     s.push_task(s.task2Json(m_list[ random.randint(0, 2) ],path_list[random.randint(0, 2)],
#                                   str(i)+".png" ,p_list[random.randint(0, 2)],b_list[random.randint(0, 2)]), block=True, timeout=None)
#     s.push_task(s.task2Json(m_list[ random.randint(0, 2) ],path_list[random.randint(0, 2)],
#                                   str(i)+".png" ,p_list[random.randint(0, 2)],b_list[random.randint(0, 2)]), block=True, timeout=None)
#     s.push_task(s.task2Json(m_list[ random.randint(0, 2) ],path_list[random.randint(0, 2)],
#                                   str(i)+".png" ,p_list[random.randint(0, 2)],b_list[random.randint(0, 2)]), block=True, timeout=None)
#
# print("***************leader:wait for finish!")
# # q.join()  # wait for finishing
# print("***************leader:all task finished!")
