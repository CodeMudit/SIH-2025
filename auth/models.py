
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
class RegisterUser(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=10)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=8)
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    land_size: float = Field(..., gt=0)

    @validator("phone")
    def must_be_ten_digits(cls, v):
        if not v.isdigit():
            raise ValueError("Phone must contain only digits")
        if len(v) != 10:
            raise ValueError("Please enter a valid 10-digit phone number")
        return v
    
    @validator("email")
    def validate_email(cls, v):
        if v:
            if "@" not in v:
                raise ValueError("Invalid Email Format")
            
        return v
    
    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be 8 characters long")
        return v
    
    @validator("land_size")
    def validate_land_size(cls, v):
        if v<=0:
            raise ValueError("Land Size Must be positive")
        
        return v
    
    # class Config:
    #     extra = "Ignore"




class LoginUser(BaseModel):
    phone: str
    password: str


class Location(BaseModel):
    lat: float
    lon: float
    state: Optional[str] = None
    district: Optional[str] = None


class UserProfile(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    location: Optional[Location] = None
    land_size: Optional[float] = None
