import requests
import logging
from .config import API_URL, API_KEY  # Import necessary settings

logger = logging.getLogger(__name__)

def fetch_data():
    """Fetches data from the Betclic API."""
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from API: {e}")
        return None  # Or handle the error differently (e.g., retry)
