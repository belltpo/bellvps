from hashlib import md5
from Crypto.Cipher import AES
import base64

def pad(data):
    pad_len = 16 - len(data) % 16
    return data + (chr(pad_len) * pad_len)

def encrypt(plainText, workingKey):
    key = md5(workingKey.encode('utf-8')).digest()  # AES-128 key
    plainText = pad(plainText)
    cipher = AES.new(key, AES.MODE_ECB)  # ECB mode, no IV
    encryptedText = cipher.encrypt(plainText.encode('utf-8'))
    return base64.b64encode(encryptedText).decode('utf-8')

def decrypt(encText, workingKey):
    key = md5(workingKey.encode('utf-8')).digest()
    encText = base64.b64decode(encText)
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(encText)
    pad_len = decrypted[-1]
    return decrypted[:-pad_len].decode('utf-8')
