# Unified-Cloud-API

## Environment

1. Create service accounts in *Google Cloud Platform*, *Microsoft Azure* and *Amazon Web Services*.

2. Download and store the *Google Cloud Platform* private key in *P12* format.

3. Create a project in *Google Cloud Platform Console*, mark down the *project ID*.

4. Create a storage account in *Microsoft Azure Portal*, mark down the *Storage Account Name* and *Storage Account Key*.

5. Create an access key in *Amazon Web Services Console*, mark down the *Access Key ID* and *Secret Access Key*.

6. All codes are based on *Python 2.7.14*. Have not tested on *Python 3* yet.

7. Install *gsutil*, *boto*, *boto3*, *botocore*, *gcs-oauth2-boto-plugin*, *azure-storage*, *azure-common* and *pycryptodome* packages by pip.

## Note
1. If you want to change to another *Google Cloud Platform Account* or another *Google Cloud Project*, you may need to manually shutdown and restart the web application to renew the environment.

2. It doesn't require restart if you only want to change *Microsoft Azure Account* or *Amazon Web Services Account*, you can simply go to *Initialize* tab and provide new credentials.

3. More detailed guidelines will be added.

Team 1009
