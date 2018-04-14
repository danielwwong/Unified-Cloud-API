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

def initialize(google_project_id, azure_account_name, azure_account_key, s3_access_key_id, s3_secret_access_key):
    global google_storage, local_file, google_header_values, azure, s3, s3_client
    # Google
    google_storage = 'gs' # URI scheme for Google Cloud Storage
    local_file = 'file' # URI scheme for accessing local files
    google_header_values = {'x-goog-project-id': google_project_id}
    # Azure
    azure = BlockBlobService(account_name = azure_account_name, account_key = azure_account_key)
    # AWS
    s3 = boto3.resource('s3', aws_access_key_id = s3_access_key_id, aws_secret_access_key = s3_secret_access_key)
    s3_client = boto3.client('s3', aws_access_key_id = s3_access_key_id, aws_secret_access_key = s3_secret_access_key)
    return None

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

def list_bucket(google_platform_check, azure_platform_check, aws_platform_check):
    # Google
    google_info = ''
    if google_platform_check == 'on':
        uri = boto.storage_uri('', google_storage)
        google_info = 'Google Buckets:<br>'
        for bucket in uri.get_all_buckets(headers = google_header_values):
            google_info = google_info + str(bucket.name) + '<br>'
    # Azure
    azure_info = ''
    if azure_platform_check == 'on':
        container_list = azure.list_containers()
        azure_info = 'Azure Containers:<br>'
        for container in container_list:
            azure_info = azure_info + str(container.name) + '<br>'
    # AWS
    aws_info = ''
    if aws_platform_check == 'on':
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        aws_info = 'AWS Buckets:<br>'
        for item in buckets:
            aws_info = aws_info + str(item) + '<br>'
    return google_info, azure_info, aws_info

def rsa_key(password):
    key = RSA.generate(2048)
    encrypted_key = key.export_key(passphrase = password, pkcs = 8, protection = "scryptAndAES128-CBC")
    # private key
    with open('static/temp/rsa_private_key.bin', 'wb') as file_out:
        file_out.write(encrypted_key)
    file_out.close()
    # public key
    with open('static/temp/rsa_private_key.bin', 'rb') as encoded_key:
        key_2 = RSA.import_key(encoded_key, passphrase = password)
        with open('static/temp/rsa_public_key.pem', 'wb') as file_out_2:
            file_out_2.write(key_2.publickey().export_key())
        file_out_2.close()
    encoded_key.close()
    return None

def encrypt_file(backup_file_path):
    data = ''
    with open(backup_file_path, 'rb') as file_read:
        data = file_read.read()
    file_read.close()
    with open(backup_file_path, 'wb') as file_output:
        recipient_key = RSA.import_key(open('static/temp/rsa_public_key.pem').read())
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

def upload_object(backup_file_path, f, google_upload_bucket, azure_upload_container, aws_upload_bucket):
    # Google
    with open(backup_file_path, 'r') as google_file:
        dst_uri = boto.storage_uri(google_upload_bucket + '/' + f.filename, google_storage)
        dst_uri.new_key().set_contents_from_file(google_file)
    # print 'Successfully Uploaded "%s/%s" to Google' % (dst_uri.bucket_name, dst_uri.object_name)
    google_file.close()
    # Azure
    azure.create_blob_from_path(azure_upload_container, f.filename, backup_file_path, content_settings = ContentSettings())
    # print 'Successfully Uploaded "%s/%s" to Azure' % (azure_upload_container, f.filename)
    # AWS
    with open(backup_file_path, 'r') as aws_file:
        s3.Object(aws_upload_bucket, f.filename).put(Body = aws_file)
        s3.Object(aws_upload_bucket, f.filename).Acl().put(ACL='public-read')
    # print 'Successfully Uploaded "%s/%s" to AWS' % (aws_upload_bucket, f.filename)
    aws_file.close()
    return None

def list_object(google_bucket_name, azure_container_name, aws_bucket_name, google_platform_check, azure_platform_check, aws_platform_check):
    # Google
    google_info = ''
    if google_platform_check == 'on':
        uri = boto.storage_uri(google_bucket_name, google_storage)
        for g_obj in uri.get_bucket():
            google_info = google_info + 'Google://' + str(uri.bucket_name) + '/' + str(g_obj.name) + '<br>'
    # Azure
    azure_info = ''
    if azure_platform_check == 'on':
        generator = azure.list_blobs(azure_container_name)
        for blob in generator:
            azure_info = azure_info + 'Azure://' + str(azure_container_name) + '/' + str(blob.name) + '<br>'
    # AWS
    aws_info = ''
    if aws_platform_check == 'on':
        bucket = s3.Bucket(aws_bucket_name)
        for a_obj in bucket.objects.all():
            aws_info = aws_info + 'AWS://' + str(a_obj.bucket_name) + '/' + str(a_obj.key) + '<br>'
    return google_info, azure_info, aws_info
