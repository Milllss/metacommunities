import gzip
import json
import re
import pandas as pn
import os
import requests
import StringIO


# chunks of code to fetch, unzip, load and get some fields from gitarchive.org

#TODO:
# 1. code to store json objects in a no-SQL database. Mongo perhaps easiest
# 2. code to put useful extracts from data into SQL tables
# 3. code to generate days for a given month
# 4. calculate how much storage we'd need for all the githubarchive data (roughly 2 years worth)


#shameless copy paste from json/decoder.py
FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)

class ConcatJSONDecoder(json.JSONDecoder):
    def decode(self, s, _w=WHITESPACE.match):
        s_len = len(s)

        objs = []
        end = 0
        while end != s_len:
            obj, end = self.raw_decode(s, idx=_w(s, end).end())
            end = _w(s, end).end()
            objs.append(obj)
        return objs

sample_file = 'data/2012-04-01-12.json.gz'


def load_local_gz(sample_file):
    """returns a DataFrame with all the data from one githubarchive gzip file."""

    gz = gzip.open(sample_file)
    fc = gz.read()
    gh= json.loads(fc, cls=ConcatJSONDecoder)

    # this creates a wide dataframe, with some fields nested. See below for a way of splitting them out. 
    df_all = pn.DataFrame.from_dict(gh)
    return df_all

## to download and open directly from the githubarchive
#wget http://data.githubarchive.org/2012-04-{01..31}-{0..23}.json.gz  # gets all the data for april
#wget http://data.githubarchive.org/2012-04-11-15.json.gz # 3pm on the day
#wget http://data.githubarchive.org/2012-04-11-{0..23}.json.gz # the whole day
#the earliest URL I could find that works: http://data.githubarchive.org/2011-02-12-15.json.gz

#example of getting an hours data from the archive

def load_archive_gz_demo():
    url = 'http://data.githubarchive.org/2012-04-1-15.json.gz' ##1-5 April 2012, 3-4pm
    response = requests.get(url)
    compressedFile = StringIO.StringIO(response.content)
    decompressedFile = gzip.GzipFile(fileobj=compressedFile)
    fc = decompressedFile.read()
    gh= json.loads(fc, cls=ConcatJSONDecoder)
    df_all = pn.DataFrame.from_dict(gh)
    return df_all

def construct_githubarchive_url(year=2012,  month=1, day=1,  hour = 12 ):

    """ Returns a url formatted for date-time retrieval of one hour of githubarchive in a json files. 
    """

    base_url = 'http://data.githubarchive.org/'
    suffix = '.json.gz'
    
    if month <10:
        month = '0' + str(month)
    else:
        month = str(month)
    
    if day <10:
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
        compressedFile = StringIO.StringIO(response.content)
        decompressedFile = gzip.GzipFile(fileobj=compressedFile)
        fc = decompressedFile.read()
        gh= json.loads(fc, cls=ConcatJSONDecoder)
        df_all = pn.DataFrame.from_dict(gh)
    except Exception, e:
        print e
    return df_all


def fetch_one_day_data(year=2012, month=1, day=1):

    """ Returns a dataframe with 1 days github events."""

    hours = range(0,24)
    df = pn.DataFrame()
    for h in hours:
        url = construct_githubarchive_url(year, month, day, h)
        df = df.append(fetch_archive(url))
        print 'fetching ' + url
    return df


def unnest_git_json(df_all):
    
    """ Returns  a dictionary of the data nested in each json object. There are 3 nested dictionaries in the json object - repos, actor_attributes and payload.    """
    #for repository
    df_rep = pn.DataFrame.from_dict(df_all['repository'].to_dict()).transpose()
    #for users
    df_actors  = pn.DataFrame.from_dict(df_all['actor_attributes'].to_dict()).transpose()
    #for payload -- whatever that is
    df_payload  = pn.DataFrame.from_dict(df_all['payload'].to_dict()).transpose()

    return {'all': df_all, 'repository':df_rep, 'actors': df_actors, 'payload':df_payload}

def github_event_explore(df_all):

    """ Returns a DataFrame with event types, and timestamps."""

    dic ={'created_at': df_all['created_at'], 'type' :df_all['type']}
    df = pn.Series(data = df_all['type'],index = df_all['created_at'])

    df_eve.type.value_counts().plot(kind='bar')
    return df

def calculate_storage_needs_in_Gbytes(days=1):

    """Returns a dictionary with compressed and uncompressed total gigabytes 
    for githubarchive data by the day. The average hourly figure  of 1133000 compressed bytes
    is based on an average filesize calculated on 700 files.
    @TODO: calculate the uncompressed values based on the uncompressed size of 700 files
    @TODO: the same calculations for stackoverflow -- Richard?
    """

    average_gz_file = float(1133000)
    gb = 1024*1024*1024; #hope this is right
    f = gzip.GzipFile('data/2012-04-01-12.json.gz')
    uc = float(len(f.read())) * days * 24/gb
    #hour = os.path.getsize('data/2012-04-01-12.json.gz')
    total_comp = days * average_gz_file *24/gb
    return {'compressed': total_comp, 'uncompressed': uc}


