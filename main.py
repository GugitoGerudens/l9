from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import jwt
import uvicorn
import os
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

# App Configuration
app = FastAPI(title="Bonus Program Service")
SECRET_KEY = "qwerty"  # Replace with a strong key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mock user data
users_db = {
    "geruto": {
        "username": "geruto",
        "password": "zxc"
    }
}

# Mock bonus program data
bonus_levels = [
    {"level": "Silver", "min_spend": 0, "max_spend": 999, "cashback": 1},
    {"level": "Gold", "min_spend": 1000, "max_spend": 4999, "cashback": 2},
    {"level": "Platinum", "min_spend": 5000, "max_spend": None, "cashback": 3},
]

user_spending = {
    "geruto": 1200  # Mock user spending
}


def get_user_spending_level(spending):
    for level in bonus_levels:
        if level["max_spend"] is None or spending <= level["max_spend"]:
            return level


# Pydantic Models
class Token(BaseModel):
    access_token: str
    token_type: str


class BonusLevel(BaseModel):
    level: str
    min_spend: int
    max_spend: Optional[int]
    cashback: int
    spending: int


# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if user and user["password"] == password:
        return user
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/bonus-program", response_model=BonusLevel)
def get_bonus_program(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    username = payload.get("sub")

    if username not in user_spending:
        raise HTTPException(status_code=404, detail="User spending data not found")

    spending = user_spending[username]
    current_level = get_user_spending_level(spending)
    next_level = None

    for level in bonus_levels:
        if level["min_spend"] > spending:
            next_level = level
            break

    return {
        "level": current_level["level"],
        "min_spend": current_level["min_spend"],
        "max_spend": current_level["max_spend"],
        "cashback": current_level["cashback"],
        "spending": spending,
        "next_level": next_level
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
