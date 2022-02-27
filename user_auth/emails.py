from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from user_auth.tokens import account_activation_token


def send_account_verification_link(request, data):
    user = data['user']
    current_site = get_current_site(request)
    mail_subject = 'Activate your account.'
    context = {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    }
    print('msg context: ', context)
    message = render_to_string('main/verification_email.html', context=context)
    print('email msg: ', message)
    to_email = data['email']
    send_mail(mail_subject, message, 'gorod.old@gmail.com', [to_email])
