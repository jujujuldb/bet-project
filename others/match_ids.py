import requests
import json


# Fonction pour interroger l'API et récupérer la liste des IDs de match
def get_match_ids():
    # URL de l'API
    url = "https://offer.cdn.begmedia.com/api/pub/v4/sports/2?application=2&countrycode=fr&hasSwitchMtc=true&language=fr&limit=1000&markettypeId=2013&offset=0&sitecode=frfr"

    # Faire la requête GET pour obtenir les données JSON depuis l'API
    response = requests.get(url)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Charger les données JSON
        data = response.json()

        # Récupérer tous les IDs de match dans la liste
        match_ids = [event['id'] for event in data.get('matches', [])]

        # Afficher la liste des IDs
        print(f"Liste des IDs de match : {match_ids}")
        print(len(match_ids))

        # Retourner la liste des IDs
        return match_ids
    else:
        print(f"Erreur {response.status_code} lors de la requête à l'API.")
        return []


# Appel de la fonction pour récupérer les IDs
match_ids = get_match_ids()

# Optionnel : Sauvegarder les IDs dans un fichier JSON
with open('match_ids.json', 'w', encoding='utf-8') as f:
    json.dump(match_ids, f, ensure_ascii=False, indent=4)

print("Les IDs de match ont été sauvegardés dans 'match_ids.json'")


def get_competition_and_contestants(match_ids):
    # Parcourir chaque ID de match
    for match_id in match_ids:
        # Première URL à essayer
        url1 = f"https://offer.cdn.begmedia.com/api/pub/v6/events/{match_id}?application=2&categorizationId=41&countrycode=fr&language=fr&"

        # Deuxième URL à essayer si la première ne fonctionne pas
        url2 = f"https://offer.cdn.begmedia.com/api/pub/v6/events/{match_id}?application=2&categorizationId=41&countrycode=fr&language=fr&sitecode=frfr"

        # Essayer de récupérer les données depuis la première URL
        response1 = requests.get(url1)
        if response1.status_code == 200:
            data = response1.json()
            if "competition" in data and "contestants" in data:
                competition_name = data['competition']['name']
                contestant_names = [contestant['name'] for contestant in data['contestants']]
                print(f"Match ID: {match_id}")
                print(f"Competition: {competition_name}")
                print(f"Contestants: {contestant_names}")
                continue  # Passer au prochain ID de match

        # Si la première URL ne fonctionne pas, essayer la deuxième
        response2 = requests.get(url2)
        if response2.status_code == 200:
            data = response2.json()
            if "competition" in data and "contestants" in data:
                competition_name = data['competition']['name']
                contestant_names = [contestant['name'] for contestant in data['contestants']]
                print(f"Match ID: {match_id}")
                print(f"Competition: {competition_name}")
                print(f"Contestants: {contestant_names}")
        else:
            print(f"Aucune donnée récupérée pour le match ID: {match_id}")


get_competition_and_contestants(match_ids)
