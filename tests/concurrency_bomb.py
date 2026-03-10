import socket, threading, time

def hit_the_bus(id):
    sock_path = "/tmp/zoe-bus.sock"
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(sock_path)
        msg = f"{{\"client\": {id}, \"intent\": \"STRESS_TEST\"}}"
        client.send(msg.encode())
        res = client.recv(1024)
        print(f"✅ Client {id} Response: {res.decode().strip()}")
        client.close()
    except Exception as e:
        print(f"❌ Client {id} Failed: {e}")

if __name__ == "__main__":
    print("🚀 Zoe-OS Bus Concurrency Bombing starting...")
    threads = []
    for i in range(20): # 先试 20 个并发
        t = threading.Thread(target=hit_the_bus, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    print("\n🏁 Test Finished.")
