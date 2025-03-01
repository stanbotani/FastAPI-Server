import os
import subprocess
import time

# ✅ Step 1: Ensure We're in the Correct Directory
PROJECT_DIR = r"C:\Users\jimmy\OneDrive\Documents\Server"
os.chdir(PROJECT_DIR)
print(f"📂 Changed working directory to: {os.getcwd()}")

# ✅ Step 2: Ensure Dependencies Are Installed
print("🔄 Checking for missing dependencies...")
subprocess.run("pip install -r requirements.txt", shell=True, check=True)

# ✅ Step 3: Start FastAPI Server
print("🚀 Starting FastAPI Server...")
server_process = subprocess.Popen("uvicorn Server:app --host 127.0.0.1 --port 8000 --reload", shell=True)

# ✅ Step 4: Give Server Time to Start
time.sleep(5)  # Wait for FastAPI to fully initialize

# ✅ Step 5: Run API Test (Check If Server is Running)
import requests
try:
    response = requests.get("http://127.0.0.1:8000/ping")
    if response.status_code == 200:
        print("✅ FastAPI is running successfully!")
    else:
        print("⚠️ FastAPI responded with unexpected status:", response.status_code)
except requests.exceptions.RequestException:
    print("❌ Error: FastAPI server is not responding.")
    server_process.terminate()
    exit(1)

# ✅ Step 6: Commit and Push to GitHub
print("📤 Pushing updates to GitHub...")
subprocess.run("git add .", shell=True, check=True)
subprocess.run('git commit -m "Auto-update and deploy FastAPI Server"', shell=True, check=True)
subprocess.run("git push origin main", shell=True, check=True)

# ✅ Step 7: Print Final Success Message
print("🎉 All tasks completed successfully!")
print("🚀 FastAPI is running at http://127.0.0.1:8000/docs")
print("📤 Updates have been pushed to GitHub.")

# ✅ Step 8: Keep Server Running
server_process.wait()