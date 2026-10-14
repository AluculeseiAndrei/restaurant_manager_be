import smtplib
import ssl

from restaurant_api.core.config import Settings
from restaurant_api.interfaces.email import EmailSender


class SmtpEmailSender:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def send(self, recipient: str, subject: str, body: str) -> None:
        if not self._settings.smtp_sender_email or not self._settings.smtp_password:
            return
        message = f"Subject: {subject}\nFrom: {self._settings.smtp_sender_email}\nTo: {recipient}\n\n{body}"
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as server:
            server.login(self._settings.smtp_sender_email, self._settings.smtp_password)
            server.sendmail(self._settings.smtp_sender_email, recipient, message)
