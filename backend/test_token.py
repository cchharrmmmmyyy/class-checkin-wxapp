import sys
sys.path.insert(0, '.')

from config import Config
print(f"SECRET_KEY: {Config.SECRET_KEY}")

from utils.auth import decode_token

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWRtaW4wMDEiLCJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIiwiY2xhc3MiOm51bGwsImV4cCI6MTc3Njk0MTAxNCwiaWF0IjoxNzc2ODU0NjE0fQ.IpIG5CcGEv821yeTCaG_NOhNl-HS2qUhw4EyW2AFNis'

try:
    payload = decode_token(token)
    print(f"Token decode result: {payload}")
    print(f"Role check: {payload.get('role') == 'admin'}")
except Exception as e:
    print(f"Error: {e}")