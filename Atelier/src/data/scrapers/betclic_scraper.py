import requests
import logging
from datetime import datetime
from Atelier.src.data.scrapers.base_scraper import BaseScraper

class BetclicScraper(BaseScraper):
    def __init__(self, config):
        self.config = config
        self.api_base = config['api']['base_url']
        self.countrycode = config['api']['countrycode']
        self.language = config['api']['language']
        self.sitecode = config['api']['sitecode']

    def get_match_ids(self, limit=1000, markettypeId=2013):
        url = f"https://offer.cdn.begmedia.com/api/pub/v4/sports/2?application=2&countrycode={self.countrycode}&hasSwitchMtc=true&language={self.language}&limit={limit}&markettypeId={markettypeId}&offset=0&sitecode={self.sitecode}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return [event['id'] for event in data.get('matches', [])]
        except requests.RequestException as e:
            logging.error(f"Error fetching match IDs: {e}")
            return []

    def get_match_details(self, match_id):
        urls = [
            f"{self.api_base}{match_id}?application=2&categorizationId=41&countrycode={self.countrycode}&language={self.language}&",
            f"{self.api_base}{match_id}?application=2&categorizationId=41&countrycode={self.countrycode}&language={self.language}&sitecode={self.sitecode}"
        ]

        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                logging.warning(f"Error fetching match details from {url}: {e}")

        logging.error(f"Failed to fetch details for match ID: {match_id}")
        return None

    def get_ace_markets(self, match_ids):
        ace_markets = [
            "Plus grand nombre d'aces",
            "Nombre total d'aces dans le match",
            "Nombre d'aces inscrits par le joueur 1 dans le match",
            "Nombre d'aces inscrits par le joueur 2 dans le match"
        ]

        match_data = []

        for match_id in match_ids:
            # Fetch match details for the given match_id
            data = self.get_match_details(match_id)
            if not data:
                print(f"Warning: No data found for match ID {match_id}")
                continue

            # Handle start date safely
            start_date_str = data.get('date', '')
            if start_date_str:
                try:
                    start_time = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                except ValueError:
                    print(f"Warning: Invalid date format for match ID {match_id}: {start_date_str}")
                    start_time = None
            else:
                print(f"Warning: Missing 'startDate' for match ID {match_id}")
                start_time = None

            contestants = data.get('contestants', [])
            match_info = {
                "match_id": match_id,
                "competition": data.get('competition', {}).get('name', 'Unknown'),
                "contestants": {
                    'joueur 1': contestants[0].get('name', 'Unknown') if len(contestants) > 0 else 'Unknown',
                    'joueur 2': contestants[1].get('name', 'Unknown') if len(contestants) > 1 else 'Unknown'
                },
                "start_time": start_time,
                "aces_data": {}  # Placeholder for aces data
            }

            if "grouped_markets" in data:
                for ace_market in ace_markets:
                    market_found = False
                    for grouped_market in data["grouped_markets"]:
                        for market in grouped_market["markets"]:
                            if market["name"] == ace_market:
                                market_info = []
                                for selection_group in market.get("selections", []):
                                    for selection in selection_group:
                                        market_info.append({
                                            "name": selection.get("name", "None"),
                                            "odds": selection.get("odds", "None")
                                        })
                                match_info["aces_data"][ace_market] = market_info
                                market_found = True
                                break
                        if market_found:
                            break

                    if not market_found:
                        match_info["aces_data"][ace_market] = "None"

            match_data.append(match_info)

        return match_data

if __name__=='__main__':
    from Atelier.src.utils.config import load_config
    config = load_config()
    scraper = BetclicScraper(config)
    match_ids = scraper.get_match_ids()
    match_details = scraper.get_match_details(match_ids)
    ace_markets = scraper.get_ace_markets(match_ids)
    print('a')