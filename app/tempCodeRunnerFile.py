from fastapi import FastAPI
from app.database.database import engine
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
@app.get("/db-test")
def test_db():
    try:
        connection = engine.connect()
        connection.close()
        return {"database": "connected"}
    except Exception as e:
        return {"database": "connection failed", "error": str(e)}