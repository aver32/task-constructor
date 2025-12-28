from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Получение значения из словаря по ключу"""
    if isinstance(dictionary, dict):
        return dictionary.get(str(key), {})
    return {}

@register.filter
def dict_keys(dictionary):
    """Получение списка ключей словаря"""
    if isinstance(dictionary, dict):
        return list(dictionary.keys())
    return []