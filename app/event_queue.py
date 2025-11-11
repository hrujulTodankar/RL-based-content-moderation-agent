import asyncio
import logging
from typing import Dict, Any, List, Callable
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

class EventQueue:
    """
    Event queue for cross-service communication
    Emits events to Omkar RL, Ashmit Analytics, and Aditya NLP
    """
    
    def __init__(self):
        self.queues = {
            "moderation_completed": asyncio.Queue(),
            "feedback_omkar_rl": asyncio.Queue(),
            "feedback_bhiv_analytics": asyncio.Queue(),
            "feedback_nlp_confidence": asyncio.Queue(),
            "file_moderation_completed": asyncio.Queue()
        }
        
        self.subscribers = {queue_name: [] for queue_name in self.queues}
        self.event_log = []
        self.max_log_size = 1000
        
        # Background tasks
        self.tasks = []
        
        logger.info("EventQueue initialized")
    
    async def initialize(self):
        """Start background workers for queue processing"""
        for queue_name in self.queues:
            task = asyncio.create_task(self._process_queue(queue_name))
            self.tasks.append(task)
        
        logger.info(f"Started {len(self.tasks)} queue processors")
    
    async def close(self):
        """Stop all background workers"""
        for task in self.tasks:
            task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)
        logger.info("EventQueue closed")
    
    async def emit(self, event_type: str, data: Dict[str, Any]):
        """
        Emit an event to the appropriate queue
        
        Args:
            event_type: Type of event (e.g., 'moderation_completed')
            data: Event data payload
        """
        try:
            if event_type not in self.queues:
                logger.warning(f"Unknown event type: {event_type}")
                return
            
            event = {
                "event_type": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "event_id": f"{event_type}_{len(self.event_log)}"
            }
            
            # Add to queue
            await self.queues[event_type].put(event)
            
            # Log event
            self._log_event(event)
            
            logger.info(f"Event emitted: {event_type} (id: {event['event_id']})")
            
        except Exception as e:
            logger.error(f"Error emitting event: {str(e)}", exc_info=True)
    
    async def _process_queue(self, queue_name: str):
        """Background worker to process events from a queue"""
        queue = self.queues[queue_name]
        
        while True:
            try:
                # Wait for event
                event = await queue.get()
                
                # Notify all subscribers
                for callback in self.subscribers[queue_name]:
                    try:
                        await callback(event)
                    except Exception as e:
                        logger.error(
                            f"Subscriber error for {queue_name}: {str(e)}",
                            exc_info=True
                        )
                
                # Mark task as done
                queue.task_done()
                
            except asyncio.CancelledError:
                logger.info(f"Queue processor {queue_name} cancelled")
                break
            except Exception as e:
                logger.error(
                    f"Error processing queue {queue_name}: {str(e)}",
                    exc_info=True
                )
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to events of a specific type
        
        Args:
            event_type: Type of event to subscribe to
            callback: Async callback function to handle events
        """
        if event_type not in self.subscribers:
            logger.warning(f"Unknown event type for subscription: {event_type}")
            return
        
        self.subscribers[event_type].append(callback)
        logger.info(f"New subscriber added to {event_type}")
    
    def _log_event(self, event: Dict[str, Any]):
        """Log event to in-memory log"""
        self.event_log.append(event)
        
        # Trim log if too large
        if len(self.event_log) > self.max_log_size:
            self.event_log = self.event_log[-self.max_log_size:]
        
        # Also write to file
        try:
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, "events.jsonl")
            with open(log_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Error writing event log: {str(e)}")
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events from the log"""
        return self.event_log[-limit:]
    
    def get_queue_sizes(self) -> Dict[str, int]:
        """Get current size of all queues"""
        return {
            queue_name: queue.qsize()
            for queue_name, queue in self.queues.items()
        }

# Global instance
event_queue = EventQueue()