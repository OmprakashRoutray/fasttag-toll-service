
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# --------------------------------------------------
# 1. DATABASE CONFIGURATION
# --------------------------------------------------

DATABASE_URL = "sqlite:///./toll_system.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


# --------------------------------------------------
# 2. DATABASE MODELS
# --------------------------------------------------

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, unique=True, nullable=False)
    account_balance = Column(Float, nullable=False, default=0.0)


class TollLog(Base):
    __tablename__ = "toll_logs"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    toll_plaza_location = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    amount_deducted = Column(Float, nullable=False)
    status = Column(String, nullable=False)


# Create tables if they do not exist.
Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# 3. DATABASE SESSION
# --------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------
# 4. API REQUEST MODELS
# --------------------------------------------------

class VehicleCreate(BaseModel):
    license_plate: str = Field(min_length=1, max_length=20)
    account_balance: float = Field(ge=0)


class TransactionRequest(BaseModel):
    vehicle_id: int = Field(gt=0)
    toll_plaza_location: str = Field(min_length=1, max_length=100)
    toll_fee: float = Field(gt=0)


# --------------------------------------------------
# 5. FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="FastTag & Toll Transaction Microservice",
    description="A REST API for toll transactions and analytics.",
    version="1.0.0",
)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head><title>FastTag Toll Service</title></head>
        <body>
            <h1>FastTag & Toll Transaction Microservice</h1>
            <p>API is running successfully.</p>
            <p><a href="/docs">Open API Documentation</a></p>
        </body>
    </html>
    """


# --------------------------------------------------
# 6. REGISTER A VEHICLE
# --------------------------------------------------

@app.post("/vehicles", status_code=201)
def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db),
):
    existing_vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.license_plate == vehicle_data.license_plate
        )
        .first()
    )

    if existing_vehicle:
        raise HTTPException(
            status_code=409,
            detail="License plate already registered.",
        )

    vehicle = Vehicle(
        license_plate=vehicle_data.license_plate,
        account_balance=vehicle_data.account_balance,
    )

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return {
        "message": "Vehicle registered successfully",
        "vehicle_id": vehicle.id,
        "license_plate": vehicle.license_plate,
        "account_balance": vehicle.account_balance,
    }


# --------------------------------------------------
# 7. VIEW VEHICLES
# --------------------------------------------------

@app.get("/vehicles")
def get_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).order_by(Vehicle.id).all()

    return [
        {
            "id": vehicle.id,
            "license_plate": vehicle.license_plate,
            "account_balance": vehicle.account_balance,
        }
        for vehicle in vehicles
    ]


# --------------------------------------------------
# 8. PROCESS A TOLL TRANSACTION
# --------------------------------------------------

@app.post("/transaction/process")
def process_transaction(
    request: TransactionRequest,
    db: Session = Depends(get_db),
):
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == request.vehicle_id)
        .with_for_update()
        .first()
    )

    if vehicle is None:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found. Register the vehicle first.",
        )

    if vehicle.account_balance >= request.toll_fee:
        vehicle.account_balance -= request.toll_fee
        status_value = "SUCCESS"
        amount_deducted = request.toll_fee
    else:
        status_value = "INSUFFICIENT_FUNDS"
        amount_deducted = 0.0

    log = TollLog(
        vehicle_id=vehicle.id,
        toll_plaza_location=request.toll_plaza_location,
        timestamp=datetime.now(timezone.utc),
        amount_deducted=amount_deducted,
        status=status_value,
    )

    try:
        db.add(log)
        db.commit()
        db.refresh(log)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Transaction could not be recorded.",
        )

    return {
        "transaction_id": log.id,
        "vehicle_id": vehicle.id,
        "toll_plaza_location": log.toll_plaza_location,
        "toll_fee": request.toll_fee,
        "amount_deducted": amount_deducted,
        "remaining_balance": vehicle.account_balance,
        "status": status_value,
        "timestamp": log.timestamp,
    }


# --------------------------------------------------
# 9. VIEW TRANSACTION LOGS
# --------------------------------------------------

@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    logs = db.query(TollLog).order_by(TollLog.id.desc()).all()

    return [
        {
            "transaction_id": log.id,
            "vehicle_id": log.vehicle_id,
            "toll_plaza_location": log.toll_plaza_location,
            "timestamp": log.timestamp,
            "amount_deducted": log.amount_deducted,
            "status": log.status,
        }
        for log in logs
    ]


# --------------------------------------------------
# 10. ANALYTICS SUMMARY
# --------------------------------------------------

@app.get("/analytics/summary")
def analytics_summary(db: Session = Depends(get_db)):
    total_transactions = db.query(TollLog).count()

    successful_transactions = (
        db.query(TollLog)
        .filter(TollLog.status == "SUCCESS")
        .count()
    )

    insufficient_funds_transactions = (
        db.query(TollLog)
        .filter(TollLog.status == "INSUFFICIENT_FUNDS")
        .count()
    )

    total_revenue = (
        db.query(func.sum(TollLog.amount_deducted)).scalar() or 0.0
    )

    return {
        "total_transactions": total_transactions,
        "successful_transactions": successful_transactions,
        "insufficient_funds_transactions": (
            insufficient_funds_transactions
        ),
        "total_revenue_collected": round(total_revenue, 2),
    }
