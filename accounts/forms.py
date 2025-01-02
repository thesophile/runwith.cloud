from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe  # Required for rendering HTML in labels

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=mark_safe("Username <span style='color: red;'>*</span>")  # Red asterisk
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=mark_safe("Password <span style='color: red;'>*</span>")  # Red asterisk
    )

class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=mark_safe("Password <span style='color: red;'>*</span>")  # Red asterisk
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=mark_safe("Confirm Password <span style='color: red;'>*</span>")  # Red asterisk
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
        labels = {
            'username': mark_safe("Username <span style='color: red;'>*</span>"),
            'email': mark_safe("Email <span style='color: gray;'>(optional)</span>"),  # Optional styling
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return password_confirm
