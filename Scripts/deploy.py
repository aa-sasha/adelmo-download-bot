import paramiko
import os
from scp import SCPClient
from dotenv import load_dotenv

load_dotenv('Credentials.env')

def create_ssh_client(server, port, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

def deploy():
    host = os.getenv('VPS_HOST')
    user = os.getenv('VPS_USER')
    password = os.getenv('VPS_PASSWORD')
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    print(f"Connecting to {host}...")
    ssh = create_ssh_client(host, 22, user, password)
    
    # Prepare directories
    print("Preparing remote directory...")
    ssh.exec_command('mkdir -p /app/telegram_bot')
    
    # Copy files
    print("Uploading files...")
    with SCPClient(ssh.get_transport()) as scp:
        # We need to upload bot.py, Dockerfile, docker-compose.yml, requirements.txt
        scp.put('Scripts/bot.py', '/app/telegram_bot/bot.py')
        scp.put('Scripts/Dockerfile', '/app/telegram_bot/Dockerfile')
        scp.put('Scripts/docker-compose.yml', '/app/telegram_bot/docker-compose.yml')
        scp.put('Scripts/requirements.txt', '/app/telegram_bot/requirements.txt')
        
    # Create .env on remote
    print("Setting up remote environment...")
    ssh.exec_command(f'echo "TELEGRAM_BOT_TOKEN={token}" > /app/telegram_bot/.env')
    
    # Install Docker if not exists (Ubuntu/Debian)
    print("Checking/Installing Docker and Docker Compose...")
    commands = [
        'apt-get update',
        'apt-get install -y docker.io docker-compose',
        'systemctl start docker',
        'systemctl enable docker'
    ]
    for cmd in commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.channel.recv_exit_status()
    
    # Start the bot manually (bypass docker-compose bugs on server)
    print("Building and starting the bot...")
    deployment_commands = [
        'cd /app/telegram_bot && docker stop tg_bot || true',
        'cd /app/telegram_bot && docker rm tg_bot || true',
        'cd /app/telegram_bot && docker build -t tg_bot_img .',
        'cd /app/telegram_bot && mkdir -p downloads',
        'cd /app/telegram_bot && docker run -d --name tg_bot --env-file .env -v $(pwd)/downloads:/app/downloads --restart always tg_bot_img'
    ]
    for cmd in deployment_commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.channel.recv_exit_status()
    
    print("Done! Bot deployed and starting.")
    ssh.close()

if __name__ == "__main__":
    deploy()
