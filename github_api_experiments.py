user='YOURUSERNAME'
password = 'YOURPASSWORD'

# better not to use these packages -- I think they complicates things
from pygithub3 import Github

gh = Github(login='YOURUSERNAME', password='YOURPASSWORD')
kennethreitz_repos = gh.repos.list('kennethreitz').all()

from github import Github
g = Github(user,password)

##########without any library is actually simpler!

import requests
import oauth2
import json
import pandas as pn
import time

r = requests.get('https://api.github.com/repos/django/django')
if(r.ok):
    repoItem = json.loads(r.text or r.content)
    print "Django repository created: " + repoItem['created_at']

## to get list of repos .... 

## the count is the number of requests to the API. Each request returns a couple of hundred repos

def repos(count=10):
	url = 'https://api.github.com/repositories'
	df = pn.DataFrame()
	for x in xrange(1,count):
		r = requests.get(url,auth=(user,password))
		url = r.links['next']['url']
		if(r.ok):
			repoItem = json.loads(r.text or r.content)
			ids = [it['id'] for it in repoItem]
			repo_names = [it['full_name'] for it in repoItem]
			repo_description = [it['description'] for it in repoItem]
			di = {'id':ids, 'repository':repo_names, 'description': repo_description}
			df_temp = pn.DataFrame.from_dict(di)
			df = df.append(df_temp)
		print 'fetched ', len(df), 'rows'
		time.sleep(1.0)
	return df
	
		
df_repos = repos(100)



