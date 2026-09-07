from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db

from app.api.v1.auth import router as auth_router
from app.api.v1.journeys import router as journeys_router
from app.api.v1.disruptions import router as disruptions_router
from app.api.v1.recovery import router as recovery_router
from app.api.v1.simulator import router as simulator_router
from app.api.v1.guardian import router as guardian_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.demo import router as demo_router

app = FastAPI(title='TripShield AI', description='Autonomous Travel Recovery & Resilience Platform', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(journeys_router, prefix="/api/v1/journeys", tags=["journeys"])
app.include_router(disruptions_router, prefix="/api/v1/disruptions", tags=["disruptions"])
app.include_router(recovery_router, prefix="/api/v1/recovery", tags=["recovery"])
app.include_router(simulator_router, prefix="/api/v1/simulator", tags=["simulator"])
app.include_router(guardian_router, prefix="/api/v1/guardian", tags=["guardian"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
app.include_router(demo_router, prefix="/api/v1/demo", tags=["demo"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
