import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import click
import spacy
import re


def type_words(word):
    """
    function to return lemma of world to describe nature of key word dictionary
    :param word: str
    :return: lemma_
    """
    nlp = spacy.load("es_core_news_md")
    doc = nlp(word)
    for token in doc:
        if token.i != 0:
            token_prev = doc[token.i - 1]
            if token.pos_ == "PROPN" and token_prev.pos_ == "PUNCT":
                return token.lemma_

@click.command()
def sratch_dict():
    """
    Function to scratch "Diccionario Geográfico de la República de Chile" in wikisource and tranform it in JSON
    Some dictionary entries are divided over several pages. The html model does not allow to parse and retrieve both
    pages. Only the last page has been kept.
    :url: https://es.wikisource.org/wiki/Diccionario_Geogr%C3%A1fico_de_la_Rep%C3%BAblica_de_Chile/A
    :return: JSON
    """

    # Variables
    global list_page
    n, page_n = 0, 1
    url_base = "https://es.wikisource.org/wiki/Diccionario_Geogr%C3%A1fico_de_la_Rep%C3%BAblica_de_Chile/"

    # Objects
    dictionary, dictionary_geo = {}, {}
    index = ["A", "B", "C", "Ch", "D", "E", "F", "G", "H", "I", "J", "K", "L", "Ll", "M", "N", "Ñ", "O", "P", "Q", "R",
             "S", "T", "U", "V", "W", "Y", "Z"]

    # REGEX
    nature = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ ]+\([A-Za-zÀ-ÖØ-öø-ÿ .-]+\)")

    for letter in index:
        # Requests http
        req_data = requests.get(url_base + letter)
        req_data.encoding = 'UTF-8'
        # Verify status
        if req_data.status_code == 200:
            n += 1
            print("__ page __ " + letter)
            # soup bs4
            data = BeautifulSoup(req_data.text, 'html.parser')
            for words in tqdm(data.find('div', attrs={'class': 'prp-pages-output'}).find_all('p')):
                word = [s for s in re.split(r"—|--", words.text)]
                # cleaning
                word[0] = word[0].replace('\n', '')
                word[-1] = word[-1].replace('\n', '')
                word[0] = word[0].replace('.-', '')
                #Careful cleaning
                letters = [s for s in word[0]]
                if "-" in letters[-2:] and "-" not in letters[-3]:
                    word[0] = word[0].replace('-', '')
                if "." in letters[-2:] and "." not in letters[-3]:
                    word[0] = word[0].replace('.','')
                #clean white space
                word[0] = word[0].strip()
                word[-1] = word[-1].strip()
                # select page number
                if words.find('span', attrs={'class': 'pagenum'}):
                    input_data = words.find('span', attrs={'class': 'pagenum'})
                    page_n = input_data['id']
                # management several keys
                if word[0] in dictionary_geo:
                    type_word = dictionary_geo[word[0]]["type"]

                    # Operation definition items
                    if isinstance(dictionary_geo[word[0]]["definition"], list):
                        list_def = dictionary_geo[word[0]]["definition"]
                        list_def.append(word[-1])
                    else:
                        list_def = [dictionary_geo[word[0]]["definition"], word[-1]]

                    # Operation page items
                    if isinstance(dictionary_geo[word[0]]["page"], list) is False and page_n != dictionary_geo[word[0]]["page"]:
                        list_page = [dictionary_geo[word[0]]["page"], page_n]
                    # Operation to add item in list if not exist or pass
                    elif isinstance(dictionary_geo[word[0]]["page"], list) is True:
                        if str(page_n) not in dictionary_geo[word[0]]["page"]:
                            list_page = dictionary_geo[word[0]]["page"]
                            list_page.append(page_n)
                    else:
                        list_page = page_n

                    # modele dict
                    dictionary_word = {
                        "type": type_word,
                        "definition": list_def,
                        "page": list_page
                    }
                # Entry new key
                else:
                    # Optimization to NLP process
                    if re.match(nature, word[0]):
                        type_word = type_words(word[0])
                    else:
                        type_word = None

                    dictionary_word = {
                        "type": type_word,
                        "definition": word[-1],
                        "page": page_n
                    }
                dictionary_geo[word[0]] = dictionary_word
        else:
            print("error : page " + letter)
        dictionary[letter] = dictionary_geo
        # reinitialisation dict
        dictionary_geo = {}

    # Write json
    with open("Diccionario_Geografico_Republica_Chile/diccionario.json", mode="w") as f:
        json.dump(dictionary, f, indent=3, ensure_ascii=False)

    # TEST
    assert n == 28, "One or more url doesn't works !"
    assert len(dictionary["H"]["Huentemó"]["definition"]) == 2, "Error indexation multi definition"
    assert len(dictionary["I"]["Incaguasi"]["page"]) == 2, "Error indexation multi page to definition"


if __name__ == '__main__':
    sratch_dict()
