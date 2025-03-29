import base64
import os

jwt_secret_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
print(jwt_secret_key)