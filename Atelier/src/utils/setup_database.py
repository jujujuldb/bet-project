import psycopg2
import logging
from Atelier.src.utils.config import load_config

def setup_database():
    config = load_config()
    db_config = config['database']

    try:
        # Connect to the PostgreSQL server
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            dbname=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password']
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id SERIAL PRIMARY KEY,
                match_id BIGINT UNIQUE NOT NULL,
                competition VARCHAR(255),
                joueur1 VARCHAR(255),
                joueur2 VARCHAR(255),
                start_time TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ace_markets (
                id SERIAL PRIMARY KEY,
                match_id BIGINT REFERENCES matches(match_id),
                market_type VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(match_id, market_type)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS odds_history (
                id SERIAL PRIMARY KEY,
                ace_market_id INTEGER REFERENCES ace_markets(id),
                selection_name VARCHAR(255) NOT NULL,
                odds DECIMAL(10, 2) NOT NULL,
                recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_match_id ON matches(match_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ace_markets_match_id ON ace_markets(match_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_odds_history_ace_market_id ON odds_history(ace_market_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_odds_history_recorded_at ON odds_history(recorded_at)")

        logging.info("Database setup completed successfully")

    except (Exception, psycopg2.Error) as error:
        logging.error(f"Error while setting up database: {error}")

    finally:
        if conn:
            cursor.close()
            conn.close()
            logging.info("Database connection closed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    setup_database()