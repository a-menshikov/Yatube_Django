from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    """Страница ошибки 404"""
    return render(request, 'core/404.html', {'path': request.path},
                  status=HTTPStatus.NOT_FOUND)


def server_error(request):
    """Страница ошибки 500"""
    return render(request, 'core/500.html',
                  status=HTTPStatus.INTERNAL_SERVER_ERROR)


def permission_denied(request, exception):
    """Страница ошибки 403"""
    return render(request, 'core/403.html', status=HTTPStatus.FORBIDDEN)


def csrf_failure(request, reason=''):
    """Страница ошибки токена 403"""
    return render(request, 'core/403csrf.html', status=HTTPStatus.FORBIDDEN)
