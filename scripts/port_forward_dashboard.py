import socket
import threading
import select

LOCAL_PORT = 3000
REMOTE_HOST = "172.25.0.8"
REMOTE_PORT = 3000

def handle_client(client_socket):
    try:
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((REMOTE_HOST, REMOTE_PORT))
    except Exception as e:
        print(f"Failed to connect to remote: {e}")
        client_socket.close()
        return

    def forward(src, dst):
        try:
            while True:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
        except:
            pass
        finally:
            src.close()
            dst.close()

    threading.Thread(target=forward, args=(client_socket, remote_socket)).start()
    threading.Thread(target=forward, args=(remote_socket, client_socket)).start()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", LOCAL_PORT))
    server.listen(5)
    print(f"Listening on 0.0.0.0:{LOCAL_PORT} -> {REMOTE_HOST}:{REMOTE_PORT}")

    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client,)).start()

if __name__ == "__main__":
    main()
