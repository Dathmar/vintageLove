from django.shortcuts import render, get_object_or_404
from .models import CertbotChallenge


def challenge(request, acme_url):
    certbot_challenge = CertbotChallenge.objects.filter(acme_url=acme_url).first()

    context = {
        'certbot_challenge': certbot_challenge,
    }
    return render(request, 'acme_challenge.html', context)
