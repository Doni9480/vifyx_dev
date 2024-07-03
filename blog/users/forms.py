from django import forms

from users.models import User


class ChangeEmailForm(forms.Form):
    email = forms.CharField()

    def clean_email(self):
        email = self.cleaned_data['email']

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('The user with such an email was not found.')
        return email

class PasswordChangeForm(forms.Form):
    password = forms.CharField(required=True)
    password2 = forms.CharField()
    
    def clean(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        
        if not (password and password2 and (password == password2)):
            raise forms.ValidationError('Passwords must match.')
        return self.cleaned_data
    