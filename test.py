import pyotp
import time
import os


def otp():
    key = "geibifdbiknsnvhfsnidnslsdubsdbdnosibkcsdvbdbdfg"
    totp = pyotp.TOTP(key)
    
    print(totp.now())
    
    code = input("Enter 2FA code:")
    print(totp.verify(code))
    
    
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHBpcmVzIjoxNzQyOTQ3NTY3Ljc2Mzk1ODV9.gBZq-quz7UHV0IN5J7udhEMtQ_HB4Ttq1RCOJh38GJQ"
    
if __name__ == "__main__":
    otp()