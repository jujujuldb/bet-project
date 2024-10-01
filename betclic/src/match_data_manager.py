import requests
import json
import time


class MatchDataManager:
    API_BASE_V6 = "https://offer.cdn.begmedia.com/api/pub/v6/events/"

    def __init__(self, countrycode='fr', language='fr', sitecode='frfr'):
        self.countrycode = countrycode
        self.language = language
        self.sitecode = sitecode

    def get_match_ids(self, limit=1000, markettypeId=2013):
        """
        Récupère la liste des IDs de match à partir de l'API.
        """
        url = f"https://offer.cdn.begmedia.com/api/pub/v4/sports/2?application=2&countrycode={self.countrycode}&hasSwitchMtc=true&language={self.language}&limit={limit}&markettypeId={markettypeId}&offset=0&sitecode={self.sitecode}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            match_ids = [event['id'] for event in data.get('matches', [])]
            return match_ids
        else:
            print(f"Erreur {response.status_code} lors de la requête à l'API.")
            return []

    def get_match_details(self, match_id):
        """
        Récupère les détails d'un match via l'API V6.
        """
        url1 = f"{self.API_BASE_V6}{match_id}?application=2&categorizationId=41&countrycode={self.countrycode}&language={self.language}&"
        url2 = f"{self.API_BASE_V6}{match_id}?application=2&categorizationId=41&countrycode={self.countrycode}&language={self.language}&sitecode={self.sitecode}"

        response1 = requests.get(url1)
        if response1.status_code == 200:
            return response1.json()

        response2 = requests.get(url2)
        if response2.status_code == 200:
            return response2.json()

        print(f"Aucune donnée récupérée pour le match ID: {match_id}")
        return None

    def get_ace_markets(self, match_ids):
        """
        Récupère les informations sur les marchés liés aux aces pour chaque match.
        """
        ace_markets = [
            "Plus grand nombre d'aces",
            "Nombre total d'aces dans le match",
            "Nombre d'aces inscrits par le joueur 1 dans le match",
            "Nombre d'aces inscrits par le joueur 2 dans le match"
        ]

        match_data = []
        for match_id in match_ids:
            data = self.get_match_details(match_id)
            if not data:
                continue

            match_info = {"match_id": match_id, "aces_data": {}}

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

    def save_to_file(self, data, filename):
        """
        Sauvegarde les données dans un fichier JSON.
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_from_file(self, filename):
        """
        Charge les données depuis un fichier JSON.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Le fichier {filename} n'existe pas.")
            return []
