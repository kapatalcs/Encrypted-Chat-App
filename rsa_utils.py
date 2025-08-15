from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64


def generate_key_pair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def encrypt_with_public_key(public_key_bytes,message):
    public_key = RSA.import_key(public_key_bytes)
    cipher = PKCS1_OAEP.new(public_key) #padding
    encrypted = cipher.encrypt(message.encode()) #encrpyt with public key
    return base64.b64encode(encrypted).decode()

def decrypt_with_private_key(private_key_bytes,encrypted_message):
    private_key = RSA.import_key(private_key_bytes)
    cipher = PKCS1_OAEP.new(private_key)
    encrypted_data = base64.b64decode(encrypted_message.encode())
    decrypted = cipher.decrypt(encrypted_data) #decrypt with private key
    return decrypted.decode()