from django.db import models


class CertbotChallenge(models.Model):
    acme_url = models.CharField(max_length=4000)
    acme_challenge = models.CharField(max_length=4000)
