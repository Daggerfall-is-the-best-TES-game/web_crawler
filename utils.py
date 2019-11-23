# TODO: make a program that can merge two lists of axfc links into one without any duplicates
#get the id of each url, check if an id already exists in main list, and add in if not
from re import search
from collections import Counter


working_directory = "C:/Users/David/Downloads/axfc downloads/" # all downloads and files are here


def get_id(url):
    return search("(?<=/)[0-9]+", url).group()


def must_keep(url):
    """certain urls should not be replaced by alternate urls that resolve
    to the same page. e.g. urls with keys in them, because a url that includes the key
    is strictly better than one that doesn't"""
    return "key" in url

# TODO: if a url has a key associated with it, we want to prioritise keeping that url. Current broken
def merge_url_lists(*args):
    master_list = dict()
    for url_list in args:
        with open(working_directory + url_list, "r", encoding="UTF-8") as file:
            for url in file.readlines():
                try:
                    if not(get_id(url) in master_list and must_keep(master_list[get_id(url)])): #don't replace urls with keys no matter what
                        master_list[get_id(url)] = url.strip()
                except AttributeError as e:
                    print(url)
                    print(e)

    with open(working_directory + "masterlist.txt", "a", encoding="UTF-8") as f:
        for url in master_list.values():
            f.write(f"{url}\n")


def count_duplicate_urls(*args):
    master_list = []
    for url_list in args:
        with open(working_directory + url_list, "r", encoding="UTF-8") as file:
            for url in file.readlines():
                try:
                    master_list.append(get_id(url))  # don't replace urls with keys no matter what
                except AttributeError as e:
                    print(url)
                    print(e)
    return Counter(master_list)

merge_url_lists("complete link list.txt", "bluefruit.txt")
