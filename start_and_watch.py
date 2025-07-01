import subprocess
import webbrowser
import time
import psutil #type: ignore
import socket
import os
import sys

PORT = 8501
URL = f"http://localhost:{PORT}"
APP_CMD = ["streamlit", "run", "app.py", "--server.headless", "true"]

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

def browser_open_to_localhost():
    for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        try:
            cmd = " ".join(proc.info["cmdline"]).lower()
            if "chrome" in cmd or "msedge" in cmd or "firefox" in cmd:
                if "localhost:8501" in cmd or "127.0.0.1:8501" in cmd:
                    return True
        except Exception:
            continue
    return False

def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
    except Exception as e:
        print(f"⚠️ Error terminating process: {e}")

# 1. Start Streamlit
print("🚀 Launching Streamlit app...")
proc = subprocess.Popen(APP_CMD)

# 2. Wait for app to start
while not is_port_in_use(PORT):
    time.sleep(0.5)

# 3. Open browser
print(f"🌐 Opening browser at {URL}")
webbrowser.open(URL)

# 4. Monitor for browser close
try:
    print("🕵️ Monitoring browser... (close tab to terminate)")
    while True:
        time.sleep(3)
        if not browser_open_to_localhost():
            print("❌ Browser tab closed. Killing Streamlit...")
            kill_process_tree(proc.pid)
            break
except KeyboardInterrupt:
    print("\n🛑 Ctrl+C pressed. Terminating Streamlit...")
    kill_process_tree(proc.pid)
    sys.exit(0)
