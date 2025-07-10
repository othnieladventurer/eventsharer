
from allauth.account.forms import SignupForm
from django import forms
from django_recaptcha.fields import ReCaptchaField




class CustomSignupForm(SignupForm):
    email = forms.EmailField(required=True, label="Email")
    password1 = forms.CharField(
        widget=forms.PasswordInput, required=True, label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput, required=True, label="Confirm Password"
    )
    captcha = ReCaptchaField()

    def save(self, request):
        user = super().save(request)
        user.email = self.cleaned_data["email"]
        user.role = 'customer'
        user.save()
        return user






class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'})
    )

