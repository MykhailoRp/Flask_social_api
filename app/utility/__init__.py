from datetime import datetime

def int_timestamp():
    return int(round(datetime.utcnow().timestamp()))

