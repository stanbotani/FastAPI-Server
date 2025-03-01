from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
import pandas as pd
from fastapi.responses import FileResponse
import os

# ✅ Debugging Step 1: Confirming Server Startup
print("🚀 Starting FastAPI server...")

# ✅ Set up the database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./accel_data.db")
print(f"📂 Using database at: {DATABASE_URL}")

engine = create_engine(DATABASE_URL, echo=True)  # Debugging SQL queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ Initialize API
app = FastAPI(title="Sensor Data API", description="An API for uploading and querying sensor data.", version="1.0.0")
print("✅ FastAPI app initialized.")

# ✅ API Key authentication
API_KEYS = {"testuser": "secretapikey123"}

def authenticate(api_key: str):
    if api_key not in API_KEYS.values():
        print(f"❌ Authentication failed for API key: {api_key}")
        raise HTTPException(status_code=401, detail="Invalid API Key")
    print("✅ Authenticated successfully.")
    return api_key

# ✅ Define the database model
class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sensor_type = Column(String, index=True)
    value = Column(Text)  # Store JSON or delimited data

print("🔧 Creating database tables if they don't exist...")
Base.metadata.create_all(bind=engine)
print("✅ Database setup complete.")

# ✅ Define request format
class SensorDataRequest(BaseModel):
    user_id: str
    sensor_type: str
    value: str  # JSON or delimited string
    timestamp: datetime = datetime.utcnow()

# ✅ Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Root endpoint (for status check)
@app.get("/")
def home():
    return {"message": "🚀 FastAPI server is running!"}

# ✅ Ping endpoint (for quick testing)
@app.get("/ping")
def ping():
    return {"message": "pong"}

# ✅ Endpoint to upload data
@app.post("/api/data/upload/")
def upload_data(data: SensorDataRequest, api_key: str = Depends(authenticate), db: Session = Depends(get_db)):
    print(f"📥 Received data upload request: {data}")
    new_entry = SensorData(**data.dict())
    db.add(new_entry)
    db.commit()
    print("✅ Data saved successfully.")
    return {"message": "Data saved successfully"}

# ✅ Endpoint to retrieve data
@app.get("/api/data/query/")
def query_data(user_id: str, sensor_type: str = None, api_key: str = Depends(authenticate), db: Session = Depends(get_db)):
    print(f"🔍 Querying data for user: {user_id}, sensor_type: {sensor_type}")
    query = db.query(SensorData).filter(SensorData.user_id == user_id)
    if sensor_type:
        query = query.filter(SensorData.sensor_type == sensor_type)
    records = query.all()
    print(f"✅ Found {len(records)} records.")
    return records

# ✅ Endpoint to download combined sensor data as an Excel file
@app.get("/api/data/download/")
def download_data(user_id: str, sensor_type: str = None, api_key: str = Depends(authenticate), db: Session = Depends(get_db)):
    print(f"📥 Downloading data for user: {user_id}, sensor_type: {sensor_type}")
    query = db.query(SensorData).filter(SensorData.user_id == user_id)
    if sensor_type:
        query = query.filter(SensorData.sensor_type == sensor_type)
    
    records = query.all()
    if not records:
        print("⚠️ No data found for the requested query.")
        raise HTTPException(status_code=404, detail="No data found")
    
    data_list = [{"user_id": r.user_id, "timestamp": r.timestamp, "sensor_type": r.sensor_type, "value": r.value} for r in records]
    df = pd.DataFrame(data_list)
    file_path = "sensor_data.xlsx"
    df.to_excel(file_path, index=False)
    print("✅ Excel file created successfully.")
    
    return FileResponse(file_path, filename="sensor_data.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



