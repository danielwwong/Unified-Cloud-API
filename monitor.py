import custom_api
import time
import threading


class Monitor(object):
    def __init__(self):
        # three flags to indicate whether it is able to access certain platform
        self.googleOn = True
        self.azureOn = True
        self.awsOn = True

        # three flags for the purpose of easy mock network block
        self.blockGoogle = False
        self.blockAzure = False
        self.blockAWS = False

    # communicate with a platform to check connection and change flags
    def connection_test(self, platform, delay, times):
        start_time = time.time()
        count = 0
        if platform == "google":
            while count < times:
                count += 1
                if self.blockGoogle:
                    self.googleOn = False
                    print("Google Cloud connect fail...")
                    time.sleep(delay - ((time.time() - start_time) % delay))
                    continue
                try:
                    custom_api.list_bucket(None, 'on', 'off', 'off')
                    self.googleOn = True
                    print("Google Cloud connect success...")
                except Exception as e:
                    self.googleOn = False
                    print "Google Cloud connect fail" + str(count)
                time.sleep(delay - ((time.time() - start_time) % delay))
        if platform == "azure":
            while count < times:
                count += 1
                if self.blockAzure:
                    self.azureOn = False
                    print("Azure connect fail...")
                    time.sleep(delay - ((time.time() - start_time) % delay))
                    continue
                try:
                    custom_api.list_bucket(None, 'off', 'on', 'off')
                    self.azureOn = True
                    print("Azure connect success...")
                except Exception as e:
                    self.azureOn = False
                    print "Azure connect fail" + str(count)
                time.sleep(delay - ((time.time() - start_time) % delay))
        if platform == "AWS":
            while count < times:
                count += 1
                if self.blockAWS:
                    self.awsOn = False
                    print("AWS connect fail...")
                    time.sleep(delay - ((time.time() - start_time) % delay))
                    continue
                try:
                    custom_api.list_bucket(None, 'off', 'off', 'on')
                    self.awsOn = True
                    print("AWS connect success...")
                except Exception as e:
                    self.awsOn = False
                    print "AWS connect fail" + str(count)
                time.sleep(delay - ((time.time() - start_time) % delay))

    def manual_block(self, platform):
        if "google" in platform:
            self.blockGoogle = True
            self.connection_test("google", 1, 1)
        if "azure" in platform:
            self.blockAzure = True
            self.connection_test("azure", 1, 1)
        if "aws" in platform:
            self.blockAWS = True
            self.connection_test("AWS", 1, 1)

    def manual_unblock(self, platform):
        if "google" in platform:
            self.blockGoogle = False
            self.connection_test("google", 1, 1)
        if "azure" in platform:
            self.blockAzure = False
            self.connection_test("azure", 1, 1)
        if "aws" in platform:
            self.blockAWS = False
            self.connection_test("AWS", 1, 1)

    def start_regular_monitor(self):
        t_google = threading.Thread(target=self.connection_test, args=('google', 30, 60), name="Monitor_GoogleCloud")
        t_azure = threading.Thread(target=self.connection_test, args=('azure', 30, 60), name="Monitor_Azure")
        t_aws = threading.Thread(target=self.connection_test, args=('AWS', 30, 60), name="Monitor_AWS")
        t_google.daemon = True
        t_google.start()
        print "Start monitor Google Cloud..."
        t_azure.daemon = True
        t_azure.start()
        print "Start monitor Azure..."
        t_aws.daemon = True
        t_aws.start()
        print "Start monitor AWS..."
