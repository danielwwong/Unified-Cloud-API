from TaskQueue import TaskQueue
import threading
import time
import random
from monitor import Monitor
import custom_api

class scheduler():
    def __init__(self, num_workers=3):
        self.monitor = Monitor()
        self.google_queue = TaskQueue(-1,"Google", self.monitor, num_workers=num_workers)
        self.azure_queue = TaskQueue(-1,"Azure", self.monitor, num_workers=num_workers)
        self.amazon_queue = TaskQueue(-1,"Amazon", self.monitor, num_workers=num_workers)
        self.maxID = 1
        self.start_reassignmet()



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
        if g_size == m_size:
            if m_size == a_size:
                ran = random.randint(0, 2)
            else:
                ran = random.randint(0, 1)
            if ran == 0:
                task["platform"] = "Google"
                self.google_queue.put(task)
                print("choose google")
            elif ran == 1:
                task["platform"] = "Azure"
                self.azure_queue.put(task)
                print("choose azure")
            elif ran == 2:
                task["platform"] = "AWS"
                self.amazon_queue.put(task)
                print "choose aws"
        elif g_size < m_size and g_size < a_size:
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


    def task2Json(self, upload_time, mission, path, filename, bucket):
        self.maxID += 1
        task = {"id": self.maxID, "mission": mission, "path": path, "file_name": filename, "time_stamp": time.time(),"platform": " ", "bucket": bucket, "uploadtime": upload_time}
        return task

    def input(self, mission, upload_time,  path, filename, bucket_name):
        if self.maxID == 1:
            t1 = time.time()
            self.monitor.connection_test("google", 1, 1)
            self.monitor.connection_test("azure", 1, 1)
            self.monitor.connection_test("AWS", 1, 1)
            self.monitor.start_regular_monitor()
            t2 = time.time()
            upload_time = upload_time + (t2 - t1)
        self.push_task(self.task2Json(upload_time, mission, path, filename, bucket_name))

    def reassignment(self):
        start_time = time.time()
        count = 0
        while count < 60:
            count += 1
            try:
                task = custom_api.wait_list.pop(0)
                task["platform"] = "AWS"
                print ("Reassign task %s because of the failure of %s" % (task["id"], task["platform"]))
                self.push_task(task)
                time.sleep(10 - ((time.time() - start_time) % 10))
            except :
                time.sleep(10 - ((time.time() - start_time) % 10))
                continue



    def start_reassignmet(self):
        t_reassign = threading.Thread(target=self.reassignment, name="reassignment")
        t_reassign.daemon = True
        t_reassign.start()

    def test_reassignment(self, mission, upload_time, path, filename, bucket_name):
        task = self.task2Json(upload_time, mission, path, filename, bucket_name)
        self.amazon_queue.put(task)
