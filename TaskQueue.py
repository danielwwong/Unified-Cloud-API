import threading
import Queue
import time
import custom_api
import random
import shared


class TaskQueue(Queue.Queue):
    def __init__(self, size, platform, monitor, num_workers=1):
        Queue.Queue.__init__(self, size)
        self.num_workers = num_workers
        self.start_workers()
        self.platform = platform
        self.monitor = monitor


    def start_workers(self):
        for i in range(self.num_workers):
            t = worker(self)
            t.daemon = True
            t.start()

class worker(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.thread_stop = False

    def run(self):
        q = self.queue
        while 1:
            try:
                task = q.get(block=True, timeout=20)  # receive msg
                result = self.execute(task)
                shared.upload_info.append(result)
                q.task_done()  # finish
                res = q.qsize()  # size
                if res > 0:
                    print("There are still %d tasks to do" % (res))
            except Queue.Empty:
                #                print("Queue empty!")
                #                time.sleep(10)
                # self.thread_stop = True
                continue

    # suppose the interfaces are backup_file_path, filename, platform, upload_container
    # [google_upload_bucket, azure_upload_container, aws_upload_bucket]
    def execute(self, task): #
        mission = task["mission"]
        platform = self.queue.platform  # = task["platform"]
        result = ""
        state = True
        if platform == "Google":
            state = self.queue.monitor.googleOn
            print "Cannot access Google Cloud..."
        elif platform == "Azure":
            state = self.queue.monitor.azureOn
            print "Cannot access Azure..."
            print(state)
        else:
            state = self.queue.monitor.awsOn
            print "Cannot access AWS..."
            print (state)
        if not state:
            # If platform disconnected, these unexcuted tasks in the queue will bu push into rescheduler queue for future execution
            task_info = "Need Reassign"
            result = {"info": task_info, "mission": "upload", "file_name": task["file_name"], "time_stamp": time.time(),"platform": platform, "bucket": task["bucket"]}
            custom_api.wait_list.append(task)
            return result
        print "start execute..."
        if mission == "upload":
            try:
                result = custom_api.upload_object(task["path"], task["file_name"],platform, task["bucket"], task["uploadtime"])
                print("work finished!")
            except:
                task_info = "Need Reassign"
                result = {"info": task_info, "mission": "upload", "file_name": task["file_name"], "time_stamp": time.time(),"platform": platform, "bucket": task["bucket"]}
                custom_api.wait_list.append(task)
        elif  mission == "delete":
            result = custom_api.upload_object(task["path"], task["file_name"],platform , task["bucket"])
        elif mission == "download":
            result = custom_api.upload_object(task["path"], task["file_name"],platform , task["bucket"])
        return result


    def stop(self):
        self.thread_stop = True

