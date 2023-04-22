from __future__ import annotations

import os
from dotenv import load_dotenv
from typing import Final

load_dotenv()

#thing for replit
try:
    #if it possible
    # os.environ['token']
    # os.getenv("mongo_uri")
    TOKEN = os.environ['token']
    MONGODB_URI = os.getenv("mongo_uri")
except:
    #no replit
    TOKEN = os.getenv("token")
    MONGODB_URI = os.getenv("mongo_uri")
# else:
#     #replit
#     TOKEN = os.environ['token']
#     MONGODB_URI = os.getenv("mongo_uri")