import os
from dotenv import load_dotenv

load_dotenv()

# Database related 
DATABASE_URL = os.getenv("DATABASE_URL")
SQLALCHEMY_POOL_SIZE = int(os.getenv("SQLALCHEMY_POOL_SIZE"))
SQLALCHEMY_MAX_OVERFLOW = int(os.getenv("SQLALCHEMY_MAX_OVERFLOW"))

# AES key 
AES_KEY = os.getenv("AES_KEY", "226c10029b502d90bc2cdf8a2390a6256c8a799298989089a15c7c0826716ae8")

# Logging level 
LOG_LEVEL = os.getenv("LOG_LEVEL")

# Host and port
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
