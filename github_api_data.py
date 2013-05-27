"""
Functions that generate dataframes from  the github api.

Authentication with the github api increases the amount of 
data that can be retrieved. 
I've set up a github user id that we can use for api calls.
It's in the 'spare_gh_pass.txt' file, and the user/pwd
are read in when the module loads.

I tried some of the packages below. 
Decided it was easier  not to use these packages. 
I think they complicate things.

e.g. from pygithub3 import Github

gh = Github(login='YOURUSERNAME', password='YOURPASSWORD')
kennethreitz_repos = gh.repos.list('kennethreitz').all()

from github import Github
g = Github(user,password)
"""

import requests
import pandas as pn
import time


# read API user/password from your local file'
USER_FILE = open('github_api_user.txt')
USER = USER_FILE.readline().rstrip('\n')
PASSWORD = USER_FILE.readline()
USER_FILE.close()


def github_timeline():
    """Returns dictionary with recent events -- not sure how many"""
    req = requests.get('https://github.com/timeline.json')
    timeline = req.json
    return timeline

def get_repos(count=10):

    """Returns a DataFrame of repositories; 
    The count is the number of requests to the API. 
    Each request returns 100 repos approximately."""

    url = 'https://api.github.com/repositories'
    repos_df = pn.DataFrame()
    while count > 0 :
        req = requests.get(url, auth=(USER, PASSWORD))
        url = req.links['next']['url']
        if(req.ok):
            repoItem = req.json
            repos_df_temp = pn.DataFrame.from_dict(repoItem)
            repos_df = repos_df.append(repos_df_temp)
            print 'fetched ', len(repos_df), 'rows'
        time.sleep(1.0)
        count -= 1
    return repos_df

def get_programming_languages(repos_df):

    """ Returns dataframe of the programming languages 
	used for repositories.

	url = 'https://github.com/search?l=Python&q=%40github&ref=searchresults&type=Repositories'

	But a more fine grained view comes from asking each repository
	what languages are being used there. 
		url = 'https://api.github.com/repos/vanpelt/jsawesome/languages'
		req = requests.get(url)
		lang = req.json
		print lang
    """

    df_lang = pn.DataFrame()

    for name, url in repos_df.ix[0:100].languages_url.iteritems():
        print 'fetching repository %s from %s'% (name, url)
        req = requests.get(url, auth=(USER, PASSWORD))
        lang = req.json
        df_temp = pn.DataFrame.from_dict({name:lang}, 'index')
        df_lang = df_lang.append(df_temp)

    df_lang = df_lang.fillna(0)
    return df_lang
