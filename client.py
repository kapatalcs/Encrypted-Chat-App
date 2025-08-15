import socket
import threading
import json
from rsa_utils import generate_key_pair, encrypt_with_public_key, decrypt_with_private_key
import sys

SERVER_HOST = "ServerIP"
SERVER_PORT = 12345

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST,SERVER_PORT))
except ConnectionRefusedError:
    print("Server is down. Please try again later.")
    sys.exit()
    

username = input("Enter username: ")
while True:
    if "," in username:
        username = input("Username cannot contain a comma. Please retry: ")
    else:
        break
print("\nTo send a message: /msg target_username message")
print("To get help: /help")

private_key, public_key = generate_key_pair()
users_lock = threading.Lock()

def send_line(sock, data):
    sock.sendall((json.dumps(data) + "\n").encode())

initial_data = {
    "username": username,
    "public_key": public_key.decode()
}
send_line(client, initial_data)

users = {}
buffer = ""
def receive_messages():
    global users,buffer
    while True:
        try:
            data = client.recv(8192).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n",1)
                if not line.split():
                    continue
                msg = json.loads(line)
                msg_type = msg.get("type")

                if msg_type == "user_list":
                    with users_lock:
                        users = {u["username"]:u["public_key"] for u in msg["users"]}
                        print("\n📋 Online users:")
                        for u in users:
                            print("-", u)
                
                elif msg_type == "new_user":
                    new_u = msg["user"]
                    users[new_u["username"]] = new_u["public_key"]
                    print(f"\n🆕 New user is connected: {new_u['username']}")
                
                elif msg_type == "message":
                    sender = msg.get("from")
                    encrypted_message = msg.get("message")
                    try:
                        decrypted = decrypt_with_private_key(private_key, encrypted_message)
                        print(f"\n📩 {sender}: {decrypted}")
                    except Exception as e:
                        print(f"\n🚫 Error while decoding {sender}'s message: {e}")
                else:
                    print(f"\n⚠️ Unknown message type: {msg_type}")

        except Exception as e:
            print(f"\n❌ Connection error: {e}")
            break

def send_messages():
    while True:
        command = input()
        if command.strip()== "":
            print()
            continue

        elif command == "/help":
            print("- To send a message to everyone: /msg all message")
            print("- To send a message a to specific user: /msg target_username message")
            print("- To send a message to multiple users: /msg target_username1,target_username2.... message")
            print("- To view users who are online: /list")
            
        elif command == "/list":
            send_line(client, {"type": "user_list_request"})

        elif command.startswith("/msg "):
            try:
                parts = command.split(' ',2)
                if len(parts) < 3:
                    print("⚠️ Usage: /msg target_username(s) message")
                    break
                targets_raw, message = parts[1], parts[2]

                if targets_raw.lower() == "all":
                    with users_lock:
                        to_list = [u for u in users if u != username]
                        for user in to_list:
                            target_public_key = users[user].encode()
                            encrypted_msg = encrypt_with_public_key(target_public_key,message)
                            msg_data = {
                                "type":"message",
                                "from":username,
                                "to":user,
                                "message": encrypted_msg
                            }
                            send_line(client,msg_data)
                else:
                    targets = [t.strip() for t in targets_raw.split(',') if t.strip()]
                    with users_lock:
                        invalid_targets = [t for t in targets if t not in users or t == username]
                        valid_targets = [t for t in targets if t in users or t != username]
                    if invalid_targets:
                        if username in invalid_targets:
                            print("You cannot send messages to yourself")
                        else:
                            print(f"⚠️ User(s) not found: {', '.join(invalid_targets)}")
                        continue
                    for target in valid_targets:
                        with users_lock:
                            target_public_key = users[target].encode()
                        encrypted_msg = encrypt_with_public_key(target_public_key,message)
                        msg_data = {
                            "type":"message",
                            "from":username,
                            "to":target,
                            "message": encrypted_msg
                        }
                        send_line(client, msg_data)
            except Exception as e:
                print(f"⚠️ Error sending message: {e}")
        else:
            print("Invalid command. To get help: /help")

recv_thread = threading.Thread(target=receive_messages, daemon=True)
recv_thread.start()

send_messages()

