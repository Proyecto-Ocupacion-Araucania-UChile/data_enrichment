import requests
from bs4 import BeautifulSoup
import os
import re
import json
import click
from pprint import pprint

@click.command()
def sratch_dict():
    """
    https://www.wikidata.org/wiki/Q5483159?uselang=es
    https://www.crummy.com/software/BeautifulSoup/bs4/doc/#descendants
    https://www.w3schools.com/cssref/css_selectors.asp
    """

    index = ["A", "B", "C", "Ch", "D", "E", "F", "G", "H", "I", "J", "K", "L", "Ll" ,"M" , "N", "Ñ", "O", "P", "Q", "R", "S",
             "T", "U", "V", "W", "Y", "Z"]
    url_base = "https://es.wikisource.org/wiki/Diccionario_Geogr%C3%A1fico_de_la_Rep%C3%BAblica_de_Chile/"

    n = 0
    id = 1

    for letter in index:
        req_data = requests.get(url_base+letter)
        if req_data.status_code == 200 and letter == "D":
            n += 1
            print("__ page __ " + letter)
            data = BeautifulSoup(req_data.text, 'html.parser')
            for words in data.find('div', attrs={'class': 'prp-pages-output'}).find_all('p'):
                for page in words.findChildren('span', attrs={'class': 'pagenum'}):
                    if page is True:
                        id += 1
                word = [s for s in words.text.split('—')]
                for sentence in word:
                    sentence.replace('\n', '')
                word[0] = word[0].replace(".-", "")
                word[0] = word[0].replace(".", "")
                dictionary_geo = {
                    word[0] : words[-1]
                }


                """if word.findParent(lambda e: e.name == 'div', attrs={'class': 'prp-pages-output'}):
                    print(len(list(zip(word))))"""
                #dictionary = dict(zip(index, list_word)
                #'div', attrs={'class': 'prp-pages-output'}

    assert n == 28, "One or more url doesn't works !"

if __name__ == '__main__':
    sratch_dict()
