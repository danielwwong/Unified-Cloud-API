# Unified-Cloud-API

## Environment

1. Create service accounts in `Google Cloud Platform`, `Microsoft Azure` and `Amazon Web Services`.

**Google**

1. In `Google Cloud Console`, go to `APIs & Services` &rightarrow; `Credentials` section, create a new credential. Choose `Service account key` option when prompted. You can choose to use an existing service account or create a new one. Please mark down `Google Service Account ID` and choose `P12` key type.

2. Mark down `Google Service Account ID`. Download and store the `Google Cloud Platform` private key in `P12` format.
(`Google Service Account ID` looks like an email address.)

3. Create a project in `Google Cloud Platform Console`, mark down the `Project ID`.

**Azure**

1. Create a storage account in `Microsoft Azure Portal`, mark down the `Storage Account Name` and `Storage Account Key`.

**AWS**

1. Create an access key in `Amazon Web Services Console`, mark down the `Access Key ID` and `Secret Access Key`.

**Package Dependencies**

1. All codes are based on `Python 2.7.14`. Have not tested on `Python 3` yet.

2. Install `gsutil`, `boto`, `boto3`, `botocore`, `gcs-oauth2-boto-plugin`, `azure-storage`, `azure-common` and `pycryptodome` packages by `pip` in terminal.

3. This back-end application was built and tested on `macOS High Sierra` Version 10.13.4. Hosting the server on macOS is recommended.

4. After successfully installed all Python packages, please navigate to the project folder in Terminal and type in the following command to start the server: `python main.py`.

5. Debug Function of the server is turned on by default. Users can cancel Debug to get higher security.

6. The server is externally invisible by default. Users can change the last line in `main.py` to be `app.run(host = '0.0.0.0')` to tell the OS to listen on all public IPs.

7. Users can use any modern browsers on any OSes to get access to the web application. By default, the address would be `127.0.0.1:5000`. `Safari` is recommended as the website was built and tested based on it.

8. For new users, please select `New User` and provide your username and password. Once created, the password cannot be changed. The password will be prompted before downloading files.

9. For returning users, please select `Existing User` and provide your username. Before downloading files, please input your password when you first created the user profile.

## Note
1. If you want to change to another `Google Cloud Platform Account` or another `Google Cloud Project` after starting the server and initializing the credentials, you may need to manually shutdown and restart the web application to renew the environment.

2. It doesn't require restart if you only want to change `Microsoft Azure Account` or `Amazon Web Services Account`, you can simply go to `Initialize` tab and provide new credentials.

3. Before upload files, users should have at least 1 bucket/container in each platform. Users can go to `Create Bucket` tab to create new buckets/containers.

4. `Block Connection` tab is used for testing only. Using this function will block the selected cloud platform.

## Known Issues
1. There `should not be any duplicated file names` across all buckets/containers on all platforms. It may cause problems on download page.

2. Does not support file names in Chinese characters, please keep all your file names across all buckets/containers on all platforms using `alphabetic characters` only.

3. Going to other tabs other than `Initialize` tab before successfully initialized may cause problems. Please go back and initialize first.

4. UTF-8 may be supported in the future.

5. More platforms may be supported in the future.
