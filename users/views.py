from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from allauth.account.views import  SignupView
from django.contrib.auth import authenticate, login, logout
from users.forms import CustomSignupForm
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect

from allauth.account.utils import send_email_confirmation
from django.contrib.auth import get_user_model






def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'account/login.html', {'error': 'Both username/email and password are required'})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            pending_slug = request.session.pop('pending_cart_add', None)
            if pending_slug:
                return redirect('cart:add', plan_slug=pending_slug)

            # ✅ Role-based redirect after login
            if user.role == 'customer':
                return redirect('dashboard:dashboard')
            else:
                return redirect('support:index')
        else:
            return render(request, 'account/login.html', {'error': 'Invalid username/email or password'})

    return render(request, 'account/login.html')





def send_welcome_email(self, email):
    subject = "Welcome to Our Platform!"
    message = (
        "Hello,\n\n"
        "Thank you for signing up! We're excited to have you on board.\n\n"
        "Best regards,\n"
        "Saasiskey LLC"
    )
    sender_email = settings.EMAIL_HOST_USER  # Use EMAIL_HOST_USER instead
    recipient_list = [email]

    send_mail(subject, message, sender_email, recipient_list, fail_silently=False)




def access_denied_view(request):
    return render(request, 'dashboard/partials/access_denied.html')



class CustomSignupView(SignupView):
    form_class = CustomSignupForm
    template_name = "account/signup.html"
    success_url = reverse_lazy("account_login")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.user
        user.role = 'customer'
        user.save()

        # ✅ Send email confirmation
        send_email_confirmation(self.request, user)

        # ✅ Send welcome email (optional/custom)
        self.send_welcome_email(user.email)

        messages.success(
            self.request,
            "You have successfully signed up. Check your email for a confirmation link and welcome message."
        )
        return response






def custom_logout(request):
    logout(request)
    return redirect('index')



