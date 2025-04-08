from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, index=True)
    phone = Column(String)
    plan = Column(String)
    monthly_charge = Column(Integer)
    contract_end_date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    requests = relationship("Request", back_populates="customer")
    bills = relationship("Bill", back_populates="customer")

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    session_id = Column(String, index=True)
    agent_type = Column(String)  # "billing", "international", or "supervisor"
    request_type = Column(String)
    status = Column(String)  # "pending", "processing", "completed", "error"
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="requests")
    responses = relationship("Response", back_populates="request")

class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(String, unique=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"))
    agent_type = Column(String)
    status = Column(String)
    content = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    request = relationship("Request", back_populates="responses")

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(String, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    month = Column(String)
    year = Column(Integer)
    amount = Column(Integer)
    status = Column(String)  # "pending", "paid", "overdue"
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="bills")

class UserSession(Base):  # Renamed from Session to UserSession
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    active = Column(Boolean, default=True)
    agent_assignments = Column(JSON)
    session_data = Column(JSON)  # Changed from metadata to session_data

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    level = Column(String)
    source = Column(String)
    message = Column(Text)
    details = Column(JSON, nullable=True)
