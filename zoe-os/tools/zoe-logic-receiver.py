import socket, time, requests, base64, os

# 从环境变量获取 Token，确保安全 (Zoe-OS Compliance)
TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "akayj/openclaw-self-class"

def github_push(file_path):
    if not TOKEN:
        print("❌ [GitHub] Missing TOKEN. Please set GITHUB_TOKEN environment variable.")
        return False
        
    print(f"🚀 [GitHub] Syncing {file_path}...")
    url = f"https://api.github.com/repos/{REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        sha = r.json()["sha"]
        content = r.json()["content"]
        payload = {"message": "Zoe-OS Triggered Sync (Secured)", "content": content, "sha": sha}
        res = requests.put(url, headers=headers, json=payload)
        print(f"✅ [GitHub] Sync Result: {res.status_code}")
        return True
    return False

def logic_loop():
    sock_path = "/tmp/zoe.sock"
    signal_trigger = "/root/.openclaw/workspace/zoe-os/sandbox/URGENT_SYNC.signal"
    
    while True:
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(sock_path)
            data = client.recv(1024).decode().strip()
            if "GITHUB_SYNC" in data:
                print(f"🧠 [Mind] Processing Intent: {data}")
                if github_push("notes/ops.md"):
                    if os.path.exists(signal_trigger):
                        os.remove(signal_trigger)
                        print("🛡️ [Balance] Physical Signal Balanced.")
            client.close()
        except Exception:
            pass
        time.sleep(1)

if __name__ == "__main__":
    logic_loop()
