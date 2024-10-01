import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_test_email():
    # Configuration des informations de l'e-mail
    sender_email = "adressedeparis@gmail.com"
    receiver_emails = ["julesdebisschop@gmail.com", "hippolyte2510@gmail.com"]
    password = "syri qfyu uppr tkjl"

    # Création du message
    subject = "Test e-mail"
    body = "Hello"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_emails)  # Assurer que les e-mails sont une chaîne séparée par des virgules
    message["Subject"] = subject

    # Attacher le texte au message
    message.attach(MIMEText(body, "plain"))

    # Essayer d'envoyer l'e-mail
    try:
        # Connexion au serveur SMTP de Gmail
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # Gmail SMTP server (SSL)
        server.login(sender_email, password)
        # Envoyer à plusieurs destinataires (s'assurer que receiver_emails est une liste)
        server.sendmail(sender_email, receiver_emails, message.as_string())
        server.quit()
        print("E-mail envoyé avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {e}")


# Appeler la fonction pour envoyer l'e-mail
if __name__ == "__main__":
    send_test_email()
