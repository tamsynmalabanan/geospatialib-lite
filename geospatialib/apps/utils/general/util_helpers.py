import string
from django.utils.text import slugify

def build_cache_key(*args):
    key_parts = [slugify(str(arg)) for arg in args]
    return ':'.join(key_parts)

def get_special_characters(value):
    return [sc for sc in list(string.punctuation) if sc in value]

def split_by_special_characters(string):
    special_chars = get_special_characters(string) + [' ']
    for sc in special_chars:
        string = string.replace(sc, ',')
    return list(set([i for i in string.split(',') if i != '']))

def get_first_substring_match(value, lst, ext=None):
    value_lower = value.lower()
    list_clean = [sub for sub in lst if sub != '']

    for sub in list_clean:
        if sub.lower() in value_lower:
            return sub
    
    current_sub = None
    current_len = 0
    for sub in list_clean:
        sections = split_by_special_characters(sub.lower())
        match_len = len([i for i in sections if i in value_lower])
        if match_len > current_len:
            current_len = match_len
            current_sub = sub

    if not current_sub and ext is not None:
        current_per = 0
        for sub, keywords in ext.items():
            if sub in lst:
                matches = [i for i in keywords if i.lower() in value_lower]
                per = len(matches) / len(keywords)
                if int(per) == 1:
                    return sub
                if per > current_per:
                    current_per = per
                    current_sub = sub

    return current_sub