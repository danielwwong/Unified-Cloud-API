from TaskQueue import TaskQueue
import threading
import time
# import random

class scheduler():
    def __init__(self, num_workers=3):
        self.google_queue = TaskQueue(-1,"Google",num_workers=num_workers)
        self.azure_queue = TaskQueue(-1,"Azure",num_workers=num_workers)
        self.amazon_queue = TaskQueue(-1,"Amazon",num_workers=num_workers)
        self.maxID = 1

    def push_task(self, task):
        g_size = self.google_queue.qsize()
        m_size = self.azure_queue.qsize()
        a_size = self.amazon_queue.qsize()
        if (g_size < m_size and g_size < a_size):
            self.google_queue.put(task)
        elif m_size < a_size:
            self.azure_queue.put(task)
        else:
            self.amazon_queue.put(task)


    def task2Json(self, mission, path, filename, platform, bucket):
        self.maxID += 1
        task = {"id": self.maxID, "mission": mission, "path": path, "file_name": filename, "time_stamp": time.time(),"platform": platform, "bucket": bucket}
        return task

    def input(self, mission, path, filename, platform, bucket_name):
        self.push_task(self.task2Json(mission, path, filename, platform, bucket_name))

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
