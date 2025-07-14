from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import random
import asyncio
import json
from datetime import datetime

from ...db.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...models.enums import TaskDifficulty
from ...services.playground.playground_service_factory import PlaygroundServiceFactory
from ...services.agent_core.llm_client_factory import LLMClientFactory
from ...core.config import settings

router = APIRouter(prefix="/playground", tags=["Playground"])
security = HTTPBearer()

# Dictionary of mock playground environments for development
PLAYGROUND_ENVIRONMENTS = {
    "omnizon": {
        "name": "Omnizon E-commerce",
        "description": "Online shopping platform",
        "tasks": ["product_search", "checkout", "review_product"]
    },
    "fly_united": {
        "name": "Fly United",
        "description": "Flight booking website",
        "tasks": ["book_flight", "check_in", "manage_booking"]
    },
    "gomail": {
        "name": "GoMail",
        "description": "Email platform",
        "tasks": ["compose_email", "organize_inbox", "schedule_meeting"]
    },
    "staynb": {
        "name": "StayNB",
        "description": "Accommodation booking",
        "tasks": ["search_accommodation", "book_room", "write_review"]
    }
}

@router.get("/health")
async def check_playground_health(current_user: User = Depends(get_current_user)):
    """Check the health of the playground system."""
    try:
        # Create playground service using factory
        playground_service = await PlaygroundServiceFactory.create_service()
        
        # Check playground health
        playground_healthy = await playground_service.health_check()
        
        # Check LLM service health
        llm_factory = LLMClientFactory()
        llm_health = await llm_factory.health_check_all_providers()
        llm_service_ready = any(llm_health.values())
        
        # Get supported providers
        supported_providers = list(llm_health.keys())
        available_providers = [provider for provider, status in llm_health.items() if status]
        
        # Get mock mode status
        mock_mode = not settings.USE_REAL_PLAYGROUND or not playground_healthy
        
        # Determine overall status
        status = "healthy"
        if not playground_healthy and not llm_service_ready:
            status = "error"
        elif not playground_healthy or not llm_service_ready:
            status = "warning"
        
        return {
            "status": status,
            "llm_service": llm_service_ready,
            "evaluation_service": playground_healthy,
            "mock_mode": mock_mode,
            "playground_version": "1.0.0",
            "supported_providers": supported_providers,
            "available_providers": available_providers,
            "supported_environments": list(PLAYGROUND_ENVIRONMENTS.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "llm_service": False,
            "evaluation_service": False,
            "mock_mode": True,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/environments")
async def get_playground_environments(current_user: User = Depends(get_current_user)):
    """Get available playground environments."""
    return list(PLAYGROUND_ENVIRONMENTS.keys())

@router.get("/environments/{environment_id}")
async def get_environment_details(
    environment_id: str,
    current_user: User = Depends(get_current_user)
):
    if environment_id not in PLAYGROUND_ENVIRONMENTS:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    return PLAYGROUND_ENVIRONMENTS[environment_id]

@router.get("/environments/{environment_id}/tasks", response_model=List[Dict[str, Any]])
async def get_environment_tasks(
    environment_id: str,
    difficulty: TaskDifficulty = None,
    current_user = Depends(get_current_user)
):
    if environment_id not in PLAYGROUND_ENVIRONMENTS:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    env = PLAYGROUND_ENVIRONMENTS[environment_id]
    tasks = []
    
    for task_type in env["tasks"]:
        task = {
            "id": f"{environment_id}_{task_type}",
            "name": task_type.replace("_", " ").title(),
            "type": task_type,
            "environment": environment_id,
            "difficulty": difficulty or random.choice(list(TaskDifficulty)),
            "description": f"Mock {task_type} task in {env['name']} environment",
            "estimated_time": f"{random.randint(5, 30)} minutes",
            "success_criteria": [
                "Complete the task objective",
                "Maintain proper interaction flow", 
                "Handle errors gracefully"
            ]
        }
        
        if difficulty is None or task["difficulty"] == difficulty:
            tasks.append(task)
    
    return tasks

@router.post("/evaluate")
async def run_playground_evaluation(
    evaluation_request: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    try:
        environment_id = evaluation_request.get("environment_id")
        task_id = evaluation_request.get("task_id")
        agent_config = evaluation_request.get("agent_config", {})
        
        if not environment_id or environment_id not in PLAYGROUND_ENVIRONMENTS:
            raise HTTPException(status_code=400, detail="Invalid environment_id")
        
        evaluation_id = str(uuid.uuid4())
        
        logger.info(f"Starting mock evaluation {evaluation_id} for {task_id}")
        
        await asyncio.sleep(1)
        
        success_rate = random.uniform(0.6, 0.95)
        
        results = {
            "evaluation_id": evaluation_id,
            "environment": environment_id,
            "task_id": task_id,
            "agent_config": agent_config,
            "status": "completed",
            "results": {
                "success": success_rate > 0.7,
                "success_rate": round(success_rate, 3),
                "steps_completed": random.randint(8, 25),
                "total_steps": random.randint(15, 30),
                "execution_time": f"{random.randint(45, 180)} seconds",
                "errors_encountered": random.randint(0, 3),
                "score": round(success_rate * 100, 1)
            },
            "metrics": {
                "task_completion": round(success_rate, 3),
                "efficiency": round(random.uniform(0.7, 0.9), 3),
                "error_handling": round(random.uniform(0.6, 0.95), 3),
                "adaptability": round(random.uniform(0.5, 0.9), 3)
            },
            "feedback": [
                "Agent successfully completed primary objectives",
                "Good error recovery mechanisms observed",
                "Could improve interaction speed",
                "Effective use of available tools"
            ][:random.randint(2, 4)]
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Playground evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@router.get("/evaluations/{evaluation_id}")
async def get_evaluation_results(
    evaluation_id: str,
    current_user = Depends(get_current_user)
):
    return {
        "evaluation_id": evaluation_id,
        "status": "completed",
        "created_at": "2024-01-15T10:30:00Z",
        "completed_at": "2024-01-15T10:32:30Z",
        "results": {
            "success": True,
            "score": 87.5,
            "details": "Mock evaluation results"
        }
    }

@router.get("/leaderboard")
async def get_playground_leaderboard(
    environment_id: str = None,
    current_user = Depends(get_current_user)
):
    mock_entries = [
        {"rank": 1, "agent_name": "GPT-4 Turbo", "score": 94.2, "evaluations": 45},
        {"rank": 2, "agent_name": "Claude-3 Opus", "score": 91.8, "evaluations": 38},
        {"rank": 3, "agent_name": "Custom Agent V2", "score": 87.5, "evaluations": 22},
        {"rank": 4, "agent_name": "Gemini Pro", "score": 84.1, "evaluations": 31},
        {"rank": 5, "agent_name": "Custom Agent V1", "score": 79.3, "evaluations": 15}
    ]
    
    return {
        "environment": environment_id or "all",
        "leaderboard": mock_entries,
        "last_updated": "2024-01-15T12:00:00Z",
        "total_evaluations": sum(entry["evaluations"] for entry in mock_entries)
    }

# -----------------------------------------------------------------------------
# Legacy direct run endpoint expected by test suite
# -----------------------------------------------------------------------------

@router.post("/run")
async def run_playground_direct(
    run_request: Dict[str, Any],
    current_user=Depends(get_current_user)
):
    """Mock execution of agent against a task, returning synthetic results."""

    execution_id = str(uuid.uuid4())
    steps_taken = random.randint(10, 60)
    total_time_seconds = round(random.uniform(5.0, 120.0), 2)

    return {
        "execution_id": execution_id,
        "status": random.choice(["completed", "failed"]),
        "steps_taken": steps_taken,
        "total_time_seconds": total_time_seconds,
        "success_rate": round(random.uniform(0.5, 1.0), 2),
        "execution_log": [
            "Step 1: Initializing agent",
            "Step 2: Navigating to URL",
            "...",
            "Step n: Finished"
        ],
    }