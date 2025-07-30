from hashlib import md5
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

def encrypt(plain_text, working_key):
    '''
    Encrypts plain text with the working key using AES CBC mode.
    '''
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    key = md5(working_key.encode('latin-1')).digest()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_text = pad(plain_text.encode('latin-1'), AES.block_size)
    encrypted_text = cipher.encrypt(padded_text)
    return base64.b64encode(encrypted_text).decode('latin-1')

def decrypt(encrypted_text, working_key):
    '''
    Decrypts encrypted text with the working key.
    '''
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    key = md5(working_key.encode('latin-1')).digest()
    encrypted_text_bytes = base64.b64decode(encrypted_text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded_text = cipher.decrypt(encrypted_text_bytes)
    decrypted_text = unpad(decrypted_padded_text, AES.block_size)
    return decrypted_text.decode('latin-1')
