import csv
import datetime
import os
import re
import sqlite3

import nltk
import requests
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from scrapy.crawler import CrawlerProcess
from sklearn.feature_extraction.text import TfidfVectorizer

import crawler as Crawler
import sys_color as write


# PROMPT 3:
def output_sentences(filename):
    file = open(filename, 'r')
    topic = file.readline()  # Get the title of the URL page
    text = [(t.strip() + '\n') for t in file.readlines() if t.strip()]  # remove leading and trailing spaces
    sentences = nltk.sent_tokenize(''.join(text))  # break into sentences
    number = filename.split('/')[1].split('_')[1]  # get the x.txt part of url_x.txt
    file = open(f'processed_texts/text_{number}', 'a')  # open text file
    for sentence in set(sentences):
        file.write(sentence + '\n')  # append sentences to the file
    return topic


# NORMALIZATION
def process_sentence(sentence):
    tokens = []
    sentence = sentence.lower().strip()  # make lowercase and remove leading and trailing spaces
    sentence = re.sub('[\\d]', '', sentence)  # remove digits
    sentence = re.sub(r'[^\w\s]', ' ', sentence)  # remove all whitespaces that are not spaces
    for t in nltk.word_tokenize(sentence):  # for each word in the sentence
        # if token is not empty & token is a word & token is not a stopword & token has > 3 characters
        if t and t.isalpha and t not in stopwords.words('english') and len(t) > 3:
            tokens.append(t + ' ')
    return ''.join(set(lemmatize(tokens)))  # lemmatize tokens and join it back into a sentence


# LEMMATIZATION
def lemmatize(tkns):
    wnl = WordNetLemmatizer()
    lemmas = [wnl.lemmatize(t) for t in tkns]
    return lemmas


# CREATE DOCUMENTS FOR CORPUS
def make_docx(filename):
    file = open(f'processed_texts/{filename}', 'r')
    sentences = []
    for s in file.readlines():  # for every sentence
        sentence = process_sentence(s).strip()  # process the sentence
        if sentence:  # if sentences is not empty
            sentences.append(sentence + ' ')  # append into array
    return ''.join(sentences)  # join it back into a document


# PROMPT 4
def get_top40(matrix, tokens, doc_no):
    all_values = {}
    for n in range(len(matrix.toarray())):  # loop through each row of tf-idf values
        tfidf_values = matrix.toarray()[n]  # get the row
        for idx in range(len(tfidf_values)):
            word = tokens[idx]  # get the corresponding word at the index
            value = tfidf_values[idx]
            if word in all_values:
                if value > all_values[word][1]:  # if new value is greater than old
                    all_values[word] = (doc_no[n], value)  # use new value
            else:
                all_values[word] = (doc_no[n], value)
    return sorted(all_values.items(), key=lambda x: x[1][1], reverse=True)  # return in descending order


# FIND THE TOP 25 TERMS FOR EACH URL PAGE: Used to decide the top 10 terms in the top 40 terms
def keywords_by_topic(matrix, tokens, topics, doc_no):
    rows = []  # rows to write out to csv
    for n in range(len(matrix.toarray())):  # loop through each row of tf-idf values
        idx = doc_no[n]  # find the x in url_x.txt that n is pointing to
        topic = topics.get(idx)  # get the topic for url_x.txt

        top_25 = {}  # to hold the top 25 word, which url it came from, and it's tf-idf number
        tfidf_values = matrix.toarray()[n]
        top_25_values = sorted(tfidf_values, reverse=True)[:25]  # top 25 values for the row in matrix
        for i in range(len(tfidf_values)):  # loop through whole row
            value = tfidf_values[i]  # get value
            if value in top_25_values:  # if value is in the list of top 25
                top_25[tokens[i]] = value  # get word at index i and store as {'word': tf-idf val}
        # sort the dictionary according to value, ('word1', 0.2), ('word2', 0.1)...
        sorted_top25 = sorted(top_25.items(), key=lambda x: x[1], reverse=True)  # sort the dictionary
        word = [k[0] for k in sorted_top25]  # get the words from sorted list
        values = [k[1] for k in sorted_top25]  # get the values from sorted list
        # OPTIONAL #
        rows.append([idx, topic])
        rows.append(word)
        rows.append(values)
        rows.append(['\n'])
        # OPTIONAL #
    return rows


def create_tables(c, conn):
    c.execute('''
              CREATE TABLE IF NOT EXISTS Articles
              ([id] TEXT PRIMARY KEY, [keyword_id] INTEGER, [title] TEXT, [description] TEXT, [url] TEXT)
              ''')
    c.execute('''
              CREATE TABLE IF NOT EXISTS Keywords
              ([id] INTEGER PRIMARY KEY, [word] TEXT)
              ''')
    conn.commit()


def insert_keywords(c, keywords, conn):
    for i in range(len(keywords)):
        word = keywords[i]
        params = (i, word)
        c.execute('SELECT * FROM Keywords WHERE Keywords.id=:x', {'x': i})
        if not c.fetchall():
            c.execute('INSERT INTO Keywords (id, word) VALUES (?, ?) ', params)
    conn.commit()


def get_articles(keywords):
    articles = {}
    apikey = '0efe81d323d843a0ad09ec1bcaf349a1'
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    for i in range(len(keywords)):
        topic = f'{keywords[i]}%20The%20Batman'
        url = f'https://newsapi.org/v2/everything?language=en&q={topic}&apiKey={apikey}&from=2022-03-04&to={today}' \
              f'&sortBy=relevancy&pageSize=5'
        json, status = api_connect(url)
        if status == 'ok':
            articles[i] = json.get('articles')
    return articles


def api_connect(url):
    response = requests.get(url)
    json = response.json()
    status = json.get('status')
    return json, status


def insert_articles(c, key_to_articles, conn):
    for k, articles in key_to_articles.items():
        for a in range(len(articles)):
            article = articles[a]
            params = (f'{k}-{a}', k, article.get('title'), article.get('description'), article.get('url'))
            c.execute('SELECT * FROM Articles WHERE Articles.id=:x', {'x': f'{k}-{a}'})
            if not c.fetchall():
                c.execute('INSERT INTO Articles (id, keyword_id, title, description, url) VALUES (?, ?, ?, ?, ?)',
                          params)
    conn.commit()


def query_for_keyword_id(c, x):
    c.execute('SELECT id FROM Keywords WHERE Keywords.word=:x', {'x': x.lower()})
    i = c.fetchone()[0]
    return i


def query_for_articles(c, x):
    c.execute('SELECT title, description, url FROM Articles WHERE Articles.keyword_id=:x', {'x': x})
    rows = c.fetchall()
    for row in rows:
        write.stdhead(row[0])
        print(row[1])
        print(row[2])
    return rows


if __name__ == "__main__":
    # NOTE:
    # If you run WEB CRAWLER again, it will pull a different set of urls and ultimately
    # will cause a different list of top 40 terms, which means you will have to re-pick the top 10 terms from those
    # 40 terms, and recreate the knowledge base... SO. Proceed with CAUTION

    # WEB CRAWLER:
    # process = CrawlerProcess()
    # process.crawl(Crawler.RedditSpider)
    # process.start()

    # CREATE PROCESSED_TEXTS:
    titles = {}  # e.g. {14: 'url title'} = title of url_14.txt is 'url title'
    for name in os.listdir('scraped_texts'):  # loops through the files in directory
        title = output_sentences(f'scraped_texts/{name}')  # create sentences from url page & return the title of page
        index = int(name.split('_')[1].split('.')[0]) - 1  # get the x part of url-x.txt
        titles[index] = title.replace('\n', '')  # remove newline and store

    # CREATE CORPUS:
    corpus = []  # holds documents made from url pages
    doc_index = []  # holds indices of documents, IMPT: requires order
    for name in os.listdir('processed_texts'):  # loops through the files in directory
        docx = make_docx(name)  # process sentences and make documents to create corpus
        doc_index.append(int(name.split('_')[1].split('.')[0]) - 1)  # get the x part of url-x.txt
        corpus.append(docx)

    # CREATE TF-IDF VALUES:
    tfidfvectorizer = TfidfVectorizer(ngram_range=(1, 2), max_df=0.95, min_df=2)
    tfidf_matrix = tfidfvectorizer.fit_transform(corpus)
    tfidf_tokens = tfidfvectorizer.get_feature_names_out()

    # CREATE TOP 40 TERMS:
    top_40 = get_top40(tfidf_matrix, tfidf_tokens, doc_index)[:40]  # Get the 40 terms
    print('TOP 40 Terms:')
    top_40_keywords = [key[0] for key in top_40]
    print(top_40_keywords)
    # # OPTIONAL #
    # csv_writer = csv.writer(open('top-40.csv', 'w', newline='', encoding='utf-8'))  # Open and create csv file
    # csv_writer.writerow(['WORD', 'DOCS', 'TF-IDF'])  # write header
    # for keyword in top_40:
    #     csv_writer.writerow([keyword[0], keyword[1][0], keyword[1][1]])  # write to row csv file
    # # OPTIONAL #

    # # CREATE KEYWORDS BY TOPICS:
    # # OPTIONAL #
    # data = keywords_by_topic(tfidf_matrix, tfidf_tokens, titles, doc_index)  # Get the keywords
    # csv_writer = csv.writer(open('tf-idf.csv', 'w', newline='', encoding='utf-8'))
    # csv_writer.writerows(data)
    # # OPTIONAL #

    # 10 TERMS FROM DOMAIN KNOWLEDGE:
    print('\nTOP 10 TERMS USING DOMAIN KNOWLEDGE')
    top_10_keywords = ['joker', 'reeves', 'keoghan', 'arkham', 'markets', 'theatre', 'knight', 'pattinson', 'dark',
                       'casting']
    print(top_10_keywords)
    print()

    # BUILDING KNOWLEDGE BASE
    connection = sqlite3.connect('Keyword_Database.sql')
    cursor = connection.cursor()

    create_tables(cursor, connection)
    insert_keywords(cursor, top_10_keywords, connection)
    insert_articles(cursor, get_articles(top_10_keywords), connection)

    # SAMPLE QUERY
    keyword_id = query_for_keyword_id(cursor, 'joker')
    query_for_articles(cursor, keyword_id)
