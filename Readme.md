# Encrypted Chat App 

This project is a multi-user CLI-based chat application developed using Python with **RSA encryption** support.
Clients obtain each other's **public keys** via the server, and messages are transmitted between clients in an **end-to-end encrypted** manner.
---

## Features
- Multi-user chat
- **End-to-end encryption** with RSA 2048-bit
- Send messages to one person, everyone, or multiple users with the `/msg` command
- List online users with the `/list` command
- Automatic notification when a new user connects

---

## Requirement
- Python 3.8+
- [PyCryptodome](https://pypi.org/project/pycryptodome/)

For installation:
```bash
pip install pycryptodome
```

---

## Running

# For server
1. **Start the server:**
```bash
python server.py
```

# For client
1. **Start the client:**
```bash
python client.py
```

2. **Enter your username and follow the instructions.**

---

## Commands
| Command | Explanation |
|-------|----------|
| `/msg all <message>` | Sends a message to all users |
| `/msg user <message>` | Sends a message to the specified user |
| `/msg user1,user2 <message>` | Sends messages to multiple users|
| `/list` | Lists online users |
| `/help` | Displays help commands |


## Notes
There is no requirement to have one client per IP. The number of clients you open will determine the number of users.
If you want to use the program globally instead of locally, don't forget to set up port forwarding on your modem.

## Security Note
This project has been developed for **learning purposes**. Additional security measures and error management should be implemented for use in the real world.
---

## License
MIT License – You are free to use, modify, and distribute this code.

## Author 
Yusuf İslam ÖZAYDIN 
