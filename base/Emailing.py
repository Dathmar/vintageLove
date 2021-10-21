import threading
from django.core.mail import send_mail
from django.conf import settings
import mailchimp_transactional as mailchimpTransactional
from mailchimp_transactional.api_client import ApiClientError


class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient, from_email, fail_silently, html_message):
        self.subject = subject
        self.recipient = recipient
        self.message = message
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run(self):
        mailchimp = mailchimpTransactional.Client(settings.EMAIL_HOST_PASSWORD)
        message = {
            "from_email": self.from_email,
            "subject": self.subject,
            "text": self.message,
            "html": self.html_message,
            "to": [
                {
                    "email": self.recipient,
                    "type": "to"
                }
            ]
        }

        try:
            response = mailchimp.messages.send({"message": message})
            print(f'API called successfully: {response}')
        except ApiClientError as error:
            print(f'An exception occurred: {error.text}')
