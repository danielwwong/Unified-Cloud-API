from flask import Flask, render_template, request
import shared
import threading
import time
import os

app = Flask(__name__)
backup_file_folder = 'static/upload_temp/'
basedir = os.path.abspath(os.path.dirname(__file__))
backup_google_key_folder = basedir
temp_file_folder = 'static/temp/'
key_file_folder = 'static/keys/'


@app.route('/initialize/', methods = ['GET', 'POST'])
def initialize():
    if request.method == 'POST':
        google_key = request.files['google_key']
        google_service_account = request.form['google_service_account']
        google_project_id = request.form['google_project_id']
        azure_account_name = request.form['azure_account_name']
        azure_account_key = request.form['azure_account_key']
        s3_access_key_id = request.form['s3_access_key_id']
        s3_secret_access_key = request.form['s3_secret_access_key']
        global username
        username = request.form['username']
        decrypt_password = request.form['decrypt_password']
        with open (basedir + '/boto', 'w') as boto_file:
            boto_file.write('[Credentials]\ngs_service_key_file = google_key.p12\ngs_service_client_id = ' + google_service_account + '\n[Boto]\nhttps_validate_certificates = True\n[GoogleCompute]\n[GSUtil]\ncontent_language = en\ndefault_project_id = ' + google_project_id + '\n[OAuth2]')
        boto_file.close()
        global custom_api
        import custom_api
        global scheduler
        from scheduler import scheduler
        scheduler = scheduler(num_workers=3)
        backup_key_path = backup_google_key_folder + '/google_key.p12'
        google_key.save(backup_key_path)
        google_info, azure_info, aws_info = custom_api.initialize(google_project_id, azure_account_name, azure_account_key, s3_access_key_id, s3_secret_access_key)
        if username == '':
            user_info = 'Failed to Initialize User!'
        else:
            if decrypt_password == '':
                if (os.path.isfile(os.path.join(basedir, key_file_folder) + username + '.pem')):
                    user_info = 'Successfully Initialized User!'
                else:
                    user_info = 'Failed to Initalize User! Please Provide Password!'
            else:
                if (os.path.isfile(os.path.join(basedir, key_file_folder) + username + '.pem')):
                    user_info = 'User Existed!'
                else:
                    # RSA public/private key generation
                    custom_api.rsa_key(decrypt_password, username)
                    user_info = 'Successfully Initialized User!'
        flag = 1
        return render_template('initialize.html', status = flag, google = google_info, azure = azure_info, aws = aws_info, user = user_info)
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
        google_info, azure_info, aws_info = custom_api.create_bucket(google_bucket_name, azure_container_name, aws_bucket_name, google_platform_check, azure_platform_check, aws_platform_check)
        flag = 1
        return render_template('create_bucket.html', status = flag, google = google_info, azure = azure_info, aws = aws_info)
    else:
        return render_template('create_bucket.html')

@app.route('/list_bucket/', methods = ['GET', 'POST'])
def list_bucket():
    if request.method == 'POST':
        google_platform_check = request.form.get('google_platform')
        azure_platform_check = request.form.get('azure_platform')
        aws_platform_check = request.form.get('aws_platform')
        page = 'list_page'
        google_info, azure_info, aws_info = custom_api.list_bucket(page, google_platform_check, azure_platform_check, aws_platform_check)
        flag = 1
        return render_template('list_bucket.html', status = flag, google = google_info, azure = azure_info, aws = aws_info)
    else:
        return render_template('list_bucket.html')

# @app.route('/upload/', methods = ['POST'])
# def upload():
#     f = request.files['file_path']
#     google_upload_bucket = request.form['google_upload_bucket']
#     azure_upload_container = request.form['azure_upload_container']
#     aws_upload_bucket = request.form['aws_upload_bucket']
#     # add a '.' in front of filename to hide the file in macOS
#     backup_file_path = backup_file_folder + f.filename
#     f.save(backup_file_path)
#     # encrypt file
#     custom_api.encrypt_file(backup_file_path, username)
#     # upload
#     google_info, azure_info, aws_info = custom_api.upload_object(backup_file_path, f.filename, google_upload_bucket, azure_upload_container, aws_upload_bucket)
#     info = google_info + '<br>' + azure_info + '<br>' + aws_info
#     return info

@app.route('/upload_status/', methods = ['POST'])
def upload_status():
    info = ''
    for information in shared.upload_info:
        info = info + '<p><i class="fa fa-check-circle fa-fw" style="font-size:24px;color:green"></i>' + information['info'] + '</p>\n'
    return info


@app.route('/block_connection/', methods = ['GET', 'POST'])
def blcok_connection():
    platform = []
    google_platform_check = request.form.get('google_platform')
    azure_platform_check = request.form.get('azure_platform')
    aws_platform_check = request.form.get('aws_platform')
    if google_platform_check == "on":
        platform.append("google")
    if azure_platform_check == "on":
        platform.append("azure")
    if aws_platform_check == "on":
        platform.append("aws")
    if request.form.get('test') == "block":
        scheduler.monitor.manual_block(platform)
    else:
        scheduler.monitor.manual_unblock(platform)
    return render_template('block_connection.html')


@app.route('/upload/', methods = ['POST'])
def upload():
    f = request.files.getlist('file_path[]')
    google_upload_bucket = request.form['google_upload_bucket']
    azure_upload_container = request.form['azure_upload_container']
    aws_upload_bucket = request.form['aws_upload_bucket']
    arg = ''
    # add a '.' in front of filename to hide the file in macOS
    for x in range(len(f)):
        backup_file_path = backup_file_folder + f[x].filename
        f[x].save(backup_file_path)
        # encrypt file
        custom_api.encrypt_file(backup_file_path, username)
        # upload
        if f[x].filename == "TestAssignment":
            scheduler.test_reassignment('upload', backup_file_path, f[x].filename, [google_upload_bucket, azure_upload_container, aws_upload_bucket])
        else:
            scheduler.input('upload', backup_file_path, f[x].filename, [google_upload_bucket, azure_upload_container, aws_upload_bucket])
    info = ''
    return info


@app.route('/upload_ajax/')
def upload_ajax():
    google_platform_check = 'on'
    azure_platform_check = 'on'
    aws_platform_check = 'on'
    page = 'upload_page'
    google_info, azure_info, aws_info = custom_api.list_bucket(page, google_platform_check, azure_platform_check, aws_platform_check)
    return render_template('upload_ajax.html', google = google_info, azure = azure_info, aws = aws_info)

#@app.route('/download_keys/private/', methods = ['GET'])
#def download_private_key():
#    return app.send_static_file('temp/' + username + '.bin')
#
#@app.route('/download_keys/public/', methods = ['GET'])
#def download_public_key():
#    return app.send_static_file('temp/rsa_public_key.pem')

@app.route('/list_object/', methods = ['GET', 'POST'])
def list_object():
    if request.method == 'POST':
        google_bucket_name = request.form['google_bucket_name']
        azure_container_name = request.form['azure_container_name']
        aws_bucket_name = request.form['aws_bucket_name']
        google_platform_check = request.form.get('google_platform')
        azure_platform_check = request.form.get('azure_platform')
        aws_platform_check = request.form.get('aws_platform')
        page = 'list_page'
        google_info, azure_info, aws_info = custom_api.list_object(page, google_bucket_name, azure_container_name, aws_bucket_name, google_platform_check, azure_platform_check, aws_platform_check)
        flag = 1
        return render_template('list_object.html', status = flag, google = google_info, azure = azure_info, aws = aws_info)
    else:
        return render_template('list_object.html')

@app.route('/download/', methods = ['POST'])
def download():
    # clear temp folder
    folder_files = [f for f in os.listdir(temp_file_folder) if not f.startswith('.')]
    if len(folder_files) != 0:
        for file in folder_files:
            try:
                os.remove(temp_file_folder + file)
            except Exception:
                pass
    # get selected download information from frontend
    platform = request.form.getlist('platform[]')
    file_source_bucket = request.form.getlist('file_source_bucket[]')
    download_file = request.form.getlist('download_file[]')
    password = request.form['input_password']
    # parse information into 3 platforms
    google_file_source_bucket = []
    google_download_file = []
    azure_file_source_container = []
    azure_download_file = []
    aws_file_source_bucket = []
    aws_download_file = []
    for x in range(len(platform)):
        if platform[x] == 'Google':
            google_file_source_bucket.append(file_source_bucket[x])
            google_download_file.append(download_file[x])
        elif platform[x] == 'Azure':
            azure_file_source_container.append(file_source_bucket[x])
            azure_download_file.append(download_file[x])
        else:
            aws_file_source_bucket.append(file_source_bucket[x])
            aws_download_file.append(download_file[x])
    # add a '.' in front of filename to hide the file in macOS
    # download
    shared.download_info = ''
    # multithreading, one platform one thread
    t1 = threading.Thread(target = custom_api.download_object, name = 'GoogleDownloadThread', args = ('Google', google_file_source_bucket, temp_file_folder, google_download_file))
    t2 = threading.Thread(target = custom_api.download_object, name = 'AzureDownloadThread', args = ('Azure', azure_file_source_container, temp_file_folder, azure_download_file))
    t3 = threading.Thread(target = custom_api.download_object, name = 'AWSDownloadThread', args = ('AWS', aws_file_source_bucket, temp_file_folder, aws_download_file))
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
    # decryption
    for x in range(len(platform)):
        file_path = temp_file_folder + download_file[x]
        info = custom_api.decrypt_file(file_path, password, download_file[x], username)
        if info.startswith('S'):
            shared.download_info = shared.download_info + 'document.getElementById("' + file_source_bucket[x] + '_' + download_file[x] + '_' + platform[x] + '").innerHTML += "<i class=\'fa fa-unlock fa-fw\' style=\'font-size:24px;color:green\'></i>";'
        else:
            shared.download_info = shared.download_info + 'document.getElementById("' + file_source_bucket[x] + '_' + download_file[x] + '_' + platform[x] + '").innerHTML += "<i class=\'fa fa-lock fa-fw\' style=\'font-size:24px;color:red\'></i>";'
    # zip
    info = custom_api.zip_file(temp_file_folder)
    flag = 0
    for x in range(len(platform)):
        if info.startswith('S'):
            flag = 1
            shared.download_info = shared.download_info + 'document.getElementById("' + file_source_bucket[x] + '_' + download_file[x] + '_' + platform[x] + '").innerHTML += "<i class=\'fa fa-file-archive-o fa-fw\' style=\'font-size:24px;color:green\'></i>";'
        else:
            shared.download_info = shared.download_info + 'document.getElementById("' + file_source_bucket[x] + '_' + download_file[x] + '_' + platform[x] + '").innerHTML += "<i class=\'fa fa-exclamation-circle fa-fw\' style=\'font-size:24px;color:red\'></i>";'
    if flag == 1:
        shared.download_info = shared.download_info + 'download();'
    return shared.download_info

@app.route('/download_ajax/')
def download_ajax():
    google_platform_check = 'on'
    azure_platform_check = 'on'
    aws_platform_check = 'on'
    page = 'download_page'
    google_bucket_name, azure_container_name, aws_bucket_name = custom_api.list_bucket(page, google_platform_check, azure_platform_check, aws_platform_check)
    arg = 'None'
    # Google
    google_info = ''
    if not isinstance(google_bucket_name, str):
        for x in range(len(google_bucket_name)):
            google_object_list, arg_2, arg_3 = custom_api.list_object(page, google_bucket_name[x], arg, arg, google_platform_check, arg, arg)
            if not isinstance(google_object_list, str):
                for y in range(len(google_object_list)):
                    google_info = google_info + '<tr class="w3-hover-light-blue w3-ripple" onclick="check_checkbox(document.getElementById(\'' + google_object_list[y] + '\'));">\n<td><input class="w3-check" type="checkbox" name="Google" id="' + google_object_list[y] + '" value="' + google_bucket_name[x] + '" onclick="check_checkbox(this);"></td>\n<td>' + google_object_list[y] + '</td>\n<td>' + google_bucket_name[x] + '</td>\n<td><i class="fa fa-google fa-fw" style="font-size:24px;color:#2196f3"></i></td>\n<td name="statusTag" id="' + google_bucket_name[x] + '_' + google_object_list[y] + '_Google"></td>\n</tr>'# name is platform, value is source bucket, id is object name
    # Azure
    azure_info = ''
    if not isinstance(azure_container_name, str):
        for x in range(len(azure_container_name)):
            arg_2, azure_object_list, arg_3 = custom_api.list_object(page, arg, azure_container_name[x], arg, arg, azure_platform_check, arg)
            if not isinstance(azure_object_list, str):
                for y in range(len(azure_object_list)):
                    azure_info = azure_info + '<tr class="w3-hover-light-blue w3-ripple" onclick="check_checkbox(document.getElementById(\'' + azure_object_list[y] + '\'));">\n<td><input class="w3-check" type="checkbox" name="Azure" id="' + azure_object_list[y] + '" value="' + azure_container_name[x] + '" onclick="check_checkbox(this);"></td>\n<td>' + azure_object_list[y] + '</td>\n<td>' + azure_container_name[x] + '</td>\n<td><i class="fa fa-windows fa-fw" style="font-size:24px;color:#2196f3"</td>\n<td name="statusTag" id="' + azure_container_name[x] + '_' + azure_object_list[y] + '_Azure"></td>\n</tr>'# name is platform, value is source bucket, id is object name
    # AWS
    aws_info = ''
    if not isinstance(aws_bucket_name, str):
        for x in range(len(aws_bucket_name)):
            arg_2, arg_3, aws_objcet_list = custom_api.list_object(page, arg, arg, aws_bucket_name[x], arg, arg, aws_platform_check)
            if not isinstance(aws_objcet_list, str):
                for y in range(len(aws_objcet_list)):
                    aws_info = aws_info + '<tr class="w3-hover-light-blue w3-ripple" onclick="check_checkbox(document.getElementById(\'' + aws_objcet_list[y] + '\'));">\n<td><input class="w3-check" type="checkbox" name="AWS" id="' + aws_objcet_list[y] + '" value="' + aws_bucket_name[x] + '" onclick="check_checkbox(this);"></td>\n<td>' + aws_objcet_list[y] + '</td>\n<td>' + aws_bucket_name[x] + '</td>\n<td><i class="fa fa-amazon fa-fw" style="font-size:24px;color:#2196f3"></td>\n<td name="statusTag" id="' + aws_bucket_name[x] + '_' + aws_objcet_list[y] + '_AWS"></td>\n</tr>'# name is platform, value is source bucket, id is object name
    if len(google_info) == 0 and len(azure_info) == 0 and len(aws_info) == 0:
        google_info = 0
    return render_template('download_ajax.html', google = google_info, azure = azure_info, aws = aws_info)

@app.route('/download_files/', methods = ['GET'])
def download_files():
    return app.send_static_file('temp/DownloadedFiles.zip')

#@app.route('/delete/', methods = ['GET', 'POST'])
#def delete():
#    if request.method == 'POST':
#        google_platform_check = request.form.get('google_platform')
#        azure_platform_check = request.form.get('azure_platform')
#        aws_platform_check = request.form.get('aws_platform')
#        platform = [google_platform_check, azure_platform_check, aws_platform_check]
#        google_bucket = request.form['google_bucket_name']
#        azure_container = request.form['azure_container_name']
#        aws_bucket = request.form['aws_bucket_name']
#        file_source_bucket = [google_bucket, azure_container, aws_bucket]
#        google_file = request.form['google_object_name']
#        azure_file = request.form['azure_object_name']
#        aws_file = request.form['aws_object_name']
#        delete_file = [google_file, azure_file, aws_file]
#        google_info, azure_info, aws_info = custom_api.delete_object(platform, file_source_bucket, delete_file)
#        flag = 1
#        return render_template('delete_object.html', status = flag, google = google_info, azure = azure_info, aws = aws_info)
#    else:
#        return render_template('delete_object.html')

@app.route('/delete_controller/', methods = ['POST'])
def delete_controller():
    # get selected download information from frontend
    platform = request.form.getlist('platform[]')
    file_source_bucket = request.form.getlist('file_source_bucket[]')
    delete_file = request.form.getlist('delete_file[]')
    # delete
    for x in range(len(platform)):
        custom_api.delete_object(platform[x], file_source_bucket[x], delete_file[x])
    info = 'Successfully Performed Deletion!'
    return info

#@app.route('/delete_private_key/', methods = ['POST'])
#def delete_private_key():
#    os.remove(key_file_folder + 'rsa_private_key.bin')
#    info = 'Successfully Deleted Private Key in Server.'
#    return info

if __name__ == '__main__':
    app.run(debug = True)
