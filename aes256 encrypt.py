#import crypto
#import sys
#sys.modules['Crypto'] = crypto

import base64
import time
from Crypto import Random
from Crypto.Cipher import AES

time.clock = time.time

BS = 16
pad = lambda s: s + (BS - len(s.encode('utf-8')) % BS) * chr(BS - len(s.encode('utf-8')) % BS)
unpad = lambda s : s[:-ord(s[len(s)-1:])]

class AESCipher:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw.encode('utf-8') ) )

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] ))
    
key = "GAYDAMBQGAYDAMBQGAYDAMBQGA======"
key = key.encode('utf-8')
data = "123456"

encrypted_data = AESCipher(bytes(key)).encrypt(data)  
print(encrypted_data.decode('utf-8'))
decrypted_data = AESCipher(bytes(key)).decrypt(encrypted_data)

print(decrypted_data.decode('utf-8'))
