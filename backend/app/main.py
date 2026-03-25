import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1 import auth, iso, line_list, pms, dashboard, users, reports

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

# Build allowed origins list from env (comma-separated), defaulting to localhost
_raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(iso.router, prefix="/api/v1/iso", tags=["iso"])
app.include_router(line_list.router, prefix="/api/v1/linelist", tags=["linelist"])
app.include_router(pms.router, prefix="/api/v1/pms", tags=["pms"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}
