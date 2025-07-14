from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime
from loguru import logger

from ...db.database import get_db
from ...controllers.admin_controller import AdminController
from ...core.security import get_current_user, get_current_admin
from ...models.user import User
from ...models.agent import Agent
from ...models.task import Task
from ...models.submission import Submission
from ...models.evaluation import EvaluationResult
from ...models.enums import UserRole, SubmissionStatus
from sqlalchemy import func, extract
from ...schemas.admin_schema import (
    AdminDashboardStats, UserManagementRequest, TaskAnalytics,
    UserAnalytics, SystemMonitoring, LeaderboardInsights,
    AdminUserResponse, AdminTaskResponse, AdminAgentResponse,
    AdminCreateTaskRequest, BulkUserAction, SystemHealthCheck
)

router = APIRouter(prefix="/admin", tags=["Admin"])
security = HTTPBearer()

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.admin_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, is_admin: bool = False):
        await websocket.accept()
        if is_admin:
            self.admin_connections.append(websocket)
        else:
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.admin_connections:
            self.admin_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_admins(self, message: dict):
        for connection in self.admin_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                await self.disconnect(connection)

    async def broadcast_system_update(self, update: dict):
        for connection in self.active_connections + self.admin_connections:
            try:
                await connection.send_text(json.dumps(update))
            except:
                await self.disconnect(connection)

manager = ConnectionManager()

# Dashboard and Analytics Routes
@router.get("/dashboard", response_model=Dict[str, Any])
async def get_admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive admin dashboard with all platform statistics"""
    admin_controller = AdminController(db)
    return admin_controller.get_dashboard_stats(current_user)

@router.get("/analytics/users", response_model=Dict[str, Any])
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed user analytics and behavior patterns"""
    admin_controller = AdminController(db)
    return admin_controller.get_user_analytics(current_user)

@router.get("/analytics/tasks", response_model=Dict[str, Any])
async def get_task_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive task performance analytics"""
    admin_controller = AdminController(db)
    return admin_controller.get_task_analytics(current_user)

@router.get("/monitoring/realtime", response_model=Dict[str, Any])
async def get_real_time_monitoring(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time system monitoring data"""
    admin_controller = AdminController(db)
    return admin_controller.get_real_time_monitoring(current_user)

@router.get("/leaderboard/insights", response_model=Dict[str, Any])
async def get_leaderboard_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive leaderboard and performance insights"""
    admin_controller = AdminController(db)
    return admin_controller.get_leaderboard_insights(current_user)

# User Management Routes
@router.post("/users/{action}")
async def manage_user(
    action: str,
    user_data: UserManagementRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Manage individual users (activate, deactivate, promote, demote, verify)"""
    admin_controller = AdminController(db)
    result = admin_controller.manage_users(action, user_data, current_user)
    
    # Send real-time update to admin dashboard
    background_tasks.add_task(
        manager.broadcast_to_admins,
        {
            "type": "user_management",
            "action": action,
            "user_id": user_data.user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "admin": current_user.email
        }
    )
    
    return result

@router.post("/users/bulk-action")
async def bulk_user_action(
    bulk_action: BulkUserAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Perform bulk actions on multiple users"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    admin_controller = AdminController(db)
    results = []
    
    for user_id in bulk_action.user_ids:
        try:
            user_request = UserManagementRequest(user_id=user_id, reason=bulk_action.reason)
            result = admin_controller.manage_users(bulk_action.action, user_request, current_user)
            results.append({"user_id": user_id, "success": True, "result": result})
        except Exception as e:
            results.append({"user_id": user_id, "success": False, "error": str(e)})
    
    # Send bulk update notification
    background_tasks.add_task(
        manager.broadcast_to_admins,
        {
            "type": "bulk_user_action",
            "action": bulk_action.action,
            "affected_users": len(bulk_action.user_ids),
            "successful": len([r for r in results if r["success"]]),
            "timestamp": datetime.utcnow().isoformat(),
            "admin": current_user.email
        }
    )
    
    return {"results": results, "summary": {"total": len(results), "successful": len([r for r in results if r["success"]])}}

# System Health and Monitoring
@router.get("/health/system", response_model=SystemHealthCheck)
async def get_system_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed system health information"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    import psutil
    import time
    
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return SystemHealthCheck(
            database_status="healthy",
            api_status="operational",
            evaluation_service="running",
            memory_usage=memory.percent,
            cpu_usage=cpu_usage,
            disk_usage=disk.percent,
            last_check=datetime.utcnow()
        )
    except Exception as e:
        return SystemHealthCheck(
            database_status="healthy",
            api_status="operational",
            evaluation_service="running",
            memory_usage=None,
            cpu_usage=None,
            disk_usage=None,
            last_check=datetime.utcnow()
        )

@router.get("/stats/platform", response_model=Dict[str, Any])
async def get_platform_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive platform statistics and trends"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    admin_controller = AdminController(db)
    
    # Combine multiple analytics for comprehensive view
    dashboard_stats = admin_controller.get_dashboard_stats(current_user)
    user_analytics = admin_controller.get_user_analytics(current_user)
    task_analytics = admin_controller.get_task_analytics(current_user)
    
    return {
        "overview": dashboard_stats,
        "user_insights": user_analytics,
        "task_insights": task_analytics,
        "generated_at": datetime.utcnow().isoformat()
    }

# Cool Feature: Agent Performance Insights
@router.get("/insights/agent-performance", response_model=Dict[str, Any])
async def get_agent_performance_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get advanced agent performance insights with ML-style analysis"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    

    
    try:
        # Agent type performance comparison
        agent_performance = db.query(
            Agent.agentType,
            func.count(Submission.id).label('total_submissions'),
            func.avg(EvaluationResult.score).label('avg_score'),
            func.avg(EvaluationResult.timeTaken).label('avg_time'),
            func.min(EvaluationResult.score).label('min_score'),
            func.max(EvaluationResult.score).label('max_score')
        ).join(Submission).join(EvaluationResult).group_by(Agent.agentType).all()
        
        # Environment difficulty analysis
        env_difficulty = db.query(
            Task.webArenaEnvironment,
            Task.difficulty,
            func.avg(EvaluationResult.score).label('avg_score'),
            func.count(Submission.id).label('attempts')
        ).join(Submission).join(EvaluationResult).group_by(
            Task.webArenaEnvironment, Task.difficulty
        ).all()
        
        # Success patterns
        success_patterns = {
            "agent_types": [
                {
                    "type": perf.agentType,
                    "submissions": perf.total_submissions,
                    "avg_score": round(perf.avg_score, 2) if perf.avg_score else 0,
                    "avg_time": round(perf.avg_time, 2) if perf.avg_time else 0,
                    "score_range": {
                        "min": round(perf.min_score, 2) if perf.min_score else 0,
                        "max": round(perf.max_score, 2) if perf.max_score else 0
                    },
                    "consistency": round((perf.avg_score / perf.max_score * 100), 2) if perf.max_score else 0
                }
                for perf in agent_performance
            ],
            "environment_analysis": {}
        }
        
        # Group environment data
        for env_data in env_difficulty:
            env_name = env_data.webArenaEnvironment
            if env_name not in success_patterns["environment_analysis"]:
                success_patterns["environment_analysis"][env_name] = {}
            
            success_patterns["environment_analysis"][env_name][env_data.difficulty.value] = {
                "avg_score": round(env_data.avg_score, 2) if env_data.avg_score else 0,
                "attempts": env_data.attempts
            }
        
        # Performance recommendations
        recommendations = []
        
        # Analyze agent types
        best_agent = max(agent_performance, key=lambda x: x.avg_score or 0, default=None)
        if best_agent:
            recommendations.append({
                "type": "agent_optimization",
                "message": f"Consider promoting {best_agent.agentType} agents - they show {round(best_agent.avg_score, 1)}% average success rate",
                "priority": "high"
            })
        
        # Analyze environment difficulty
        hardest_env = max(
            success_patterns["environment_analysis"].items(),
            key=lambda x: len([d for d in x[1].values() if d["avg_score"] < 50]),
            default=None
        )
        if hardest_env:
            recommendations.append({
                "type": "task_balancing",
                "message": f"Environment '{hardest_env[0]}' shows low success rates - consider task difficulty review",
                "priority": "medium"
            })
        
        return {
            "performance_analysis": success_patterns,
            "recommendations": recommendations,
            "insights": {
                "total_agent_types": len(agent_performance),
                "most_active_type": max(agent_performance, key=lambda x: x.total_submissions, default=None).agentType if agent_performance else "N/A",
                "performance_spread": {
                    "highest_avg": round(max(agent_performance, key=lambda x: x.avg_score or 0, default=None).avg_score or 0, 2),
                    "lowest_avg": round(min(agent_performance, key=lambda x: x.avg_score or 100, default=None).avg_score or 0, 2)
                }
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

# Cool Feature: Platform Activity Heatmap
@router.get("/insights/activity-heatmap", response_model=Dict[str, Any])
async def get_activity_heatmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate platform activity heatmap for visualization"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from datetime import datetime, timedelta
    
    try:
        # Get submission activity by hour of day and day of week
        activity_data = db.query(
            extract('hour', Submission.submittedAt).label('hour'),
            extract('dow', Submission.submittedAt).label('day_of_week'),
            func.count(Submission.id).label('activity_count')
        ).filter(
            Submission.submittedAt >= datetime.utcnow() - timedelta(days=30)
        ).group_by('hour', 'day_of_week').all()
        
        # Create heatmap matrix
        heatmap = {}
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        for day_idx, day_name in enumerate(days):
            heatmap[day_name] = {}
            for hour in range(24):
                heatmap[day_name][f"hour_{hour}"] = 0
        
        # Fill with actual data
        for activity in activity_data:
            day_name = days[int(activity.day_of_week)]
            hour_key = f"hour_{int(activity.hour)}"
            heatmap[day_name][hour_key] = activity.activity_count
        
        # Calculate peak activity insights
        peak_activity = max(activity_data, key=lambda x: x.activity_count, default=None)
        total_activity = sum(activity.activity_count for activity in activity_data)
        
        return {
            "heatmap_data": heatmap,
            "insights": {
                "peak_hour": int(peak_activity.hour) if peak_activity else 0,
                "peak_day": days[int(peak_activity.day_of_week)] if peak_activity else "Unknown",
                "peak_activity_count": peak_activity.activity_count if peak_activity else 0,
                "total_submissions_30d": total_activity,
                "average_hourly_activity": round(total_activity / (24 * 7), 2)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating heatmap: {str(e)}")

# WebSocket for real-time admin updates
@router.websocket("/ws/realtime")
async def websocket_admin_realtime(websocket: WebSocket):
    await manager.connect(websocket, is_admin=True)
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(30)  # Update every 30 seconds
            
            # You can add real-time metrics here
            update = {
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "healthy"
            }
            await manager.send_personal_message(json.dumps(update), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Cool Feature: Export Platform Data
@router.get("/export/{data_type}")
async def export_platform_data(
    data_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    format: str = "json"
):
    """Export platform data in various formats (JSON, CSV)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    

    import pandas as pd
    from io import StringIO
    
    try:
        if data_type == "users":
            users = db.query(User).all()
            data = [
                {
                    "id": user.id,
                    "email": user.email,
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "role": user.role.value,
                    "isActive": user.isActive,
                    "createdAt": user.createdAt.isoformat(),
                    "loginCount": user.loginCount
                }
                for user in users
            ]
        elif data_type == "agents":
            agents = db.query(Agent).all()
            data = [
                {
                    "id": agent.id,
                    "name": agent.name,
                    "agentType": agent.agentType,
                    "userId": agent.userId,
                    "isActive": agent.isActive,
                    "createdAt": agent.createdAt.isoformat()
                }
                for agent in agents
            ]
        elif data_type == "submissions":
            submissions = db.query(Submission).all()
            data = [
                {
                    "id": sub.id,
                    "userId": sub.userId,
                    "agentId": sub.agentId,
                    "taskId": sub.taskId,
                    "status": sub.status.value,
                    "submittedAt": sub.submittedAt.isoformat()
                }
                for sub in submissions
            ]
        else:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        if format.lower() == "csv":
            df = pd.DataFrame(data)
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            return {
                "format": "csv",
                "data": csv_buffer.getvalue(),
                "filename": f"{data_type}_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        else:
            return {
                "format": "json",
                "data": data,
                "count": len(data),
                "exported_at": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")

# Background task for sending notifications
async def send_admin_notification(notification_type: str, data: dict):
    """Send real-time notifications to admin dashboard"""
    await manager.broadcast_to_admins({
        "type": notification_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    })

@router.get("/stats", response_model=Dict[str, Any])
async def get_admin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get basic admin statistics for dashboard"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    admin_controller = AdminController(db)
    
    try:
        # Get basic stats
        total_users = db.query(User).count()
        total_agents = db.query(Agent).count()
        total_tasks = db.query(Task).count()
        total_submissions = db.query(Submission).count()
        completed_submissions = db.query(Submission).filter(
            Submission.status == SubmissionStatus.COMPLETED
        ).count()
        active_users = db.query(User).filter(User.isActive == True).count()
        
        # Calculate performance metrics
        avg_score = db.query(func.avg(EvaluationResult.score)).scalar() or 0
        
        # Get recent activity
        recent_submissions = db.query(Submission).order_by(
            Submission.submittedAt.desc()
        ).limit(10).all()
        
        # Recent activity formatted
        recent_activity = []
        for submission in recent_submissions:
            user = db.query(User).filter(User.id == submission.userId).first()
            task = db.query(Task).filter(Task.id == submission.taskId).first()
            
            recent_activity.append({
                "id": str(submission.id),
                "type": "submission",
                "user": f"{user.firstName} {user.lastName}" if user else "Unknown User",
                "task": task.title if task else "Unknown Task",
                "status": submission.status.value,
                "timestamp": submission.submittedAt.isoformat() if submission.submittedAt else None
            })
        
        # Format response
        stats = {
            "total_users": total_users,
            "active_users": active_users,
            "total_agents": total_agents,
            "total_tasks": total_tasks,
            "total_submissions": total_submissions,
            "completed_submissions": completed_submissions,
            "avg_score": round(avg_score, 2),
            "success_rate": round((completed_submissions / total_submissions * 100) if total_submissions > 0 else 0, 2),
            "recent_activity": recent_activity
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error fetching admin stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching admin stats: {str(e)}")

@router.get("/dashboard/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get real dashboard statistics."""
    try:
        # Get user statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.isActive == True).count()
        
        # Get agent statistics
        total_agents = db.query(Agent).count()
        user_agents = db.query(Agent).filter(Agent.userId == current_admin.id).count()
        
        # Get task statistics
        total_tasks = db.query(Task).count()
        active_tasks = db.query(Task).filter(Task.isActive == True).count()
        
        # Get submission statistics
        total_submissions = db.query(Submission).count()
        user_submissions = db.query(Submission).filter(Submission.userId == current_admin.id).count()
        completed_submissions = db.query(Submission).filter(Submission.status == SubmissionStatus.COMPLETED).count()
        
        # Get recent activity
        recent_submissions = (
            db.query(Submission)
            .order_by(Submission.createdAt.desc())
            .limit(5)
            .all()
        )
        
        recent_agents = (
            db.query(Agent)
            .order_by(Agent.createdAt.desc())
            .limit(5)
            .all()
        )
        
        return {
            "user_stats": {
                "total_users": total_users,
                "active_users": active_users,
            },
            "agent_stats": {
                "total_agents": total_agents,
                "user_agents": user_agents,
            },
            "task_stats": {
                "total_tasks": total_tasks,
                "active_tasks": active_tasks,
            },
            "submission_stats": {
                "total_submissions": total_submissions,
                "user_submissions": user_submissions,
                "completed_submissions": completed_submissions,
            },
            "recent_activity": {
                "submissions": [
                    {
                        "id": sub.id,
                        "task_name": sub.task.name if sub.task else "Unknown Task",
                        "status": sub.status,
                        "created_at": sub.createdAt.isoformat(),
                        "score": sub.score
                    }
                    for sub in recent_submissions
                ],
                "agents": [
                    {
                        "id": agent.id,
                        "name": agent.name,
                        "created_at": agent.createdAt.isoformat(),
                        "agent_type": agent.agentType
                    }
                    for agent in recent_agents
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard statistics")

@router.get("/user/dashboard/stats", response_model=Dict[str, Any])
async def get_user_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard statistics."""
    try:
        # Get user's agents
        user_agents = db.query(Agent).filter(Agent.userId == current_user.id).count()
        
        # Get user's submissions
        user_submissions = db.query(Submission).filter(Submission.userId == current_user.id).count()
        completed_submissions = db.query(Submission).filter(
            Submission.userId == current_user.id,
            Submission.status == SubmissionStatus.COMPLETED
        ).count()
        
        # Get available tasks
        available_tasks = db.query(Task).filter(Task.isActive == True).count()
        
        # Get user's recent submissions
        recent_submissions = (
            db.query(Submission)
            .filter(Submission.userId == current_user.id)
            .order_by(Submission.createdAt.desc())
            .limit(5)
            .all()
        )
        
        # Get user's recent agents
        recent_agents = (
            db.query(Agent)
            .filter(Agent.userId == current_user.id)
            .order_by(Agent.createdAt.desc())
            .limit(5)
            .all()
        )
        
        # Calculate average score
        avg_score = 0
        if completed_submissions > 0:
            total_score = db.query(Submission.score).filter(
                Submission.userId == current_user.id,
                Submission.status == SubmissionStatus.COMPLETED,
                Submission.score.isnot(None)
            ).scalar()
            if total_score:
                avg_score = total_score / completed_submissions
        
        return {
            "user_stats": {
                "agents": user_agents,
                "submissions": user_submissions,
                "completed_submissions": completed_submissions,
                "available_tasks": available_tasks,
                "average_score": round(avg_score, 2) if avg_score > 0 else 0
            },
            "recent_activity": {
                "submissions": [
                    {
                        "id": sub.id,
                        "task_name": sub.task.name if sub.task else "Unknown Task",
                        "status": sub.status,
                        "created_at": sub.createdAt.isoformat(),
                        "score": sub.score
                    }
                    for sub in recent_submissions
                ],
                "agents": [
                    {
                        "id": agent.id,
                        "name": agent.name,
                        "created_at": agent.createdAt.isoformat(),
                        "agent_type": agent.agentType
                    }
                    for agent in recent_agents
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error getting user dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard statistics")

@router.get("/user/profile/analytics", response_model=Dict[str, Any])
async def get_user_profile_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for the current user's profile"""
    try:
        # Get user's submissions
        total_submissions = db.query(Submission).filter(
            Submission.userId == current_user.id
        ).count()
        
        # Get user's completed submissions
        completed_submissions = db.query(Submission).filter(
            Submission.userId == current_user.id,
            Submission.status == SubmissionStatus.COMPLETED
        ).count()
        
        # Get user's best score
        best_score = db.query(func.max(EvaluationResult.score)).join(Submission).filter(
            Submission.userId == current_user.id
        ).scalar() or 0
        
        # Get user's average score
        avg_score = db.query(func.avg(EvaluationResult.score)).join(Submission).filter(
            Submission.userId == current_user.id
        ).scalar() or 0
        
        # Get total time spent
        total_time = db.query(func.sum(EvaluationResult.timeTaken)).join(Submission).filter(
            Submission.userId == current_user.id
        ).scalar() or 0
        
        # Calculate success rate
        success_rate = (completed_submissions / total_submissions * 100) if total_submissions > 0 else 0
        
        # Get efficiency score (average of score divided by time taken)
        efficiency_score = db.query(func.avg(EvaluationResult.score / EvaluationResult.timeTaken * 100)).join(Submission).filter(
            Submission.userId == current_user.id,
            EvaluationResult.timeTaken > 0
        ).scalar() or 0
        
        # Get reliability (percentage of non-failed submissions)
        non_failed = db.query(Submission).filter(
            Submission.userId == current_user.id,
            Submission.status != SubmissionStatus.FAILED
        ).count()
        reliability = (non_failed / total_submissions * 100) if total_submissions > 0 else 0
        
        return {
            "totalTests": total_submissions,
            "avgScore": round(avg_score, 1),
            "bestScore": round(best_score, 1),
            "totalRuntime": round(total_time, 1),
            "efficiency": round(efficiency_score, 1),
            "reliability": round(reliability, 1),
            "successRate": round(success_rate, 1)
        }
    except Exception as e:
        logger.error(f"Error fetching user profile analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching user profile analytics: {str(e)}")