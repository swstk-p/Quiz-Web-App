from django.conf import settings
from django.core.mail import send_mail
def send_email_token(email, token):
    try:
        subject = 'Verify your account'
        message = f'Verify your account using this link: thsqz.com/verify/{token}/'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        a= send_mail(subject, message, email_from, recipient_list)

    except Exception as e:
        return e
    return True