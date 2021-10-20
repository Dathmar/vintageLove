import threading
from django.core.mail import send_mail


class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list, from_email, fail_silently, html_message):
        self.subject = subject
        self.recipient_list = recipient_list
        self.message = message
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run(self):
        msg = send_mail(subject=self.subject, message=self.message, from_email=self.from_email,
                        recipient_list=self.recipient_list, fail_silently=self.fail_silently,
                        html_message=self.html_message)