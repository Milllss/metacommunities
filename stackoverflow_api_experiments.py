import requests
import pandas as pn
import nltk

# initial experiments with StackOverflow API

# get some questions
url='https://api.stackexchange.com//2.1/questions?order=desc&sort=activity&site=stackoverflow'
r = requests.get(url)
df_qus = pn.DataFrame.from_dict(r.json['items'])
df_qus.head()


# get some answers
url='https://api.stackexchange.com//2.1/answers?order=desc&sort=activity&site=stackoverflow'
r = requests.get(url)
df_ans = pn.DataFrame.from_dict(r.json['items'])
df_ans.head()


# find the objects (named entities) in some questions titles
titles = df_qus.title
words = [nltk.wordpunct_tokenize(s) for s in titles]
words_pos_tagged = [nltk.pos_tag(t) for t in words]

#to get the named entities
named_entities =nltk.batch_ne_chunk(words_pos_tagged)