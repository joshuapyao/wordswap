#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2

import os
import logging
import urllib, urllib2, json
import random, re
from __builtin__ import str


JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("In MainHandler")
        template_values={}
        d = urllib2.urlopen('https://translate.yandex.net/api/v1.5/tr.json/getLangs?key=trnsl.1.1.20151118T003201Z.e37cbce184690dd5.f91649d0b33c90329ded4b92f29ea9999d2af13d&ui=en')
        lang = json.loads(d.read())
           
        template_values['languages'] = sorted(lang['langs'], key = lambda x: lang['langs'][x])
        template_values['langdictionary'] = lang['langs']
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
        
class TranslateHandler(webapp2.RequestHandler):
    def post(self):
        vals = {}
        url = self.request.get('url')
        text = getText(url)
        go = self.request.get('gobtn')
        if url != '' and text != '' and text != None:
            title = getTitle(url)
            lang = self.request.get('lang')
            
            d = urllib2.urlopen('https://translate.yandex.net/api/v1.5/tr.json/getLangs?key=trnsl.1.1.20151118T003201Z.e37cbce184690dd5.f91649d0b33c90329ded4b92f29ea9999d2af13d&ui=en')
            ld = json.loads(d.read())
            ld = ld['langs']
            vals['translatedlang'] = 'We Word Swapped ' + ld[lang] + ' into the Article'
            #How many words
            n = 0
            amount = self.request.get('amount')
            if (amount == 'few'):
                n = 0.01
            elif (amount == 'many'):
                n = 0.05
            else:
                n = 0.1
            
            l = text.split() #Gets text
            #print len(l)
             
            stopwords = open("stopwords.txt", 'r').read()
            stopwords = stopwords.split('\r\n')
             
            words = []
            n = len(l) * n
            #Get the words from article
            while n > 0:
                x = random.randint(0, len(l) - 2)
                if (l[x].strip() not in stopwords):
                    if (re.match('^[a-z]*$', l[x])):
                        if (l[x] not in words):
                            words.append(l[x])
                            n = n - 1
            wordvalues = translateTo(lang, words).encode('utf-8')
            translated = wordvalues.split('\n')
            
            s = text     
            for w in words:
                index = words.index(w)
                s = s.replace(' ' + w + ' ', '<a class="tooltip"><span><strong>' + w + '</strong><br /></span><mark> ' + translated[index] + ' </mark></a>', 1)
            s = s.decode('utf-8')
            vals['text'] = s
            vals['title'] = title  
        else:
            vals['text'] = 'There was an error getting the article. Please try a different one <br /> Note: Cannot retrieve FoxNews articles' 
        
        template = JINJA_ENVIRONMENT.get_template('translate.html')
        self.response.write(template.render(vals))
        
    

# for all URLs except alt.html, use MainHandler
application = webapp2.WSGIApplication([ \
                                      ('/translate', TranslateHandler),
                                      ('/.*', MainHandler)
                                      ],
                                     debug=True)
#----------------
# For reference   

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




def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def extract(url, type):
    params = urllib.urlencode({'apikey':'62d03a715cda6805338dda08f6822a58cf324115', 
                          'outputMode':'json',
                          'url':url})
    
    baseurl = 'http://gateway-a.watsonplatform.net/calls/url/URLGet' + type
    request = baseurl + '?' + params
    temp = urllib2.urlopen(request)
    s = temp.read()
    return json.loads(s)

def safeExtract(url, type): 
    try:
        return extract(url, type)
    except urllib2.URLError, e:
        if hasattr(e,"code"):
            print "The server couldn't fulfill the request." 
            print "Error code: ", e.code
        elif hasattr(e,'reason'):
            print "We failed to reach a server" 
            print "Reason: ", e.reason
        return None

def getText(url):    
    t = safeExtract(url, 'Text')
    if (t['status'] != 'ERROR'):
        return t['text'].encode('utf-8') #From unicode to string
    else:
        return None

def getTitle(url):
    t = safeExtract(url, 'Title')
    return t['title']
    
#getText('http://www.cnn.com/2009/CRIME/01/13/missing.pilot/index.html') #Gets text

def translateTo(lang, t):
    s = ""
    for word in t:
        s += word + "\n"
    params = urllib.urlencode({'key': 'trnsl.1.1.20151118T003201Z.e37cbce184690dd5.f91649d0b33c90329ded4b92f29ea9999d2af13d',
                               'text': s,
                               'lang': lang,
                               'format': 'html'})
    baseurl = 'https://translate.yandex.net/api/v1.5/tr.json/translate' 
    request = baseurl + '?' + params
    temp = urllib2.urlopen(request)
    s = temp.read()
    word = json.loads(s)
    return word['text'][0]
    
#translateTo('th', 'puppy') #Translates 'Puppy' to Thai
