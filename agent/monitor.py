import docker
import psutil
import time
from datetime import datetime
from claude_agent import run_agent

# Connect to Docker
client = docker.from_env()

# Settings
CONTAINERS_TO_WATCH = ['web-app']
CHECK_INTERVAL = 10  # check every 10 seconds
CPU_THRESHOLD = 80
MEMORY_THRESHOLD = 80

def get_container_status(name):
    try:
        container = client.containers.get(name)
        return container.status
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

    # Track previous state to avoid duplicate alerts
    previous_status = {}

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Checking...")

        for name in CONTAINERS_TO_WATCH:
            status = get_container_status(name)

            if status == "running":
                print(f"✅ {name} is RUNNING")
                previous_status[name] = "running"

            elif status != previous_status.get(name):
                # Status changed → alert + diagnose
                print(f"⚠️  {name} is {status.upper()}")
                logs = get_container_logs(name)
                print(f"    Last logs:\n{logs}")

                # Ask AI to diagnose
                diagnosis = run_agent(name, status, logs)
                print(f"\n🤖 AI Diagnosis:\n{diagnosis}")
                print("-" * 50)

                previous_status[name] = status

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
