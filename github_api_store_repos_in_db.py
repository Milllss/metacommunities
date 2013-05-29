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

import requests
import pandas as pn
import time
import MySQLdb
from pandas.io import sql

USER_FILE = open('github_api_user.txt')
USER = USER_FILE.readline().rstrip('\n')
PASSWORD = USER_FILE.readline().rstrip('\n')
USER_FILE.close()



def save_repos(count=1000000):
    """ to get list of repos .... 
    the count is the number of requests to the API. Each request returns 100 repos
    to 'resume' this after already adding records to table, 
    add ?since=x where x is the last ID in your table.
    I'm only saving 6 variables right now because most of the variables returned 
    are URLs that follow a set structure and therefore could be easily built from the full_name'
    """

    con = MySQLdb.connect("localhost", USER, PASSWORD, "git", charset='utf8')
    url = 'https://api.github.com/repositories'
    for x in xrange(1,count):
        req = requests.get(url,auth=(USER,PASSWORD))
        url = req.links['next']['url']
        df_temp = pn.DataFrame()
        if(req.ok):
            repoItem = req.json
            repos_df_temp = pn.DataFrame.from_dict(repoItem)
            df_temp = repos_df_temp[['id','name','private','full_name','description','fork']]
            df_temp = df_temp.fillna('')		
            sql.write_frame(df_temp, con=con, name='repos', 
                if_exists='append', flavor='mysql')
        print 'fetched 100 rows'
        time.sleep(1.0)
    return df_temp

       





