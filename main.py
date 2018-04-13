from flask import Flask, render_template, request
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
#from werkzeug import secure_filename

app = Flask(__name__)

@app.route('/initialize/', methods = ['GET', 'POST'])
def initialize():
    if request.method == 'POST':
        google_project_id = request.form['google_project_id']
        azure_account_name = request.form['azure_account_name']
        azure_account_key = request.form['azure_account_key']
        s3_access_key_id = request.form['s3_access_key_id']
        s3_secret_access_key = request.form['s3_secret_access_key']
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
        info = 1
        return render_template('initialize.html', information = info)
    else:
        return render_template('initialize.html')

@app.route('/create_bucket/', methods = ['GET', 'POST'])
def create_bucket():
    if request.method == 'POST':
        google_bucket_name = request.form['google_bucket_name']
        azure_container_name = request.form['azure_container_name']
        aws_bucket_name = request.form['aws_bucket_name']
        google_platform_check = request.form.get('google_platform')
        azure_platform_check = request.form.get('azure_platform')
        aws_platform_check = request.form.get('aws_platform')
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
        flag = 1
        return render_template('create_bucket.html', status = flag, google = google_info, azure = azure_info, aws = aws_info)
    else:
        return render_template('create_bucket.html')

@app.route('/upload/', methods = ['POST'])
def upload():
    f = request.files['file_path']
    google_upload_bucket = request.form['google_upload_bucket']
    azure_upload_container = request.form['azure_upload_container']
    aws_upload_bucket = request.form['aws_upload_bucket']
    # add a '.' in front of filename to hide the file in macOS
    backup_file_path = '/Users/danielwong/' + f.filename
    f.save(backup_file_path)
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
    return render_template('upload_ajax.html')

@app.route('/upload_ajax/')
def upload_ajax():
    return render_template('upload_ajax.html')

if __name__ == '__main__':
    app.run(debug = True)
