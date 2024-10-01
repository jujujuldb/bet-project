import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Comparator:
    def compare_ace_market_files(self, old_file, new_file, output_file):
        """
        Compare deux fichiers ace_market_data et génère un fichier avec les changements.
        Si des changements sont détectés, envoie un e-mail.
        """
        # Charger les anciens et nouveaux fichiers
        old_data = self.load_json(old_file)
        new_data = self.load_json(new_file)

        # Dictionnaires pour un accès rapide par match_id
        old_dict = {match['match_id']: match['aces_data'] for match in old_data}
        new_dict = {match['match_id']: match['aces_data'] for match in new_data}

        changes = []

        # Comparer les données
        for match_id, new_aces_data in new_dict.items():
            if match_id in old_dict:
                old_aces_data = old_dict[match_id]
                match_changes = self.compare_aces_data(match_id, old_aces_data, new_aces_data)
                if match_changes:
                    changes.append(match_changes)

        # Sauvegarder les changements dans un fichier si des changements existent
        if changes:
            self.save_to_file(changes, output_file)
            self.send_email(changes)
        else:
            print("Aucun changement détecté.")

    def compare_aces_data(self, match_id, old_data, new_data):
        """
        Compare les données d'aces pour un match donné et renvoie les différences.
        """
        changes = {}
        for market in new_data:
            if market in old_data and new_data[market] != old_data[market]:
                changes[market] = {
                    "old": old_data[market],
                    "new": new_data[market]
                }

        if changes:
            return {"match_id": match_id, "changes": changes}
        return None

    def load_json(self, filename):
        """
        Charge un fichier JSON.
        """
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_to_file(self, data, filename):
        """
        Sauvegarde les données dans un fichier JSON.
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def send_email(self, changes):
        """
        Envoie un e-mail lorsqu'un changement est détecté.
        """
        # Configurer l'e-mail
        sender_email = "adressedeparis@gmail.com"
        receiver_emails = ["julesdebisschop@gmail.com", "hippolyte2510@gmail.com"]  # Liste des destinataires
        password = "syri qfyu uppr tkjl"  # Remplace par ton mot de passe d'application

        # Créer le message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Changements détectés dans les marchés d'aces",
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_emails)  # Convertir la liste en une chaîne de caractères

        # Créer le contenu de l'e-mail
        text = f"Les changements suivants ont été détectés dans les marchés d'aces:\n\n{json.dumps(changes, indent=4)}"
        part = MIMEText(text, "plain")
        message.attach(part)

        # Envoyer l'e-mail via SMTP
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # Gmail SMTP server
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_emails, message.as_string())  # Accepter une liste de destinataires
            server.quit()
            print("E-mail envoyé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'e-mail : {e}")
