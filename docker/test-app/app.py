from flask import Flask
import os
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello! App is running fine.", 200

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

@app.route('/crash')
def crash():
    os._exit(1)  # forcefully kills the app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

