from flask import Flask, render_template, request
import custom_api

app = Flask(__name__)
backup_file_folder = '/Users/danielwong/'

@app.route('/initialize/', methods = ['GET', 'POST'])
def initialize():
    if request.method == 'POST':
        google_project_id = request.form['google_project_id']
        azure_account_name = request.form['azure_account_name']
        azure_account_key = request.form['azure_account_key']
        s3_access_key_id = request.form['s3_access_key_id']
        s3_secret_access_key = request.form['s3_secret_access_key']
        custom_api.initialize(google_project_id, azure_account_name, azure_account_key, s3_access_key_id, s3_secret_access_key)
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
        google_info, azure_info, aws_info = custom_api.list_bucket(google_platform_check, azure_platform_check, aws_platform_check)
        flag = 1
        return render_template('list_bucket.html', status = flag, google = google_info, azure = azure_info, aws = aws_info)
    else:
        return render_template('list_bucket.html')

@app.route('/upload/', methods = ['POST'])
def upload():
    f = request.files['file_path']
    google_upload_bucket = request.form['google_upload_bucket']
    azure_upload_container = request.form['azure_upload_container']
    aws_upload_bucket = request.form['aws_upload_bucket']
    check_encrypt = request.form.get('encryption_check')
    password = request.form['input_password']
    # add a '.' in front of filename to hide the file in macOS
    backup_file_path = backup_file_folder + f.filename
    f.save(backup_file_path)
    # encryption
    if check_encrypt == 'on':
        # RSA public/private key generation
        custom_api.rsa_key(password)
        # encrypt file
        custom_api.encrypt_file(backup_file_path)
    # upload
    custom_api.upload_object(backup_file_path, f, google_upload_bucket, azure_upload_container, aws_upload_bucket)
    return render_template('upload_ajax.html')

@app.route('/upload_ajax/')
def upload_ajax():
    return render_template('upload_ajax.html')

@app.route('/download_keys/private/', methods = ['GET'])
def download_private_key():
    return app.send_static_file('temp/rsa_private_key.bin')

@app.route('/download_keys/public/', methods = ['GET'])
def download_public_key():
    return app.send_static_file('temp/rsa_public_key.pem')

@app.route('/list_object/', methods = ['GET', 'POST'])
def list_object():
    if request.method == 'POST':
        google_bucket_name = request.form['google_bucket_name']
        azure_container_name = request.form['azure_container_name']
        aws_bucket_name = request.form['aws_bucket_name']
        google_platform_check = request.form.get('google_platform')
        azure_platform_check = request.form.get('azure_platform')
        aws_platform_check = request.form.get('aws_platform')
        google_info, azure_info, aws_info = custom_api.list_object(google_bucket_name, azure_container_name, aws_bucket_name, google_platform_check, azure_platform_check, aws_platform_check)
        flag = 1
        return render_template('list_object.html', status = flag, google = google_info, azure = azure_info, aws = aws_info)
    else:
        return render_template('list_object.html')

if __name__ == '__main__':
    app.run(debug = True)
