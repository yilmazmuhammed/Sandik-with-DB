import csv
import io
import ssl
import urllib.request


def read_data_online(url, data_type, delimiter=';'):
    context = ssl._create_unverified_context()
    web_page = urllib.request.urlopen(url, context=context)
    data_reader = csv.reader(io.TextIOWrapper(web_page), delimiter=delimiter, quotechar='|')

    data_list = []
    for row in data_reader:
        data_ = data_type(*row)
        data_list.append(data_)

    return data_list
