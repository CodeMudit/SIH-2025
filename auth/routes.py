from fastapi import APIRouter, HTTPException
import traceback
from auth.models import RegisterUser, LoginUser, UserProfile, Location
from auth.database import users_collection, pwd_context, user_helper
from location_detector.location import get_location_from_coords

router = APIRouter()

@router.post("/register/")
async def register(user: RegisterUser):
    try:
        # Check if phone already exists
        existing_phone = await users_collection.find_one({"phone": user.phone})
        existing_email = await users_collection.find_one({"email": user.email})

        if existing_phone and existing_email : 
            raise HTTPException(status_code=400, detail="Both the phone number and email already registered")

        elif existing_phone :
            raise HTTPException(status_code=400, detail="Phone already registered")
        elif existing_email :
            raise HTTPException(status_code=400, detail="Email already registered")
        

        # Hash password
        hashed_pw = pwd_context.hash(user.password)

        new_user = user.dict()
        if user.lat and user.lon:
            location = get_location_from_coords(user.lat, user.lon)
            new_user["location"] = {
                "lat": user.lat,
                "lon": user.lon,
                "state": location["state"],
                "district": location["district"]
            }
        new_user["password"] = hashed_pw
    

        # Insert into MongoDB
        result = await users_collection.insert_one(new_user)
        return {"message": "User registered successfully", "id": str(result.inserted_id)}
    except Exception as e:
        print(f"Error in /register: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/login")
async def login(user: LoginUser):
    try:
        existing_user = await users_collection.find_one({"phone": user.phone})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        if not pwd_context.verify(user.password, existing_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid password")

        return {"message": f"Welcome {existing_user['name']}, login successful!"}
    except Exception as e:
        print(f"Error in /login: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/profile/{phone}", response_model=UserProfile)
async def get_profile(phone: str):
    try:
        user = await users_collection.find_one({"phone": phone})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        profile = {
            "name": user.get("name"),
            "phone": user.get("phone"),
            "email": user.get("email"),
            "land_size": user.get("land_size"),
            "location": user.get("location"),
        }

        # Normalize location into expected shape if present
        if profile["location"] and isinstance(profile["location"], dict):
            loc = profile["location"]
            profile["location"] = Location(
                lat=loc.get("lat"),
                lon=loc.get("lon"),
                state=loc.get("state"),
                district=loc.get("district"),
            )

        return UserProfile(**profile)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /profile/{{phone}}: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")