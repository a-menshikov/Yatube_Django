from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Добавляет полю метод as_widget с атрибутом класса"""
    return field.as_widget(attrs={'class': css})
