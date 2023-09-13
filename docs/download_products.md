## 1. Download Files from Google Drive

The most convenient way to download files from Google Drive is to add Google Drive to Windows File Explorer, To do so, the following steps must be followed:

(1) Go to Download - Google Drive site and click “Download Drive for Desktop” to download the app to your local PC.

(2) Double click the downloaded app installer in your download driectiory. In the “User Account Control” prompt that opens, choose “Yes”.

(3) On the “Install Google Drive?” page of the installation wizard, choose the options you’d like to add and then click “Install”.

(4) Once the app is installed, you will see a “Sign in to Google Drive” window. Click “Sign in With Browser”. Your PC’s default web browser will open and take you to the Google site. Over there, Google will ask if you’d like to allow your newly installed app to access your Drive files. Enable this permission by clicking “Sign in”. Google will display a message saying you‘ve successfully signed in to your Google account in the Drive app.

(5) Open File Explorer, in its left sidebar, you should be able to see a new item called “Google Drive”. Now, you can operate that drive as your local drive.

## 2. Download Files from Google Cloud Storage

(1) Install Google Cloud CLI on your local PC and answer questions such as project name, computer engine zone.

(2) To download floders/files from Google Cloud Storage, issue a command similar to: **gsutil -m cp -r gs://bucket D:\test**. On the other hand, issue a command similar to: gsutil -m cp D:\file gs://bucket. Note: the destination path must point to an existing directory, which means “test” directory must exist in the above example command.

Google Cloud CLI has been installed on the desktop computer in the downstairs living room (installed location is C:\Users\fqq\AppData\Local\Google\Cloud SDK). There is a link called “Google Cloud SDE Shell” on the desktop, by which various google cloud commands (including gsutil) can be issued.

