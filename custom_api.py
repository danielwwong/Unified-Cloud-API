import boto
import gcs_oauth2_boto_plugin
import os
import StringIO
from azure.storage.blob import BlockBlobService
from azure.storage.blob import PublicAccess
from azure.storage.blob import ContentSettings
from azure.common import AzureHttpError
import boto3
import botocore
import getpass
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import base64

def initialize(google_project_id, azure_account_name, azure_account_key, s3_access_key_id, s3_secret_access_key):
    global google_storage, local_file, google_header_values, azure, s3, s3_client
    # Google
    google_info = ''
    try:
        google_storage = 'gs' # URI scheme for Google Cloud Storage
        local_file = 'file' # URI scheme for accessing local files
        google_header_values = {'x-goog-project-id': google_project_id}
        # test list buckets
        uri = boto.storage_uri('', google_storage)
        uri.get_all_buckets(headers = google_header_values)
        google_info = 'Successfully Initialized Google Cloud Storage!'
    except Exception as g_e:
        google_info = 'Failed to Initialize Google Cloud Storage!</p><p>' + str(g_e)
    # Azure
    azure_info = ''
    try:
        azure = BlockBlobService(account_name = azure_account_name, account_key = azure_account_key)
        # test if account_key is base64
        base64.decodestring(azure_account_key)
        # test list containers
        container_list = azure.list_containers()
        azure_info = 'Successfully Initialized Microsoft Azure!'
    except Exception as m_e:
        azure_info = 'Failed to Initialize Microsoft Azure!</p><p>' + str(m_e)
    # AWS
    aws_info = ''
    try:
        s3 = boto3.resource('s3', aws_access_key_id = s3_access_key_id, aws_secret_access_key = s3_secret_access_key)
        s3_client = boto3.client('s3', aws_access_key_id = s3_access_key_id, aws_secret_access_key = s3_secret_access_key)
        # test list buckets
        s3_client.list_buckets()
        aws_info = 'Successfully Initialized Amazon S3!'
    except Exception as a_e:
        aws_info = 'Failed to Initialize Amazon S3!</p><p>' + str(a_e)
    return google_info, azure_info, aws_info

def create_bucket(google_bucket_name, azure_container_name, aws_bucket_name, google_platform_check, azure_platform_check, aws_platform_check):
    # Google
    google_info = ''
    if google_platform_check == 'on':
        try:
            uri = boto.storage_uri(google_bucket_name, google_storage) # instantiate a BucketStorageUri object
            uri.create_bucket(headers = google_header_values)
            google_info = 'Successfully Created Google Bucket ' + google_bucket_name
        except Exception as g_e:
            google_info = 'Failed to Create Google Bucket: ' + str(g_e)
    # Azure
    azure_info = ''
    if azure_platform_check == 'on':
        try:
            azure.create_container(azure_container_name, public_access = PublicAccess.Container)
            # the second parameter makes the container accessible to public
            azure_info = 'Successfully Created Azure Container ' + azure_container_name
        except Exception as m_e:
            azure_info = 'Failed to Create Azure Container: ' + str(m_e)
    # AWS
    aws_info = ''
    if aws_platform_check == 'on':
        try:
            s3.create_bucket(Bucket = aws_bucket_name)
            # the AWS bucket will be hosted in N. Virginia
            bucket = s3.Bucket(aws_bucket_name)
            bucket.Acl().put(ACL='public-read')
            # make the bucket and blobs public readable
            aws_info = 'Successfully Created AWS Bucket ' + aws_bucket_name
        except Exception as a_e:
            aws_info = 'Failed to Create AWS Bucket: ' + str(a_e)
    return google_info, azure_info, aws_info

def list_bucket(page, google_platform_check, azure_platform_check, aws_platform_check):
    # Google
    if google_platform_check == 'on':
        uri = boto.storage_uri('', google_storage)
        google_bucket_list = uri.get_all_buckets(headers = google_header_values)
        if len(google_bucket_list) == 0:
            google_info = 'No Google Buckets!<br>'
        else:
            if page == 'upload_page':
                google_info = ''
                for bucket in google_bucket_list:
                    google_info = google_info + '<input type="radio" name="google_upload_bucket" id="g_' + str(bucket.name) + '" value="' + str(bucket.name) + '"><label for="g_' + str(bucket.name) + '">' + str(bucket.name) + '</label><br>'
            elif page == 'download_page':
                google_info = []
                for bucket in google_bucket_list:
                    google_info.append(str(bucket.name))
            else:
                google_info = 'Google Buckets:<br>'
                for bucket in google_bucket_list:
                    google_info = google_info + str(bucket.name) + '<br>'
    else:
        google_info = ''
    # Azure
    if azure_platform_check == 'on':
        container_list = azure.list_containers()
        if len(list(container_list)) == 0:
            azure_info = 'No Azure Containers!<br>'
        else:
            if page == 'upload_page':
                azure_info = ''
                for container in container_list:
                    azure_info = azure_info + '<input type="radio" name="azure_upload_container" id="m_' + str(container.name) + '" value="' + str(container.name) + '"><label for="m_' + str(container.name) + '">' + str(container.name) + '</label><br>'
            elif page == 'download_page':
                azure_info = []
                for container in container_list:
                    azure_info.append(str(container.name))
            else:
                azure_info = 'Azure Containers:<br>'
                for container in container_list:
                    azure_info = azure_info + str(container.name) + '<br>'
    else:
        azure_info = ''
    # AWS
    if aws_platform_check == 'on':
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        if len(buckets) == 0:
            aws_info = 'No AWS Buckets!<br>'
        else:
            if page == 'upload_page':
                aws_info = ''
                for item in buckets:
                    aws_info = aws_info + '<input type="radio" name="aws_upload_bucket" id="a_' + str(item) + '" value="' + str(item) + '"><label for="a_' + str(item) + '">' + str(item) + '</label><br>'
            elif page == 'download_page':
                aws_info = []
                for item in buckets:
                    aws_info.append(str(item))
            else:
                aws_info = 'AWS Buckets:<br>'
                for item in buckets:
                    aws_info = aws_info + str(item) + '<br>'
    else:
        aws_info = ''
    return google_info, azure_info, aws_info

def rsa_key(password, username):
    key = RSA.generate(2048)
    encrypted_key = key.export_key(passphrase = password, pkcs = 8, protection = "scryptAndAES128-CBC")
    # private key
    with open('static/keys/' + username + '.bin', 'wb') as file_out:
        file_out.write(encrypted_key)
    file_out.close()
    # public key
    with open('static/keys/' + username + '.bin', 'rb') as encoded_key:
        key_2 = RSA.import_key(encoded_key, passphrase = password)
        with open('static/keys/' + username + '.pem', 'wb') as file_out_2:
            file_out_2.write(key_2.publickey().export_key())
        file_out_2.close()
    encoded_key.close()
    return None

def encrypt_file(backup_file_path, username):
    data = ''
    with open(backup_file_path, 'rb') as file_read:
        data = file_read.read()
    file_read.close()
    with open(backup_file_path, 'wb') as file_output:
        recipient_key = RSA.import_key(open('static/keys/' + username + '.pem').read())
        session_key = get_random_bytes(16)
        # encrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        enc_session_key = cipher_rsa.encrypt(session_key)
        # encrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)
        # write the encrypted data back to file
        file_output.write(enc_session_key)
        file_output.write(cipher_aes.nonce)
        file_output.write(tag)
        file_output.write(ciphertext)
    file_output.close()
    # print 'Successfully Encrypted "%s"' % backup_file_path
    return None

def decrypt_file(file_path, password, download_file, username):
    try:
        with open(file_path, 'rb') as f:
            private_key = RSA.import_key(open('static/keys/' + username + '.bin').read(), passphrase = password)
            enc_session_key, nonce, tag, ciphertext = [f.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1)]
            # decrypt the session key with the private RSA key
            cipher_rsa = PKCS1_OAEP.new(private_key)
            session_key = cipher_rsa.decrypt(enc_session_key)
            # decrypt the data with the AES session key
            cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
            data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        f.close()
        # write the decrypted data back to file
        with open(file_path, 'wb') as o:
            o.write(data)
        o.close()
        info = 'Successfully Decrypted ' + str(download_file)
    except Exception as e:
        info = 'Failed to Decrypt: ' + str(e)
    return info

def upload_object(backup_file_path, filename, google_upload_bucket, azure_upload_container, aws_upload_bucket):
    # Google
    google_info = ''
    with open(backup_file_path, 'r') as google_file:
        dst_uri = boto.storage_uri(google_upload_bucket + '/' + filename, google_storage)
        dst_uri.new_key().set_contents_from_file(google_file)
    google_info = 'Successfully Uploaded ' + dst_uri.bucket_name + '/' + dst_uri.object_name + ' to Google!'
    google_file.close()
    # Azure
    azure_info = ''
    azure.create_blob_from_path(azure_upload_container, filename, backup_file_path, content_settings = ContentSettings())
    azure_info = 'Successfully Uploaded ' + azure_upload_container + '/' + filename + ' to Azure!'
    # AWS
    aws_info = ''
    with open(backup_file_path, 'r') as aws_file:
        s3.Object(aws_upload_bucket, filename).put(Body = aws_file)
        s3.Object(aws_upload_bucket, filename).Acl().put(ACL='public-read')
    aws_info = 'Successfully Uploaded ' + aws_upload_bucket + '/' + filename + ' to AWS!'
    aws_file.close()
    return google_info, azure_info, aws_info

def list_object(page, google_bucket_name, azure_container_name, aws_bucket_name, google_platform_check, azure_platform_check, aws_platform_check):
    # Google
    if google_platform_check == 'on':
        uri = boto.storage_uri(google_bucket_name, google_storage)
        google_object_list = uri.get_bucket()
        i = 0
        for key in google_object_list.list():
            i += 1
        if i == 0:
            google_info = 'No Objects in This Google Bucket!<br>'
        else:
            if page == 'download_page':
                google_info = []
                for g_obj in google_object_list:
                    google_info.append(str(g_obj.name))
            else:
                google_info = ''
                for g_obj in google_object_list:
                    google_info = google_info + 'Google://' + str(uri.bucket_name) + '/' + str(g_obj.name) + '<br>'
    else:
        google_info = ''
    # Azure
    if azure_platform_check == 'on':
        generator = azure.list_blobs(azure_container_name)
        if len(list(generator)) == 0:
            azure_info = 'No Objects in This Azure Container!<br>'
        else:
            if page == 'download_page':
                azure_info = []
                for blob in generator:
                    azure_info.append(str(blob.name))
            else:
                azure_info = ''
                for blob in generator:
                    azure_info = azure_info + 'Azure://' + str(azure_container_name) + '/' + str(blob.name) + '<br>'
    else:
        azure_info = ''
    # AWS
    if aws_platform_check == 'on':
        bucket = s3.Bucket(aws_bucket_name)
        aws_object_list = bucket.objects.all()
        size = sum(1 for _ in aws_object_list)
        if size == 0:
            aws_info = 'No Objects in This Google Bucket!<br>'
        else:
            if page == 'download_page':
                aws_info = []
                for a_obj in aws_object_list:
                    aws_info.append(str(a_obj.key))
            else:
                aws_info = ''
                for a_obj in aws_object_list:
                    aws_info = aws_info + 'AWS://' + str(a_obj.bucket_name) + '/' + str(a_obj.key) + '<br>'
    else:
        aws_info = ''
    return google_info, azure_info, aws_info

def download_object(platform, file_source_bucket, destination_path, download_file):
    info = ''
    # Google
    if platform == 'Google':
        src_uri = boto.storage_uri(file_source_bucket + '/' + download_file, google_storage)
        object_contents = StringIO.StringIO() # a file-like object for holding the object contents
        src_uri.get_key().get_file(object_contents) # writes the contents to object_contents
        dst_uri = boto.storage_uri(os.path.join(destination_path, download_file), local_file)
        object_contents.seek(0) # the beginning of the file
        dst_uri.new_key().set_contents_from_file(object_contents)
        object_contents.close()
        info = 'Successfully Downloaded ' + download_file + ' from Google://' + file_source_bucket
    # Azure
    elif platform == 'Azure':
        azure.get_blob_to_path(file_source_bucket, download_file, destination_path + download_file)
        info = 'Successfully Downloaded ' + download_file + ' from Azure://' + file_source_bucket
    # AWS
    elif platform == 'AWS':
        try:
            s3.Bucket(file_source_bucket).download_file(download_file, destination_path + download_file)
            info = 'Successfully Downloaded ' + download_file + ' from AWS://' + file_source_bucket
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                info = 'The object does not exist.'
            else:
                raise
    return info

def delete_object(platform, file_source_bucket, delete_file):
    # Google
    google_info = ''
    if platform[0] == 'on':
        try:
            uri = boto.storage_uri(file_source_bucket[0] + '/' + delete_file[0], google_storage)
            uri.delete_key()
            google_info = 'Google: Deleted Object ' + str(file_source_bucket[0]) + '/' + str(delete_file[0]) + '<br>'
        except Exception as g_e:
            google_info = 'Failed to Delete Object in Google: ' + str(g_e) + '<br>'
    # Azure
    azure_info = ''
    if platform[1] == 'on':
        try:
            azure.delete_blob(file_source_bucket[1], delete_file[1])
            azure_info = 'Azure: Deleted Object ' + str(file_source_bucket[1]) + '/' + str(delete_file[1]) + '<br>'
        except Exception as m_e:
            azure_info = 'Failed to Delete Object in Azure: ' + str(m_e) + '<br>'
    # AWS
    aws_info = ''
    if platform[2] == 'on':
        try:
            s3.Object(file_source_bucket[2], delete_file[2]).delete()
            aws_info = 'AWS: Deleted Object ' + str(file_source_bucket[2]) + '/' + str(delete_file[2]) + '<br>'
        except Exception as a_e:
            aws_info = 'Failed to Delete Object in AWS: ' + str(a_e) + '<br>'
    return google_info, azure_info, aws_info
