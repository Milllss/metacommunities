import requests
import pandas as pn

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
