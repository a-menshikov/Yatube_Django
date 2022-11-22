from django.contrib.auth.views import (PasswordChangeView,
                                       PasswordResetConfirmView,
                                       PasswordResetView)
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm, PasswordChangeForm, PasswordResetForm


class SignUp(CreateView):
    """Регистрация нового пользователя"""
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChange(PasswordChangeView):
    """Смена пароля пользователем"""
    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change.html'


class PasswordResetView(PasswordResetView):
    """Запрос сброса пароля пользователем"""
    form_class = PasswordResetForm
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_form.html'


class PasswordResetConfirmView(PasswordResetConfirmView):
    """Установка нового пароля после сброса"""
    success_url = reverse_lazy('users:password_reset_complete')
    template_name = 'users/password_reset_confirm.html'
