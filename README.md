# pyshotcutupload
A Python utility for uploading Shotcut projects to a server for rendering/exporting. 

(Shotcut)[https://shotcut.org/] is an open-source, cross-platform video editor built upon the (MLT)[https://www.mltframework.org/] framework. This was originally written so I could reuse a Linux Mint desktop as a rendering/export server for Shotcut, along with getting some further experience with Python.

## Requirements
A server with Shotcut installed. SSH must be enabled on this and set to use SSH keys.
Python 3.8.10 or later

## Installation
`pip install -r requirements.txt`

### SSH setup
If SSH is _not_ set up on your server (e.g. you are repurposing an old desktop) or does not use SSH keys, set up SSH as follows:
1. Set your server to have a static IP address. Doing so is beyond the scope of this guide.
2. Enable SSH on the server by running `systemctl enable sshd`. Optionally, set it to use a port other than 22.
3. Create an SSH key by running `ssh-keygen` on your local computer. 
	- Take note of the path to the file; this utility expects the filename to be "id_rsa".
	- Fill out the passphrase. Take note of this for later.
4. Copy this to your server by running `ssh-copy-id user@server`, e.g. `ssh-copy-id admin@1.2.3.4`. When prompted for a password, use the password associated with the remote server. Do *not* use the passphrase for the SSH key.

## How to use this

### Configuration file
Copy the config.example.yml file to config.yml and update as follows:
1. Replace the username field with the username you will use to access the server
2. Replace the host with the IP address or hostname of the server.
3. If your server uses a different port to 22 (the standard SSH/SFTP port), replace the port entry with the expected value.
4. Replace the path in the key_path variable with the actual path to the folder that contains the `id_rsa` file. In most cases, this will be `$HOME/.ssh`.
5. Replace the key_pass variable with the passphrase defined above.

### Running
`python uploader.py path/to/mlt_file path/to/remote_dir`
- The mtl_file is the format in which Shotcut saves projects.
- The remote_dir is the remote directory to which to upload them, relative to the remote user's home directory (e.g. Videos/Test instead of /home/admin/Videos/Test)

### Troubleshooting
TODO

## Licence
MIT (see the (LICENCE)[./LICENCE] file).