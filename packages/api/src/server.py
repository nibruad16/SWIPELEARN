"""
SwipeLearn API Server
Entry point — mirrors ride-share's packages/api/src/server.ts
FastAPI app with CORS, mounted routers.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import router

app = FastAPI(
    title="SwipeLearn API",
    description="Transform blog posts into swipeable Knowledge Cards",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

PORT = 8000

if __name__ == "__main__":
    uvicorn.run("src.server:app", host="0.0.0.0", port=PORT, reload=True)
    print(f"🚀 SwipeLearn API running on http://localhost:{PORT}/api")
