"""
Functions that retrieve stuff from githubarchive.org
and package it  in more usable forms

To download and open directly from the githubarchive:

- gets all the data for april:
#wget http://data.githubarchive.org/2012-04-{01..31}-{0..23}.json.gz  

- get 3-4 pm on the day:
#wget http://data.githubarchive.org/2012-04-11-15.json.gz 

- get one whole day (24 hours:
#wget http://data.githubarchive.org/2012-04-11-{0..23}.json.gz

n.b. the earliest URL I could find that works: 
#http://data.githubarchive.org/2011-02-12-15.json.gz

 @TODO:
 1. code to store json objects in a no-SQL database. Mongo perhaps easiest
 2. code to put useful extracts from data into SQL tables
 3. code to generate days for a given month
 4. calculate how much storage we'd need for all the githubarchive data 
 (roughly 2 years worth)

"""

import gzip
import json
import re
import pandas as pn
import requests
import StringIO
import numpy as np

#shameless copy paste from json/decoder.py
FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)

class ConcatJSONDecoder(json.JSONDecoder):

    """Helper class for decoding compressed unicodedata"""

    def decode(self, stri, whspace_match=WHITESPACE.match):
        s_len = len(stri)

        objs = []
        end = 0
        while end != s_len:
            obj, end = self.raw_decode(stri, idx=whspace_match(stri, end).end())
            end = whspace_match(stri, end).end()
            objs.append(obj)
        return objs

def load_local_archive(sample_file  = 'data/2012-04-01-12.json.gz'):

    """returns a DataFrame with all the data 
    from one sample githubarchive gzip file."""

    gzfile = gzip.open(sample_file)
    decompressed_file = gzfile.read()
    git_json = json.loads(decompressed_file, cls=ConcatJSONDecoder)

    # this creates a wide dataframe, with some fields nested. 
    # See below for a way of splitting them out. 
    df_all = pn.DataFrame.from_dict(git_json)
    return df_all

def construct_githubarchive_url(year=2012,  month=1, day=1,  hour = 12 ):

    """ Returns a url formatted for date-time retrieval of 
    1 hour of githubarchive in a json file. 
    """

    base_url = 'http://data.githubarchive.org/'
    suffix = '.json.gz'
    
    if month < 10:
        month = '0' + str(month)
    else:
        month = str(month)
    
    if day < 10:
        day = '0' + str(day)
    else:
        day = str(day)

    date_url = base_url +str(year) +'-'+month +'-' + day + '-' + str(hour) +suffix
    return date_url

def fetch_archive(url):

    """ Returns a dataframe  with  all data for the specified hour. """

    df_all = pn.DataFrame()

    try:
        response = requests.get(url)
        compressed_file = StringIO.StringIO(response.content)
        decompressed_file = gzip.GzipFile(fileobj=compressed_file)
        decompressed_file = decompressed_file.read()
        git_json = json.loads(decompressed_file, cls=ConcatJSONDecoder)
        df_all = pn.DataFrame.from_dict(git_json)
    except Exception, exce:
        print exce
    return df_all

def fetch_archive_demo():

    """Returns DataFrame with 1 hour of sample github data """

    url = 'http://data.githubarchive.org/2012-04-1-15.json.gz' 
    return fetch_archive(url)

def fetch_one_day(year=2012, month=1, day=1):

    """ Returns a dataframe with 1 days github events."""

    hours = range(0, 24)
    day_df   = pn.DataFrame()
    for hour in hours:
        url = construct_githubarchive_url(year, month, day, hour)
        day_df   = day_df .append(fetch_archive(url))
        print 'fetching ' + url
    return day_df   

def unnest_git_json(df_all):
    
    """ Returns  a dictionary of the data nested in each json object. 
    There are 3 nested dictionaries in the json object:
     - repos, actor_attributes and payload.    """
    #for repository
    df_rep = pn.DataFrame.from_dict(df_all['repository'].to_dict()).transpose()
    #for users
    df_actors  = pn.DataFrame.from_dict(df_all['actor_attributes'].
        to_dict()).transpose()
    #for payload -- whatever that is
    df_payload  = pn.DataFrame.from_dict(
        df_all['payload'].to_dict()).transpose()
    df_dict = {'all': df_all, 'repository':df_rep, 
        'actors': df_actors, 
        'payload':df_payload}
    return  df_dict

def github_event_explore(df_all):

    """ Returns a DataFrame with event types, and timestamps."""

    event_df = pn.Series(data = df_all['type'], index = df_all['created_at'])
    return event_df

def calculate_storage_in_gbytes(days=1):

    """Returns a dictionary with compressed and uncompressed total gigabytes 
        for githubarchive data by the day. The average hourly figure  of 1133000 compressed bytes
        is based on an average filesize calculated on 700 files.
        @TODO: calculate the uncompressed values based on the uncompressed size of 700 files
        @TODO: the same calculations for stackoverflow -- Richard?
    """

    average_gz_file = float(1133000)
    gbyte = 1024*1024*1024 #hope this is right
    #sample file only -- not necessarily representative!
    gzip_file = gzip.GzipFile('data/2012-04-01-12.json.gz')
    uncompressed_size = float(len(gzip_file.read())) * days * 24/gbyte
    #hour = os.path.getsize('data/2012-04-01-12.json.gz')
    total_comp = days * average_gz_file *24/gbyte
    return {'compressed': total_comp, 'uncompressed': uncompressed_size}

def uncompressed_hourly_average(hours=1):
    
    """Returns an average hourly uncompressed data size 
        based on a random sample of hours
        from 10 days over 3 years
        @TODO: this is broken -- needs debug
    """

    hrs = np.random.random_integers(0, 24, hours)
    days = np.random.random_integers(1, 28, 10)
    months = np.random.random_integers(1, 12, 3)
    years = np.random.random_integers(2011, 2013, 3)
    files = []
    for year in years:
        for month in months:
            for day in days:
                for hour in hrs:
                    files.append(
                        construct_githubarchive_url(year, month, day, hour))
    for fil in files:
        try:
            response = requests.get(fil)
            compressed_file = StringIO.StringIO(response.content)
            uncompressed_size = float(len(gzip.GzipFile(
                fileobj=compressed_file).read()))
            print uncompressed_size
        except Exception, exce:
            print exce

