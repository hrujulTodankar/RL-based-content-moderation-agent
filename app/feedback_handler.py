import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

# Database support (works with both SQLite and PostgreSQL/Supabase)
try:
    import asyncpg
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

import aiosqlite

logger = logging.getLogger(__name__)

class FeedbackHandler:
    """Handles user feedback storage and retrieval with multi-DB support"""
    
    def __init__(self):
        self.db_type = os.getenv("DB_TYPE", "sqlite")  # sqlite or postgres
        self.db_path = os.getenv("DB_PATH", "logs/moderation.db")
        self.postgres_url = os.getenv("DATABASE_URL", None)
        
        # Connection management
        self.db_conn = None
        self.pool = None
        self._connection_retries = 3
        self._retry_delay = 0.1  # 100ms delay between retries
        
        # SQLite connection pool simulation
        self._sqlite_connections = []
        self._max_sqlite_connections = 5
        
        logger.info(f"FeedbackHandler initialized with {self.db_type}")
    
    async def initialize(self):
        """Initialize database connection and create tables"""
        try:
            if self.db_type == "postgres" and POSTGRES_AVAILABLE and self.postgres_url:
                await self._init_postgres()
            else:
                await self._init_sqlite()
            
            logger.info("FeedbackHandler database initialized")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}", exc_info=True)
            raise
    
    async def _get_sqlite_connection(self):
        """Get a healthy SQLite connection with retry logic"""
        # Clean up closed connections
        self._sqlite_connections = [conn for conn in self._sqlite_connections if not conn.is_closed()]
        
        # Return existing connection if available
        if self._sqlite_connections:
            return self._sqlite_connections[0]
        
        # Create new connection
        for attempt in range(self._connection_retries):
            try:
                conn = await aiosqlite.connect(self.db_path)
                await conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for better concurrency
                await conn.execute("PRAGMA synchronous=NORMAL")  # Balance performance and safety
                await conn.execute("PRAGMA cache_size=1000")  # Increase cache size
                self._sqlite_connections.append(conn)
                logger.debug(f"Created new SQLite connection (attempt {attempt + 1})")
                return conn
            except Exception as e:
                logger.warning(f"SQLite connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < self._connection_retries - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
        
        raise ConnectionError("Failed to establish SQLite connection after retries")
    
    async def _ensure_postgres_pool(self):
        """Ensure PostgreSQL connection pool is healthy"""
        if self.pool is None or self.pool.is_closing():
            logger.info("Recreating PostgreSQL connection pool")
            self.pool = await asyncpg.create_pool(
                self.postgres_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
    
    async def _init_sqlite(self):
        """Initialize SQLite database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Create initial connection for schema setup
        conn = await self._get_sqlite_connection()
        
        # Create moderation table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS moderations (
                moderation_id TEXT PRIMARY KEY,
                content_type TEXT NOT NULL,
                flagged BOOLEAN NOT NULL,
                score REAL NOT NULL,
                confidence REAL NOT NULL,
                mcp_weighted_score REAL,
                reasons TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create feedback table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id TEXT PRIMARY KEY,
                moderation_id TEXT NOT NULL,
                user_id TEXT,
                feedback_type TEXT NOT NULL,
                rating INTEGER,
                comment TEXT,
                reward_value REAL NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (moderation_id) REFERENCES moderations(moderation_id)
            )
        """)
        
        # Create indexes
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_moderation_timestamp ON moderations(timestamp)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_feedback_moderation ON feedback(moderation_id)"
        )
        
        await conn.commit()
        logger.info("SQLite database schema initialized")
    
    async def _init_postgres(self):
        """Initialize PostgreSQL/Supabase connection"""
        await self._ensure_postgres_pool()
        
        async with self.pool.acquire() as conn:
            # Create moderation table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS moderations (
                    moderation_id TEXT PRIMARY KEY,
                    content_type TEXT NOT NULL,
                    flagged BOOLEAN NOT NULL,
                    score REAL NOT NULL,
                    confidence REAL NOT NULL,
                    mcp_weighted_score REAL,
                    reasons JSONB,
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create feedback table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    moderation_id TEXT NOT NULL,
                    user_id TEXT,
                    feedback_type TEXT NOT NULL,
                    rating INTEGER,
                    comment TEXT,
                    reward_value REAL NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (moderation_id) REFERENCES moderations(moderation_id)
                )
            """)
            
            # Create indexes
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_moderation_timestamp ON moderations(timestamp)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_feedback_moderation ON feedback(moderation_id)"
            )
    
    async def close(self):
        """Close all database connections"""
        # Close SQLite connections
        for conn in self._sqlite_connections:
            if not conn.is_closed():
                await conn.close()
        self._sqlite_connections.clear()
        
        # Close PostgreSQL pool
        if self.pool and not self.pool.is_closing():
            await self.pool.close()
        
        logger.info("All database connections closed")
    
    async def store_moderation(self, moderation_record: Dict[str, Any]):
        """Store moderation result"""
        try:
            if self.db_type == "postgres" and self.pool:
                await self._store_moderation_postgres(moderation_record)
            else:
                await self._store_moderation_sqlite(moderation_record)
            
            logger.info(f"Stored moderation {moderation_record['moderation_id']}")
        except Exception as e:
            logger.error(f"Error storing moderation: {str(e)}", exc_info=True)
            raise
    
    async def _store_moderation_sqlite(self, record: Dict[str, Any]):
        """Store moderation in SQLite"""
        conn = await self._get_sqlite_connection()

        await conn.execute("""
            INSERT INTO moderations
            (moderation_id, content_type, flagged, score, confidence,
             mcp_weighted_score, reasons, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record["moderation_id"],
            record["content_type"],
            record["flagged"],
            record["score"],
            record["confidence"],
            record.get("mcp_weighted_score"),
            json.dumps(record["reasons"]),
            record["timestamp"]
        ))
        await conn.commit()
    
    async def _store_moderation_postgres(self, record: Dict[str, Any]):
        """Store moderation in PostgreSQL"""
        await self._ensure_postgres_pool()
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO moderations 
                (moderation_id, content_type, flagged, score, confidence, 
                 mcp_weighted_score, reasons, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                record["moderation_id"],
                record["content_type"],
                record["flagged"],
                record["score"],
                record["confidence"],
                record.get("mcp_weighted_score"),
                json.dumps(record["reasons"]),
                datetime.fromisoformat(record["timestamp"])
            )
    
    async def store_feedback(self, feedback_record: Dict[str, Any]):
        """Store user feedback"""
        try:
            if self.db_type == "postgres" and self.pool:
                await self._store_feedback_postgres(feedback_record)
            else:
                await self._store_feedback_sqlite(feedback_record)
            
            logger.info(f"Stored feedback {feedback_record['feedback_id']}")
        except Exception as e:
            logger.error(f"Error storing feedback: {str(e)}", exc_info=True)
            raise
    
    async def _store_feedback_sqlite(self, record: Dict[str, Any]):
        """Store feedback in SQLite"""
        conn = await self._get_sqlite_connection()

        await conn.execute("""
            INSERT INTO feedback
            (feedback_id, moderation_id, user_id, feedback_type,
             rating, comment, reward_value, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record["feedback_id"],
            record["moderation_id"],
            record.get("user_id"),
            record["feedback_type"],
            record.get("rating"),
            record.get("comment"),
            record["reward_value"],
            record["timestamp"]
        ))
        await conn.commit()
    
    async def _store_feedback_postgres(self, record: Dict[str, Any]):
        """Store feedback in PostgreSQL"""
        await self._ensure_postgres_pool()
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO feedback 
                (feedback_id, moderation_id, user_id, feedback_type, 
                 rating, comment, reward_value, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                record["feedback_id"],
                record["moderation_id"],
                record.get("user_id"),
                record["feedback_type"],
                record.get("rating"),
                record.get("comment"),
                record["reward_value"],
                datetime.fromisoformat(record["timestamp"])
            )
    
    async def get_feedback_by_moderation(
        self, 
        moderation_id: str
    ) -> List[Dict[str, Any]]:
        """Get all feedback for a specific moderation"""
        try:
            if self.db_type == "postgres" and self.pool:
                return await self._get_feedback_postgres(moderation_id)
            else:
                return await self._get_feedback_sqlite(moderation_id)
        except Exception as e:
            logger.error(f"Error retrieving feedback: {str(e)}")
            return []
    
    async def _get_feedback_sqlite(
        self,
        moderation_id: str
    ) -> List[Dict[str, Any]]:
        """Get feedback from SQLite"""
        conn = await self._get_sqlite_connection()

        cursor = await conn.execute("""
            SELECT feedback_id, moderation_id, user_id, feedback_type,
                   rating, comment, reward_value, timestamp
            FROM feedback
            WHERE moderation_id = ?
            ORDER BY timestamp DESC
        """, (moderation_id,))

        rows = await cursor.fetchall()

        return [
            {
                "feedback_id": row[0],
                "moderation_id": row[1],
                "user_id": row[2],
                "feedback_type": row[3],
                "rating": row[4],
                "comment": row[5],
                "reward_value": row[6],
                "timestamp": row[7]
            }
            for row in rows
        ]
    
    async def _get_feedback_postgres(
        self, 
        moderation_id: str
    ) -> List[Dict[str, Any]]:
        """Get feedback from PostgreSQL"""
        await self._ensure_postgres_pool()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT feedback_id, moderation_id, user_id, feedback_type,
                       rating, comment, reward_value, timestamp
                FROM feedback
                WHERE moderation_id = $1
                ORDER BY timestamp DESC
            """, moderation_id)
            
            return [dict(row) for row in rows]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get moderation and feedback statistics"""
        try:
            if self.db_type == "postgres" and self.pool:
                return await self._get_stats_postgres()
            else:
                return await self._get_stats_sqlite()
        except Exception as e:
            logger.error(f"Error retrieving statistics: {str(e)}")
            return {}
    
    async def _get_stats_sqlite(self) -> Dict[str, Any]:
        """Get statistics from SQLite"""
        conn = await self._get_sqlite_connection()

        cursor = await conn.execute("""
            SELECT
                COUNT(*) as total_moderations,
                SUM(CASE WHEN flagged = 1 THEN 1 ELSE 0 END) as flagged_count,
                AVG(score) as avg_score,
                AVG(confidence) as avg_confidence
            FROM moderations
        """)
        mod_stats = await cursor.fetchone()

        cursor = await conn.execute("""
            SELECT
                COUNT(*) as total_feedback,
                SUM(CASE WHEN feedback_type = 'thumbs_up' THEN 1 ELSE 0 END) as positive,
                SUM(CASE WHEN feedback_type = 'thumbs_down' THEN 1 ELSE 0 END) as negative,
                AVG(reward_value) as avg_reward
            FROM feedback
        """)
        fb_stats = await cursor.fetchone()

        cursor = await conn.execute("""
            SELECT content_type, COUNT(*) as count
            FROM moderations
            GROUP BY content_type
        """)
        content_type_stats = await cursor.fetchall()

        return {
            "total_moderations": mod_stats[0] or 0,
            "flagged_count": mod_stats[1] or 0,
            "avg_score": float(mod_stats[2]) if mod_stats[2] else 0.0,
            "avg_confidence": float(mod_stats[3]) if mod_stats[3] else 0.0,
            "total_feedback": fb_stats[0] or 0,
            "positive_feedback": fb_stats[1] or 0,
            "negative_feedback": fb_stats[2] or 0,
            "avg_reward": float(fb_stats[3]) if fb_stats[3] else 0.0,
            "content_types": {row[0]: row[1] for row in content_type_stats}
        }
    
    async def _get_stats_postgres(self) -> Dict[str, Any]:
        """Get statistics from PostgreSQL"""
        await self._ensure_postgres_pool()
        async with self.pool.acquire() as conn:
            mod_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_moderations,
                    SUM(CASE WHEN flagged THEN 1 ELSE 0 END) as flagged_count,
                    AVG(score) as avg_score,
                    AVG(confidence) as avg_confidence
                FROM moderations
            """)
            
            fb_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_feedback,
                    SUM(CASE WHEN feedback_type = 'thumbs_up' THEN 1 ELSE 0 END) as positive,
                    SUM(CASE WHEN feedback_type = 'thumbs_down' THEN 1 ELSE 0 END) as negative,
                    AVG(reward_value) as avg_reward
                FROM feedback
            """)
            
            content_type_stats = await conn.fetch("""
                SELECT content_type, COUNT(*) as count
                FROM moderations
                GROUP BY content_type
            """)
            
            return {
                "total_moderations": mod_stats["total_moderations"] or 0,
                "flagged_count": mod_stats["flagged_count"] or 0,
                "avg_score": float(mod_stats["avg_score"]) if mod_stats["avg_score"] else 0.0,
                "avg_confidence": float(mod_stats["avg_confidence"]) if mod_stats["avg_confidence"] else 0.0,
                "total_feedback": fb_stats["total_feedback"] or 0,
                "positive_feedback": fb_stats["positive"] or 0,
                "negative_feedback": fb_stats["negative"] or 0,
                "avg_reward": float(fb_stats["avg_reward"]) if fb_stats["avg_reward"] else 0.0,
                "content_types": {row["content_type"]: row["count"] for row in content_type_stats}
            }
    
    def normalize_feedback(
        self, 
        feedback_type: str, 
        rating: Optional[int] = None
    ) -> float:
        """
        Normalize user feedback to reward value for RL
        Returns: reward value between -1.0 and 1.0
        """
        if feedback_type == "thumbs_up":
            base_reward = 0.5
            # Use rating if provided (1-5 scale)
            if rating:
                base_reward = (rating - 3) / 2  # Maps 1->-1, 3->0, 5->1
            return max(base_reward, 0.1)
        
        elif feedback_type == "thumbs_down":
            base_reward = -0.5
            # Use rating if provided
            if rating:
                base_reward = (rating - 3) / 2
            return min(base_reward, -0.1)
        
        return 0.0

# Global instance
feedback_handler = FeedbackHandler()