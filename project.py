# For reference   
# New York Times Most Popular API 
# http://api.nytimes.com/svc/mostpopular/v2/mostviewed/arts/30?api-key=2c061abf2edd04e7732169d34673da19%3A18%3A73399455&offset=20
# API Key: 2c061abf2edd04e7732169d34673da19%3A18%3A73399455

# Alchemy API Text Extraction
# Base URL:http://gateway-a.watsonplatform.net/calls/url/URLGetText
# API Key: 62d03a715cda6805338dda08f6822a58cf324115
# outputMode: json
# url: ______
# E.g.: http://gateway-a.watsonplatform.net/calls/url/URLGetText?apikey=62d03a715cda6805338dda08f6822a58cf324115&outputMode=json&url=http%3A%2F%2Fwww.cnn.com%2F2009%2FCRIME%2F01%2F13%2Fmissing.pilot%2Findex.html

# Yandex Translate API
# API Key(key): trnsl.1.1.20151118T003201Z.e37cbce184690dd5.f91649d0b33c90329ded4b92f29ea9999d2af13d
# Base URL: https://translate.yandex.net/api/v1.5/tr.json/translate
# Text(text): ____
# Lang: ____
# E.g.: https://translate.yandex.net/api/v1.5/tr.json/translate?key=trnsl.1.1.20151118T003201Z.e37cbce184690dd5.f91649d0b33c90329ded4b92f29ea9999d2af13d&text=puppy&lang=th

import random, re
import urllib, urllib2, json
from __builtin__ import str

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def extractText(url):
    params = urllib.urlencode({'apikey':'62d03a715cda6805338dda08f6822a58cf324115', 
                          'outputMode':'json',
                          'url':url})
    
    baseurl = 'http://gateway-a.watsonplatform.net/calls/url/URLGetText'
    request = baseurl + '?' + params
    temp = urllib2.urlopen(request)
    s = temp.read()
    return json.loads(s)

def safeExtractText(url): 
    try:
        return extractText(url)
    except urllib2.URLError, e:
        if hasattr(e,"code"):
            print "The server couldn't fulfill the request." 
            print "Error code: ", e.code
        elif hasattr(e,'reason'):
            print "We failed to reach a server" 
            print "Reason: ", e.reason
        return None
#-----------------------------------
def getText(url):    
    t = safeExtractText(url)
    return t['text'].encode('utf-8') #From unicode to string
    
l = ['been', 'praised', 'cow','sheep','chicken','soup']#getText('http://www.cnn.com/2009/CRIME/01/13/missing.pilot/index.html').split() #Gets text
print len(l)

n = 2

stopwords = open("stopwords.txt", 'r').read()
stopwords = stopwords.split('\r\n')

words = []
#Get the words from article
while n > 0:
    x = random.randint(0, len(l) - 2)
    if (l[x].strip() not in stopwords):
        if (re.match('^[a-z]*$', l[x])):
            if (l[x] not in words):
                words.append(l[x])
                n = n - 1
print words

#Translate each word in the list

#---------------------------------------
def translateTo(lang, t):
    params = urllib.urlencode({'key': 'trnsl.1.1.20151118T003201Z.e37cbce184690dd5.f91649d0b33c90329ded4b92f29ea9999d2af13d',
                               'text': t,
                               'lang': lang})
    baseurl = 'https://translate.yandex.net/api/v1.5/tr.json/translate' 
    request = baseurl + '?' + params
    temp = urllib2.urlopen(request)
    s = temp.read()
    word = json.loads(s)
    return word['text'][0] #Change to return later
    
#print translateTo('th', 'puppy') #Translates 'Puppy' to Thai
translated = []
for w in words:
    new = type(translateTo('th', w).encode('utf-8'))
    translated.append(new)
 
print translated

def extract(url, t):
    params = urllib.urlencode({'apikey':'62d03a715cda6805338dda08f6822a58cf324115', 
                          'outputMode':'json',
                          'url':url})
    
    baseurl = 'http://gateway-a.watsonplatform.net/calls/url/URLGet' + t
    request = baseurl + '?' + params
    temp = urllib2.urlopen(request)
    s = temp.read()
    return json.loads(s)

def safeExtract(url, t): 
    try:
        return extract(url, t)
    except urllib2.URLError, e:
        if hasattr(e,"code"):
            print "The server couldn't fulfill the request." 
            print "Error code: ", e.code
        elif hasattr(e,'reason'):
            print "We failed to reach a server" 
            print "Reason: ", e.reason
        return None

def getTitle(url):
    t = safeExtract(url, 'Title')
    return t['title']

s = "<style/>" + "hello"
print s.decode('utf-8')

print urllib.urlencode({'url':'http://www.foxnews.com/us/2015/12/07/terror-couple-bombs-were-set-to-kill-first-repsonders/'})

#---------------------------------------
def getArticles(section):
    param_str = urllib.urlencode({'api-key': '2c061abf2edd04e7732169d34673da19:18:73399455'})
    baseurl = 'http://api.nytimes.com/svc/mostpopular/v2/mostviewed/%s/1' % section
    request = baseurl + "?" + param_str
    temp = urllib2.urlopen(request)
    str = temp.read()
    return json.loads(str)

def safeGetArticles(section): 
    try:
        return getArticles(section)
    except urllib2.URLError, e:
        if hasattr(e,"code"):
            print "The server couldn't fulfill the request." 
            print "Error code: ", e.code
        elif hasattr(e,'reason'):
            print "We failed to reach a server" 
            print "Reason: ", e.reason
        return None

def printResults(section):
    data = safeGetArticles(section)
    print '***Most Popular Today from ' + data['results'][0]['section'] + '***\n'
    
    for a in data['results']:
        print a['title']
        print a['abstract'] 
        if len(a['des_facet']) != 0: 
            tags = a['des_facet'][0]
            if len(a['des_facet']) > 1:
                for tag in a['des_facet'][1:len(a['des_facet'])]:
                    tags += ', ' + tag
            print 'Tags: ' + tags
        else:
            print 'Tags: None'
        print a['url'] + '\n'
    print '---------------\n'

categories = ['fashion','arts','technology']

#for c in categories:
#    printResults(c)
