import os
import json
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

import redis
import pika
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Local imports (to be implemented)
from database import get_db
from models import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("API")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Pelephone AI Agent System",
    description="API for Pelephone's system of specialized AI agents",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("JWT_SECRET", "development_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Connect to Redis
redis_url = os.getenv("REDIS_URL", "redis://:password@redis:6379/0")
redis_client = redis.from_url(redis_url)

# Connect to RabbitMQ for message handling
rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://pelephone:password@rabbitmq:5672/")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserInDB(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    hashed_password: str

class BillingRequest(BaseModel):
    customer_id: str
    request_type: str
    details: Dict[str, Any]

class InternationalRequest(BaseModel):
    customer_id: str
    request_type: str
    details: Dict[str, Any]

class CustomerSession(BaseModel):
    session_id: str
    customer_id: str
    start_time: str
    agent_assignments: Dict[str, str]

# Helper functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(db, username: str):
    # This would normally query from the database
    # For demonstration purposes, we'll return a mock user
    return {
        "username": username,
        "email": f"{username}@example.com",
        "full_name": "Test User",
        "disabled": False,
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # "password"
    }

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    # In a real app, you would verify the password here
    # For demo purposes, we're accepting any password
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_rabbitmq_connection():
    """Establish a connection to RabbitMQ"""
    return pika.BlockingConnection(pika.URLParameters(rabbitmq_url))

def publish_to_queue(queue_name, message):
    """Publish a message to a RabbitMQ queue"""
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    
    # Ensure queue exists
    channel.queue_declare(queue=queue_name, durable=True)
    
    # Publish message
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            correlation_id=str(uuid.uuid4())
        )
    )
    
    connection.close()

def get_session_data(session_id):
    """Retrieve session data from Redis"""
    session_data = redis_client.get(f"session:{session_id}")
    if session_data:
        return json.loads(session_data)
    return None

def save_session_data(session_id, data):
    """Save session data to Redis"""
    redis_client.setex(
        f"session:{session_id}",
        3600,  # 1 hour expiration
        json.dumps(data)
    )

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to Pelephone AI Agent System API"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/sessions")
async def create_session(customer_id: str, user = Depends(get_current_user)):
    """Create a new customer session"""
    session_id = str(uuid.uuid4())
    session_data = {
        "session_id": session_id,
        "customer_id": customer_id,
        "start_time": datetime.utcnow().isoformat(),
        "user_id": user["username"],
        "active": True,
        "agent_assignments": {}
    }
    
    save_session_data(session_id, session_data)
    
    return {"session_id": session_id, "status": "created"}

@app.get("/sessions/{session_id}")
async def get_session(session_id: str, user = Depends(get_current_user)):
    """Get session details"""
    session_data = get_session_data(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    return session_data

@app.post("/billing/requests")
async def create_billing_request(request: BillingRequest, session_id: str, user = Depends(get_current_user)):
    """Create a new billing request"""
    # Check if session exists
    session_data = get_session_data(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    # Package request for the billing agent
    billing_request = {
        "request_id": request_id,
        "session_id": session_id,
        "customer_id": request.customer_id,
        "type": request.request_type,
        "details": request.details,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Publish to the billing queue
    try:
        publish_to_queue("billing_requests", billing_request)
        
        # Update session with request info
        session_data["last_request"] = {
            "request_id": request_id,
            "type": "billing",
            "timestamp": datetime.utcnow().isoformat()
        }
        save_session_data(session_id, session_data)
        
        return {
            "request_id": request_id,
            "status": "submitted",
            "message": "Billing request submitted successfully"
        }
    except Exception as e:
        logger.error(f"Error publishing to billing queue: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit billing request: {str(e)}"
        )

@app.post("/international/requests")
async def create_international_request(request: InternationalRequest, session_id: str, user = Depends(get_current_user)):
    """Create a new international calls request"""
    # Check if session exists
    session_data = get_session_data(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    # Package request for the international calls agent
    international_request = {
        "request_id": request_id,
        "session_id": session_id,
        "customer_id": request.customer_id,
        "type": request.request_type,
        "details": request.details,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Publish to the international calls queue
    try:
        publish_to_queue("international_requests", international_request)
        
        # Update session with request info
        session_data["last_request"] = {
            "request_id": request_id,
            "type": "international",
            "timestamp": datetime.utcnow().isoformat()
        }
        save_session_data(session_id, session_data)
        
        return {
            "request_id": request_id,
            "status": "submitted",
            "message": "International calls request submitted successfully"
        }
    except Exception as e:
        logger.error(f"Error publishing to international queue: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit international calls request: {str(e)}"
        )

@app.get("/responses/{request_id}")
async def get_response(request_id: str, user = Depends(get_current_user)):
    """Get response for a specific request"""
    # In a real implementation, this would check a responses database or Redis
    # For this example, we'll return a mock response
    return {
        "request_id": request_id,
        "status": "completed",
        "response": {
            "message": "Your billing issue has been resolved",
            "details": {
                "action_taken": "Credit applied",
                "amount": 25.00,
                "effective_date": datetime.utcnow().isoformat()
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)