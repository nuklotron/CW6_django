from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm

from emailer.forms import StyleFormMixin
from users.models import User


class LoginForm(StyleFormMixin, AuthenticationForm):

    class Meta:
        model = User
        fields = ('email', 'password')


class UserRegisterForm(StyleFormMixin, UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'first_name', 'last_name',)


class UserProfileForm(StyleFormMixin, UserChangeForm):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.HiddenInput()


class ManagerUserForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = User
        fields = ('is_active',)
