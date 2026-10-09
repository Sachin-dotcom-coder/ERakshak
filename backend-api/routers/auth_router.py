import os
import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import random

load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# In-memory dictionary to store active OTPs for each email
otp_store = {}
OTP_REQUEST_WINDOW_SECONDS = 60
OTP_EMAIL_LIMIT = 3
OTP_IP_LIMIT = 10
OTP_RATE_LIMIT_CAPACITY = 10_000
otp_request_times = defaultdict(deque)

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

def _check_otp_request_limit(key: str, limit: int, now: float) -> None:
    if key not in otp_request_times and len(otp_request_times) >= OTP_RATE_LIMIT_CAPACITY:
        cutoff = now - OTP_REQUEST_WINDOW_SECONDS
        expired_keys = [
            stored_key for stored_key, times in otp_request_times.items()
            if not times or times[-1] <= cutoff
        ]
        for stored_key in expired_keys:
            del otp_request_times[stored_key]
        if len(otp_request_times) >= OTP_RATE_LIMIT_CAPACITY:
            oldest_key = next(iter(otp_request_times))
            del otp_request_times[oldest_key]

    request_times = otp_request_times[key]
    cutoff = now - OTP_REQUEST_WINDOW_SECONDS
    while request_times and request_times[0] <= cutoff:
        request_times.popleft()

    if len(request_times) >= limit:
        retry_after = max(1, int(request_times[0] + OTP_REQUEST_WINDOW_SECONDS - now))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP requests. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    request_times.append(now)


@router.post("/request-otp")
async def request_otp(data: OTPRequest, request: Request):
    allowed_emails = {
        email.strip().lower()
        for email in os.getenv("AUTHORIZED_EMAILS", "").split(",")
        if email.strip()
    }
    if not allowed_emails:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OTP access is not configured.",
        )

    email = str(data.email).strip().lower()
    if email not in allowed_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This email is not authorized to request an OTP.",
        )

    now = time.monotonic()
    client_ip = request.client.host if request.client else "unknown"
    _check_otp_request_limit(f"email:{email}", OTP_EMAIL_LIMIT, now)
    _check_otp_request_limit(f"ip:{client_ip}", OTP_IP_LIMIT, now)

    # Generate a new random 6-digit number on every request
    generated_otp = f"{random.randint(100000, 999999)}"
    
    # Store it in memory mapped to the user's email
    otp_store[email] = generated_otp

    # Print dynamically to your FastAPI terminal
    print("\n" + "=" * 50)
    print(f"[DYNAMIC DEV OTP] Code for {email}: {generated_otp}")
    print("=" * 50 + "\n")

    return {"message": "OTP generated successfully"}

@router.post("/verify-otp")
async def verify_otp(data: OTPVerify):
    stored_otp = otp_store.get(data.email)

    if not stored_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No OTP requested for this email."
        )

    # Check if user input matches the generated code
    if stored_otp != data.otp.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid OTP code. Check your terminal output."
        )

    # Clean up OTP after successful verification
    del otp_store[data.email]

    return {
        "access_token": f"erakshak_jwt_{random.randint(1000, 9999)}",
        "token_type": "bearer",
        "role": "operator"
    }