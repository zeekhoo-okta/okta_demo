from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from okta import UsersClient


class LoginForm(forms.Form):
    username = forms.EmailField(
        widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("username"))
    password = forms.RegexField(
        regex=r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{4,30}$',
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)),
        label=_("password"),
        error_messages={'invalid': _("Minimum length 4. Must contain at least 1 digit, 1 uppercase letter, 1 lowercase letter")})


class RegistrationForm(forms.Form):
    firstName = forms.CharField(max_length=100, required=True)
    lastName = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("email"))
    password1 = forms.RegexField(
        regex=r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{4,30}$',
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)),
        label=_("password"),
        error_messages={'invalid': _("Minimum length 4. Must contain at least 1 digit, 1 uppercase letter, 1 lowercase letter")})
    password2 = forms.RegexField(
        regex=r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{4,30}$',
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)),
        label=_("password (again)"),
        error_messages={'invalid': _("Minimum length 4. Must contain at least 1 digit, 1 uppercase letter, 1 lowercase letter")})

    def clean_email(self):
        """
        email field validation to check if the username is already in Okta

        """
        readCount = 0
        try:
            usersClient = UsersClient(''.join(['https://', settings.OKTA_ORG]), settings.OKTA_API_TOKEN)
            result = usersClient.get_users(filter_string='profile.login eq "' + self.cleaned_data['email'] + '"')
            readCount = len(result)
        except Exception as e:
            return self.cleaned_data['email']

        if readCount > 0:
            raise forms.ValidationError("The username already exists")

        return self.cleaned_data['email']

    def clean_password2(self):

        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields did not match."))

        return self.cleaned_data['password2']


class mfaForm(forms.Form):
    code = forms.CharField(max_length=100, required=True)
    stateToken = forms.CharField(max_length=100, required=True)
    factorId = forms.CharField(max_length=100, required=True)
    provider = forms.CharField(max_length=100, required=True)