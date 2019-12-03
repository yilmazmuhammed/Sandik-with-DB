import csv
import io
import json
import ssl
import urllib.request

from flask import session

translation = {}


def read_data_online(url, data_type, delimiter=';'):
    context = ssl._create_unverified_context()
    web_page = urllib.request.urlopen(url, context=context)
    data_reader = csv.reader(io.TextIOWrapper(web_page), delimiter=delimiter, quotechar='|')

    data_list = []
    for row in data_reader:
        data_ = data_type(*row)
        data_list.append(data_)

    return data_list


def set_translation():
    global translation
    language = None#session.get('language')
    default_language = 'tr_TR'
    print("set_translation:", language)
    # TODO is None or in not LANGUAGES
    select_translation = {}
    if language is not None:
        with open('languages/%s/translations.json' % language, 'r') as f:
            select_translation = json.load(f)
    with open('languages/%s/translations.json' % default_language, 'r') as f:
        translation = json.load(f)
    translation.update(select_translation)
    return translation


def get_translation():
    if len(translation) == 0:
        set_translation()
    return translation
