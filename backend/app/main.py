from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import CORS_ORIGINS
from .api.routes import router

app = FastAPI(
    title="MIRRORLINE",
    description="Memory evolution and knowledge drift agent",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in CORS_ORIGINS if x.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "MIRRORLINE"}
