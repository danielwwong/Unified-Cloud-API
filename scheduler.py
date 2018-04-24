from TaskQueue import TaskQueue
import threading
import time
import custom_api
# import random

class scheduler():
    def __init__(self, num_workers=1):
        self.google_queue = TaskQueue(-1,"Google",num_workers=num_workers)
        self.azure_queue = TaskQueue(-1,"Azure",num_workers=num_workers)
        self.amazon_queue = TaskQueue(-1,"Amazon",num_workers=num_workers)
        self.maxID = 1

    def push_task(self, task):
        g_size = self.google_queue.qsize()
        m_size = self.azure_queue.qsize()
        a_size = self.amazon_queue.qsize()
        print "push"
        print str(g_size) + " " + str(m_size) + " " + str(a_size) + " "
        if (g_size < m_size and g_size < a_size):
            print "in Google"
            task["platform"] = "Google"
            self.google_queue.put(task)
        # elif m_size <= a_size and m_size <= g_size:
        elif m_size < a_size:
            print "in Azure"
            task["platform"] = "Azure"
            self.azure_queue.put(task)
        else:
            print "in AWS"
            task["platform"] = "AWS"
            self.amazon_queue.put(task)


    def task2Json(self, mission, path, filename, platform, bucket):
        self.maxID += 1
        task = {"id": self.maxID, "mission": mission, "path": path, "file_name": filename, "time_stamp": time.time(),"platform": platform, "bucket": bucket}
        return task

    def input(self, mission, path, filename, platform, bucket_name):
        self.push_task(self.task2Json(mission, path, filename, platform, bucket_name))


