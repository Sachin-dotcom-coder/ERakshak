# backend-api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="E-Rakshak Traffic Optimization API")

# Allow dashboard to connect locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "message": "Backend API is up and running"}

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy"}