import os
import json
from groq import Groq
from dotenv import load_dotenv
from tools import TOOLS, TOOL_MAP

# Load API key from .env file
load_dotenv()

# Connect to Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_agent(container_name, status, logs):
    """AI agent that diagnoses AND fixes problems using tools"""
    
    print(f"\n🤖 AI Agent activated for {container_name}...")
    
    messages = [
        {
            "role": "system",
            "content": "You are a DevOps agent. When a container fails, analyze the situation and use the available tools to fix it. Always restart crashed containers and send an alert explaining what happened."
        },
        {
            "role": "user",
            "content": f"Container '{container_name}' is {status}. Last logs:\n{logs}\n\nPlease diagnose and fix this issue."
        }
    ]

    # Agentic loop
    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=500,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        msg = response.choices[0].message

        # If AI wants to call a tool
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                print(f"🔧 AI calling tool: {tool_name}({tool_args})")

                # Execute the tool
                tool_func = TOOL_MAP[tool_name]
                result = tool_func(**tool_args)

                print(f"   Result: {result}")

                # Add tool result back to messages
                messages.append({"role": "assistant", "tool_calls": msg.tool_calls})
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

        else:
            # AI is done — print final response
            print(f"\n✅ AI Agent finished:")
            print(msg.content)
            break

if __name__ == '__main__':
    # Test the agent
    run_agent(
        container_name="web-app",
        status="exited",
        logs="Error: Connection refused\nContainer stopped unexpectedly"
    )
