# pyshotcutupload
A Python utility for uploading Shotcut projects to a server for rendering/exporting.

[Shotcut](https://shotcut.org/) is an open-source, cross-platform video editor built upon the [MLT](https://www.mltframework.org/) framework. This was originally written so I could reuse a Linux Mint desktop as a rendering/export server for Shotcut, along with getting some further experience with Python.

## How it works
This performs the following tasks in order:
1. Parse required arguments.
2. Read configuration from the config.yml file.
3. Issue a ping command to the server to check if it is up (and exit if this fails).
4. Parse the MLT file into which Shotcut saves projects, looking for any tag defined as `<property name="resource">`.
5. Copy each file mentioned in the above tags to the local directory and strip out the path from the tag. This effectively points the Shotcut project at the local files instead of using absolute paths
6. Rewrite the MTL file's XML tree into a new file to preserve the original.
7. Upload all files to the server.
8. Delete the temporary files

### Limitations
- There may be issues on different operating systems. This is currently tested on Ubuntu under WSL, but the original development work was done under Git Bash on Windows.
- This will not open Shotcut on the remote server, and using the MLT framework directly has not been tested.
- There is currently no way to check when Shotcut has finished exporting.

## Requirements
- A server with Shotcut installed. SSH must be enabled on this and set to use SSH keys.
- Python 3.8.10 or later on your local machine

## Building and configuring
Install the required packages (paramiko and pyyaml) by running `pip install -r requirements.txt`.

### SSH setup
If SSH is _not_ set up on your server (e.g. you are repurposing an old desktop) or does not use SSH keys, set up SSH as follows:
1. Set your server to have a static IP address. Doing so is beyond the scope of this guide.
2. Enable SSH on the server by running `systemctl enable sshd`. Optionally, set it to use a port other than 22.
3. Create an SSH key by running `ssh-keygen` on your local computer. 
	- Take note of the path to the file; this utility expects the filename to be "id_rsa".
	- Fill out the passphrase. Take note of this for later.
4. Copy this to your server by running `ssh-copy-id user@server`, e.g. `ssh-copy-id admin@1.2.3.4`. When prompted for a password, use the password associated with the remote server. Do *not* use the passphrase for the SSH key.

### Configuration file
Copy the config.example.yml file to config.yml and update as follows:
1. Replace the username field with the username you will use to access the server
2. Replace the host with the IP address or hostname of the server.
3. If your server uses a different port to 22 (the standard SSH/SFTP port), replace the port entry with the expected value.
4. Replace the path in the key_path variable with the actual path to the folder that contains the `id_rsa` file. In most cases, this will be `$HOME/.ssh`.
5. Replace the key_pass variable with the passphrase defined above.

## Running
Run the following command: `python3 uploader.py path/to/mlt_file path/to/remote_dir`, e.g. `python3 uploader.py examples/PyShotcutUploader.mlt Videos/UploadedFailer`
Both parameters are required.
- The `mlt_file` is the format in which Shotcut saves projects.
- The `remote_dir` is the remote directory to which to upload them, relative to the remote user's home directory (e.g. Videos/Test instead of /home/admin/Videos/Test)

### Videos of this running
- [Failure](https://youtu.be/tduc-3BZ388)
- [Success](https://youtu.be/CVf-wkTxUVs)

### Troubleshooting
- Check that you haven't missed the config.yml file and that all paths are correct in the Shotcut project.
- Check that the SSH host, port, SSH key and passphrase match that of the server

## Licence
MIT (see the [LICENCE](./LICENCE) file).

### Other files
- [MODEM_3.aiff](https://freesound.org/people/G_M_D_THREE/sounds/454649/) (CC0)
- [wah wah sad trombone.wav](https://freesound.org/people/kirbydx/sounds/175409/) (CC0)