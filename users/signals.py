from allauth.account.signals import user_signed_up
from django.core.mail import send_mail
from django.dispatch import receiver








@receiver(user_signed_up)
def send_welcome_email(request, user, **kwargs):
    subject = "Welcome to Our Platform!"
    message = f"Hi {user.firusernamest_name},\n\nThank you for registering! We're thrilled to have you on board."
    from_email = "your_email@example.com"  # Replace with your sender email
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)


