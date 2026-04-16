from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm


class RegistrationForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150, required=False, label="Full Name")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise ValidationError("Email is required")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email address already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise ValidationError("Username is required")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError({
                'password2': "The two password fields didn’t match.",
            })

        if password1 and len(password1) < 8:
            raise ValidationError({
                'password1': "Password must be at least 8 characters long.",
            })

        if password1 and not any(c.isupper() for c in password1):
            raise ValidationError({
                'password1': "Password must contain at least one uppercase letter.",
            })

        special_characters = "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~"
        if password1 and not any(c in special_characters for c in password1):
            raise ValidationError({
                'password1': "Password must contain at least one special character (e.g. !@#$%).",
            })

        return cleaned_data

    def save(self, commit=True):
        user = super(forms.ModelForm, self).save(commit=False)
        full_name = self.cleaned_data.get('full_name', '').strip()
        if full_name:
            parts = full_name.split(None, 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''

        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    identifier = forms.CharField(label="Email or Username", widget=forms.TextInput(attrs={'autocomplete': 'username', 'placeholder': 'Email or Username'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get('identifier')
        password = cleaned_data.get('password')

        if identifier and password:
            user = None

            if '@' in identifier:
                try:
                    user = User.objects.get(email__iexact=identifier)
                except User.DoesNotExist:
                    user = None
            else:
                try:
                    user = User.objects.get(username__iexact=identifier)
                except User.DoesNotExist:
                    user = None

            if user is None:
                raise forms.ValidationError("Invalid username or email or password.")

            from django.contrib.auth import authenticate
            user = authenticate(username=user.username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid username or email or password.")
            cleaned_data['user'] = user

        return cleaned_data
