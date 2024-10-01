from Atelier.src.data.storage.db_manager import DBManager
from Atelier.src.utils.config import load_config
import logging

logging.basicConfig(level=logging.INFO)


def test_database():
    config = load_config()
    db = DBManager(config['database'])

    try:
        db.connect()

        # Test inserting a match
        match_data = {
            "id": "12345",
            "teams": ["Team A", "Team B"],
            "date": "2023-09-16"
        }
        db.insert_match("12345", match_data)
        logging.info("Inserted test match")

        # Test inserting an ace market
        ace_market_data = {
            "market": "Total Aces",
            "odds": {"over": 1.5, "under": 2.5}
        }
        db.insert_ace_market("12345", "Total Aces", ace_market_data)
        logging.info("Inserted test ace market")

        # Test retrieving data
        match = db.get_match("12345")
        logging.info(f"Retrieved match: {match}")

        ace_markets = db.get_ace_markets("12345")
        logging.info(f"Retrieved ace markets: {ace_markets}")

        recent_matches = db.get_recent_matches(5)
        logging.info(f"Retrieved recent matches: {recent_matches}")

    finally:
        db.disconnect()


if __name__ == "__main__":
    test_database()