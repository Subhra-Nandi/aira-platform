from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional

from app.services.agent_orchestrator import execute_task

router = APIRouter(prefix="/api/v1", tags=["Tasks"])

tasks_db = {}


class TaskRequest(BaseModel):
    goal: str
    background: Optional[str] = "unknown"
    industry: Optional[str] = "general"
    risk_appetite: Optional[str] = "medium"
    technical_level: Optional[str] = "intermediate"
    location: Optional[str] = "unknown"
    budget: Optional[str] = "unknown"
    team_size: Optional[str] = "solo"



@router.post("/tasks")
def create_task(task: TaskRequest):

    task_id = str(uuid.uuid4())
    print(f"Received task: {task.goal}")

    user_profile = {
        "background": task.background,
        "industry": task.industry,
        "risk_appetite": task.risk_appetite,
        "technical_level": task.technical_level,
        "location": task.location,
        "budget": task.budget,
        "team_size": task.team_size
    }

    try:
        tasks_db[task_id] = {
            "task_id": task_id,
            "goal": task.goal,
            "status": "running",
            "created_at": datetime.utcnow().isoformat(),
            "result": None
        }

        result = execute_task(task.goal, user_profile=user_profile)

        
        if isinstance(result, dict) and result.get("error") == "token_limit_exceeded":
            tasks_db[task_id]["status"] = "failed"
            tasks_db[task_id]["result"] = result
            raise HTTPException(status_code=400, detail=result["message"])

        tasks_db[task_id]["status"] = "completed"
        tasks_db[task_id]["result"] = result

        
        return {
            "task_id": task_id,
            "status": "completed",
            "result": result
        }

    except HTTPException:
        raise

    except Exception as e:
        tasks_db[task_id]["status"] = "failed"
        raise HTTPException(
            status_code=500,
            detail=f"Task execution failed: {str(e)}"
        )


# GET ALL TASKS
@router.get("/tasks")
def get_tasks():
    return {
        "tasks": [
            {
                "task_id": t["task_id"],
                "status": t["status"]
            }
            for t in tasks_db.values()
        ]
    }


# GET SINGLE TASK
@router.get("/tasks/{task_id}")
def get_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks_db[task_id]

    return {
        "task_id": task_id,
        "status": task["status"],
        "result": task["result"]   
    }