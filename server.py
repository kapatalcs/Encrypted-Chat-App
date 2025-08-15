import socket
import threading
import json

HOST = '0.0.0.0'
PORT = 12345

clients = {}
lock = threading.Lock()

def start_server():
    print(f"Starting server... {HOST}:{PORT}")
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((HOST,PORT))
    server.listen()

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn,addr))
        thread.start()

def receive_line(conn, buffer):
    try:
        data = conn.recv(8192).decode()
        if not data:
            conn.close()
            return None,buffer
        buffer += data
        if "\n" not in buffer:
            while "\n" not in buffer:
                buffer += conn.recv(8192).decode()
        line, buffer = buffer.split("\n", 1)
        return line,buffer
    except (ConnectionResetError, ConnectionAbortedError):
        return None, buffer
    except Exception as e:
        print(f"[!] receive_line error: {e}")
        return None, buffer

def add_client(conn, username, public_key):
    with lock:
        clients[conn] = {"username": username, "public_key": public_key}

def send_line(conn,data):
    conn.sendall((json.dumps(data) + "\n").encode())
def send_user_list(conn):
    user_list = []
    with lock:
        for c in clients:
            user_list.append({
                "username": clients[c]["username"],
                "public_key": clients[c]["public_key"]
            })
    send_line(conn,{"type":"user_list","users": user_list})
    
def broadcast_new_user(new_user):
    data = {"type": "new_user", "user": new_user}
    with lock:
        for c in clients:
            try:
                send_line(c,data)
            except:
                c.close()
                del clients[c]


def get_conn_by_username(username):
    with lock:
        for c, user in clients.items():
            if user["username"] == username:
                return c
    return None

def remove_client(conn):
    with lock:
        if conn in clients:
            del clients[conn]

def process_message(msg_obj, conn):
    if msg_obj.get("type") == "message":
        targets = msg_obj.get("to")
        if isinstance(targets, str):
            targets = [targets]

        for target_username in targets:
            target_conn = get_conn_by_username(target_username)
            if target_conn:
                try:
                    send_line(target_conn, msg_obj)
                except Exception:
                    remove_client(target_conn)
                    target_conn.close()
    else:
        pass
def list_request(msg_obj,conn):
    if msg_obj.get("type") == "user_list_request":
        send_user_list(conn)

def handle_client(conn, addr):
    print(f"[+] New connection: {addr}")
    buffer = ""
    line, buffer = receive_line(conn,buffer)
    if line is None:
        conn.close()
        return   
    try:
        user_data = json.loads(line)
        username = user_data["username"]
        public_key = user_data["public_key"]

        add_client(conn,username,public_key)
        send_user_list(conn)
        broadcast_new_user({"username": username, "public_key": public_key})
        
        print(f"[i] {username} ({addr}) is connected")

    except Exception as e:
        print(f"[!] Connection error: {e}")
        conn.close()
        return

    while True:
        line, buffer = receive_line(conn,buffer)
        if line is None:
            break
        if not line.strip():
            continue
        try:
            msg_obj = json.loads(line)
            if list_request(msg_obj,conn):
                continue
            process_message(msg_obj, conn)
        except Exception as e:
            print(f"[!] Error: {e}")
            break

    print(f"[-] Disconnected: {addr}")
    with lock:
        if conn in clients:
            del clients[conn]
    conn.close()


if __name__ == "__main__":
    start_server()