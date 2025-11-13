#!/usr/bin/env python3
"""
Async task queue for background content moderation processing
Handles batch operations, analytics, and cleanup tasks with retry logic
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import uuid
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class Task:
    id: str
    task_type: str
    payload: Dict[str, Any]
    status: TaskStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class AsyncTaskQueue:
    """Async task queue for background content moderation processing"""

    def __init__(self, max_concurrent_tasks: int = 3):
        self.tasks: Dict[str, Task] = {}
        self.pending_queue = asyncio.Queue()
        self.max_concurrent_tasks = max_concurrent_tasks
        self.running_tasks = set()
        self.workers_started = False

    async def start_workers(self):
        """Start background worker tasks"""
        if self.workers_started:
            return

        self.workers_started = True
        for i in range(self.max_concurrent_tasks):
            asyncio.create_task(self._worker(f"moderation_worker_{i}"))

    async def add_task(self, task_type: str, payload: Dict[str, Any], max_retries: int = 3) -> str:
        """Add a task to the queue"""
        task_id = f"{task_type}_{uuid.uuid4().hex[:8]}"

        task = Task(
            id=task_id,
            task_type=task_type,
            payload=payload,
            status=TaskStatus.PENDING,
            created_at=time.time(),
            max_retries=max_retries
        )

        self.tasks[task_id] = task
        await self.pending_queue.put(task_id)

        logger.info(f"Task {task_id} added to queue: {task_type}")

        return task_id

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and result"""
        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "id": task.id,
            "task_type": task.task_type,
            "status": task.status.value,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "retry_count": task.retry_count,
            "max_retries": task.max_retries,
            "error": task.error,
            "result": task.result,
            "progress": self._calculate_progress(task)
        }

    def _calculate_progress(self, task: Task) -> float:
        """Calculate task progress (0-1)"""
        if task.status == TaskStatus.COMPLETED:
            return 1.0
        elif task.status == TaskStatus.FAILED:
            return 0.0
        elif task.status == TaskStatus.RUNNING:
            # Estimate progress based on task type and elapsed time
            if task.started_at:
                elapsed = time.time() - task.started_at
                if task.task_type == "batch_moderation":
                    # Batch moderation: estimate based on item count
                    total_items = task.payload.get("total_items", 1)
                    return min(0.9, elapsed / (total_items * 0.1))  # Rough estimate
                elif task.task_type == "analytics_generation":
                    return min(0.9, elapsed / 30.0)  # 30 seconds estimate
                elif task.task_type == "cleanup_operation":
                    return min(0.9, elapsed / 60.0)  # 1 minute estimate
            return 0.5  # Default mid-progress
        return 0.0

    async def _worker(self, worker_name: str):
        """Background worker to process tasks"""
        while True:
            try:
                # Get next task from queue
                task_id = await self.pending_queue.get()
                task = self.tasks.get(task_id)

                if not task or task.status != TaskStatus.PENDING:
                    continue

                # Mark task as running
                task.status = TaskStatus.RUNNING
                task.started_at = time.time()
                self.running_tasks.add(task_id)

                logger.info(f"Worker {worker_name} started task {task_id}")

                try:
                    # Process the task
                    result = await self._process_task(task)

                    # Mark as completed
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = time.time()
                    task.result = result

                    logger.info(f"Task {task_id} completed by {worker_name}")

                except Exception as e:
                    # Handle task failure
                    task.error = str(e)

                    if task.retry_count < task.max_retries:
                        # Retry the task
                        task.retry_count += 1
                        task.status = TaskStatus.RETRYING

                        # Add back to queue with delay
                        await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff
                        await self.pending_queue.put(task_id)

                        logger.warning(f"Task {task_id} retrying (attempt {task.retry_count})")
                    else:
                        # Max retries exceeded
                        task.status = TaskStatus.FAILED
                        task.completed_at = time.time()

                        logger.error(f"Task {task_id} failed permanently")

                finally:
                    self.running_tasks.discard(task_id)

            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)

    async def _process_task(self, task: Task) -> Dict[str, Any]:
        """Process a specific task based on its type"""
        task_type = task.task_type

        if task_type == "batch_moderation":
            return await self._process_batch_moderation(task.payload)
        elif task_type == "analytics_generation":
            return await self._process_analytics_generation(task.payload)
        elif task_type == "cleanup_operation":
            return await self._process_cleanup_operation(task.payload)
        elif task_type == "sentiment_analysis":
            return await self._process_sentiment_analysis(task.payload)
        elif task_type == "feedback_processing":
            return await self._process_feedback_processing(task.payload)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _process_batch_moderation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process batch content moderation"""
        from .moderation_agent import moderation_agent

        contents = payload.get("contents", [])
        content_type = payload.get("content_type", "text")
        metadata = payload.get("metadata", {})

        results = []
        total_processed = 0
        total_flagged = 0

        for i, content in enumerate(contents):
            try:
                # Update task progress (simulate)
                await asyncio.sleep(0.01)  # Small delay for progress tracking

                result = await moderation_agent.moderate(content, content_type, metadata)
                results.append({
                    "content_index": i,
                    "content": content[:100] + "..." if len(content) > 100 else content,
                    "result": result
                })

                total_processed += 1
                if result.get("flagged", False):
                    total_flagged += 1

            except Exception as e:
                results.append({
                    "content_index": i,
                    "error": str(e),
                    "content": content[:100] + "..." if len(content) > 100 else content
                })

        return {
            "total_items": len(contents),
            "processed": total_processed,
            "flagged": total_flagged,
            "results": results,
            "processing_time": time.time()
        }

    async def _process_analytics_generation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analytics data"""
        from .sentiment_analyzer import sentiment_analyzer

        # Generate mock analytics - in real implementation, query actual data
        await asyncio.sleep(2)  # Simulate processing time

        # Generate sentiment analysis for recent content
        mock_feedbacks = [
            {"text": f"Feedback {i}", "rating": (i % 5) + 1}
            for i in range(50)
        ]

        texts = [fb["text"] for fb in mock_feedbacks]
        ratings = [fb["rating"] for fb in mock_feedbacks]

        sentiment_results = sentiment_analyzer.analyze_batch(texts, ratings, "analytics")
        sentiment_summary = sentiment_analyzer.get_sentiment_summary(sentiment_results)

        return {
            "analytics_type": payload.get("analytics_type", "comprehensive"),
            "time_range": payload.get("time_range", "24h"),
            "sentiment_analysis": sentiment_summary,
            "total_feedbacks_analyzed": len(sentiment_results),
            "generated_at": datetime.utcnow().isoformat()
        }

    async def _process_cleanup_operation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process cleanup operations"""
        from .storage import storage_manager

        operation_type = payload.get("operation_type", "temp_files")
        max_age_days = payload.get("max_age_days", 30)

        if operation_type == "temp_files":
            segment = "temp"
        elif operation_type == "old_logs":
            segment = "logs"
        else:
            segment = "temp"

        cleaned_count = storage_manager.cleanup_old_files(segment, max_age_days)

        return {
            "operation_type": operation_type,
            "segment": segment,
            "max_age_days": max_age_days,
            "files_cleaned": cleaned_count,
            "cleanup_time": datetime.utcnow().isoformat()
        }

    async def _process_sentiment_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process sentiment analysis for content"""
        from .sentiment_analyzer import sentiment_analyzer

        texts = payload.get("texts", [])
        ratings = payload.get("ratings")
        context = payload.get("context", "general")

        results = sentiment_analyzer.analyze_batch(texts, ratings, context)
        summary = sentiment_analyzer.get_sentiment_summary(results)

        return {
            "texts_analyzed": len(texts),
            "context": context,
            "results": results,
            "summary": summary,
            "processing_time": time.time()
        }

    async def _process_feedback_processing(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process user feedback for RL learning"""
        from .moderation_agent import moderation_agent

        moderation_id = payload.get("moderation_id")
        reward = payload.get("reward", 0.0)

        if moderation_id:
            await moderation_agent.update_with_feedback(moderation_id, reward)

        return {
            "moderation_id": moderation_id,
            "reward_applied": reward,
            "rl_agent_updated": True,
            "processing_time": time.time()
        }

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        status_counts = {}
        for task in self.tasks.values():
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        # Calculate average processing times
        completed_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
        avg_processing_time = 0.0
        if completed_tasks:
            total_time = sum((t.completed_at - t.started_at) for t in completed_tasks if t.started_at and t.completed_at)
            avg_processing_time = total_time / len(completed_tasks)

        return {
            "total_tasks": len(self.tasks),
            "status_breakdown": status_counts,
            "pending_queue_size": self.pending_queue.qsize(),
            "running_tasks": len(self.running_tasks),
            "workers_started": self.workers_started,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "avg_processing_time_seconds": round(avg_processing_time, 2),
            "success_rate": len(completed_tasks) / len(self.tasks) if self.tasks else 0.0
        }

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.FAILED
            task.error = "Task cancelled by user"
            task.completed_at = time.time()
            return True
        return False

    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks from memory"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        tasks_to_remove = []

        for task_id, task in self.tasks.items():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                if task.completed_at and task.completed_at < cutoff_time:
                    tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self.tasks[task_id]

        return len(tasks_to_remove)

# Global task queue instance
task_queue = AsyncTaskQueue(max_concurrent_tasks=3)