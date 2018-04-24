import threading
import Queue
import time
import custom_api
# import random
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
        while not self.thread_stop:
            while not self.thread_stop:
                # print("thread%d %s: waiting for task" % (self.ident, self.name))
                try:
                    task = q.get(block=True, timeout=20)  # receive msg
                except Queue.Empty:
                    time.sleep(0.1)
                    break 


                result = self.excute(task)

                print("work finished!")
                shared.upload_info.append(result)
                q.task_done()  # finish

    # suppose the interfaces are backup_file_path, filename, platform, upload_container
    # [google_upload_bucket, azure_upload_container, aws_upload_bucket]
    def excute(self, task): # 
        mission = task["mission"]
        print mission +"  " +task["file_name"] + " from " + task["path"]
        platform = self.queue.platform  # = task["platform"]
        result = ""
        if mission == "upload" :
                        # Google
            if platform == 'Google':
                custom_api.upload_object_2_Google(task["path"], task["file_name"], platform, task["bucket"][0])
            # Azure
            elif platform == 'Azure':
                custom_api.upload_object_2_Azure(task["path"], task["file_name"], platform, task["bucket"][1])
            # AWS
            else:
                custom_api.upload_object_2_AWS(task["path"], task["file_name"], platform, task["bucket"][2])
            # result = custom_api.upload_object(task["path"], task["file_name"],platform , task["bucket"])
        elif  mission == "delete":
            result = custom_api.upload_object(task["path"], task["file_name"],platform , task["bucket"])
        elif mission == "download": 
            result = custom_api.upload_object(task["path"], task["file_name"],platform , task["bucket"])

        # print "result :  " 
        # print result
        return result


    def stop(self):
        self.thread_stop = True


def upload_object_2_Google(backup_file_path, filename, platform, upload_container):
    google_info = ''
    with open(backup_file_path, 'r') as google_file:
        dst_uri = boto.storage_uri(upload_container + '/' + filename, google_storage)
        dst_uri.new_key().set_contents_from_file(google_file)
    google_info = 'Successfully Uploaded ' + dst_uri.bucket_name + '/' + dst_uri.object_name + ' to Google!'
    google_file.close()
    print google_info
    shared.upload_info.append(google_info)
    task = {"info": google_info, "mission": "upload", "file_name": filename, "time_stamp": time.time(),"platform": platform, "bucket": dst_uri.bucket_name}
    return task


def upload_object_2_Azure(backup_file_path, filename, platform, upload_container):
    azure_info = ''
    azure.create_blob_from_path(upload_container, filename, backup_file_path, content_settings = ContentSettings())
    azure_info = 'Successfully Uploaded ' + upload_container + '/' + filename + ' to Azure!'
    print azure_info
    shared.upload_info.append(azure_info)
    task = {"info": azure_info, "mission": "upload", "file_name": filename, "time_stamp": time.time(),"platform": platform, "bucket": upload_container[1]}
    return task


def upload_object_2_AWS(backup_file_path, filename, platform, upload_container):
    aws_info = ''
    print backup_file_path+" 2 aws " + upload_container
    with open("./"+backup_file_path, 'r') as aws_file:
        print "open"
        print aws_file
        s3.Object(upload_container, filename).put(Body = aws_file)
        s3.Object(upload_container, filename).Acl().put(ACL='public-read')
    aws_info = 'Successfully Uploaded ' + upload_container + '/' + filename + ' to AWS!'
    aws_file.close()
    print aws_info
    shared.upload_info.append(aws_info)
    task = {"info": aws_info, "mission": "upload", "file_name": filename, "time_stamp": time.time(),"platform": platform, "bucket": upload_container[2]}
    return task