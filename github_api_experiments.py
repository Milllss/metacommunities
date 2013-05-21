# better not to use these packages -- I think they complicates things
from pygithub3 import Github

gh = Github(login='YOURUSERNAME', password='YOURPASSWORD')
kennethreitz_repos = gh.repos.list('kennethreitz').all()

from github import Github
g = Github('YOURUSERNAME', 'YOURPASSWORD')

##########without any library

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

def repos(count=10):
	url = 'https://api.github.com/repositories'
	df = pn.DataFrame()
	for x in xrange(1,count):
		r = requests.get(url,auth=('YOURUSERNAME', 'YOURPASSWORD'))
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
	
		
#to get the next ones
r.links['next']['url']
  # e.g.  https://api.github.com/repositories?since=364

#token: bf354f5a19fe1e71428b857f1f490c7407c3177e

## with authentication
r = requests.get(url, auth=('YOURUSERNAME', 'YOURPASSWORD'))




