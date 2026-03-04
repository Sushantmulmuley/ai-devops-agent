import docker
import psutil
import time
from datetime import datetime

# Connect to Docker
client = docker.from_env()

# Settings
CONTAINERS_TO_WATCH = ['web-app']
CHECK_INTERVAL = 10  # check every 10 seconds
CPU_THRESHOLD = 80   # alert if CPU > 80%
MEMORY_THRESHOLD = 80  # alert if memory > 80%

def get_container_status(name):
    try:
        container = client.containers.get(name)
        return container.status  # running, exited, paused
    except docker.errors.NotFound:
        return "not found"

def get_container_logs(name, lines=10):
    try:
        container = client.containers.get(name)
        logs = container.logs(tail=lines).decode('utf-8')
        return logs
    except:
        return "could not fetch logs"

def check_system_resources():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return cpu, memory, disk

def monitor():
    print("🚀 AI DevOps Agent Started - Monitoring...")
    print(f"Watching containers: {CONTAINERS_TO_WATCH}")
    print("-" * 50)

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Checking...")

        # Check each container
        for name in CONTAINERS_TO_WATCH:
            status = get_container_status(name)

            if status == "running":
                print(f"✅ {name} is RUNNING")
            elif status == "not found":
                print(f"❌ {name} NOT FOUND")
            else:
                print(f"⚠️  {name} is {status.upper()}")
                print(f"    Last logs:")
                print(get_container_logs(name))

        # Check system resources
        cpu, memory, disk = check_system_resources()
        print(f"💻 System - CPU: {cpu}% | Memory: {memory}% | Disk: {disk}%")

        if cpu > CPU_THRESHOLD:
            print(f"⚠️  HIGH CPU ALERT: {cpu}%")
        if memory > MEMORY_THRESHOLD:
            print(f"⚠️  HIGH MEMORY ALERT: {memory}%")

        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    monitor()
