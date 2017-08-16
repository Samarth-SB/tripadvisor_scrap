
# coding: utf-8

# In[1]:

import re
import requests
from bs4 import BeautifulSoup as BS
import json
import numpy as np
import pandas as pd
from pymongo import MongoClient
import csv
import os.path

# In[2]:

userReviewURL = []
memberOverlayLink = []
memberProfileURL = []


# In[3]:
    
#input url
#url = 'https://www.tripadvisor.com.sg/ShowUserReviews-g294217-d300697-r512026251-JW_Marriott_Hotel_Hong_Kong-Hong_Kong.html#REVIEWS'
url = 'https://www.tripadvisor.com.sg/ShowUserReviews-g294217-d300697-r512988117-JW_Marriott_Hotel_Hong_Kong-Hong_Kong.html#REVIEWS'

#input page counter
counter = 313


# In[4]:

userReviewURL.append(url)


# In[5]:
if not os.path.isfile("jwmarriot_review_urls.csv"):
    f = open('jwmarriot_review_urls.csv','w')
    for i in range(counter-1):
        print('Load URLs from web')
        html = requests.get(userReviewURL[i])
        soup = BS(html.content,'html.parser')
        container = soup.find('a',{'data-page-number':i+2})
        urlTemp = 'https://www.tripadvisor.com.sg' + container['href']
        userReviewURL.append(urlTemp)
        print(str(i) + ':' + urlTemp)
        f.write(urlTemp + '\r')
else:
    with open('jwmarriot_review_urls.csv','rU') as f:
        line = csv.reader(f)
        i = 0
        for row in line:
            print('Load URLs from file')
            print(str(i) + ':' + row[0])
            userReviewURL.append(row[0])
            i = i + 1
f.close()

# In[6]:

names = []
ratings = []
dates = []
titles = []
bodies = []
recommendTitles = []
recommendAnswers = []
uids = []


# In[7]:

for i in range(len(userReviewURL)):
    html = requests.get(userReviewURL[i])
    soup = BS(html.content,'html.parser')
    container = soup.find('div',{'id':'SHOW_USER_REVIEW'})    
    print('Parsing url : ' + userReviewURL[i])

    for j in range(5):
        temp = container.findAll('div',{'id':re.compile('^review_')})[j]
        name = temp.find('span',{'class':re.compile('^expand_inline')})
        rating = temp.find('span',{'class':re.compile('^ui_bubble_rating')})['class'][1]
        date = temp.find('span',{'class':'ratingDate'}).next_element
            
        if j == 0:
            title = temp.find('div',{'property':'name'})
            body = temp.find('p',{'property':'reviewBody'})
        else:
            title = temp.find('span',{'class':'noQuotes'})
            body = temp.find('p',{'id':re.compile('^review_')})
        recommendTitle = temp.find('span',{'class':'recommend-titleInline'})
        recommendAnswer = temp.findAll('li',{'class':'recommend-answer'})
        memberInfo = temp.find('div',{'class':'member_info'})
        print(memberInfo)
        memberOverlayLink = memberInfo.find('div',{'class':'memberOverlayLink'})
        if(memberOverlayLink is not None):
            uid = memberOverlayLink['id']
            print('uid : ' + uid)
        else:
            uid = ""
    
        if name is not None and len(name) > 0:
            names.append(name.text)
        else:
            names.append('')
        if rating is not None and len(rating) > 0:
            ratings.append(rating[7])
        else:
            ratings.append('')
        if date is not None and len(date) > 0:
            dates.append(date)
        else:
            dates.append('')
        if title is not None and len(title) > 0:
            titles.append(title.text)
        else:
            titles.append('')
        if body is not None and len(body) > 0:
            bodies.append(body.text.strip('\n'))
        else:
            bodies.append('')
        if recommendTitle is not None and len(recommendTitle) > 0:
            recommendTitles.append(recommendTitle.text)
        else:
            recommendTitles.append('')
        if recommendAnswer is not None and len(recommendAnswer) > 0:
            jsonTemp = {}
            for k in range(len(recommendAnswer)):
                jsonTemp[recommendAnswer[k].text.strip('\n')] = recommendAnswer[k].find('span')['alt'][0]
            recommendAnswers.append(json.dumps(jsonTemp))
        else:
            recommendAnswers.append('')
        if uid is not None and len(uid) > 0:
            uids.append(uid[4:uid.find('-SRC')])
        else:
            uids.append('')


# In[8]:

namesDF = pd.DataFrame(np.array(names))
ratingsDF = pd.DataFrame(np.array(ratings))
datesDF = pd.DataFrame(np.array(dates))
titlesDF = pd.DataFrame(np.array(titles))
bodiesDF = pd.DataFrame(np.array(bodies))
recommendTitlesDF = pd.DataFrame(np.array(recommendTitles))
recommendAnswersDF = pd.DataFrame(np.array(recommendAnswers))


# In[9]:

df = pd.concat([namesDF,ratingsDF,datesDF,titlesDF,bodiesDF,recommendTitlesDF,recommendAnswersDF], axis=1)
df.columns = ['Name','Rating','Date','Title','Body','Recommended Title','Recommended Answer']


# In[10]:

print(df)


# In[11]:

for i in range(len(uids)):
    if len(uids[i]) > 0:
        memberOverlayLink.append('https://www.tripadvisor.com.sg/MemberOverlay?Mode=owa&uid=' + str(uids[i]))
        memberProfileURL.append('https://www.tripadvisor.com.sg/MemberProfile-a_uid.' + str(uids[i]))
    else:
        memberOverlayLink.append('')
        memberProfileURL.append('')


# In[12]:

ageGenders = []
hometowns = []
travelStyleTags = []
points = []
levels = []


# In[13]:

for i in range(len(memberProfileURL)):
    html = requests.get(memberProfileURL[i])
    soup = BS(html.content,'html.parser')
    container = soup.find('div',{'id':'MODULES_MEMBER_CENTER'})

    ageGender = container.find('div',{'class':'ageSince'})
    hometown = container.find('div',{'class':'hometown'})
    travelStyleTag = container.findAll('div',{'class':'tagBubble unclickable'})
    point = container.find('div',{'class':'points'})
    level = container.find('div',{'class':'level tripcollectiveinfo'})

    if len(ageGender) > 0:
        ageGenders.append(ageGender.text[14:].strip())
    else:
        ageGenders.append('')
    if len(hometown) > 0:
        hometowns.append(hometown.text)
    else:
        hometowns.append('')
    if len(travelStyleTag) > 0:
        listTemp = []
        for j in range(len(travelStyleTag)):
            listTemp.append(travelStyleTag[j].text.strip())
        travelStyleTags.append(listTemp)
    else:
        travelStyleTags.append('')
    if len(point) > 0:
        points.append(int(str(point.text.strip()).replace(',','')))
    else:
        points.append('')
    if level is not None:
        levels.append(level.text[6:level.text.find(' ',6)].strip())
    else:
        levels.append('')


# In[14]:
if(ageGenders is not None):
    ageGendersDF = pd.DataFrame(np.array(ageGenders))
else:
    ageGendersDF = ""
if(hometowns is not None):
    hometownsDF = pd.DataFrame(np.array(hometowns))
else:
    hometownsDF = ""
if(travelStyleTags is not None):
    travelStyleTagsDF = pd.DataFrame(travelStyleTags)
else:
    travelStyleTagsDF = ""
if(points is not None):
    pointsDF = pd.DataFrame(np.array(points))
else:
    pointsDF = ""
if(levels is not None):
    levelsDF = pd.DataFrame(np.array(levels))
else:
    levelsDF = ""


# In[15]:

df2 = pd.concat([ageGendersDF,hometownsDF,travelStyleTagsDF,pointsDF,levelsDF], axis=1)
df2.columns = ['Age Gender','Hometown','Travel Style','Point','Level']


# In[16]:

print(df2)


# Save to mongodb

# db host
#client = MongoClient("localhost", 27017)
client = MongoClient("mongodb://ke5016:ke5016!@cluster0-shard-00-00-5ymmp.mongodb.net:27017,cluster0-shard-00-01-5ymmp.mongodb.net:27017,cluster0-shard-00-02-5ymmp.mongodb.net:27017/admin?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin")

# db name
db = client.tripadvisor

# collection name
collection = db.jwmarriot

# reset jwmarriot collection
collection.remove({})

num = len(names)
for i in range(num):
    document = {'Name':names[i].strip(),
                'Rating':ratings[i]}
    collection.insert(document)

print("number of documents inserted :", collection.count())

for x in collection.find():
    print(x['Name'])

client.close()

