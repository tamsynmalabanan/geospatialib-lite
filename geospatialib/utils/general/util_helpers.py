import string
from django.utils.text import slugify
from urllib.parse import urlparse, urlunparse
from django.contrib import messages
import random


def get_domain_name(url):
    domain = urlparse(url).netloc
    domain_parts = domain.split('.')
    if len(domain_parts) == 1:
        return domain
    if len(domain_parts) == 2:
        return domain_parts[0]
    if len(domain_parts) > 2:
        return domain_parts[1]

def build_cache_key(*args):
    key_parts = [slugify(str(arg)) for arg in args]
    return ':'.join(key_parts)

def get_special_characters(value):
    puncts = list(string.punctuation) + [' ']
    if len(value) > len(puncts):
        scs = [sc for sc in puncts if sc in value]
    else:
        scs = [char for char in value if char in puncts]
    return list(set(scs))

def split_by_special_characters(value, excluded_chars=[]):
    special_chars = get_special_characters(value)

    if len(excluded_chars) > 0:
        for i in excluded_chars:
            try:
                special_chars.remove(i)
            except ValueError:
                pass

    delimiter = ','
    while delimiter in excluded_chars:
        delimiter = random.choice(list(string.punctuation))

    for sc in special_chars:
        value = value.replace(sc, delimiter)
    return list(set([i for i in value.split(delimiter) if i != '']))

def get_first_substring_match(value, lst, helpers=None):
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

    if not current_sub and helpers is not None:
        current_per = 0
        for sub, keywords in helpers.items():
            if sub in lst:
                matches = [i for i in keywords if i.lower() in value_lower]
                per = len(matches) / len(keywords)
                if int(per) == 1:
                    return sub
                if per > current_per:
                    current_per = per
                    current_sub = sub

    return current_sub

def remove_query_params(url):
  parsed_url = urlparse(url)
  return urlunparse(parsed_url._replace(query=''))

def check_or_add_message(request, method, message, tags):
    msgs = messages.get_messages(request)
    for msg in msgs:
        if msg.message == message and msg.extra_tags == tags:
            return
    method(request, message, tags)