# ============================================================
# FILE: main.py
# ============================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.database import Database
from api.routes import auth, employees

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await Database.connect_db()
    await Database.init_tenant_db("tenant_techcorp")
    yield
    # Shutdown
    await Database.close_db()

app = FastAPI(
    title="HRMS MVP",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])

@app.get("/")
async def root():
    return {
        "message": "HRMS MVP API",
        "version": "1.0.0",
        "docs": "/docs"
    }