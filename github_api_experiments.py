# -*- coding: utf-8 -*-
# <nbformat>2</nbformat>

# <markdowncell>

# ## Exploring github repository profiles using the github api.
# 
# Authentication with the github api increases the amount of data that can be retrieved. I've set up a github user id that we can use of api calls. 
# 
# The code that generates the data is now separate from this notebook. 

# <codecell>

# functions to fetch from github api
import github_api_data as gh

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

# get a sample of repos
df_repos = gh.get_repos(1)


# we are interested in the platforms and languages of repositories. How do get that from the repository data?
df_repos.columns

# <codecell>

df_lang = gh.get_programming_languages(df_repos[0:5])
    

# <codecell>

import matplotlib.pyplot as plt
plt.subplots(nrows=1, ncols=2)
#plt.figure() 

#the use of languages
df_lang.apply(lambda x: np.count_nonzero(x)).plot(kind='bar', title = 'language usage')
#how much code is written in each language
plt.figure()
df_lang.sum().plot(kind='bar',title = 'code size')

# <markdowncell>

# The figures show that the amount of code written in different languages differs greatly from the number of projects that use languages.
# So while Javascript is a very popular language in terms of numbers of repositories using it, it looks like much more coding is done in 
# Ruby, C and C++. Obviously only a small sample (a couple of hundred repositories), but might be worth following this up.  

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

df_repos.description[df_repos.fork==True]

# <markdowncell>

# In terms of the metacommunity idea, I think it would be worth processing the titles and descriptions to get a catalogue of 'named entities.' 
# I've started to do this with some of the stackoverflow data, using the natural language toolkit. 

