from betclic.scraper import MatchDataManager

def main():
    manager = MatchDataManager()

    # Étape 1: Récupérer les IDs des matchs
    match_ids = manager.get_match_ids()

    # Optionnel: Sauvegarder les IDs dans un fichier JSON
    manager.save_to_file(match_ids, 'match_ids.json')

    # Étape 2: Récupérer les détails des compétitions et des joueurs
    match_details = manager.get_competition_and_contestants(match_ids)
    manager.save_to_file(match_details, 'match_details.json')

    # Étape 3: Récupérer les informations des marchés sur les aces
    ace_market_data = manager.get_ace_markets(match_ids)
    manager.save_to_file(ace_market_data, 'ace_market_data.json')

if __name__ == "__main__":
    main()
