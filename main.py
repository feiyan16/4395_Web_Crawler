import crawler
import os
import re
import nltk
import math
import csv
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from scrapy.crawler import CrawlerProcess

from sklearn.feature_extraction.text import TfidfVectorizer


def output_sentences(filename):
    file = open(filename, 'r')
    text = [(t.strip() + '\n') for t in file.readlines() if t.strip()]  # remove leading and trailing spaces
    sentences = nltk.sent_tokenize(''.join(text))
    number = filename.split('/')[1].split('_')[1]
    file = open(f'processed_texts/text_{number}', 'a')
    for sentence in set(sentences):
        file.write(sentence + '\n')


def process_sentence(sentence):
    tokens = []
    sentence = sentence.lower().strip()
    sentence = re.sub('[\\d]', '', sentence)
    sentence = re.sub(r'[^\w\s]', ' ', sentence)
    for t in nltk.word_tokenize(sentence):
        if t and t.isalpha and t not in stopwords.words('english') and len(t) > 3:
            tokens.append(t + ' ')
    return ''.join(set(lemmatize(tokens)))


def lemmatize(tkns):
    wnl = WordNetLemmatizer()
    lemmas = [wnl.lemmatize(t) for t in tkns]
    return lemmas


def make_data(filename):
    file = open(f'processed_texts/{filename}', 'r')
    sentences = []
    for s in file.readlines():
        sentence = process_sentence(s).strip()
        if sentence:
            sentences.append(sentence + ' ')
    return ''.join(sentences)


def get_tf(doc):
    tokens = nltk.word_tokenize(doc)
    token_set = set(tokens)
    tf_dict = {t: tokens.count(t) for t in token_set}
    for t in tf_dict.keys():
        tf_dict[t] = tf_dict[t] / len(tokens)
    return tf_dict


def get_idf(docs, tf_s):
    idf_dict = {}
    vocab = []
    for key in [list(tf.keys()) for tf in tf_s]:
        vocab += key
    for word in vocab:
        count = ['x' for doc in docs if word in doc]
        idf_dict[word] = math.log((1 + len(docs)) / (1 + len(count)))
    return idf_dict


def get_tfidf(tf, idf):
    tf_idf = {}
    for t in tf.keys():
        tf_idf[t] = tf[t] * idf[t]

    return tf_idf


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(crawler.RedditSpider)
    process.start()

    for name in os.listdir('scraped_texts'):
        output_sentences(f'scraped_texts/{name}')

    documents = []
    tf_set = []
    doc_names = []
    for name in os.listdir('processed_texts'):
        docx = make_data(name)
        doc_names.append(name)
        documents.append(docx)
        # term_freq = get_tf(docx)
        # tf_set.append(term_freq)

    tfidfvectorizer = TfidfVectorizer(ngram_range=(1, 2), max_df=0.95, min_df=2)
    tfidf_matrix = tfidfvectorizer.fit_transform(documents)
    tfidf_tokens = tfidfvectorizer.get_feature_names_out()
    # tfidf_vect = pd.DataFrame(data=tfidf_matrix.toarray(), index=doc_names, columns=tfidf_tokens)

    rows = []
    for n in range(len(tfidf_matrix.toarray())):
        tfidf_values = tfidf_matrix.toarray()[n]
        top_25 = {}
        top_25_values = sorted(tfidf_values, reverse=True)[:25]
        rows.append([f'DOCUMENT: {doc_names[n]}'])
        for i in range(len(tfidf_values)):
            value = tfidf_values[i]
            if value in top_25_values:
                top_25[tfidf_tokens[i]] = value
        sorted_top25 = sorted(top_25.items(), key=lambda x: x[1], reverse=True)
        keywords = [k[0] for k in sorted_top25]
        values = [k[1] for k in sorted_top25]
        rows.append(keywords)
        rows.append(values)
        rows.append(['\n'])
    csv_writer = csv.writer(open('tf-idf.csv', 'w', newline='', encoding='utf-8'))
    csv_writer.writerows(rows)
    # idf_set = get_idf(documents, tf_set)
    # sorted_sets = []
    # for tf_item in tf_set:
    #     sorted_sets += sorted(get_tfidf(tf_item, idf_set).items(), key=lambda x: x[1], reverse=True)
    # sorted_tfidf = list(set(sorted(sorted_sets, key=lambda x: x[1], reverse=True)))
    # for item in sorted(sorted_tfidf, key=lambda x: x[1], reverse=True)[:40]:
    #     print(item)

