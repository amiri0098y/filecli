import os
import uuid
import requests
import ftplib

FTP_HOST = "213.171.50.155"
FTP_USER = "anonymous"
FTP_PASS = ""

API_URL = "https://token.giftcard-e2d.workers.dev/token"  # Replace with your Worker URL

LOCAL_TOKEN_FILE = "my_token.txt"

def save_token_to_d1(token):
    try:
        r = requests.post(API_URL, json={"token": token})
        return r.status_code in [200, 409]
    except:
        return False

def validate_token(token):
    try:
        r = requests.get(API_URL, params={"token": token})
        return r.status_code == 200
    except:
        return False

def load_or_create_token():
    if os.path.exists(LOCAL_TOKEN_FILE):
        return open(LOCAL_TOKEN_FILE).read().strip()
    token = str(uuid.uuid4())
    if save_token_to_d1(token):
        with open(LOCAL_TOKEN_FILE, 'w') as f:
            f.write(token)
        return token
    else:
        exit("Failed to save token.")

def connect_ftp():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp

def ensure_token_dir(ftp, token):
    try:
        ftp.cwd(token)
    except ftplib.error_perm:
        ftp.mkd(token)
        ftp.cwd(token)

def is_inside_token_dir(current_path, token):
    return current_path.startswith(f"/{token}")

def upload_file(ftp, filename):
    if not os.path.exists(filename):
        print("File not found.")
        return
    with open(filename, 'rb') as f:
        ftp.storbinary(f"STOR {os.path.basename(filename)}", f)
    print("Uploaded.")

def download_file(ftp, filename):
    with open(filename, 'wb') as f:
        ftp.retrbinary("RETR " + filename, f.write)
    print("Downloaded.")

def delete_file(ftp, filename):
    ftp.delete(filename)
    print("Deleted.")

def rename_file(ftp, old, new):
    ftp.rename(old, new)
    print("Renamed.")

def copy_file(ftp, src, dst):
    tmp = "__tmp__"
    with open(tmp, 'wb') as f:
        ftp.retrbinary("RETR " + src, f.write)
    with open(tmp, 'rb') as f:
        ftp.storbinary("STOR " + dst, f)
    os.remove(tmp)
    print("Copied.")

def make_dir(ftp, name):
    ftp.mkd(name)
    print(f"Folder '{name}' created.")

def change_dir(ftp, token, new_dir):
    current = ftp.pwd()
    try:
        ftp.cwd(new_dir)
        new_path = ftp.pwd()
        if not is_inside_token_dir(new_path, token):
            ftp.cwd(current)
            print("Access denied.")
        else:
            print("Changed directory to:", new_path)
    except:
        print("Folder not found.")

def list_files(ftp):
    items = ftp.nlst()
    print("Contents:")
    for i in items:
        print(" -", i)

def main():
    token = load_or_create_token()
    print("Your token:", token)

    input_token = input("Enter your token to continue: ").strip()
    if not validate_token(input_token):
        print("Invalid token.")
        return

    ftp = connect_ftp()
    ensure_token_dir(ftp, input_token)
    print("Connected to your private directory.")

    while True:
        cmd = input(">> ").strip().split()
        if not cmd:
            continue
        if cmd[0] == "exit":
            break
        elif cmd[0] == "ulf" and len(cmd) == 2:
            upload_file(ftp, cmd[1])
        elif cmd[0] == "dlf" and len(cmd) == 2:
            download_file(ftp, cmd[1])
        elif cmd[0] == "rm" and len(cmd) == 2:
            delete_file(ftp, cmd[1])
        elif cmd[0] == "mv" and len(cmd) == 3:
            rename_file(ftp, cmd[1], cmd[2])
        elif cmd[0] == "cp" and len(cmd) == 3:
            copy_file(ftp, cmd[1], cmd[2])
        elif cmd[0] == "ls":
            list_files(ftp)
        elif cmd[0] == "pwd":
            print("Current directory:", ftp.pwd())
        elif cmd[0] == "mkdir" and len(cmd) == 2:
            make_dir(ftp, cmd[1])
        elif cmd[0] == "cd" and len(cmd) == 2:
            change_dir(ftp, token, cmd[1])
        else:
            print("Unknown command.")

    ftp.quit()

if __name__ == "__main__":
    main()
