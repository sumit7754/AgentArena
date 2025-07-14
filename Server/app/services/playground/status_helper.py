"""
Helper functions for creating properly formatted PlaygroundStatus objects.
This ensures all required fields are present regardless of which schema definition is used.
"""

import time
import uuid
from typing import Optional, Dict, Any


def create_playground_status(
    submission_id: str,
    execution_id: Optional[str] = None,
    status: str = "PROCESSING",
    progress: float = 0.0,
    progress_percentage: float = 0.0,
    current_step: int = 0,
    estimated_remaining_seconds: Optional[int] = 300,
    last_action: Optional[str] = "Starting execution",
    error_message: Optional[str] = None,
) -> dict:
    """
    Create a dictionary with all necessary fields for PlaygroundStatus.
    This ensures all required fields like execution_id and start_time are always included.
    
    Args:
        submission_id: ID of the submission
        execution_id: Unique ID for this execution (generated if None)
        status: Current execution status
        progress: Progress value between 0 and 1
        progress_percentage: Progress as a percentage
        current_step: Current execution step
        estimated_remaining_seconds: Estimated seconds remaining
        last_action: Description of the last action
        error_message: Error message if any
        
    Returns:
        Dict with all fields required for PlaygroundStatus
    """
    # Generate a unique execution ID if none is provided
    if execution_id is None:
        execution_id = str(uuid.uuid4())
    
    # Current timestamp for start_time
    start_time = time.time()
    
    # Return a complete dict with all required fields
    return {
        "submission_id": submission_id,
        "execution_id": execution_id,
        "status": status,
        "progress": progress,
        "progress_percentage": progress_percentage,
        "current_step": current_step,
        "estimated_remaining_seconds": estimated_remaining_seconds,
        "last_action": last_action,
        "error_message": error_message,
        "start_time": start_time,
        "logs": []
    }


def update_status(status_obj: Any, **updates) -> None:
    """
    Safely update a PlaygroundStatus object ensuring required fields are preserved.
    This is useful when you have an existing status object you want to update.
    
    Args:
        status_obj: The PlaygroundStatus object to update
        **updates: Fields to update as keyword arguments
        
    Returns:
        None - updates are applied directly to the object
    """
    # Make sure we don't accidentally remove required fields
    required_fields = ["execution_id", "start_time"]
    
    # Apply updates only if they don't remove required fields
    for key, value in updates.items():
        if key in required_fields and (value is None or value == ""):
            continue  # Skip empty updates to required fields
        
        # Update the attribute if it exists
        if hasattr(status_obj, key):
            setattr(status_obj, key, value) 