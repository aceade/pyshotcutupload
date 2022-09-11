# coding: utf-8
import argparse
import subprocess
import logging
import sys
from pathlib import Path, PurePath
import xml.etree.cElementTree as et
from paramiko.client import SSHClient
from paramiko.ssh_exception import BadHostKeyException, SSHException
from yaml import load, Loader

def check_server_up(address):
    logging.info("Issuing ping to %s", address)
    proc = subprocess.run(["ping", "-c", '2', address], check=True)
    return proc.returncode == 0

def upload_files(directory, remote_dir, config):
    username = config["username"]
    host = config["host"]
    port = config["port"] or 22
    private_key = str(config["key_path"]) + "/id_rsa"
    private_key_pass = config["key_pass"]
    logging.info("Uploading to %s", remote_dir)

    try:
        client = SSHClient()
        client.load_system_host_keys()
        client.connect(host, port=port, username=username,
                       key_filename=private_key, passphrase=private_key_pass)
        sftp = client.open_sftp()

        # Check if the folder exists. If not, create it
        try:
            sftp.listdir(remote_dir)
        except IOError:
            sftp.mkdir(remote_dir)

        sftp.chdir(remote_dir)
        try:
            for file in directory:
                logging.info("Uploading %s", file)
                # The remotepath should contain the file name.
                # If the forward slash is omitted, it becomes e.g. AAutomationTestsadtrombone.wav
                sftp.put(localpath=file, remotepath=remote_dir + '/' + file, confirm=True)
            logging.info("All files uploaded")
        except FileNotFoundError as err:
            logging.error(err)
        client.close()
    except BlockingIOError:
        logging.error("Can't reach the server. Check that you have the right SSH port")
    except BadHostKeyException:
        logging.error("Bad Host Key. Check that the SSH key matches the server")
    except SSHException as ssh_error:
        logging.error(ssh_error)


def get_resource_paths(file):
    paths = []
    tree = et.parse(file)
    root = tree.getroot()
    for element in root.iter("chain"):
        for prop in element.iter("property"):
            # The resource attribute is what contains the path to the file
            if prop.attrib['name'] == 'resource':
                paths.append(prop.text)
    # prevent duplicates
    return list(set(paths))

def clean_paths(file, res_paths):
    cleaned_file = file.replace('.mlt', '_fixed.mlt')
    cleaned_paths = []
    tree = et.parse(file)
    root = tree.getroot()
    for element in root.iter("chain"):
        for prop in element.iter("property"):
            if prop.attrib['name'] == 'resource' and prop.text in res_paths:
                cleaned = prop.text[(prop.text.rindex('/'))+1:]
                cleaned_paths.append(cleaned)
                prop.text = cleaned

    # Save to a new file with all paths adjusted to be relative to the project
    tree.write(cleaned_file)
    cleaned_paths.append(str(Path(cleaned_file).name))
    return cleaned_paths

def get_resource_files(file):
    res_paths = get_resource_paths(file)
    for path in res_paths:
        if path.startswith("/") is False:
            # accounting for relative paths
            file_path = PurePath(file.replace(str(PurePath(file).name), '') + "/" + path)
        else:
            # Account for WSL. There is probably a better way to do this
            file_path = PurePath(path.replace('C:', '/mnt/c').replace('D:', '/mnt/d'))
        logging.info(file_path)
        subprocess.run(["cp", "-r", file_path, "."], check=True)
    return clean_paths(file, res_paths)

def get_config():
    try:
        with open("config.yml") as file:
            return load(file, Loader=Loader)
    except FileNotFoundError:
        logging.error("config.yml not found! Check that the file exists and is named correctly!")
        subprocess.run(["ls"], check=True)
        sys.exit(-1)

def loop_server(host):
    attempts = 0
    is_up = False
    while attempts < 5:
        is_up = check_server_up(host)
        if is_up is True:
            break
        logging.info("Attempt %i failed", attempts+1)
        attempts += 1

    return is_up

def remove_temporary_files(files):
    logging.info("Cleaning up %i temporary files", len(files))
    for file in files:
        subprocess.run(["rm", file], check=True)


def main():
    parser = argparse.ArgumentParser(description="Upload files")
    parser.add_argument("file", type=str, help="The path to the MLT file")
    parser.add_argument("upload_dir", type=str,
                        help="Where to upload it to, relative to the user's home directory")

    args = parser.parse_args()
    mlt_file = args.file
    remote_dir = args.upload_dir

    logging.basicConfig(level=logging.DEBUG)
    config = get_config()
    host = config["host"]

    if loop_server(host) is True:
        logging.info("Server is up, we shall proceed")
        files = set(get_resource_files(mlt_file))
        subprocess.run(["cp", mlt_file.replace(".mlt", "_fixed.mlt"), "."], check=True)
        logging.info("Files: %s", files)
        upload_files(files, str("/home/" + config["username"] + "/" + remote_dir), config)
        remove_temporary_files(files)
    else:
        logging.warning("The server is not up yet!")

main()
