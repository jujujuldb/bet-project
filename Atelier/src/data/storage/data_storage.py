import psycopg2
from psycopg2 import pool
from typing import Any, Dict, List
import logging
import json
import hashlib

logger = logging.getLogger(__name__)


class DataStorage:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.db_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=5,
            host=config['database']['host'],
            port=config['database']['port'],
            dbname=config['database']['dbname'],
            user=config['database']['user'],
            password=config['database']['password']
        )


    def save_match_data(self, match_data: Dict[str, Any]) -> None:
        conn = self.db_pool.getconn()
        try:
            with conn:
                with conn.cursor() as cur:
                    # Serialize aces_data consistently
                    aces_data_serialized = json.dumps(match_data['aces_data'], sort_keys=True)
                    # Compute the hash of aces_data
                    aces_data_hash = hashlib.sha256(aces_data_serialized.encode('utf-8')).hexdigest()

                    # Insert match data with the computed aces_data_hash
                    cur.execute("""
                        INSERT INTO matches (match_id, competition, joueur1, joueur2, start_time, aces_data, aces_data_hash)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (match_id, aces_data_hash) DO NOTHING
                    """, (
                        match_data['match_id'],
                        match_data['competition'],
                        match_data['contestants']['joueur 1'],
                        match_data['contestants']['joueur 2'],
                        match_data['start_time'],
                        json.dumps(match_data['aces_data']),  # Store as JSONB
                        aces_data_hash
                    ))

        except Exception as e:
            logger.error(f"Error while saving match data for match_id {match_data.get('match_id')}: {e}")
            raise
        finally:
            self.db_pool.putconn(conn)

    def get_latest_odds(self, match_id: int) -> Dict[str, Any]:
        """
        Retrieves the latest odds from the aces_data for a given match_id.

        Parameters:
        - match_id: The ID of the match to retrieve latest odds for.

        Returns:
        - A dictionary containing the aces_data.
        """
        conn = self.db_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT aces_data
                    FROM matches
                    WHERE match_id = %s
                """, (match_id,))
                result = cur.fetchone()
                if result:
                    aces_data = result[0]  # JSON data
                    return aces_data
                else:

                    return {}
        except Exception as e:
            logger.error(f"Error while fetching latest odds: {e}")
            return {}
        finally:
            self.db_pool.putconn(conn)

    def get_odds_changes(self, match_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves odds changes from the matches_history for a given match_id.

        Parameters:
        - match_id: The ID of the match to retrieve odds changes for.

        Returns:
        - A list of dictionaries containing the changes in aces_data over time.
        """
        conn = self.db_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT aces_data, updated_at
                    FROM matches
                    WHERE match_id = %s
                    ORDER BY updated_at ASC
                """, (match_id,))
                rows = cur.fetchall()
                odds_changes = []
                previous_aces_data = None
                for row in rows:
                    try:
                        current_aces_data = row[0]  # JSON data
                        updated_at = row[1]
                        if previous_aces_data is not None:
                            # Compare previous and current aces_data to find changes
                            changes = self._find_aces_data_changes(previous_aces_data, current_aces_data)
                            if changes:
                                odds_changes.append({
                                    'changes': changes,
                                    'timestamp': updated_at
                                })
                        previous_aces_data = current_aces_data
                    except Exception as row_error:
                        logging.error(f"Error processing row for match {match_id}: {row_error}")
                        # Continue to the next row
                        continue
                return odds_changes
        except Exception as e:
            logging.error(f"Error while fetching odds changes for match {match_id}: {e}")
            return []
        finally:
            self.db_pool.putconn(conn)

    def _find_aces_data_changes(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Compares old and new aces_data to find changes.

        Returns:
        - A list of changes found between the two datasets.
        """
        changes = []
        if not isinstance(old_data, dict) or not isinstance(new_data, dict):
            logging.warning(f"Invalid data types: old_data is {type(old_data)}, new_data is {type(new_data)}")
            return changes

        for market_type, new_market in new_data.items():
            old_market = old_data.get(market_type)

            if new_market == "None" and old_market != "None":
                changes.append({
                    'market_type': market_type,
                    'change': 'Market removed',
                    'old_value': str(old_market),
                    'new_value': 'None'
                })
            elif new_market != "None" and old_market == "None":
                changes.append({
                    'market_type': market_type,
                    'change': 'Market added',
                    'old_value': 'None',
                    'new_value': str(new_market)
                })
            elif isinstance(new_market, list) and isinstance(old_market, list):
                for new_selection in new_market:
                    if not isinstance(new_selection, dict):
                        continue

                    old_selection = next((item for item in old_market if
                                          isinstance(item, dict) and item.get('name') == new_selection.get('name')),
                                         None)

                    if old_selection and old_selection.get('odds') != new_selection.get('odds'):
                        changes.append({
                            'market_type': market_type,
                            'selection_name': new_selection.get('name', 'Unknown'),
                            'old_odds': old_selection.get('odds', 'Unknown'),
                            'new_odds': new_selection.get('odds', 'Unknown')
                        })

        return changes

    def close_pool(self) -> None:
        """
        Closes all connections in the connection pool.
        """
        self.db_pool.closeall()
        logger.info("Database connection pool closed.")
