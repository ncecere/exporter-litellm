import logging
from typing import Any, Dict, Optional

import backoff
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from ..config import DatabaseConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection_pool = None
        self.setup_connection_pool()

    def setup_connection_pool(self):
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                self.config.min_connections,
                self.config.max_connections,
                host=self.config.host,
                port=self.config.port,
                database=self.config.name,
                user=self.config.user,
                password=self.config.password,
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Error creating connection pool: {e}")
            raise

    @backoff.on_exception(backoff.expo, Exception, max_tries=5)
    def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> list:
        conn = None
        cur = None
        try:
            conn = self.connection_pool.getconn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(query, params or {})
            return cur.fetchall()
        except Exception as e:
            logger.error(f"Database query error: {e}")
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                self.connection_pool.putconn(conn)
