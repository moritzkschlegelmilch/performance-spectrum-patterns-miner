import os

from fastapi import FastAPI

import env
from routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Create uploads folder
os.makedirs(env.UPLOAD_DIR, exist_ok=True)

# Make sure we do not get blocked by CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[env.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize routes
app.include_router(router, prefix="/api", tags=["users"])
