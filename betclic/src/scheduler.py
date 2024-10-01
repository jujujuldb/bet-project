import time
import os
from match_data_manager import MatchDataManager
from comparator import Comparator

class Scheduler:
    def __init__(self, interval=600):
        self.interval = interval
        self.manager = MatchDataManager()
        self.comparator = Comparator()
        self.data_directory = 'data'  # Répertoire où les fichiers seront enregistrés

    def ensure_directory_exists(self):
        """
        Vérifie si le répertoire de données existe et le crée si nécessaire.
        """
        if not os.path.exists(self.data_directory):
            print(f"Le répertoire {self.data_directory} n'existe pas. Création du répertoire...")
            os.makedirs(self.data_directory)

    def run(self):
        """
        Planification de la tâche toutes les 10 minutes.
        """
        cycle_count = 0  # Compte le nombre de cycles pour vérifier la répétition
        while True:
            try:
                cycle_count += 1
                print(f"\nCycle n°{cycle_count} démarré...")

                # Vérifier si le répertoire de données existe, sinon le créer
                self.ensure_directory_exists()

                # Étape 1 : Récupérer les données des marchés d'aces
                print("Récupération des IDs de matchs...")
                match_ids = self.manager.get_match_ids()
                if not match_ids:
                    print("Aucun match trouvé. Réessayez dans 10 minutes.")
                else:
                    print(f"Nombre de matchs récupérés : {len(match_ids)}")

                    # Étape 2 : Récupérer les nouvelles données et les sauvegarder
                    new_file = os.path.join(self.data_directory, 'ace_market_data_new.json')
                    old_file = os.path.join(self.data_directory, 'ace_market_data_old.json')
                    changes_file = os.path.join(self.data_directory, 'changes.json')

                    print("Récupération des données des marchés d'aces...")
                    new_data = self.manager.get_ace_markets(match_ids)

                    print(f"Sauvegarde des données dans {new_file}...")
                    self.manager.save_to_file(new_data, new_file)

                    # Étape 3 : Vérifier si le fichier old existe
                    if not os.path.exists(old_file):
                        print(f"Aucun fichier old trouvé. Sauvegarde du nouveau fichier sous {old_file}.")
                        self.manager.save_to_file(new_data, old_file)
                    else:
                        # Étape 4 : Comparer avec l'ancien fichier
                        print("Comparaison des fichiers...")
                        self.comparator.compare_ace_market_files(old_file, new_file, changes_file)

                        # Étape 5 : Remplacer l'ancien fichier par le nouveau pour la prochaine itération
                        print(f"Sauvegarde des nouvelles données sous {old_file} pour le prochain cycle.")
                        self.manager.save_to_file(new_data, old_file)

                # Étape 6 : Attendre 10 minutes
                print(f"Attente de {self.interval / 60} minutes avant la prochaine exécution.")
                time.sleep(self.interval)

            except Exception as e:
                print(f"Une erreur est survenue dans le cycle n°{cycle_count} : {e}")
                # Attendre avant de réessayer même en cas d'erreur
                print(f"Réessai dans {self.interval / 60} minutes après l'erreur.")
                time.sleep(self.interval)


# Ajouter le bloc if __name__ == "__main__" pour exécuter le scheduler
if __name__ == "__main__":
    scheduler = Scheduler(interval=600)  # Intervalle de 10 minutes
    scheduler.run()
