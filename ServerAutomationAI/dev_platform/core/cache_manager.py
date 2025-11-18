"""
Lightweight Cache & State Manager
Using diskcache + SQLite for efficient caching
"""

import sqlite3
import json
from pathlib import Path
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from diskcache import Cache


class CacheManager:
    """
    Lightweight cache and state manager
    
    Features:
    - File-based cache (diskcache)
    - SQLite for structured state
    - Low memory usage (~50 MB)
    - Fast read/write
    """
    
    def __init__(self, cache_dir: str = "data/cache", db_file: str = "data/state.db"):
        self.cache_dir = Path(cache_dir)
        self.db_file = Path(db_file)
        
        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize cache
        self.cache = Cache(str(self.cache_dir))
        
        # Initialize SQLite database
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database schema"""
        with sqlite3.connect(str(self.db_file)) as conn:
            cursor = conn.cursor()
            
            # Agent state table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_state (
                    agent_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    last_activity TIMESTAMP NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Task history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    result TEXT,
                    metadata TEXT
                )
            """)
            
            # Model usage tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    tokens_used INTEGER NOT NULL,
                    request_time REAL NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    success BOOLEAN NOT NULL
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_history_agent 
                ON task_history(agent_id, created_at DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_usage_provider 
                ON model_usage(provider, timestamp DESC)
            """)
            
            conn.commit()
    
    # ===== Cache Operations =====
    
    def cache_get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        return self.cache.get(key, default)
    
    def cache_set(self, key: str, value: Any, expire: Optional[int] = None):
        """Set value in cache with optional expiration (seconds)"""
        self.cache.set(key, value, expire=expire)
    
    def cache_delete(self, key: str):
        """Delete key from cache"""
        self.cache.delete(key)
    
    def cache_clear(self):
        """Clear all cache"""
        self.cache.clear()
    
    # ===== Agent State Management =====
    
    def save_agent_state(self, agent_id: str, state: str, metadata: Optional[Dict] = None):
        """Save agent state to database"""
        with sqlite3.connect(str(self.db_file)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO agent_state (agent_id, state, last_activity, metadata)
                VALUES (?, ?, ?, ?)
            """, (
                agent_id,
                state,
                datetime.now(),
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
    
    def get_agent_state(self, agent_id: str) -> Optional[Dict]:
        """Get agent state from database"""
        with sqlite3.connect(str(self.db_file)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT state, last_activity, metadata 
                FROM agent_state 
                WHERE agent_id = ?
            """, (agent_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "state": row[0],
                    "last_activity": row[1],
                    "metadata": json.loads(row[2]) if row[2] else None
                }
        return None
    
    def list_agents(self) -> List[Dict]:
        """List all agents and their states"""
        with sqlite3.connect(str(self.db_file)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT agent_id, state, last_activity 
                FROM agent_state 
                ORDER BY last_activity DESC
            """)
            
            return [
                {
                    "agent_id": row[0],
                    "state": row[1],
                    "last_activity": row[2]
                }
                for row in cursor.fetchall()
            ]
    
    # ===== Task History =====
    
    def save_task(self, task_id: str, agent_id: str, status: str, 
                  result: Optional[str] = None, metadata: Optional[Dict] = None):
        """Save task to history"""
        with sqlite3.connect(str(self.db_file)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO task_history 
                (task_id, agent_id, status, created_at, result, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                agent_id,
                status,
                datetime.now(),
                result,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
    
    def update_task(self, task_id: str, status: str, result: Optional[str] = None):
        """Update task status"""
        with sqlite3.connect(str(self.db_file)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE task_history 
                SET status = ?, completed_at = ?, result = ?
                WHERE task_id = ?
            """, (status, datetime.now(), result, task_id))
            conn.commit()
    
    def get_task_history(self, agent_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get task history"""
        with sqlite3.connect(str(self.db_file)) as conn:
            cursor = conn.cursor()
            
            if agent_id:
                cursor.execute("""
                    SELECT task_id, agent_id, status, created_at, completed_at, result
                    FROM task_history
                    WHERE agent_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (agent_id, limit))
            else:
                cursor.execute("""
                    SELECT task_id, agent_id, status, created_at, completed_at, result
                    FROM task_history
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
            
            return [
                {
                    "task_id": row[0],
                    "agent_id": row[1],
                    "status": row[2],
                    "created_at": row[3],
                    "completed_at": row[4],
                    "result": row[5]
                }
                for row in cursor.fetchall()
            ]
    
    # ===== Model Usage Tracking =====
    
    def log_model_usage(self, provider: str, model: str, tokens_used: int, 
                       request_time: float, success: bool = True):
        """Log model API usage"""
        with sqlite3.connect(str(self.db_file)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO model_usage 
                (provider, model, tokens_used, request_time, timestamp, success)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (provider, model, tokens_used, request_time, datetime.now(), success))
            conn.commit()
    
    def get_model_stats(self, hours: int = 24) -> Dict:
        """Get model usage statistics"""
        since = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(str(self.db_file)) as conn:
            cursor = conn.cursor()
            
            # Total requests and tokens
            cursor.execute("""
                SELECT 
                    provider,
                    COUNT(*) as requests,
                    SUM(tokens_used) as total_tokens,
                    AVG(request_time) as avg_time,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful
                FROM model_usage
                WHERE timestamp > ?
                GROUP BY provider
            """, (since,))
            
            stats = {}
            for row in cursor.fetchall():
                stats[row[0]] = {
                    "requests": row[1],
                    "total_tokens": row[2] or 0,
                    "avg_response_time": round(row[3] or 0, 3),
                    "successful": row[4],
                    "success_rate": round((row[4] / row[1]) * 100, 2) if row[1] > 0 else 0
                }
            
            return stats
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data from database"""
        cutoff = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(str(self.db_file)) as conn:
            cursor = conn.cursor()
            
            # Clean old task history
            cursor.execute("""
                DELETE FROM task_history 
                WHERE created_at < ?
            """, (cutoff,))
            
            # Clean old model usage logs
            cursor.execute("""
                DELETE FROM model_usage 
                WHERE timestamp < ?
            """, (cutoff,))
            
            conn.commit()
            
            # Vacuum database to reclaim space
            cursor.execute("VACUUM")


# Global instance
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
