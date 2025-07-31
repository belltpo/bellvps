from Crypto.Cipher import AES
import hashlib
from binascii import hexlify, unhexlify

#pycryptodome
def pad(data):
    length = 16 - (len(data) % 16)
    return data + (chr(length) * length).encode()

def unpad(data):
    return data[:-data[-1]]

def encrypt(plain_text, working_key):
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    plain_text = pad(plain_text.encode())
    enc_cipher = AES.new(hashlib.md5(working_key.encode()).digest(), AES.MODE_CBC, iv)
    return hexlify(enc_cipher.encrypt(plain_text)).decode()

def decrypt(encrypted_text, working_key):
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    encrypted_text = unhexlify(encrypted_text)
    dec_cipher = AES.new(hashlib.md5(working_key.encode()).digest(), AES.MODE_CBC, iv)
    return unpad(dec_cipher.decrypt(encrypted_text)).decode()
