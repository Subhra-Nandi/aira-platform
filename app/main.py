from dotenv import load_dotenv
import os
load_dotenv()

from fastapi import FastAPI
from app.api.routes import task_routes

app = FastAPI(
    title="AIRA Platform",
    description="Autonomous Intelligence Research & Automation Platform",
    version="1.0"
)

app.include_router(task_routes.router)


@app.get("/")
def root():
    return {"message": "AIRA backend running"}


@app.get("/health")
def health():
    return {"status": "ok"}