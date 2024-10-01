import psycopg2
from psycopg2.extras import RealDictCursor
import logging

class DBManager:
    def __init__(self, config):
        self.config = config
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.config['host'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            logging.info("Successfully connected to the database")
        except (Exception, psycopg2.Error) as error:
            logging.error(f"Error while connecting to PostgreSQL: {error}")

    def disconnect(self):
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed")

    def execute_query(self, query, params=None):
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                self.conn.commit()
                if cur.description:
                    return cur.fetchall()
        except (Exception, psycopg2.Error) as error:
            logging.error(f"Error executing query: {error}")
            self.conn.rollback()

    def insert_match(self, match_id, data):
        query = """
        INSERT INTO matches (match_id, data)
        VALUES (%s, %s)
        ON CONFLICT (match_id) DO UPDATE
        SET data = EXCLUDED.data, timestamp = CURRENT_TIMESTAMP;
        """
        self.execute_query(query, (match_id, psycopg2.Json(data)))

    def insert_ace_market(self, match_id, market_type, odds):
        query = """
        INSERT INTO ace_markets (match_id, market_type, odds)
        VALUES (%s, %s, %s);
        """
        self.execute_query(query, (match_id, market_type, psycopg2.Json(odds)))

    def get_match(self, match_id):
        query = "SELECT * FROM matches WHERE match_id = %s"
        return self.execute_query(query, (match_id,))

    def get_ace_markets(self, match_id):
        query = "SELECT * FROM ace_markets WHERE match_id = %s"
        return self.execute_query(query, (match_id,))

    def get_recent_matches(self, limit=10):
        query = "SELECT * FROM matches ORDER BY timestamp DESC LIMIT %s"
        return self.execute_query(query, (limit,))