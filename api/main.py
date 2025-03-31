from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
import logging
import tempfile
from datetime import date, datetime, timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

from .auth import (
    Token,
    TokenData,
    Credentials,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Garmin Connect API",
    description="REST API wrapper for Garmin Connect",
    version="0.1.0",
)

# Rate limiting error handling
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class DateRange(BaseModel):
    start_date: date
    end_date: date

# Dependency to get Garmin client
async def get_garmin_client(credentials: TokenData = Depends(get_current_active_user)) -> Garmin:
    try:
        # Create temporary directory for tokens
        # temp_dir = tempfile.mkdtemp()
        # logger.info(f"Created temporary directory for tokens: {temp_dir}")
        
        # Try to use temporary directory for tokens
        api = Garmin(credentials.email, credentials.password)
    
        logger.info(f"Authenticating user: {credentials.email}")
        # login() is not an async method
        api.login()
        return api
    except (GarminConnectAuthenticationError, GarminConnectConnectionError) as err:
        logger.error(f"Authentication error: {err}")
        raise HTTPException(status_code=401, detail=str(err))
    except Exception as err:
        logger.error(f"Unexpected error: {err}")
        raise HTTPException(status_code=500, detail=str(err))

@app.post("/token", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        logger.info(f"Login attempt for user: {form_data.username}")
        
        # Create temporary directory for tokens
        # temp_dir = tempfile.mkdtemp()
        # logger.info(f"Created temporary directory for tokens: {temp_dir}")
        
        # Try to use temporary directory
        api = Garmin(form_data.username, form_data.password)
            
        # logger.info("Calling login() method for Garmin Connect API")
        api.login()

        logger.info("Successfully authenticated with Garmin Connect API")
        
        # Create a token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": form_data.username, "password": form_data.password},
            expires_delta=access_token_expires
        )        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_at": datetime.utcnow() + access_token_expires
        }
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=f"Incorrect username or password: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/")
async def root():
    return {"message": "Welcome to Garmin Connect API"}

@app.get("/user/profile")
@limiter.limit("30/minute")
async def get_user_profile(
    request: Request,
    api: Garmin = Depends(get_garmin_client)
):
    try:
        return api.get_user_summary()
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/activities")
@limiter.limit("30/minute")
async def get_activities(
    request: Request,
    start_date: date,
    end_date: date,
    api: Garmin = Depends(get_garmin_client)
):
    try:
        return api.get_last_activity()
    except Exception as e:
        logger.error(f"Error retrieving activities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats-and-body")
@limiter.limit("30/minute")
async def get_stats(
    request: Request,
    date: date,
    api: Garmin = Depends(get_garmin_client)
):
    try:
        return api.get_stats_and_body(date.isoformat())
    except Exception as e:
        logger.error(f"Error retrieving stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/body-composition")
@limiter.limit("30/minute")
async def get_body_composition(
    request: Request,
    date_range: DateRange,
    api: Garmin = Depends(get_garmin_client)
):
    try:
        return api.get_body_composition(
            date_range.start_date.isoformat(),
            date_range.end_date.isoformat()
        )
    except Exception as e:
        logger.error(f"Error retrieving body composition data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/steps")
@limiter.limit("30/minute")
async def get_steps(
    request: Request,
    date: date,
    api: Garmin = Depends(get_garmin_client)
):
    try:
        return api.get_steps_data(date.isoformat())
    except Exception as e:
        logger.error(f"Error retrieving steps data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/heart-rate")
@limiter.limit("30/minute")
async def get_heart_rate(
    request: Request,
    date: date,
    api: Garmin = Depends(get_garmin_client)
):
    try:
        return api.get_heart_rates(date.isoformat())
    except Exception as e:
        logger.error(f"Error retrieving heart rate data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sleep")
@limiter.limit("30/minute")
async def get_sleep(
    request: Request,
    date: date,
    api: Garmin = Depends(get_garmin_client)
):
    try:
        return api.get_sleep_data(date.isoformat())
    except Exception as e:
        logger.error(f"Error retrieving sleep data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stress")
@limiter.limit("30/minute")
async def get_stress(
    request: Request,
    date: date,
    api: Garmin = Depends(get_garmin_client)
):
    try:
        return api.get_stress_data(date.isoformat())
    except Exception as e:
        logger.error(f"Error retrieving stress data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/body-battery")
@limiter.limit("30/minute")
async def get_body_battery(
    request: Request,
    date_range: DateRange,
    api: Garmin = Depends(get_garmin_client)
):
    try:
        return api.get_body_composition(
            date_range.start_date.isoformat(),
            date_range.end_date.isoformat()
        )
    except Exception as e:
        logger.error(f"Error retrieving body battery data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get("/fitness-age")
@limiter.limit("30/minute")
async def get_fitness_age(
    request: Request,
    date: date,
    api: Garmin = Depends(get_garmin_client)
):
    try:
        return api.get_fitnessage_data(
            date.isoformat()
        )
    except Exception as e:
        logger.error(f"Error retrieving fitness age data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 