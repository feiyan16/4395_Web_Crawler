
import crawler as Crawler
from scrapy.crawler import CrawlerProcess
import os
import re
import nltk
import csv
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer


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


# def get_tf(doc):
#     tokens = nltk.word_tokenize(doc)
#     token_set = set(tokens)
#     tf_dict = {t: tokens.count(t) for t in token_set}
#     for t in tf_dict.keys():
#         tf_dict[t] = tf_dict[t] / len(tokens)
#     return tf_dict
#
#
# def get_idf(docs, tf_s):
#     idf_dict = {}
#     vocab = []
#     for key in [list(tf.keys()) for tf in tf_s]:
#         vocab += key
#     for word in vocab:
#         count = ['x' for doc in docs if word in doc]
#         idf_dict[word] = math.log((1 + len(docs)) / (1 + len(count)))
#     return idf_dict
#
#
# def get_tfidf(tf, idf):
#     tf_idf = {}
#     for t in tf.keys():
#         tf_idf[t] = tf[t] * idf[t]
#
#     return tf_idf


# PROMPT 4
def get_top40_keywords(matrix, tokens, doc_no):
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


if __name__ == "__main__":
    # NOTE:
    # If you run WEB CRAWLER again, it will pull a different set of urls and ultimately
    # will cause a different list of top 40 terms, which means you will have to re-pick the top 10 terms from those
    # 40 terms, and recreate the knowledge base... SO. Proceed with CAUTION

    # WEB CRAWLER:
    process = CrawlerProcess()
    process.crawl(Crawler.RedditSpider)
    process.start()

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
    top_40_keywords = get_top40_keywords(tfidf_matrix, tfidf_tokens, doc_index)[:40]  # Get the 40 terms
    # OPTIONAL #
    # csv_writer = csv.writer(open('top-40.csv', 'w', newline='', encoding='utf-8'))  # Open and create csv file
    # csv_writer.writerow(['WORD', 'DOCS', 'TF-IDF'])  # write header
    # for keyword in top_40_keywords:
    #     csv_writer.writerow([keyword[0], keyword[1][0], keyword[1][1]])  # write to row csv file
    # OPTIONAL #
    print('TOP 40 Terms:')
    keywords = [key[0] for key in top_40_keywords]
    print(keywords)

    # CREATE KEYWORDS BY TOPICS:
    # OPTIONAL #
    # data = keywords_by_topic(tfidf_matrix, tfidf_tokens, titles, doc_index)  # Get the keywords
    # csv_writer = csv.writer(open('tf-idf.csv', 'w', newline='', encoding='utf-8'))
    # csv_writer.writerows(data)
    # OPTIONAL #

    # 10 TERMS FROM DOMAIN KNOWLEDGE:
    print('\nTOP 10 TERMS USING DOMAIN KNOWLEDGE')
    terms_10 = ['joker', 'reeves', 'million', 'arkham', 'markets', 'love', 'knight', 'pattinson', 'dark', 'casting']
    print(terms_10)

    # idf_set = get_idf(documents, tf_set)
    # sorted_sets = []
    # for tf_item in tf_set:
    #     sorted_sets += sorted(get_tfidf(tf_item, idf_set).items(), key=lambda x: x[1], reverse=True)
    # sorted_tfidf = list(set(sorted(sorted_sets, key=lambda x: x[1], reverse=True)))
    # for item in sorted(sorted_tfidf, key=lambda x: x[1], reverse=True)[:40]:
    #     print(item)

