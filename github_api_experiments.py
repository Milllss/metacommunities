# -*- coding: utf-8 -*-
# <nbformat>2</nbformat>

# <markdowncell>

# ## Exploring github repository profiles using the github api.
# 
# Authentication with the github api increases the amount of data that can be retrieved.

# <codecell>

import requests
import oauth2
import json
import pandas as pn
import time


# better not to use these packages -- I think they complicate things.
# Without any library is actually simpler!

# from pygithub3 import Github

# gh = Github(login='YOURUSERNAME', password='YOURPASSWORD')
# kennethreitz_repos = gh.repos.list('kennethreitz').all()

# from github import Github
# g = Github(user,password)



user='YOU'
password = 'YOURS'


def github_timeline():
	"""Returns dictionary with recent events -- not sure how many"""
	r = requests.get('https://github.com/timeline.json')
	timeline = r.json
	return timeline



def get_repos(count=10):

	"""Returns a DataFrame of repositories; 
	The count is the number of requests to the API. 
	Each request returns 100 repos approximately."""

	url = 'https://api.github.com/repositories'
	df = pn.DataFrame()
	for x in xrange(1,count):
		r = requests.get(url,auth=(user,password))
		url = r.links['next']['url']
		if(r.ok):
			repoItem = r.json
			df_temp = pn.DataFrame.from_dict(repoItem)
			df = df.append(df_temp)
		print 'fetched ', len(df), 'rows'
		time.sleep(1.0)
	return df
	
		

# <markdowncell>

# # The problem of programming languages
# 
# We know roughly what programming languages are used on github [https://github.com/languages](https://github.com/languages)

# <codecell>

# to get view of programming languages, need to query by language.

url = 'https://github.com/search?l=Python&q=%40github&ref=searchresults&type=Repositories'

# But a more fine grained view comes from asking each repository what languages are being used there. 
url = 'https://api.github.com/repos/vanpelt/jsawesome/languages'
r = requests.get(url)
lang = r.json
print lang

# <markdowncell>

# I think the numbers here refer to lines of code. Or maybe character counts.
# So, user vanpelt's [jawesome repository](https://github.com/vanpelt/jsawesome) has definitely has some javascript. 
# Does it have Ruby code? 
# Run in a shell: git clone https://github.com/vanpelt/jsawesome
# Cd into jsawesome, and there are definitely both Ruby and Javascript files there. The charcounts on the files are about right. They add up to ~9600 characters for the Ruby files.
# So this give some sense of the relative importance of the different programming languages in each repo.

# <codecell>

# get a sample of 1000 repos
df_repos = get_repos(10)


# we are interested in the platforms and languages of repositories. How do get that from the repository data?
df_repos.columns

# <codecell>

# need to reindex them -- the id numbers that are assigned are not unique?
df_repos = df_repos.set_index('name')
df_repos.languages_url.head()
df_lang = pn.DataFrame()

for name, url in df_repos.languages_url.iteritems():
    print 'fetching repository %s from %s'% (name, url)

    r = requests.get(url,auth=(user,password))
    lang = r.json
    di = {name:lang}
    df_temp=pn.DataFrame.from_dict(di, 'index')
    df_lang = df_lang.append(df_temp)
    

# <codecell>

df_lang = df_lang.fillna(0)
print df_lang.shape
df_lang

# <markdowncell>

# ## What can we get by looking at the forked repositories. Questions might be:
#     1. what do they fork from?
#     2. what kinds of repositories are likely to be forked?
#     3. do forks have lives of their own, or are they mainly dead ends?
#     

# <codecell>

# interesting to look at how many repositories are forks of others
# could we build a picture of github in terms of forks?

df_repos.fork.value_counts()
df_repos.fork.value_counts().plot(kind='bar')

# <codecell>



# <codecell>

df_repos.description[df_repos.fork==True]

