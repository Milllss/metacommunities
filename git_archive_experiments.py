import gzip
import json
import re
import pandas as pn
import os
import requests
import urllib2
import StringIO



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

def load_hourly_git(file):
            gz = gzip.open(file)
            fc = gz.read()
            gh= json.loads(fc, cls=ConcatJSONDecoder)
            df=pn.DataFrame.from_dict(gh)
            return df

## get the list of hourly dumps
files = os.listdir('data/')

# load 1st 100 hours as test  iinto a single data frame
df = pn.DataFrame()
for f in files[0:5]:
            gh = load_hourly_git('data/'+f)
            # timestamps = [x['created_at'] for x in gh]
            # types=[x['type'] for x in gh]
            df = df.append(gh)
            print 'loaded '+f



sample_file = 'data/2012-04-06-21.json.gz'

##old testing lines    
gz = gzip.open('data/2012-04-06-21.json.gz')
fc = gz.read()
gh= json.loads(fc, cls=ConcatJSONDecoder)

##to look at times

df = pn.DataFrame(timestamps, types)


##to download and open directly from the githubarchive
# to get some data
# wget http://data.githubarchive.org/2012-04-{01..31}-{0..23}.json.gz  # gets all the data for april
#wget http://data.githubarchive.org/2012-04-11-15.json.gz # 3pm on the day
#wget http://data.githubarchive.org/2012-04-11-{0..23}.json.gz # the whole day
#the earliest URL I could find that works: http://data.githubarchive.org/2011-02-12-15.json.gz

#example
url = 'http://data.githubarchive.org/2012-04-1-15.json.gz' ##1-5 April 2012, 3-4pm
response = urllib2.urlopen(url)
compressedFile = StringIO.StringIO(response.read())
decompressedFile = gzip.GzipFile(fileobj=compressedFile)
fc = decompressedFile.read()
gh= json.loads(fc, cls=ConcatJSONDecoder)
df_all = pn.DataFrame.from_dict(gh)

## there are 3 nested dictionaries in - repos, actor_attributes and payload
#to deal with nested json for repos, etc
df_rep = pn.DataFrame.from_dict(df_all.repository.to_dict()).transpose()

#for users
df_actors  = pn.DataFrame.from_dict(df_all['actor_attributes'].to_dict()).transpose()

#for payload -- whatever that is
df_payload  = pn.DataFrame.from_dict(df_all['payload'].to_dict()).transpose()


# days and hours can be given in range: e.g. {0..23} is 24 hours; {01..31} is the whole month

def construct_githubarchive_url(year=2012,  month=1, days = '{01..31}', hours = '{0..23}' ):
    base_url = 'http://data.githubarchive.org/'
    suffix = '.json.gz'
    date_url = base_url +str(year) +'-'+str(month) +'-' + str(days) + '-' + str(hours) +suffix
    return date_url
