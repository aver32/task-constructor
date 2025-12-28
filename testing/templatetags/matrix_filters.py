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

@register.filter
def default_dict(value):
    """Возвращает пустой словарь если значение не является словарем"""
    return value if isinstance(value, dict) else {}

@register.filter
def is_in(value, container):
    """Проверяет, содержится ли значение в контейнере"""
    if container is None:
        return False
    return str(value) in container

@register.filter
def lists_equal(list1, list2):
    """Сравнивает два списка"""
    if list1 is None or list2 is None:
        return False
    for idx, _ in enumerate(list1):
        list1[idx] = str(list1[idx])
    for idx, _ in enumerate(list2):
        list2[idx] = str(list2[idx])
    if len(list1) > 1:
        list1 = [", ".join(list1)]
    if len(list2) > 1:
        list2 = [", ".join(list2)]
    print(list1)
    print(list2)
    return sorted(list1) == sorted(list2)