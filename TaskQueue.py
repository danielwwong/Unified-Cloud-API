import threading
import Queue
import time
import custom_api
import random
import shared

class TaskQueue(Queue.Queue):
    def __init__(self, size, platform, num_workers=1 ):
        Queue.Queue.__init__(self, size)
        self.num_workers = num_workers
        self.start_workers()
        self.platform = platform

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
            print("thread%d %s: waiting for task" % (self.ident, self.name))
            try:
                task = q.get(block=True, timeout=20)  # receive msg
                result = self.execute(task)
            
                print("work finished!")
                shared.upload_info.append(result)
                q.task_done()  # finish
                res = q.qsize()  # size
                if res > 0:
                    print("There are still %d tasks to do" % (res))
            except Queue.Empty:
#                print("Queue empty!")
#                time.sleep(10)
                # self.thread_stop = True
                pass
            # print("task recv:%s ,task No:%d" % (task[0], task[1]))



    # suppose the interfaces are backup_file_path, filename, platform, upload_container
    # [google_upload_bucket, azure_upload_container, aws_upload_bucket]
    def execute(self, task): #
        mission = task["mission"]
        print mission

        platform = self.queue.platform  # = task["platform"]
        result = ""
        if mission == "upload" :
            result = custom_api.upload_object(task["path"], task["file_name"],platform , task["bucket"])
        elif  mission == "delete":
            result = custom_api.upload_object(task["path"], task["file_name"],platform , task["bucket"])
        elif mission == "download": 
            result = custom_api.upload_object(task["path"], task["file_name"],platform , task["bucket"])
        return result


    def stop(self):
        self.thread_stop = True

# class maker():
#     def __init__(self):
#         self.maxID = 1

#     def createMission( self, mission, path, filename, platform, bucket):
#         self.maxID += 1
#         task = {"id":self.maxID, "mission":mission, "path":path, "file_name":filename, "time_stamp":time.time(),"platform":platform, "bucket": bucket }
#         return task

# if __name__ == "__main__":
#     q = TaskQueue(-1,platform="Google",num_workers = 3)
#     # for i in range(3):
#     #     worker_t = worker(q)
#     #     worker_t.start()
#     maker = maker()

#     m_list = ["uplaod","download","delete"]
#     p_list = ["google","amazon","azure"]
#     path_list = [".//f:", "e:backup", "cd:could up"]
#     b_list = ["bucket_1", "bucket_2", "bucket_3"]

#     for i in range(3):
#         q.put(maker.createMission(m_list[ random.randint(0, 2) ],path_list[random.randint(0, 2)], str(i)+".png" ,p_list[random.randint(0, 2)],b_list[random.randint(0, 2)]), block=True, timeout=None)
#         q.put(maker.createMission(m_list[random.randint(0, 2)], path_list[random.randint(0, 2)], str(i) + ".png",
#                                   p_list[random.randint(0, 2)], b_list[random.randint(0, 2)]), block=True, timeout=None)
#         q.put(maker.createMission(m_list[random.randint(0, 2)], path_list[random.randint(0, 2)], str(i) + ".png",
#                                   p_list[random.randint(0, 2)], b_list[random.randint(0, 2)]), block=True, timeout=None)

#     print("***************leader:wait for finish!")
#     q.join()  # wait for finishing
#     print("***************leader:all task finished!")
