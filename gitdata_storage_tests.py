""" Tests to try out retrieving gitdata from different
filestores -- mysql, hd5, pickle, csv, mongodb.
They time how long one day of github data
takes to load into memory
"""

import timeit
import pickle
import pandas as pn
import pandas.io.sql as sql
import pandas.io.pytables as pyt
import MySQLdb
import githubarchive_data as ghd
from pymongo import MongoClient
import os

# read passwords in.
# I'm using the same one for API and sqldb
USER_FILE = open('github_api_user.txt')
USER = USER_FILE.readline().rstrip('\n')
PASSWORD = USER_FILE.readline()
USER_FILE.close()

def mysql_setup():
    """Returns a mysql connection for the git database.
    Assuming that a database called 'git' exists on the server
    """
    try:
        con = MySQLdb.connect("localhost", 
            USER, PASSWORD, "git", charset='utf8')
    except Exception, e:
        print e
    return con
    
def setup_test_data():
    """Function uses sample githubarchive data.
    It saves a few hundred copies as a csv, as a python pickle file,
    as a hdf5 store, as mysql table and as mondodb.
    If you haven't run  timing tests before, you will need
    to run this first.
    """
    print 'use one hour of sample and replicate 100 times'
    #use only the repository data --
    onehr_df = ghd.load_local_archive_dataframe()
    onehr_json = ghd.load_local_archive_json()
    one_hr_repo_df = ghd.unnest_git_json(onehr_df)['repository']
    many_hr_repo_df = pn.DataFrame()
    for i in range(1,100):
        many_hr_repo_df = many_hr_repo_df.append(one_hr_repo_df)
    print('saving dataframe with', many_hr_repo_df.shape, "rows")
    print 'saving data to a csv file'
    many_hr_repo_df.to_csv('data/oneday.csv', encoding='utf-8')
    print 'dumping data to python pickle'
    pickle.dump(many_hr_repo_df, open('data/oneday.pyd', 'wb'))
    print 'dumping data to mysql database'
    con = mysql_setup()
    many_hr_repo_df_clean = many_hr_repo_df.fillna('')
    sql.write_frame(many_hr_repo_df_clean, 'oneday', con, 'mysql')
    print 'saving data to hdf5 filestore'
    store = pyt.HDFStore('data/git.h5')
    store.put('oneday', many_hr_repo_df)
    print 'saving data to mongodb'
    # repos_son = onehr_df['repository']
    many_hr_repo_df = many_hr_repo_df.dropna()    
    client = MongoClient()
    dbm = client['git']
    collection = dbm['gittest']
    # many_hr_repo_df = many_hr_repo_df.set_index(many_hr_repo_df.name)
    [collection.insert(onehr_json) for i in range(1,100)]

def clean_test_data():

    """Function removes all datasets made for 
    for testing purposes
    """
    con = mysql_setup()
    query = 'drop table oneday;'
    sql.execute(con = con, sql = query)    
    gh_csv = 'data/oneday.csv'
    gh_pick = 'data/oneday.pyd'
    gh_hd5 = 'data/git.h5'
    os.remove(gh_csv)
    os.remove(gh_pick)
    os.remove(gh_hd5)


def time_data_retrieval(number_of_tests=1):

    """ Runs some timeit tests on one day of github data stored in
    - python pickle file
    - pytables hd5
    - mysql table
    - mongodb
    """
    gh_csv = 'data/oneday.csv'
    gh_pick = 'data/oneday.pyd'
    gh_hd5 = 'data/git.h5'

    csv_timer = timeit.Timer(lambda: load_csv_df(gh_csv))
    print('csv:', csv_timer.timeit(number_of_tests))

    pickle_timer = timeit.Timer(lambda: load_pickle_df(gh_pick))
    print('pickle:', pickle_timer.timeit(number_of_tests))

    con = mysql_setup()
    query = 'select * from git.oneday;'
    mysql_timer = timeit.Timer(lambda:load_mysql_df(con, query))
    print('mysql:', mysql_timer.timeit(number_of_tests))

    store = pyt.HDFStore(gh_hd5)
    hd5_timer = timeit.Timer(lambda: load_hd5_df(store))
    print('hd5:', hd5_timer.timeit(number_of_tests))

    client = MongoClient()
    dbm = client['git']
    mong_timer = timeit.Timer(lambda: load_mongo_df(dbm))
    print('mongodb:', mong_timer.timeit(number_of_tests))
    
    test_df = load_hd5_df(store)
    print('Test data size: ', test_df.shape)
    
    
def load_csv_df(gh_csv):
    """ load test data from csv"""
    csv_df = pn.DataFrame.from_csv(gh_csv)
    return csv_df


def load_pickle_df(gh_pick):
    """ load test data from  from pickle file"""
    pickle_handle = open(gh_pick, 'rb')
    pickle_df = pickle.load(pickle_handle)
    return pickle_df

def load_hd5_df(store):
    """ load test data  from hd5 filestore
    """
    hd5df = store.get('oneday')
    return hd5df

def load_mysql_df(con, query):
    """ load test data from  mysql
    """
    sql_df = sql.execute(con = con, sql = query)
    return sql_df

def load_mongo_df(dbm):
    """load test data from mongdb"""

    cursor = dbm['gittest'].find({})
    mongo_df =  pn.DataFrame(list(cursor))
    return mongo_df


