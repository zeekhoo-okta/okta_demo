from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=120)
    password = forms.CharField(label='password', max_length=200)