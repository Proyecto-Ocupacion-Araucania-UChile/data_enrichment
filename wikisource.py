import requests
from bs4 import BeautifulSoup
import json
import click
import spacy
import re


def type_words(words):
    nlp = spacy.load("es_core_news_md")
    doc = nlp(words)
    for token in doc:
        if token.i != 0:
            token_prev = doc[token.i - 1]
            if token.pos_ == "PROPN" and token_prev.pos_ == "PUNCT":
                return token.lemma

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
    page_n = 1

    dictionary = {}
    dictionary_geo = {}

    nature = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ ]+\([A-Za-zÀ-ÖØ-öø-ÿ .-]+\)")

    for letter in index:
        req_data = requests.get(url_base+letter)
        req_data.encoding = 'UTF-8'
        if req_data.status_code == 200:
            n += 1
            print("__ page __ " + letter)
            data = BeautifulSoup(req_data.text, 'html.parser')
            for words in data.find('div', attrs={'class': 'prp-pages-output'}).find_all('p'):
                word = [s for s in words.text.split('—')]
                word[0].replace('\\n', '')
                word[-1].replace('\\n', '')
                word[0] = word[0].replace(".-", "")
                word[0] = word[0].replace(".", "")
                if words.find('span', attrs={'class': 'pagenum'}):
                    input_data = words.find('span', attrs={'class': 'pagenum'})
                    page_n = input_data['id']
                if word[0] in dictionary_geo:
                    type_word = dictionary_geo[word[0]]["type"]

                    # Operation definition items
                    if dictionary_geo[word[0]]["definition"] is not list:
                        list_def = [dictionary_geo[word[0]]["definition"], word[-1]]
                    else:
                        list_def = dictionary_geo[word[0]]["definition"].append(word[-1])

                    #Operation page items
                    if page_n != dictionary_geo[word[0]]["page"] and dictionary_geo[word[0]]["page"] is not list:
                        list_page = [dictionary_geo[word[0]]["page"], page_n]
                    elif dictionary_geo[word[0]]["page"] is list:
                        list_page = dictionary_geo[word[0]]["page"].append(page_n)
                    else:
                        list_page = page_n

                    dictionary_word = {
                        "type": type_word,
                        "definition": list_def,
                        "page": list_page
                    }
                else:
                    if re.match(nature, word[0]):
                        type_word = type_words(word[0])
                    else:
                        type_word = "n.c."
                    dictionary_word = {
                        "type": type_word,
                        "definition": word[-1],
                        "page": page_n
                    }
                dictionary_geo[word[0]] = dictionary_word
        dictionary[letter] = dictionary_geo
        #reinitialisation dict
        dictionary_geo = {}

    with open("Diccionario_Geografico_Republica_Chile/diccionario.json", mode="w") as f:
        json.dump(dictionary, f, indent=3, ensure_ascii=False)

    print(dictionary["H"]["Huenutil"]["page"])

    assert n == 28, "One or more url doesn't works !"
    assert len(dictionary["H"]["Huentemó"]["definition"]) == 2, "Error indexation multi definition"
    assert len(dictionary["I"]["Incaguasi"]["page"]) == 2, "Error indexation multi page to definition"

if __name__ == '__main__':
    sratch_dict()
