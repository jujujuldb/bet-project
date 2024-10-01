import requests
import json

# URL de l'API
url = "https://offer.cdn.begmedia.com/api/pub/v6/events/3002553100?application=2&countrycode=fr&language=fr&sitecode=frfr"
url = "https://offer.cdn.begmedia.com/api/pub/v6/events/3002552572?application=2&categorizationId=41&countrycode=fr&language=fr&"
url = "https://offer.cdn.begmedia.com/api/pub/v6/events/3002551309?application=2&categorizationId=41&countrycode=fr&language=fr&sitecode=frfr"
url = "https://offer.cdn.begmedia.com/api/pub/v4/sports/2?application=2&countrycode=fr&hasSwitchMtc=true&language=fr&limit=1000&markettypeId=2013&offset=0&sitecode=frfr"

# Faire la requête GET pour obtenir le JSON depuis l'API
response = requests.get(url)

# Vérifier si la requête a réussi
if response.status_code == 200:
    # Charger les données JSON
    data = response.json()

    # Décomposer le JSON en format lisible
    readable_json = json.dumps(data, indent=4, ensure_ascii=False)

    # Afficher le JSON formaté
    print(readable_json)

    # Option pour sauvegarder le JSON formaté dans un fichier
    with open('readable_json_output_tennis.json', 'w', encoding='utf-8') as f:
        f.write(readable_json)

    print("JSON décomposé et sauvegardé dans 'readable_json_output.json'")
else:
    print(f"Erreur {response.status_code} lors de la requête à l'API.")
