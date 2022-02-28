
import pyotp
import datetime

otp_key = 'GAYDAMBQGAYDAMBQGAYDAMBQGA======'

totp = pyotp.TOTP(otp_key)

now = datetime.datetime.now()

print('currunt time : ', now)

print("now totp.at: " + str(totp.at(datetime.datetime.now())) + ", totp.now : " + totp.now())

print('next otp: ', totp.at(int(now.timestamp())+30))


