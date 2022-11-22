from django.core.paginator import Paginator


def paginate_queryset(request, queryset, per_page):
    """Разбивает полученный queryset на страницы"""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def check_urls_status(object, client, urls):
    """Проверка статуса ответа."""
    for url, status in urls.items():
        with object.subTest(url=url, client=client):
            response = client.get(url)
            object.assertEqual(response.status_code, status)


def check_urls_redirect(object, client, urls):
    """Проверка редиректа."""
    for url, redirect_url in urls.items():
        with object.subTest(url=url, client=client):
            response = client.get(url, follow=True)
            object.assertRedirects(response, redirect_url)
