from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..models.user import User
from ..models.agent import Agent
from ..models.task import Task
from ..models.submission import Submission
from ..models.evaluation import EvaluationResult
from ..models.leaderboard import Leaderboard
from ..models.enums import UserRole, TaskDifficulty, SubmissionStatus, EvaluationStatus
from ..schemas.admin_schema import AdminDashboardStats, UserManagementRequest, TaskAnalytics
from ..core.security import get_current_user
import json

class AdminController:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_stats(self, current_user: User = Depends(get_current_user)) -> AdminDashboardStats:
        """Get comprehensive dashboard statistics for admin"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        try:
            # User Statistics
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(User.isActive == True).count()
            new_users_week = self.db.query(User).filter(
                User.createdAt >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            # Agent Statistics
            total_agents = self.db.query(Agent).count()
            active_agents = self.db.query(Agent).filter(Agent.isActive == True).count()
            
            # Task Statistics
            total_tasks = self.db.query(Task).count()
            easy_tasks = self.db.query(Task).filter(Task.difficulty == TaskDifficulty.EASY).count()
            medium_tasks = self.db.query(Task).filter(Task.difficulty == TaskDifficulty.MEDIUM).count()
            hard_tasks = self.db.query(Task).filter(Task.difficulty == TaskDifficulty.HARD).count()
            
            # Submission Statistics
            total_submissions = self.db.query(Submission).count()
            completed_submissions = self.db.query(Submission).filter(
                Submission.status == SubmissionStatus.COMPLETED
            ).count()
            failed_submissions = self.db.query(Submission).filter(
                Submission.status == SubmissionStatus.FAILED
            ).count()
            pending_submissions = self.db.query(Submission).filter(
                Submission.status.in_([SubmissionStatus.PENDING, SubmissionStatus.PROCESSING])
            ).count()
            
            # Success rate
            success_rate = (completed_submissions / total_submissions * 100) if total_submissions > 0 else 0
            
            # Recent activity
            recent_submissions = self.db.query(Submission).filter(
                Submission.submittedAt >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            # Average scores
            avg_score = self.db.query(func.avg(EvaluationResult.score)).scalar() or 0
            
            # Environment usage
            environment_usage = self.db.query(
                Task.webArenaEnvironment,
                func.count(Submission.id).label('submissions_count')
            ).join(Submission).group_by(Task.webArenaEnvironment).all()
            
            dashboard = {
                "total_users": total_users,
                "total_agents": total_agents,
                "total_tasks": total_tasks,
                "total_submissions": total_submissions,
                "activity_metrics": {
                    "recent_submissions_24h": recent_submissions,
                    "avg_completion_time": self._get_avg_completion_time(),
                    "most_popular_environment": self._get_most_popular_environment()
                },
                "submission_metrics": {
                    "completed": completed_submissions,
                    "failed": failed_submissions,
                    "pending": pending_submissions,
                    "success_rate": round(success_rate, 2),
                    "average_score": round(avg_score, 2)
                },
                "task_distribution": {
                    "easy": easy_tasks,
                    "medium": medium_tasks,
                    "hard": hard_tasks
                },
                "environment_usage": {env: count for env, count in environment_usage},
                "system_health": {
                    "database_status": "healthy",
                    "api_status": "operational",
                    "evaluation_service": "running"
                }
            }
            return dashboard
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}")

    def get_user_analytics(self, current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
        """Get detailed user analytics and behavior patterns"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        try:
            # User registration trends (last 30 days)
            registration_trend = []
            for i in range(30):
                date = datetime.utcnow() - timedelta(days=i)
                count = self.db.query(User).filter(
                    func.date(User.createdAt) == date.date()
                ).count()
                registration_trend.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "registrations": count
                })
            
            # Top performing users
            top_users = self.db.query(
                User.id,
                User.firstName,
                User.lastName,
                User.email,
                func.count(Submission.id).label('submission_count'),
                func.avg(EvaluationResult.score).label('avg_score')
            ).join(Submission).join(EvaluationResult).group_by(User.id).order_by(
                desc('avg_score')
            ).limit(10).all()
            
            # Agent type distribution
            agent_types = self.db.query(
                Agent.agentType,
                func.count(Agent.id).label('count')
            ).group_by(Agent.agentType).all()
            
            return {
                "registration_trend": registration_trend,
                "top_performers": [
                    {
                        "user_id": user.id,
                        "name": f"{user.firstName} {user.lastName or ''}".strip(),
                        "email": user.email,
                        "submissions": user.submission_count,
                        "average_score": round(user.avg_score, 2) if user.avg_score else 0
                    }
                    for user in top_users
                ],
                "agent_distribution": {agent_type: count for agent_type, count in agent_types},
                "user_engagement": self._get_user_engagement_metrics()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching user analytics: {str(e)}")

    def get_task_analytics(self, current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
        """Get comprehensive task performance analytics"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        try:
            # Task completion rates
            task_performance = self.db.query(
                Task.id,
                Task.title,
                Task.difficulty,
                Task.webArenaEnvironment,
                func.count(Submission.id).label('total_attempts'),
                func.count(
                    func.case([(Submission.status == SubmissionStatus.COMPLETED, 1)])
                ).label('successful_completions'),
                func.avg(EvaluationResult.score).label('avg_score'),
                func.avg(EvaluationResult.timeTaken).label('avg_time')
            ).outerjoin(Submission).outerjoin(EvaluationResult).group_by(Task.id).all()
            
            # Difficulty analysis
            difficulty_stats = {}
            for difficulty in TaskDifficulty:
                stats = self.db.query(
                    func.count(Task.id).label('task_count'),
                    func.avg(EvaluationResult.score).label('avg_score'),
                    func.avg(EvaluationResult.timeTaken).label('avg_time')
                ).join(Submission).join(EvaluationResult).filter(
                    Task.difficulty == difficulty
                ).first()
                
                difficulty_stats[difficulty.value] = {
                    "task_count": stats.task_count if stats.task_count else 0,
                    "average_score": round(stats.avg_score, 2) if stats.avg_score else 0,
                    "average_time": round(stats.avg_time, 2) if stats.avg_time else 0
                }
            
            return {
                "task_performance": [
                    {
                        "task_id": task.id,
                        "title": task.title,
                        "difficulty": task.difficulty.value,
                        "environment": task.webArenaEnvironment,
                        "total_attempts": task.total_attempts or 0,
                        "successful_completions": task.successful_completions or 0,
                        "success_rate": round(
                            (task.successful_completions / task.total_attempts * 100) 
                            if task.total_attempts > 0 else 0, 2
                        ),
                        "average_score": round(task.avg_score, 2) if task.avg_score else 0,
                        "average_time": round(task.avg_time, 2) if task.avg_time else 0
                    }
                    for task in task_performance
                ],
                "difficulty_analysis": difficulty_stats,
                "environment_performance": self._get_environment_performance()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching task analytics: {str(e)}")

    def get_real_time_monitoring(self, current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
        """Get real-time system monitoring data"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        try:
            # Active submissions (last hour)
            active_submissions = self.db.query(Submission).filter(
                and_(
                    Submission.status.in_([SubmissionStatus.PENDING, SubmissionStatus.PROCESSING]),
                    Submission.submittedAt >= datetime.utcnow() - timedelta(hours=1)
                )
            ).all()
            
            # Recent completions (last hour)
            recent_completions = self.db.query(Submission).filter(
                and_(
                    Submission.status == SubmissionStatus.COMPLETED,
                    Submission.updatedAt >= datetime.utcnow() - timedelta(hours=1)
                )
            ).count()
            
            # System load indicators
            queue_length = self.db.query(Submission).filter(
                Submission.status == SubmissionStatus.QUEUED
            ).count()
            
            processing_count = self.db.query(Submission).filter(
                Submission.status == SubmissionStatus.PROCESSING
            ).count()
            
            return {
                "active_evaluations": len(active_submissions),
                "queue_length": queue_length,
                "processing_count": processing_count,
                "recent_completions": recent_completions,
                "system_load": {
                    "evaluation_queue": queue_length,
                    "active_processes": processing_count,
                    "hourly_throughput": recent_completions
                },
                "active_submissions": [
                    {
                        "id": sub.id,
                        "user_id": sub.userId,
                        "task_id": sub.taskId,
                        "status": sub.status.value,
                        "submitted_at": sub.submittedAt.isoformat(),
                        "estimated_completion": self._estimate_completion_time(sub)
                    }
                    for sub in active_submissions
                ]
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching monitoring data: {str(e)}")

    def manage_users(self, action: str, user_data: UserManagementRequest, 
                    current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
        """Manage users (activate, deactivate, promote, etc.)"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        try:
            target_user = self.db.query(User).filter(User.id == user_data.user_id).first()
            if not target_user:
                raise HTTPException(status_code=404, detail="User not found")
            
            if action == "activate":
                target_user.isActive = True
            elif action == "deactivate":
                target_user.isActive = False
            elif action == "promote":
                target_user.role = UserRole.ADMIN
            elif action == "demote":
                target_user.role = UserRole.USER
            elif action == "verify_email":
                target_user.isEmailVerified = True
            else:
                raise HTTPException(status_code=400, detail="Invalid action")
            
            self.db.commit()
            
            return {
                "success": True,
                "message": f"User {action} completed successfully",
                "user": {
                    "id": target_user.id,
                    "email": target_user.email,
                    "role": target_user.role.value,
                    "is_active": target_user.isActive,
                    "is_verified": target_user.isEmailVerified
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error managing user: {str(e)}")

    def get_leaderboard_insights(self, current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
        """Get comprehensive leaderboard and performance insights"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        try:
            # Global top performers
            global_leaderboard = self.db.query(
                Agent.id,
                Agent.name,
                User.firstName,
                User.lastName,
                func.avg(Leaderboard.score).label('avg_score'),
                func.count(Leaderboard.id).label('submissions'),
                func.avg(Leaderboard.timeTaken).label('avg_time')
            ).join(User).join(Leaderboard).group_by(Agent.id).order_by(
                desc('avg_score')
            ).limit(20).all()
            
            # Task-specific leaderboards
            task_leaderboards = {}
            tasks = self.db.query(Task).all()
            
            for task in tasks:
                top_agents = self.db.query(
                    Agent.id,
                    Agent.name,
                    Leaderboard.score,
                    Leaderboard.timeTaken,
                    Leaderboard.rank
                ).join(Leaderboard).filter(
                    Leaderboard.taskId == task.id
                ).order_by(Leaderboard.rank).limit(5).all()
                
                task_leaderboards[task.id] = {
                    "task_title": task.title,
                    "top_agents": [
                        {
                            "agent_id": agent.id,
                            "agent_name": agent.name,
                            "score": agent.score,
                            "time_taken": agent.timeTaken,
                            "rank": agent.rank
                        }
                        for agent in top_agents
                    ]
                }
            
            return {
                "global_leaderboard": [
                    {
                        "agent_id": agent.id,
                        "agent_name": agent.name,
                        "user_name": f"{agent.firstName} {agent.lastName or ''}".strip(),
                        "average_score": round(agent.avg_score, 2),
                        "total_submissions": agent.submissions,
                        "average_time": round(agent.avg_time, 2) if agent.avg_time else 0
                    }
                    for agent in global_leaderboard
                ],
                "task_leaderboards": task_leaderboards,
                "performance_trends": self._get_performance_trends()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching leaderboard insights: {str(e)}")

    # Helper methods
    def _get_avg_completion_time(self) -> float:
        """Calculate average completion time for all tasks"""
        result = self.db.query(func.avg(EvaluationResult.timeTaken)).scalar()
        return round(result, 2) if result else 0

    def _get_most_popular_environment(self) -> str:
        """Get the most frequently used environment"""
        result = self.db.query(
            Task.webArenaEnvironment,
            func.count(Submission.id).label('count')
        ).join(Submission).group_by(Task.webArenaEnvironment).order_by(
            desc('count')
        ).first()
        return result.webArenaEnvironment if result else "N/A"

    def _get_user_engagement_metrics(self) -> Dict[str, Any]:
        """Calculate user engagement metrics"""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(
            User.lastLoginAt >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return {
            "weekly_active_users": active_users,
            "engagement_rate": round((active_users / total_users * 100), 2) if total_users > 0 else 0,
            "avg_submissions_per_user": self._get_avg_submissions_per_user()
        }

    def _get_avg_submissions_per_user(self) -> float:
        """Calculate average submissions per user"""
        result = self.db.query(
            func.count(Submission.id) / func.count(func.distinct(Submission.userId))
        ).scalar()
        return round(result, 2) if result else 0

    def _get_environment_performance(self) -> Dict[str, Any]:
        """Get performance metrics for each environment"""
        environments = self.db.query(Task.webArenaEnvironment).distinct().all()
        performance_data = {}
        
        for env in environments:
            env_name = env.webArenaEnvironment
            stats = self.db.query(
                func.avg(EvaluationResult.score).label('avg_score'),
                func.avg(EvaluationResult.timeTaken).label('avg_time'),
                func.count(Submission.id).label('total_submissions')
            ).join(Task).join(Submission).filter(
                Task.webArenaEnvironment == env_name
            ).first()
            
            performance_data[env_name] = {
                "average_score": round(stats.avg_score, 2) if stats.avg_score else 0,
                "average_time": round(stats.avg_time, 2) if stats.avg_time else 0,
                "total_submissions": stats.total_submissions or 0
            }
        
        return performance_data

    def _estimate_completion_time(self, submission: Submission) -> str:
        """Estimate completion time for active submission"""
        # Simple estimation based on task's expected completion time
        task = self.db.query(Task).filter(Task.id == submission.taskId).first()
        if task:
            elapsed = (datetime.utcnow() - submission.submittedAt).total_seconds()
            remaining = max(0, task.expectedCompletionTime - elapsed)
            return f"{int(remaining)}s"
        return "Unknown"

    def _get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends over time"""
        # Last 30 days performance
        trend_data = []
        for i in range(30):
            date = datetime.utcnow() - timedelta(days=i)
            daily_stats = self.db.query(
                func.avg(EvaluationResult.score).label('avg_score'),
                func.count(EvaluationResult.id).label('submissions')
            ).filter(
                func.date(EvaluationResult.completedAt) == date.date()
            ).first()
            
            trend_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "average_score": round(daily_stats.avg_score, 2) if daily_stats.avg_score else 0,
                "submissions": daily_stats.submissions or 0
            })
        
        return {"daily_trends": trend_data}