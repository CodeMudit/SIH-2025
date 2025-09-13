from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import certifi
import os


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB connection (local or Atlas)
# Prefer environment variables; fall back to sensible local defaults
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "farmerdb")

# Enable TLS only for Atlas (mongodb+srv) or when explicitly requested
use_tls = MONGO_URI.startswith("mongodb+srv://") or os.getenv("MONGO_TLS", "false").lower() == "true"

if use_tls:
    client = AsyncIOMotorClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
else:
    client = AsyncIOMotorClient(MONGO_URI)

db = client[DB_NAME]
users_collection = db["users"]


# Helper to format MongoDB user document
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "phone": user["phone"],
        "email": user.get("email"),
        "password": user["password"],
        "location": user["location"],
        "land_size": user["land_size"]
    }
