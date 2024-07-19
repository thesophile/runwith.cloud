# utils.py (or any module you prefer)
from django.core.cache import cache

def save_to_cache(code):
    cache.set('previous_code', code)


def get_previous_code():
    code = cache.get('previous_code')
    return code if code is not None else ''

#Current Code (A variable to keep track which code is crrently being edited)
     
def set_current_code_name(code_name):
    cache.set('current_code_name', code_name)


def get_current_code_name():
    code_name = cache.get('current_code_name')
    return code_name      