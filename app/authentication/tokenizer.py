import jwt
from time import time

def generate_token(u_id, u_pass_hash):
    return jwt.encode({"id": u_id, "expires": int(time())}, u_pass_hash, algorithm="HS256")