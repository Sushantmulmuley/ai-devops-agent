import docker
import requests
import os
from dotenv import load_dotenv

load_dotenv()

client = docker.from_env()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def restart_container(container_name):
    """Restart a Docker container"""
    try:
        container = client.containers.get(container_name)
        container.restart()
        return f"✅ Successfully restarted {container_name}"
    except docker.errors.NotFound:
        return f"❌ Container {container_name} not found"
    except Exception as e:
        return f"❌ Failed to restart {container_name}: {str(e)}"

def get_logs(container_name, lines=20):
    """Get last N lines of container logs"""
    try:
        container = client.containers.get(container_name)
        logs = container.logs(tail=lines).decode('utf-8')
        return logs
    except docker.errors.NotFound:
        return f"❌ Container {container_name} not found"
    except Exception as e:
        return f"❌ Could not fetch logs: {str(e)}"

def send_alert(message):
    """Send real Slack alert"""
    try:
        payload = {
            "text": f":rotating_light: *DevOps Agent Alert*\n{message}"
        }
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            print(f"\n🚨 Slack alert sent!")
            return "Slack alert sent successfully"
        else:
            return f"Failed to send Slack alert: {response.status_code}"
    except Exception as e:
        return f"❌ Slack error: {str(e)}"

# Tool definitions for AI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "restart_container",
            "description": "Restart a Docker container that is down or crashed",
            "parameters": {
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Name of the container to restart"
                    }
                },
                "required": ["container_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_logs",
            "description": "Get recent logs from a container",
            "parameters": {
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Name of the container"
                    }
                },
                "required": ["container_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_alert",
            "description": "Send a Slack alert message about an incident",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Alert message to send"
                    }
                },
                "required": ["message"]
            }
        }
    }
]

# Map tool names to actual functions
TOOL_MAP = {
    "restart_container": restart_container,
    "get_logs": get_logs,
    "send_alert": send_alert
}
