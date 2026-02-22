import paramiko
import os
from dotenv import load_dotenv

load_dotenv('Credentials.env')

def check_logs():
    host = os.getenv('VPS_HOST')
    user = os.getenv('VPS_USER')
    password = os.getenv('VPS_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, 22, user, password)
    
    print("--- Docker PS ---")
    stdin, stdout, stderr = client.exec_command('docker ps -a')
    print(stdout.read().decode())
    
    print("--- Directory Content ---")
    stdin, stdout, stderr = client.exec_command('ls -la /app/telegram_bot')
    print(stdout.read().decode())
    
    print("--- Manual Rebuild and Run ---")
    commands = [
        'cd /app/telegram_bot && docker stop tg_bot || true',
        'cd /app/telegram_bot && docker rm tg_bot || true',
        'cd /app/telegram_bot && docker build -t tg_bot_img .',
        'cd /app/telegram_bot && mkdir -p downloads',
        'cd /app/telegram_bot && docker run -d --name tg_bot --env-file .env -v $(pwd)/downloads:/app/downloads --restart always tg_bot_img'
    ]
    for cmd in commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())

    print("--- Final Status ---")
    stdin, stdout, stderr = client.exec_command('docker ps')
    print(stdout.read().decode())
    
    print("--- Container Logs ---")
    stdin, stdout, stderr = client.exec_command('docker logs tg_bot')
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    client.close()

def view_logs():
    host = os.getenv('VPS_HOST')
    user = os.getenv('VPS_USER')
    password = os.getenv('VPS_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, 22, user, password)
    stdin, stdout, stderr = client.exec_command('docker logs tg_bot')
    print(stdout.read().decode())
    print(stderr.read().decode())
    client.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "logs":
        view_logs()
    else:
        check_logs()
