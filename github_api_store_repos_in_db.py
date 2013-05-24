user='You'
password = 'YourPassword'

dbuser = "Database-login"
dbpassword = "Database-password"

import requests
import oauth2
import json
import pandas as pn
import time
import MySQLdb
from pandas.io import sql

con = MySQLdb.connect("localhost", dbuser, dbpassword, "git", charset='utf8')

''' This is for making the 'repos' table for the data to go in
CREATE TABLE  `git`.`repos` (
`id` INT( 11 ) NOT NULL ,
 `name` TEXT COLLATE utf8_bin NOT NULL ,
 `full_name` TEXT COLLATE utf8_bin NOT NULL ,
 `private` TINYINT( 1 ) NOT NULL ,
 `description` TEXT COLLATE utf8_bin NOT NULL ,
 `fork` TINYINT( 1 ) NOT NULL ,
PRIMARY KEY (  `id` )
) ENGINE = INNODB DEFAULT CHARSET = utf8 COLLATE = utf8_bin
'''

# to get list of repos .... 

## the count is the number of requests to the API. Each request returns 100 repos
#to 'resume' this after already adding records to table, add ?since=x where x is the last ID in your table
def save_repos(count=1000000):
	url = 'https://api.github.com/repositories/since=65792'
	for x in xrange(1,count):
		r = requests.get(url,auth=(user,password))
		url = r.links['next']['url']
		df_temp = pn.DataFrame()
		if(r.ok):
			repoItem = json.loads(r.text or r.content)
			ids = [it['id'] for it in repoItem]
			names = [it['name'] for it in repoItem]
			private = [it['private'] for it in repoItem]
			full_names = [it['full_name'] for it in repoItem]
			repo_description = [it['description'] for it in repoItem]
			fork = [it['fork'] for it in repoItem]
			di = {'id':ids, 'name':names, 'full_name':full_names, 'private':private, 'description': repo_description, 'fork': fork}
			df_temp = pn.DataFrame.from_dict(di)
			sql.write_frame(df_temp, con=con, name='repos', 
			if_exists='append', flavor='mysql')
		print 'fetched 100 rows'
		time.sleep(1.0)

'''I'm only saving 6 variables right now because most of the variables returned 
are URLs that follow a set structure and therefore could be easily built from the full_name'''			





