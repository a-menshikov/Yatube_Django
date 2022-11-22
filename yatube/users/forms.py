from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (PasswordChangeForm, PasswordResetForm,
                                       UserCreationForm)

User = get_user_model()


class CreationForm(UserCreationForm):
    """Форма создания нового пользователя"""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PasswordChangeForm(PasswordChangeForm):
    """Форма смены пароля пользователем"""
    class Meta:
        model = User


class PasswordResetForm(PasswordResetForm):
    """Форма сброса пароля"""
    class Meta:
        model = User
