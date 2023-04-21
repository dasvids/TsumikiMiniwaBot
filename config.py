from __future__ import annotations

import os
from dotenv import load_dotenv
from typing import Final

load_dotenv()

TOKEN = os.getenv("token")

MONGODB_URI = os.getenv("mongo_uri")