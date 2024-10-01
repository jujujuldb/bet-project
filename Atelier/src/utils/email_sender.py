import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSender:
    def __init__(self, config):
        self.sender_email = config['sender']
        self.password = config['password']
        self.receiver_emails = config['recipients']

    def send_email(self, subject, content):
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = self.sender_email
        message["To"] = ", ".join(self.receiver_emails)

        text = MIMEText(content, "plain")
        message.attach(text)

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, self.receiver_emails, message.as_string())
            print("Email sent successfully")
        except Exception as e:
            print(f"Error sending email: {e}")