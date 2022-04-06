from encodings import utf_8
import socketserver
import threading
import pyotp
from datetime import date, datetime, timezone, timedelta
import pytz
import base64
import time
from Crypto import Random
from Crypto.Cipher import AES

time.clock = time.time

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-ord(s[-1])]




HOST = 'ec2-13-209-98-41.ap-northeast-2.compute.amazonaws.com'
PORT = 4000
lock = threading.Lock() # syncronized 동기화 진행하는 스레드 생성
otp_key = 'QWERQWERQWERQWERQWERQWERQWERQWER'
key = otp_key.encode('utf-8')
totp = pyotp.TOTP(otp_key, interval = 60)
KST = pytz.timezone('Asia/Seoul')
time_record = datetime.now(KST)


class UserManager: # 사용자관리 및 채팅 메세지 전송을 담당하는 클래스
				   # ① 채팅 서버로 입장한 사용자의 등록
				   # ② 채팅을 종료하는 사용자의 퇴장 관리
				   # ③ 사용자가 입장하고 퇴장하는 관리
				   # ④ 사용자가 입력한 메세지를 채팅 서버에 접속한 모두에게 전송

   def __init__(self):
      self.users = {} # 사용자의 등록 정보를 담을 사전 {사용자 이름:(소켓,주소),...}

   def addUser(self, username, conn, addr): # 사용자 ID를 self.users에 추가하는 함수
      if username in self.users: # 이미 등록된 사용자라면
         conn.send('%s' %totp.now().encode())
         return None

      # 새로운 사용자를 등록함
      lock.acquire() # 스레드 동기화를 막기위한 락
      self.users[username] = (conn, addr)
      lock.release() # 업데이트 후 락 해제
      beforeCipher = pad(totp.now())
      cipher = AES.new(otp_key, AES.MODE_CBC, IV=iv)
      afterCipher = base64.b64encode(cipher.encrypt(beforeCipher))
      self.sendMessageToAll('%s' %afterCipher.decode('utf-8'))
      return username

   def removeUser(self, username): #사용자를 제거하는 함수
      if username not in self.users:
         return

      lock.acquire()
      del self.users[username]
      lock.release()

      self.sendMessageToAll('%s' %totp.now())

   def messageHandler(self, username, msg): # 전송한 msg를 처리하는 부분
      if msg[0] != '/': # 보낸 메세지의 첫문자가 '/'가 아니면
         beforeCipher = pad(totp.now())
         cipher = AES.new(otp_key, AES.MODE_CBC, IV=iv)
         afterCipher = base64.b64encode(cipher.encrypt(beforeCipher))
         self.sendMessageToAll('%s' %afterCipher.decode('utf-8'))
         return

      if msg.strip() == '/quit': # 보낸 메세지가 'quit'이면
         self.removeUser(username)
         return -1

   def sendMessageToAll(self, msg):
      for conn, addr in self.users.values():
         conn.send(msg.encode())
         
          

class MyTcpHandler(socketserver.BaseRequestHandler):
   userman = UserManager()
    
   def handle(self): # 클라이언트가 접속시 클라이언트 주소 출력

      try:
         username = self.registerUsername()
         msg = self.request.recv(1024)
         print('%s[%s] Connected' %(username, self.client_address[0]))
         now = datetime.now(KST)
         nowTime = now.strftime('%H:%M:%S')  
         print("totp.now : %s, now time : %s"  %(totp.now(), nowTime))
         while msg:
            print(msg.decode())
            if self.userman.messageHandler(username, msg.decode()) == -1:
               self.request.close()
               break
            msg = self.request.recv(1024)
                
      except Exception as e:
         print(e)

      self.userman.removeUser(username)

   def registerUsername(self):
      while True:
         username = self.request.recv(1024)
         username = username.decode().strip()
         if self.userman.addUser(username, self.request, self.client_address):
            return username

class ChatingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
        
def runServer():
   global iv 
   iv = '0123456789012345' # 16bit
   now = datetime.now(KST)
   nowTime = now.strftime('%H:%M:%S')  
   print('+++ Running Server. now time : '+nowTime)
   print("totp.now : " + totp.now())
   beforeCipher = pad(totp.now())
   cipher = AES.new(otp_key, AES.MODE_CBC, IV=iv)
   afterCipher = base64.b64encode(cipher.encrypt(beforeCipher))
   print(afterCipher.decode('utf-8'))
   try:
      server = ChatingServer((HOST, PORT), MyTcpHandler)
      server.serve_forever()
   except KeyboardInterrupt:
      print('--- Close server.')
      server.shutdown()
      server.server_close()

runServer()
